# -*- coding: utf-8 -*-
"""
MultiCapture  -  multi-screenshot board for Windows

* Every capture is kept (nothing is overwritten) - history panel on the left
* Board views: Single / 2x2 / 3x3 / 4x4 / All  - drag cells to reorder
* The current view is copied to the clipboard automatically (paste into Outlook,
  Word, Excel, Teams ... exactly what you see: single image or the whole grid)
* Editable annotations (Select tool: move / resize / restyle / delete at any time)
    pen, highlighter, line, arrow, rectangle, ellipse,
    Word-like text boxes (font, size, bold, italic, underline, colour, background,
    border, alignment), callouts, numbered markers, stamps, blur
* PDF-style measurement: distance, perimeter, area, angle, calibrated scale
* Notes panel per screenshot (optionally included when copying / exporting)
* Export PNG / JPG / BMP / PDF, all screenshots to PNG files or one PDF
* Global hotkey Ctrl+Alt+S
* Optional extras (off by default, Options -> Extra features): pin to screen, text recognition (OCR),
  scrolling capture, screen recording to GIF / MP4 - see extras.py
"""
import copy
import ctypes
import ctypes.wintypes as wt
import io
import json
import math
import os
import queue
import random
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import uuid
from datetime import datetime
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageGrab, ImageTk

import extras
import solid3d
import themes
from i18n import LANG, LANGS, detect_lang, guide_text, shortcuts_text, tr

MODE_KEYS = ["Region", "Full screen", "Last region"]
SCROLL_MODE = "Scrolling"          # extra capture mode, only offered when scrolling capture is switched on
ALL_MODES = MODE_KEYS + [SCROLL_MODE]
# Optional features: settings key -> menu label. All are off until switched on in Options -> Extra features.
FEATURES = [("feat_pin", "Pin to screen"), ("feat_ocr", "Text recognition (OCR)"),
            ("feat_scroll", "Scrolling capture"), ("feat_record", "Screen recording (GIF / MP4)")]
REC_FPS = [5, 10, 15]
DELAY_KEYS = ["No delay", "3 s", "5 s", "10 s"]

APP_NAME = "MultiCapture"
VERSION = "1.4.0"
# Full-size screenshots kept in RAM at once; older ones are reloaded from the session folder on demand.
MAX_LOADED = 16

# --------------------------------------------------------------------------- DPI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
# Taskbar identity: the packaged .exe sets NO AppUserModelID, so Windows identifies it by the .exe
# path and takes the icon embedded in the .exe (pinning then works like any normal program).
# Only when running the .py with python.exe do we set one, to get our own taskbar button.
if not getattr(sys, "frozen", False):
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MultiCapture.Dev")
    except Exception:
        pass

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# --------------------------------------------------------------------------- paths
def package_family_name():
    """Family name when running as an MSIX package (Microsoft Store), else None."""
    try:
        n = ctypes.c_uint32(0)
        kernel32.GetCurrentPackageFamilyName(ctypes.byref(n), None)   # asks for the length
        if not n.value:
            return None
        buf = ctypes.create_unicode_buffer(n.value)
        if kernel32.GetCurrentPackageFamilyName(ctypes.byref(n), buf) != 0:
            return None
        return buf.value or None
    except Exception:
        return None


PACKAGE_FAMILY = package_family_name()
_APPDATA_BASE = os.environ.get("APPDATA", os.path.expanduser("~"))
if PACKAGE_FAMILY:
    # Store version: Windows would silently redirect writes under %APPDATA% into the package,
    # so "Open folder" in Explorer would show an empty folder. Use the package's own data folder
    # directly instead, so the app and Explorer see the same files. Windows removes it on uninstall.
    _APPDATA_BASE = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
                                 "Packages", PACKAGE_FAMILY, "LocalState")
APPDATA = os.path.join(_APPDATA_BASE, "MultiCapture")
_OLD_APPDATA = os.path.join(_APPDATA_BASE, "MultiCapture_HAO")   # folder name used up to v1.3.1
if not os.path.exists(APPDATA) and os.path.isdir(_OLD_APPDATA):
    try:
        os.rename(_OLD_APPDATA, APPDATA)   # keep history and settings from older versions
    except OSError:
        APPDATA = _OLD_APPDATA
SESSION_DIR = os.path.join(APPDATA, "session")
SETTINGS_FILE = os.path.join(APPDATA, "settings.json")
DEFAULT_SAVE_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "MultiCapture")
RES_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
THEMES_BUILTIN = os.path.join(RES_DIR, "themes")     # shipped with the program
THEMES_USER = os.path.join(APPDATA, "themes")         # downloaded, imported or self-made themes
THEMES_DOC_URL = f"https://github.com/{themes.REPO}/blob/{themes.BRANCH}/docs/THEMES.md"

# --------------------------------------------------------------------------- look
ACCENT = "#2563EB"
ACCENT_D = "#1D4ED8"
ACCENT_L = "#E8EFFE"
BG = "#F3F4F6"
PANEL = "#FFFFFF"
BORDER = "#E5E7EB"
TEXT = "#111827"
MUTED = "#6B7280"
CANVAS_BG = "#E7EAEE"
BTN = "#F3F4F6"          # small grey buttons
BTN_H = "#E5E7EB"
HOVER = "#EEF2F7"
ICON_C = "#374151"
ICON_ACC = "#2563EB"
SHADOW = "#C8CDD5"
NOTES_BG = "#FBFBFC"
TIP_BG = "#111827"
TIP_FG = "#FFFFFF"
OK_C = "#15803D"
FIELD = ["#FFFFFF"]      # drop-down / spin box background
THEME = [None]           # active themes.Theme (set by apply_theme before the UI is built)


def apply_theme(theme):
    """Sets the UI colours from a theme. Called once at start-up, before any widget exists."""
    global ACCENT, ACCENT_D, ACCENT_L, BG, PANEL, BORDER, TEXT, MUTED, CANVAS_BG
    global BTN, BTN_H, HOVER, ICON_C, ICON_ACC, SHADOW, NOTES_BG, TIP_BG, TIP_FG, OK_C
    c = theme.colors
    ACCENT, ACCENT_D, ACCENT_L = c["accent"], c["accent_dark"], c["accent_light"]
    BG, PANEL, BORDER, TEXT, MUTED, CANVAS_BG = c["bg"], c["panel"], c["border"], c["text"], c["muted"], c["canvas"]
    BTN, BTN_H, HOVER = c["button"], c["button_hover"], c["hover"]
    ICON_C, ICON_ACC, SHADOW, NOTES_BG = c["icon"], c["icon_accent"], c["shadow"], c["notes_bg"]
    TIP_BG, TIP_FG, OK_C = c["tooltip_bg"], c["tooltip_text"], c["success"]
    FIELD[0] = c["field"]
    THEME[0] = theme


def load_themes():
    return themes.discover([(THEMES_BUILTIN, "builtin"), (THEMES_USER, "user")])


def pick_random_theme(all_themes, current=None):
    """A random installed theme id, different from `current` when there is another one (None if none)."""
    ids = sorted(all_themes)
    others = [t for t in ids if t != current]
    return random.choice(others or ids) if ids else None


UI = ("Segoe UI", 9)
UI_B = ("Segoe UI Semibold", 9)
UI_H = ("Segoe UI Semibold", 8)
UI_S = ("Segoe UI", 8)
UI_BIG = ("Segoe UI Semibold", 10)

PALETTE = ["#E53935", "#FB8C00", "#FDD835", "#43A047", "#00ACC1", "#1E88E5",
           "#3949AB", "#8E24AA", "#D81B60", "#000000", "#757575", "#FFFFFF"]
VIEW_MODES = [("Single", 1), ("2×2", 4), ("3×3", 9), ("4×4", 16), ("All", 0)]
STAMPS = ["✔", "✘", "★", "!", "?", "⚠", "●", "➜", "♥", "✚"]
UNITS = ["mm", "cm", "m", "µm", "in", "ft"]

TOOLS = [
    ("select", "Select / move / resize  (V)", "v"),
    None,
    ("pen", "Pen  (P)", "p"),
    ("highlight", "Highlighter  (H)", "h"),
    ("line", "Line  (L)  - hold Shift for 45°", "l"),
    ("arrow", "Arrow  (A)  - hold Shift for 45°", "a"),
    ("rect", "Rectangle  (R)  - hold Shift for square", "r"),
    ("ellipse", "Ellipse  (E)  - hold Shift for circle", "e"),
    None,
    ("text", "Text box  (T)  - Word-like formatting on the right", "t"),
    ("callout", "Callout: drag from target to text  (C)", "c"),
    ("marker", "Numbered marker  (N)", "n"),
    ("stamp", "Stamp / symbol  (S)", "s"),
    ("mosaic", "Blur / pixelate area  (B)", "b"),
    None,
    ("dist", "Measure distance  (D)", "d"),
    ("perim", "Measure perimeter / polyline  (M)\nclick points, double-click or Enter to finish", "m"),
    ("area", "Measure area (polygon)  (G)\nclick points, double-click or Enter to finish", "g"),
    ("angle", "Measure angle  (Q) - click 3 points, vertex 2nd", "q"),
    ("calib", "Set scale from a known length  (K)", "k"),
]
TOOL_NAMES = {"select": "Select", "pen": "Pen", "highlight": "Highlighter", "line": "Line",
              "arrow": "Arrow", "rect": "Rectangle", "ellipse": "Ellipse", "text": "Text box",
              "callout": "Callout", "marker": "Numbered marker", "stamp": "Stamp",
              "mosaic": "Blur", "dist": "Distance", "perim": "Perimeter", "area": "Area",
              "angle": "Angle", "calib": "Scale reference"}

DEFAULT_SETTINGS = {
    "autocopy": True, "include_notes": True, "autosave": False, "save_dir": DEFAULT_SAVE_DIR,
    "keep_history": True, "history_limit": 200, "view": "Single", "color": "#E53935",
    "width": 3, "fill_on": False, "fill_color": "#FFF59D", "fill_alpha": 40,
    "family": "Segoe UI", "fsize": 20, "bold": False, "italic": False, "underline": False,
    "align": "left", "tbg_on": False, "tbg_color": "#FFFFFF", "border": False,
    "stamp": "✔", "decimals": 2, "default_scale": None, "next_num": 1,
    "geometry": "1440x880", "mode": "Region", "delay": "No delay", "lang": None, "guide_shown": False,
    "ask_on_close": True, "last_dir": DEFAULT_SAVE_DIR, "close_fmt": "PNG", "close_what": "unsaved",
    "open_after_save": False, "theme": "default", "theme_frame": True, "theme_random": False,
    "feat_pin": False, "feat_ocr": False, "feat_scroll": False, "feat_record": False,
    "ocr_lang": "", "rec_fps": 10, "rec_format": "mp4", "rec_mic": False, "rec_system": False,
}

# --------------------------------------------------------------------------- fonts
FONT_FILES = {  # regular, bold, italic, bold-italic
    "Segoe UI": ("segoeui.ttf", "segoeuib.ttf", "segoeuii.ttf", "segoeuiz.ttf"),
    "Arial": ("arial.ttf", "arialbd.ttf", "ariali.ttf", "arialbi.ttf"),
    "Calibri": ("calibri.ttf", "calibrib.ttf", "calibrii.ttf", "calibriz.ttf"),
    "Cambria": ("cambria.ttc", "cambriab.ttf", "cambriai.ttf", "cambriaz.ttf"),
    "Times New Roman": ("times.ttf", "timesbd.ttf", "timesi.ttf", "timesbi.ttf"),
    "Georgia": ("georgia.ttf", "georgiab.ttf", "georgiai.ttf", "georgiaz.ttf"),
    "Verdana": ("verdana.ttf", "verdanab.ttf", "verdanai.ttf", "verdanaz.ttf"),
    "Tahoma": ("tahoma.ttf", "tahomabd.ttf", None, None),
    "Trebuchet MS": ("trebuc.ttf", "trebucbd.ttf", "trebucit.ttf", "trebucbi.ttf"),
    "Consolas": ("consola.ttf", "consolab.ttf", "consolai.ttf", "consolaz.ttf"),
    "Courier New": ("cour.ttf", "courbd.ttf", "couri.ttf", "courbi.ttf"),
    "Comic Sans MS": ("comic.ttf", "comicbd.ttf", "comici.ttf", "comicz.ttf"),
    "Impact": ("impact.ttf", None, None, None),
    "Microsoft YaHei": ("msyh.ttc", "msyhbd.ttc", None, None),
    "SimSun": ("simsun.ttc", None, None, None),
    "SimHei": ("simhei.ttf", None, None, None),
    "KaiTi": ("simkai.ttf", None, None, None),
}
CJK_FAMILIES = {"Microsoft YaHei", "SimSun", "SimHei", "KaiTi"}
_font_cache = {}


def available_families():
    return [f for f, files in FONT_FILES.items()
            if files[0] and os.path.exists(os.path.join(FONTS_DIR, files[0]))] or ["Segoe UI"]


def pil_font(family, size, bold=False, italic=False):
    """Returns (font, synthetic_bold, synthetic_italic)."""
    size = max(4, int(round(size)))
    key = (family, size, bold, italic)
    if key in _font_cache:
        return _font_cache[key]
    files = FONT_FILES.get(family) or FONT_FILES["Segoe UI"]
    idx = (1 if bold else 0) + (2 if italic else 0)
    cand = [(idx, False, False)]
    if bold and italic:
        cand += [(1, False, True), (2, True, False), (0, True, True)]
    elif bold:
        cand += [(0, True, False)]
    elif italic:
        cand += [(0, False, True)]
    res = None
    for i, sb, si in cand:
        fn = files[i]
        if fn and os.path.exists(os.path.join(FONTS_DIR, fn)):
            try:
                res = (ImageFont.truetype(os.path.join(FONTS_DIR, fn), size), sb, si)
                break
            except OSError:
                pass
    if res is None:
        try:
            res = (ImageFont.truetype(os.path.join(FONTS_DIR, "segoeui.ttf"), size), bold, italic)
        except OSError:
            res = (ImageFont.load_default(size), bold, italic)
    _font_cache[key] = res
    return res


def _num_opt(v, default, lo, hi):
    try:
        return max(lo, min(hi, float(v)))
    except (TypeError, ValueError):
        return default


def frame_font(size, bold=False, text=""):
    return pil_font("Microsoft YaHei" if needs_cjk(text) else "Segoe UI", size, bold)[0]


def symbol_font(size):
    size = max(4, int(round(size)))
    key = ("__sym", size)
    if key not in _font_cache:
        for fn in ("seguisym.ttf", "seguiemj.ttf", "segoeui.ttf", "arial.ttf"):
            p = os.path.join(FONTS_DIR, fn)
            if os.path.exists(p):
                try:
                    _font_cache[key] = ImageFont.truetype(p, size)
                    break
                except OSError:
                    pass
        else:
            _font_cache[key] = ImageFont.load_default(size)
    return _font_cache[key]


def needs_cjk(text):
    return any(ord(ch) >= 0x2E80 for ch in text)


# --------------------------------------------------------------------------- colours
def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgba(h, a):
    return hex_rgb(h) + (int(a),)


def contrast(h):
    r, g, b = hex_rgb(h)
    return "#111111" if (0.299 * r + 0.587 * g + 0.114 * b) > 165 else "#FFFFFF"


# --------------------------------------------------------------------------- Windows helpers
def virtual_screen():
    return (user32.GetSystemMetrics(76), user32.GetSystemMetrics(77),
            user32.GetSystemMetrics(78), user32.GetSystemMetrics(79))


kernel32.GlobalAlloc.restype = ctypes.c_void_p
kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
user32.SetClipboardData.restype = ctypes.c_void_p
user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
user32.OpenClipboard.argtypes = [ctypes.c_void_p]
user32.RegisterClipboardFormatW.argtypes = [ctypes.c_wchar_p]
user32.RegisterClipboardFormatW.restype = ctypes.c_uint


def _hglobal(data):
    h = kernel32.GlobalAlloc(0x0002, len(data))
    if not h:
        return None
    p = kernel32.GlobalLock(h)
    ctypes.memmove(p, data, len(data))
    kernel32.GlobalUnlock(h)
    return h


def set_clipboard_image(img):
    """Puts the image on the clipboard as DIB + PNG (Outlook, Word, Excel, Teams...)."""
    rgb = img.convert("RGB")
    b = io.BytesIO()
    rgb.save(b, "BMP")
    dib = b.getvalue()[14:]
    b = io.BytesIO()
    rgb.save(b, "PNG", compress_level=1)
    png = b.getvalue()
    for _ in range(25):
        if user32.OpenClipboard(None):
            break
        time.sleep(0.03)
    else:
        return False
    try:
        user32.EmptyClipboard()
        for fmt, data in ((8, dib), (user32.RegisterClipboardFormatW("PNG"), png)):
            h = _hglobal(data)
            if h and not user32.SetClipboardData(fmt, h):
                kernel32.GlobalFree(h)
    finally:
        user32.CloseClipboard()
    return True


def hotkey_thread(q):
    MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x1, 0x2, 0x4000
    if not user32.RegisterHotKey(None, 1, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x53):
        q.put(("hotkey_failed",))
        return
    msg = wt.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        if msg.message == 0x0312:
            q.put(("capture",))


# --------------------------------------------------------------------------- geometry
def norm_box(b):
    x0, y0, x1, y1 = b
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def poly_dist(pts, x, y, closed=False):
    if len(pts) == 1:
        return math.hypot(x - pts[0][0], y - pts[0][1])
    seq = list(pts) + ([pts[0]] if closed else [])
    return min(seg_dist(x, y, *seq[i], *seq[i + 1]) for i in range(len(seq) - 1))


def point_in_poly(pts, x, y):
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-9) + x1:
            inside = not inside
    return inside


def poly_len(pts, closed=False):
    seq = list(pts) + ([pts[0]] if closed and len(pts) > 2 else [])
    return sum(math.hypot(seq[i + 1][0] - seq[i][0], seq[i + 1][1] - seq[i][1]) for i in range(len(seq) - 1))


def poly_area(pts):
    a = 0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


def angle_of(pts):
    (ax, ay), (vx, vy), (bx, by) = pts[:3]
    a1 = math.atan2(ay - vy, ax - vx)
    a2 = math.atan2(by - vy, bx - vx)
    d = abs(math.degrees(a1 - a2)) % 360
    return 360 - d if d > 180 else d


# --------------------------------------------------------------------------- measurement format
_DEC = [2]


def fmt_len(px, sc):
    k, u = sc
    return f"{px:.0f} px" if u == "px" else f"{px * k:.{_DEC[0]}f} {u}"


def fmt_area(px2, sc):
    k, u = sc
    return f"{px2:.0f} px²" if u == "px" else f"{px2 * k * k:.{_DEC[0]}f} {u}²"


# --------------------------------------------------------------------------- drawing primitives
def paste_rgba(img, layer, x, y):
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        if sx >= layer.width or sy >= layer.height:
            return
        layer = layer.crop((sx, sy, layer.width, layer.height))
        x, y = x + sx, y + sy
    if x >= img.width or y >= img.height:
        return
    img.alpha_composite(layer, (x, y))


def blend_draw(img, bbox, fn):
    """Draw translucent content: fn(draw, offset_x, offset_y) on a local layer."""
    x0, y0, x1, y1 = bbox
    x0 = max(0, int(math.floor(x0)) - 2)
    y0 = max(0, int(math.floor(y0)) - 2)
    x1 = min(img.width, int(math.ceil(x1)) + 2)
    y1 = min(img.height, int(math.ceil(y1)) + 2)
    if x1 <= x0 or y1 <= y0:
        return
    layer = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    fn(ImageDraw.Draw(layer), x0, y0)
    img.alpha_composite(layer, (x0, y0))


def draw_label(img, x, y, text, color, fs, anchor="mm"):
    font = pil_font("Segoe UI", fs, True)[0]
    d = ImageDraw.Draw(img)
    bb = d.multiline_textbbox((0, 0), text, font=font, spacing=2)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    pad = max(2, fs * 0.35)
    if anchor == "mm":
        bx, by = x - w / 2 - pad, y - h / 2 - pad
    else:  # "la": left-above
        bx, by = x + pad, y - h - 3 * pad
    d.rounded_rectangle((bx, by, bx + w + 2 * pad, by + h + 2 * pad), radius=max(2, fs * 0.3),
                        fill=color, outline="#FFFFFF", width=1)
    d.multiline_text((bx + pad - bb[0], by + pad - bb[1]), text, font=font, fill=contrast(color), spacing=2)


def dashed_line(d, p1, p2, fill, width, dash):
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    if L == 0:
        return
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    t, on = 0.0, True
    while t < L:
        t2 = min(L, t + dash)
        if on:
            d.line((x1 + ux * t, y1 + uy * t, x1 + ux * t2, y1 + uy * t2), fill=fill, width=width)
        t, on = t2, not on


def round_caps(d, pts, color, w):
    if w < 3:
        return
    r = w / 2
    for (x, y) in (pts[0], pts[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=color)


# --------------------------------------------------------------------------- text layout
def text_layout(o, s):
    fam = o.get("family", "Segoe UI")
    if needs_cjk(o.get("text", "")) and fam not in CJK_FAMILIES:
        fam = "Microsoft YaHei"
    font, sb, si = pil_font(fam, o["size"] * s, o.get("bold"), o.get("italic"))
    lines = o.get("text", "").split("\n")
    asc, desc = font.getmetrics()
    lh = (asc + desc) * 1.12
    widths = [font.getlength(l) for l in lines]
    tw = max(widths + [o["size"] * s * 0.5])
    pad = max(2.0, o["size"] * s * 0.28)
    H = lh * len(lines) + 2 * pad
    extra = (0.2 * H if si else 0) + (2 if sb else 0)
    W = tw + 2 * pad + extra
    return {"font": font, "sb": sb, "si": si, "lines": lines, "asc": asc, "lh": lh,
            "widths": widths, "tw": tw, "pad": pad, "W": W, "H": H}


def render_text_layer(o, s, L):
    Wi, Hi = int(math.ceil(L["W"])) + 1, int(math.ceil(L["H"])) + 1
    base = Image.new("RGBA", (Wi, Hi), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    if o.get("bg"):
        d.rectangle((0, 0, Wi - 1, Hi - 1), fill=o["bg"])
    txt = Image.new("RGBA", (Wi, Hi), (0, 0, 0, 0))
    dt = ImageDraw.Draw(txt)
    pad, tw, lh = L["pad"], L["tw"], L["lh"]
    sw = max(1, round(o["size"] * s / 28)) if L["sb"] else 0
    for i, line in enumerate(L["lines"]):
        al = o.get("align", "left")
        x = pad + ((tw - L["widths"][i]) / 2 if al == "center" else (tw - L["widths"][i]) if al == "right" else 0)
        y = pad + i * lh
        if line:
            dt.text((x, y), line, font=L["font"], fill=o["color"], stroke_width=sw, stroke_fill=o["color"])
            if o.get("underline"):
                uy = y + L["asc"] + max(1, o["size"] * s * 0.07)
                dt.line((x, uy, x + L["widths"][i], uy), fill=o["color"],
                        width=max(1, round(o["size"] * s / 15)))
    if L["si"]:
        k = 0.2
        txt = txt.transform(txt.size, Image.AFFINE, (1, k, -k * Hi, 0, 1, 0), resample=Image.BICUBIC)
    base.alpha_composite(txt)
    if o.get("border"):
        d.rectangle((0, 0, Wi - 1, Hi - 1), outline=o.get("border_color") or o["color"],
                    width=max(1, round(1.5 * s)))
    return base


# --------------------------------------------------------------------------- object rendering
def draw_objects(img, objs, s, ox, oy, sc, skip_id=None):
    tf = lambda x, y: ((x - ox) * s, (y - oy) * s)  # noqa: E731
    for o in objs:
        try:
            if o.get("id") == skip_id and o["type"] == "text":
                draw_text_obj(img, o, s, tf, only_leader=True)
                continue
            DRAWERS[o["type"]](img, o, s, tf, sc)
        except Exception as ex:  # never let a single bad object break rendering
            print("draw error", o.get("type"), ex)
    return img


def _lw(o, s, mult=1.0):
    return max(1, int(round(o.get("width", 3) * mult * s)))


def d_pen(img, o, s, tf, sc):
    pts = [tf(*p) for p in o["pts"]]
    w = _lw(o, s)
    d = ImageDraw.Draw(img)
    if len(pts) == 1:
        x, y = pts[0]
        r = max(1, w / 2)
        d.ellipse((x - r, y - r, x + r, y + r), fill=o["color"])
        return
    d.line(pts, fill=o["color"], width=w, joint="curve")
    round_caps(d, pts, o["color"], w)


def d_highlight(img, o, s, tf, sc):
    pts = [tf(*p) for p in o["pts"]]
    w = _lw(o, s, 3)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    col = rgba(o["color"], 105)

    def fn(d, x0, y0):
        q = [(x - x0, y - y0) for x, y in pts]
        if len(q) == 1:
            q = q * 2
        d.line(q, fill=col, width=w, joint="curve")
        round_caps(d, q, col, w)
    blend_draw(img, (min(xs) - w, min(ys) - w, max(xs) + w, max(ys) + w), fn)


def d_line(img, o, s, tf, sc):
    p1, p2 = tf(*o["p"][0]), tf(*o["p"][1])
    w = _lw(o, s)
    d = ImageDraw.Draw(img)
    d.line((p1, p2), fill=o["color"], width=w)
    round_caps(d, [p1, p2], o["color"], w)


def arrow_head(d, p1, p2, color, w, hl):
    (x0, y0), (x1, y1) = p1, p2
    ang = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    hl = min(hl, L * 0.9) if L > 0 else hl
    bx, by = x1 - hl * 0.75 * math.cos(ang), y1 - hl * 0.75 * math.sin(ang)
    d.line((x0, y0, bx, by), fill=color, width=w)
    a = 0.42
    d.polygon([(x1, y1), (x1 - hl * math.cos(ang - a), y1 - hl * math.sin(ang - a)),
               (x1 - hl * math.cos(ang + a), y1 - hl * math.sin(ang + a))], fill=color)


def d_arrow(img, o, s, tf, sc):
    p1, p2 = tf(*o["p"][0]), tf(*o["p"][1])
    w = _lw(o, s)
    arrow_head(ImageDraw.Draw(img), p1, p2, o["color"], w, (10 + o.get("width", 3) * 3) * s)


def d_shape(img, o, s, tf, sc):
    if o.get("solid"):
        return solid3d.d_solid(img, o, s, tf, sc)
    x0, y0, x1, y1 = norm_box(o["box"])
    (a, b), (c, e) = tf(x0, y0), tf(x1, y1)
    w = _lw(o, s)
    ell = o["type"] == "ellipse"
    if o.get("fill"):
        col = rgba(o["fill"], o.get("fill_alpha", 40) * 2.55)

        def fn(d, ox_, oy_):
            (d.ellipse if ell else d.rectangle)((a - ox_, b - oy_, c - ox_, e - oy_), fill=col)
        blend_draw(img, (a, b, c, e), fn)
    if o.get("width", 3) > 0:
        d = ImageDraw.Draw(img)
        (d.ellipse if ell else d.rectangle)((a, b, max(a, c), max(b, e)), outline=o["color"], width=w)


def d_mosaic(img, o, s, tf, sc):
    x0, y0, x1, y1 = norm_box(o["box"])
    (a, b), (c, e) = tf(x0, y0), tf(x1, y1)
    a, b = max(0, int(a)), max(0, int(b))
    c, e = min(img.width, int(c)), min(img.height, int(e))
    if c - a < 2 or e - b < 2:
        return
    blk = max(2, int(round(o.get("block", 10) * s)))
    reg = img.crop((a, b, c, e)).convert("RGB")
    small = reg.resize((max(1, reg.width // blk), max(1, reg.height // blk)), Image.BOX)
    img.paste(small.resize(reg.size, Image.NEAREST).convert("RGBA"), (a, b))


def draw_text_obj(img, o, s, tf, sc=None, only_leader=False):
    L = text_layout(o, s)
    bx, by = tf(o["x"], o["y"])
    W, H = L["W"], L["H"]
    if o.get("leader"):
        lx, ly = tf(*o["leader"])
        if not (bx <= lx <= bx + W and by <= ly <= by + H):
            nx = min(max(lx, bx), bx + W)
            ny = min(max(ly, by), by + H)
            if bx < nx < bx + W:            # attach to middle of top / bottom side
                nx = bx + W / 2
            elif by < ny < by + H:          # attach to middle of left / right side
                ny = by + H / 2
            d = ImageDraw.Draw(img)
            lw = _lw(o, s)
            d.line((lx, ly, nx, ny), fill=o["color"], width=lw)
            r = max(2.5, lw * 1.6)
            d.ellipse((lx - r, ly - r, lx + r, ly + r), fill=o["color"])
    if only_leader:
        return
    paste_rgba(img, render_text_layer(o, s, L), bx, by)


def d_marker(img, o, s, tf, sc):
    x, y = tf(o["x"], o["y"])
    r = o["size"] * 0.85 * s
    d = ImageDraw.Draw(img)
    d.ellipse((x - r, y - r, x + r, y + r), fill=o["color"], outline="#FFFFFF", width=max(1, round(r * 0.12)))
    font = pil_font("Segoe UI", r * (1.15 if o["n"] < 10 else 0.9), True)[0]
    d.text((x, y), str(o["n"]), font=font, fill=contrast(o["color"]), anchor="mm")


def d_stamp(img, o, s, tf, sc):
    x, y = tf(o["x"], o["y"])
    font = symbol_font(o["size"] * 1.6 * s)
    ImageDraw.Draw(img).text((x, y), o["sym"], font=font, fill=o["color"], anchor="mm",
                             stroke_width=max(1, round(o["size"] * s / 12)), stroke_fill="#FFFFFF")


def d_dist(img, o, s, tf, sc):
    p1, p2 = tf(*o["p"][0]), tf(*o["p"][1])
    w = _lw(o, s)
    d = ImageDraw.Draw(img)
    calib = o["type"] == "calib"
    if calib:
        dashed_line(d, p1, p2, o["color"], w, max(4, 6 * s + w * 2))
    else:
        d.line((p1, p2), fill=o["color"], width=w)
    L = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    if L > 0:
        nx, ny = -(p2[1] - p1[1]) / L, (p2[0] - p1[0]) / L
        t = (6 + o.get("width", 3) * 2) * s
        for (x, y) in (p1, p2):
            d.line((x - nx * t, y - ny * t, x + nx * t, y + ny * t), fill=o["color"], width=w)
        px = math.hypot(o["p"][1][0] - o["p"][0][0], o["p"][1][1] - o["p"][0][1])
        txt = (f"Ref {o['real']:g} {o['unit']}" if calib else fmt_len(px, sc))
        fs = o.get("fs", 14) * s
        off = fs * 1.1
        if ny > 0:
            nx, ny = -nx, -ny
        mx, my = (p1[0] + p2[0]) / 2 + nx * off, (p1[1] + p2[1]) / 2 + ny * off
        draw_label(img, mx, my, txt, o["color"], fs)


def d_perim(img, o, s, tf, sc):
    pts = [tf(*p) for p in o["pts"]]
    w = _lw(o, s)
    d = ImageDraw.Draw(img)
    if len(pts) > 1:
        d.line(pts, fill=o["color"], width=w, joint="curve")
    r = max(2, w * 1.2)
    for x, y in pts:
        d.ellipse((x - r, y - r, x + r, y + r), fill=o["color"])
    if len(pts) > 1:
        x, y = pts[-1]
        draw_label(img, x, y, fmt_len(poly_len(o["pts"]), sc), o["color"], o.get("fs", 14) * s, anchor="la")


def d_area(img, o, s, tf, sc):
    if o.get("solid") and len(o["pts"]) >= 3:
        return solid3d.d_solid(img, o, s, tf, sc)
    pts = [tf(*p) for p in o["pts"]]
    w = _lw(o, s)
    if len(pts) >= 3:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        col = rgba(o["color"], o.get("fill_alpha", 25) * 2.55)
        blend_draw(img, (min(xs), min(ys), max(xs), max(ys)),
                   lambda d, x0, y0: d.polygon([(x - x0, y - y0) for x, y in pts], fill=col))
    d = ImageDraw.Draw(img)
    if len(pts) > 1:
        d.line(pts + ([pts[0]] if len(pts) > 2 else []), fill=o["color"], width=w, joint="curve")
    r = max(2, w * 1.2)
    for x, y in pts:
        d.ellipse((x - r, y - r, x + r, y + r), fill=o["color"])
    if len(pts) >= 3:
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        txt = f"A = {fmt_area(poly_area(o['pts']), sc)}\nP = {fmt_len(poly_len(o['pts'], True), sc)}"
        draw_label(img, cx, cy, txt, o["color"], o.get("fs", 14) * s)


def d_angle(img, o, s, tf, sc):
    pts = [tf(*p) for p in o["pts"]]
    w = _lw(o, s)
    d = ImageDraw.Draw(img)
    if len(pts) > 1:
        d.line(pts[:3], fill=o["color"], width=w, joint="curve")
    r = max(2, w * 1.2)
    for x, y in pts[:3]:
        d.ellipse((x - r, y - r, x + r, y + r), fill=o["color"])
    if len(pts) >= 3:
        (ax, ay), (vx, vy), (bx, by) = pts[:3]
        a1 = math.degrees(math.atan2(ay - vy, ax - vx))
        a2 = math.degrees(math.atan2(by - vy, bx - vx))
        start, end = a1, a2
        if (end - start) % 360 > 180:
            start, end = end, start
        rad = max(12 * s, min(math.hypot(ax - vx, ay - vy), math.hypot(bx - vx, by - vy)) * 0.3)
        d.arc((vx - rad, vy - rad, vx + rad, vy + rad), start, end, fill=o["color"], width=max(1, w))
        mid = math.radians(start + ((end - start) % 360) / 2)
        lr = rad + o.get("fs", 14) * s * 1.6
        draw_label(img, vx + lr * math.cos(mid), vy + lr * math.sin(mid),
                   f"{angle_of(o['pts']):.1f}°", o["color"], o.get("fs", 14) * s)


DRAWERS = {"pen": d_pen, "highlight": d_highlight, "line": d_line, "arrow": d_arrow,
           "rect": d_shape, "ellipse": d_shape, "mosaic": d_mosaic, "text": draw_text_obj,
           "marker": d_marker, "stamp": d_stamp, "dist": d_dist, "calib": d_dist,
           "perim": d_perim, "area": d_area, "angle": d_angle}


# --------------------------------------------------------------------------- object geometry
def obj_bbox(o):
    t = o["type"]
    if o.get("solid") and t in solid3d.SOLID_TYPES:
        return solid3d.solid_bbox(o)
    if t in ("pen", "highlight", "perim", "area", "angle", "line", "arrow", "dist", "calib"):
        pts = o["pts"] if "pts" in o else o["p"]
        m = o.get("width", 2) * (1.5 if t == "highlight" else 0.5)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return [min(xs) - m, min(ys) - m, max(xs) + m, max(ys) + m]
    if t in ("rect", "ellipse", "mosaic"):
        return norm_box(o["box"])
    if t == "text":
        L = text_layout(o, 1)
        return [o["x"], o["y"], o["x"] + L["W"], o["y"] + L["H"]]
    if t in ("marker", "stamp"):
        r = o["size"] * (0.85 if t == "marker" else 0.9)
        return [o["x"] - r, o["y"] - r, o["x"] + r, o["y"] + r]
    return [0, 0, 0, 0]


def hit_obj(o, x, y, tol):
    t = o["type"]
    if o.get("solid") and t in solid3d.SOLID_TYPES:
        return solid3d.solid_hit(o, x, y, tol)
    w = o.get("width", 2)
    if t in ("pen", "perim", "angle"):
        return poly_dist(o["pts"], x, y) <= tol + w / 2
    if t == "highlight":
        return poly_dist(o["pts"], x, y) <= tol + w * 1.5
    if t in ("line", "arrow", "dist", "calib"):
        return seg_dist(x, y, *o["p"][0], *o["p"][1]) <= tol + w / 2
    if t == "area":
        return point_in_poly(o["pts"], x, y) or poly_dist(o["pts"], x, y, True) <= tol + w / 2
    if t in ("rect", "ellipse") and not o.get("fill"):
        x0, y0, x1, y1 = norm_box(o["box"])
        m = tol + w / 2
        if t == "rect":
            outer = x0 - m <= x <= x1 + m and y0 - m <= y <= y1 + m
            inner = x0 + m < x < x1 - m and y0 + m < y < y1 - m
            return outer and not inner
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, max(1, (x1 - x0) / 2), max(1, (y1 - y0) / 2)
        v = math.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
        return abs(v - 1) * min(rx, ry) <= m
    x0, y0, x1, y1 = obj_bbox(o)
    if t == "text" and o.get("leader") and seg_dist(x, y, *o["leader"], (x0 + x1) / 2, (y0 + y1) / 2) <= tol:
        return True
    return x0 - tol <= x <= x1 + tol and y0 - tol <= y <= y1 + tol


def move_obj(o, dx, dy):
    for k in ("pts", "p"):
        if k in o:
            o[k] = [[px + dx, py + dy] for px, py in o[k]]
    if "box" in o:
        b = o["box"]
        o["box"] = [b[0] + dx, b[1] + dy, b[2] + dx, b[3] + dy]
    if "x" in o:
        o["x"] += dx
        o["y"] += dy
    if o.get("leader"):
        o["leader"] = [o["leader"][0] + dx, o["leader"][1] + dy]


def handles(o):
    """Resize handles. A pseudo-3D solid gets one more at the end: the depth / angle handle."""
    base = _base_handles(o)
    if o.get("solid") and o["type"] in solid3d.SOLID_TYPES:
        base.append(solid3d.solid_handle(o))
    return base


def _base_handles(o):
    t = o["type"]
    if t in ("rect", "ellipse", "mosaic"):
        x0, y0, x1, y1 = o["box"]
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if t in ("line", "arrow", "dist", "calib"):
        return [tuple(p) for p in o["p"]]
    if t in ("perim", "area", "angle"):
        return [tuple(p) for p in o["pts"]]
    if t == "text" and o.get("leader"):
        return [tuple(o["leader"])]
    return []


def set_handle(o, i, x, y):
    t = o["type"]
    if o.get("solid") and t in solid3d.SOLID_TYPES and i == len(_base_handles(o)):
        solid3d.set_solid_handle(o, x, y)
        return
    if t in ("rect", "ellipse", "mosaic"):
        b = o["box"]
        if i == 0:
            b[0], b[1] = x, y
        elif i == 1:
            b[2], b[1] = x, y
        elif i == 2:
            b[2], b[3] = x, y
        else:
            b[0], b[3] = x, y
    elif t in ("line", "arrow", "dist", "calib"):
        o["p"][i] = [x, y]
    elif t in ("perim", "area", "angle"):
        o["pts"][i] = [x, y]
    elif t == "text":
        o["leader"] = [x, y]


# --------------------------------------------------------------------------- composition
def wrap_text(text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if font.getlength(line + ch) <= maxw or not line:
                line += ch
            else:
                sp = line.rfind(" ")
                if sp > 0 and ch != " ":
                    out.append(line[:sp])
                    line = line[sp + 1:] + ch
                else:
                    out.append(line)
                    line = ch.lstrip()
        out.append(line)
    return out


def add_notes_strip(img, notes, title=None):
    W = max(img.width, 360)
    fs = max(13, min(22, W // 55))
    font = pil_font("Microsoft YaHei" if needs_cjk(notes) else "Segoe UI", fs)[0]
    bold = pil_font("Segoe UI", fs * 0.85, True)[0]
    pad = fs
    lines = wrap_text(notes.strip(), font, W - 2 * pad - 6)
    lh = int(fs * 1.5)
    head = int(fs * 1.4) if title else 0
    H = pad * 2 + lh * len(lines) + head
    out = Image.new("RGB", (W, img.height + H), "#FFFFFF")
    out.paste(img.convert("RGB"), ((W - img.width) // 2, 0))
    d = ImageDraw.Draw(out)
    d.rectangle((0, img.height, W, out.height), fill="#F8FAFC")
    d.line((0, img.height, W, img.height), fill="#D0D5DD", width=1)
    d.rectangle((0, img.height + 1, 3, out.height), fill=ACCENT)
    y = img.height + pad
    if title:
        d.text((pad + 4, y), title, font=bold, fill=ACCENT)
        y += head
    for l in lines:
        d.text((pad + 4, y), l, font=font, fill="#1F2937")
        y += lh
    return out


def grid_shape(n):
    cols = max(1, math.ceil(math.sqrt(n)))
    return cols, max(1, math.ceil(n / cols))


def compose_grid(images, gap=12, max_cell=1000, bg="#FFFFFF"):
    cols, rows = grid_shape(len(images))
    cw = min(max_cell, max(i.width for i in images))
    ch = min(max_cell, max(i.height for i in images))
    out = Image.new("RGB", (cols * cw + (cols + 1) * gap, rows * ch + (rows + 1) * gap), bg)
    d = ImageDraw.Draw(out)
    for k, im in enumerate(images):
        r, c = divmod(k, cols)
        t = im.convert("RGB")
        s = min(cw / t.width, ch / t.height, 1.0)
        if s < 1:
            t = t.resize((max(1, int(t.width * s)), max(1, int(t.height * s))), Image.LANCZOS)
        x = gap + c * (cw + gap) + (cw - t.width) // 2
        y = gap + r * (ch + gap) + (ch - t.height) // 2
        out.paste(t, (x, y))
        d.rectangle((x - 1, y - 1, x + t.width, y + t.height), outline="#D0D5DD")
    return out


SAVE_FORMATS = {"PNG": ".png", "JPG": ".jpg", "BMP": ".bmp", "TIFF": ".tif", "WEBP": ".webp", "PDF": ".pdf"}
SAVE_FILETYPES = [("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("BMP image", "*.bmp"),
                  ("TIFF image", "*.tif"), ("WebP image", "*.webp"), ("PDF document", "*.pdf")]


def save_image(img, p):
    ext = os.path.splitext(p)[1].lower()
    if ext == ".pdf":
        img.convert("RGB").save(p, "PDF", resolution=96)
    elif ext in (".jpg", ".jpeg"):
        img.convert("RGB").save(p, quality=95)
    elif ext == ".bmp":
        img.convert("RGB").save(p)
    elif ext in (".tif", ".tiff"):
        img.save(p, compression="tiff_lzw")
    elif ext == ".webp":
        img.save(p, quality=95)
    else:
        img.save(p)


def unique_path(folder, name, ext):
    p = os.path.join(folder, name + ext)
    i = 1
    while os.path.exists(p):
        p = os.path.join(folder, f"{name}_{i}{ext}")
        i += 1
    return p


# --------------------------------------------------------------------------- tool icons
def make_tool_icon(key, px):
    return ImageTk.PhotoImage(theme_icon(THEME[0], key, px))


def theme_icon(theme, key, px):
    """RGBA icon for a function: the theme's own picture if it has one, else the built-in drawing."""
    im = theme.icon(key) if theme else None
    if im is not None:
        im = im.copy()
        im.thumbnail((px, px), Image.LANCZOS)
        out = Image.new("RGBA", (px, px), (0, 0, 0, 0))
        out.alpha_composite(im, ((px - im.width) // 2, (px - im.height) // 2))
        return out
    if key not in themes.TOOL_ICON_KEYS:
        return None
    c = theme.colors if theme else themes.DEFAULT_COLORS
    return tool_icon_image(key, c["icon"], c["icon_accent"]).resize((px, px), Image.LANCZOS)


def tool_icon_image(key, color="#374151", accent="#2563EB"):
    S = 96
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = hex_rgb(color) + (255,)
    acc = hex_rgb(accent) + (255,)
    w = 7
    if key == "select":
        d.polygon([(28, 12), (28, 78), (44, 63), (56, 86), (68, 80), (56, 58), (78, 58)], fill=c)
    elif key == "pen":
        d.line((26, 70, 70, 26), fill=c, width=16)
        d.polygon([(14, 82), (19, 63), (33, 77)], fill=c)
        d.line((62, 18, 78, 34), fill=acc, width=16)
    elif key == "highlight":
        d.rectangle((10, 66, 86, 82), fill=(253, 216, 53, 230))
        d.polygon([(34, 58), (58, 14), (78, 26), (54, 70)], fill=c)
        d.polygon([(34, 58), (54, 70), (40, 76)], fill=(253, 200, 20, 255))
    elif key == "line":
        d.line((16, 80, 80, 16), fill=c, width=w)
    elif key == "arrow":
        d.line((16, 80, 64, 32), fill=c, width=w)
        d.polygon([(82, 14), (50, 24), (72, 46)], fill=c)
    elif key == "rect":
        d.rectangle((14, 24, 82, 72), outline=c, width=w)
    elif key == "ellipse":
        d.ellipse((12, 22, 84, 74), outline=c, width=w)
    elif key == "text":
        d.text((48, 50), "T", font=pil_font("Segoe UI", 84, True)[0], fill=c, anchor="mm")
    elif key == "callout":
        d.rounded_rectangle((8, 12, 88, 62), radius=12, outline=c, width=w)
        d.polygon([(26, 58), (18, 86), (46, 58)], fill=c)
        d.line((22, 30, 74, 30), fill=c, width=6)
        d.line((22, 44, 58, 44), fill=c, width=6)
    elif key == "marker":
        d.ellipse((12, 12, 84, 84), fill=acc)
        d.text((48, 49), "1", font=pil_font("Segoe UI", 56, True)[0], fill="white", anchor="mm")
    elif key == "stamp":
        d.line([(16, 50), (40, 74), (82, 24)], fill=(67, 160, 71, 255), width=14, joint="curve")
    elif key == "mosaic":
        for i in range(4):
            for j in range(4):
                g = 90 + ((i + j) % 2) * 90 + (i * 7)
                d.rectangle((12 + i * 18, 12 + j * 18, 29 + i * 18, 29 + j * 18), fill=(g, g, g + 10, 255))
    elif key == "dist":
        d.line((14, 48, 82, 48), fill=c, width=6)
        d.line((10, 28, 10, 68), fill=c, width=6)
        d.line((86, 28, 86, 68), fill=c, width=6)
        d.polygon([(14, 48), (30, 38), (30, 58)], fill=c)
        d.polygon([(82, 48), (66, 38), (66, 58)], fill=c)
    elif key == "perim":
        pts = [(12, 76), (34, 28), (60, 64), (84, 20)]
        d.line(pts, fill=c, width=6, joint="curve")
        for x, y in pts:
            d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=acc)
    elif key == "area":
        pts = [(20, 28), (62, 12), (86, 52), (56, 84), (12, 64)]
        d.polygon(pts, fill=acc[:3] + (80,))
        d.line(pts + [pts[0]], fill=c, width=6, joint="curve")
    elif key == "angle":
        d.line((14, 80, 86, 80), fill=c, width=6)
        d.line((14, 80, 66, 18), fill=c, width=6)
        d.arc((-22, 44, 50, 116), -50, 0, fill=acc, width=7)
    elif key == "calib":
        d.rounded_rectangle((6, 32, 90, 64), radius=6, outline=c, width=6)
        for i, x in enumerate(range(18, 86, 10)):
            d.line((x, 34, x, 46 if i % 2 else 52), fill=c, width=4)
    return im


# --------------------------------------------------------------------------- small widgets
class Tooltip:
    def __init__(self, w, text, below=False):
        self.w, self.text, self.below, self.tip, self.job = w, text, below, None, None
        w.bind("<Enter>", self._sched, add="+")
        w.bind("<Leave>", self._hide, add="+")
        w.bind("<ButtonPress>", self._hide, add="+")

    def _sched(self, e):
        self._cancel()
        self.job = self.w.after(450, self._show)

    def _cancel(self):
        if self.job:
            self.w.after_cancel(self.job)
            self.job = None

    def _show(self):
        if self.below:
            x, y = self.w.winfo_rootx(), self.w.winfo_rooty() + self.w.winfo_height() + 4
        else:
            x, y = self.w.winfo_rootx() + self.w.winfo_width() + 6, self.w.winfo_rooty() + 2
        self.tip = tk.Toplevel(self.w)
        self.tip.overrideredirect(True)
        self.tip.attributes("-topmost", True)
        tk.Label(self.tip, text=self.text, bg=TIP_BG, fg=TIP_FG, font=UI_S, padx=8, pady=4,
                 justify="left").pack()
        self.tip.geometry(f"+{x}+{y}")

    def _hide(self, e=None):
        self._cancel()
        if self.tip:
            self.tip.destroy()
            self.tip = None


class FlatButton(tk.Label):
    """Label based button: never steals keyboard focus (important while editing text)."""

    def __init__(self, parent, text="", command=None, bg=None, fg=None, hover=None,
                 font=UI, padx=10, pady=4, tip=None, tip_below=True, **kw):
        bg = PANEL if bg is None else bg
        fg = TEXT if fg is None else fg
        hover = HOVER if hover is None else hover
        super().__init__(parent, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady,
                         cursor="hand2", **kw)
        self._bg, self._hover, self.command = bg, hover, command
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))
        self.bind("<Button-1>", self._click)
        if tip:
            Tooltip(self, tip, below=tip_below)

    def _click(self, e):
        if self.command:
            self.command()

    def set_colors(self, bg, fg=None, hover=None):
        self._bg = bg
        self._hover = hover or self._hover
        self.configure(bg=bg)
        if fg:
            self.configure(fg=fg)


# --------------------------------------------------------------------------- region selector
class RegionSelector:
    def __init__(self, master, screenshot, origin, on_done):
        self.full, self.on_done = screenshot, on_done
        vx, vy, vw, vh = origin
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.geometry(f"{vw}x{vh}{vx:+d}{vy:+d}")
        self.win.configure(cursor="crosshair")
        self.bg = ImageTk.PhotoImage(ImageEnhance.Brightness(screenshot).enhance(0.5))
        self.c = tk.Canvas(self.win, width=vw, height=vh, highlightthickness=0, bd=0)
        self.c.pack(fill="both", expand=True)
        self.c.create_image(0, 0, anchor="nw", image=self.bg)
        hint = self.c.create_text(-vx + 32, -vy + 33, anchor="w", fill="white", font=("Segoe UI", 11),
                                  text=tr("Drag to select an area   ·   Esc / right-click to cancel"))
        bb = self.c.bbox(hint)
        bg_ = self.c.create_rectangle(-vx + 20, -vy + 16, bb[2] + 12, -vy + 50, fill="#111827", outline="")
        self.c.tag_raise(hint, bg_)
        self.hx = self.c.create_line(0, 0, 0, 0, fill="#93C5FD", dash=(3, 3))
        self.hy = self.c.create_line(0, 0, 0, 0, fill="#93C5FD", dash=(3, 3))
        self.vw, self.vh = vw, vh
        self.start, self.crop_img, self.ids = None, None, []
        self.c.bind("<Motion>", self.move)
        self.c.bind("<ButtonPress-1>", lambda e: setattr(self, "start", (e.x, e.y)))
        self.c.bind("<B1-Motion>", self.drag)
        self.c.bind("<ButtonRelease-1>", self.release)
        self.win.bind("<Escape>", lambda e: self.finish(None))
        self.c.bind("<ButtonPress-3>", lambda e: self.finish(None))
        self.win.after(40, self.win.focus_force)

    def move(self, e):
        self.c.coords(self.hx, 0, e.y, self.vw, e.y)
        self.c.coords(self.hy, e.x, 0, e.x, self.vh)

    def _box(self, e):
        x0, y0 = self.start
        return min(x0, e.x), min(y0, e.y), max(x0, e.x), max(y0, e.y)

    def drag(self, e):
        self.move(e)
        if not self.start:
            return
        x0, y0, x1, y1 = self._box(e)
        for i in self.ids:
            self.c.delete(i)
        self.ids = []
        if x1 - x0 > 1 and y1 - y0 > 1:
            self.crop_img = ImageTk.PhotoImage(self.full.crop((x0, y0, x1, y1)))
            self.ids.append(self.c.create_image(x0, y0, anchor="nw", image=self.crop_img))
        self.ids.append(self.c.create_rectangle(x0, y0, x1, y1, outline="#3B82F6", width=2))
        ty = y0 - 14 if y0 > 30 else y1 + 14
        self.ids.append(self.c.create_rectangle(x0, ty - 11, x0 + 92, ty + 11, fill="#2563EB", outline=""))
        self.ids.append(self.c.create_text(x0 + 46, ty, fill="white", text=f"{x1 - x0} × {y1 - y0}",
                                           font=("Segoe UI", 9, "bold")))

    def release(self, e):
        if not self.start:
            return
        x0, y0, x1, y1 = self._box(e)
        if x1 - x0 < 3 or y1 - y0 < 3:
            self.start = None
            return
        self.finish(self.full.crop((x0, y0, x1, y1)), (x0, y0, x1, y1))

    def finish(self, img, box=None):
        self.win.destroy()
        self.on_done(img, box)


# --------------------------------------------------------------------------- dialogs
class ScaleDialog(tk.Toplevel):
    """Ask for a real-world length (calibration) or a direct 'unit per pixel' value."""

    def __init__(self, master, title, prompt, value="", unit="mm", show_all=True):
        super().__init__(master)
        self.title(title)
        self.configure(bg=PANEL, padx=18, pady=14)
        self.resizable(False, False)
        self.transient(master)
        self.result = None
        tk.Label(self, text=prompt, bg=PANEL, font=UI, justify="left").grid(row=0, column=0, columnspan=2, sticky="w")
        self.val = tk.StringVar(value=value)
        self.unit = tk.StringVar(value=unit)
        e = ttk.Entry(self, textvariable=self.val, width=14)
        e.grid(row=1, column=0, pady=10, sticky="w")
        ttk.Combobox(self, textvariable=self.unit, values=UNITS, width=6, state="readonly").grid(row=1, column=1, padx=6, sticky="w")
        self.all = tk.BooleanVar(value=False)
        if show_all:
            ttk.Checkbutton(self, text=tr("Use as default scale for all screenshots without their own scale"),
                            variable=self.all).grid(row=2, column=0, columnspan=2, sticky="w")
        bf = tk.Frame(self, bg=PANEL)
        bf.grid(row=3, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(bf, text=tr("Cancel"), command=self.destroy).pack(side="right")
        ttk.Button(bf, text=tr("OK"), command=self.ok).pack(side="right", padx=6)
        self.bind("<Return>", lambda ev: self.ok())
        self.bind("<Escape>", lambda ev: self.destroy())
        e.focus_set()
        e.select_range(0, "end")
        self.update_idletasks()
        x = master.winfo_rootx() + master.winfo_width() // 2 - self.winfo_width() // 2
        y = master.winfo_rooty() + master.winfo_height() // 3
        self.geometry(f"+{x}+{y}")
        self.grab_set()
        self.wait_window()

    def ok(self):
        try:
            v = float(self.val.get().replace(",", "."))
            if v <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(tr("Scale"), tr("Please enter a positive number."), parent=self)
            return
        self.result = (v, self.unit.get(), self.all.get())
        self.destroy()


class CloseDialog(tk.Toplevel):
    """Asked when closing with screenshots that were never saved to a file."""

    def __init__(self, master, n_unsaved, st, view_label):
        super().__init__(master)
        self.title(tr("Save before closing?"))
        self.configure(bg=PANEL, padx=22, pady=16)
        self.resizable(False, False)
        self.transient(master)
        self.result = None
        lbl = dict(bg=PANEL, anchor="w", justify="left")
        tk.Label(self, text=tr("Save before closing?"), font=("Segoe UI Semibold", 13), fg=TEXT, **lbl).pack(fill="x")
        tk.Label(self, text=tr("{n} screenshot(s) have not been saved to a file yet.", n=n_unsaved), font=UI,
                 fg=MUTED, **lbl).pack(fill="x", pady=(2, 10))

        def head(t):
            tk.Label(self, text=tr(t), font=UI_H, fg=MUTED, **lbl).pack(fill="x", pady=(8, 3))

        head("WHAT TO SAVE")
        self.what = tk.StringVar(value=st.get("close_what", "unsaved"))
        for val, txt in (("view", tr("Current view ({v})", v=view_label)),
                         ("unsaved", tr("Only unsaved screenshots – one file each")),
                         ("each", tr("All screenshots – one file each")),
                         ("pdf", tr("All screenshots in one PDF"))):
            ttk.Radiobutton(self, text=txt, value=val, variable=self.what, command=self._sync).pack(anchor="w")

        head("FORMAT")
        self.fmt = tk.StringVar(value=st.get("close_fmt", "PNG"))
        self.fmt_cb = ttk.Combobox(self, textvariable=self.fmt, values=list(SAVE_FORMATS), state="readonly", width=10)
        self.fmt_cb.pack(anchor="w")

        head("FOLDER")
        fr = tk.Frame(self, bg=PANEL)
        fr.pack(fill="x")
        self.folder = tk.StringVar(value=st.get("last_dir") or DEFAULT_SAVE_DIR)
        ttk.Entry(fr, textvariable=self.folder, width=52).pack(side="left", fill="x", expand=True)
        ttk.Button(fr, text=tr("Browse…"), command=self._browse).pack(side="left", padx=(6, 0))

        head("FILE NAME")
        self.prefix = tk.StringVar(value=f"Capture_{datetime.now():%Y%m%d_%H%M}")
        ttk.Entry(self, textvariable=self.prefix, width=34).pack(anchor="w")

        self.open_after = tk.BooleanVar(value=st.get("open_after_save", False))
        self.ask = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text=tr("Open the folder after saving"), variable=self.open_after).pack(anchor="w", pady=(12, 0))
        ttk.Checkbutton(self, text=tr("Ask every time I close the app"), variable=self.ask).pack(anchor="w")

        bf = tk.Frame(self, bg=PANEL)
        bf.pack(fill="x", pady=(16, 0))
        FlatButton(bf, tr("Save and close"), lambda: self._done("save"), bg=ACCENT, fg="white", hover=ACCENT_D,
                   font=UI_B, padx=14, pady=5).pack(side="right")
        FlatButton(bf, tr("Close without saving"), lambda: self._done("close"), bg=BTN, hover=BTN_H,
                   padx=12, pady=5).pack(side="right", padx=6)
        FlatButton(bf, tr("Cancel"), self.destroy, bg=BTN, hover=BTN_H, padx=12, pady=5).pack(side="left")
        self.bind("<Return>", lambda e: self._done("save"))
        self.bind("<Escape>", lambda e: self.destroy())
        self._sync()
        self.update_idletasks()
        x = master.winfo_rootx() + master.winfo_width() // 2 - self.winfo_width() // 2
        y = master.winfo_rooty() + max(40, master.winfo_height() // 2 - self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        self.grab_set()
        self.focus_force()
        self.wait_window()

    def _sync(self):
        if self.what.get() == "pdf":
            self.fmt.set("PDF")
            self.fmt_cb.configure(state="disabled")
        else:
            self.fmt_cb.configure(state="readonly")

    def _browse(self):
        d = filedialog.askdirectory(parent=self, initialdir=self.folder.get(), title=tr("FOLDER"))
        if d:
            self.folder.set(os.path.normpath(d))

    def _done(self, action):
        if action == "save":
            if not self.folder.get().strip():
                messagebox.showwarning(tr("FOLDER"), tr("Please choose a folder."), parent=self)
                return
            name = "".join(ch for ch in self.prefix.get().strip() if ch not in '\\/:*?"<>|') or "Capture"
            self.prefix.set(name)
        self.result = {"action": action, "what": self.what.get(), "fmt": self.fmt.get(),
                       "folder": self.folder.get().strip(), "prefix": self.prefix.get(),
                       "open": self.open_after.get(), "ask": self.ask.get()}
        self.destroy()


class ThemeDialog(tk.Toplevel):
    """Theme manager: preview and choose a theme, get themes from GitHub, import / export / create."""

    def __init__(self, app):
        super().__init__(app.root)
        self.app = app
        self.k = app.k
        self.title(tr("Themes") + " – " + APP_NAME)
        self.configure(bg=PANEL)
        self.transient(app.root)
        self.geometry(f"+{app.root.winfo_rootx() + 70}+{app.root.winfo_rooty() + 50}")
        self.rows = []          # {"theme": Theme, "local": bool, "entry": online entry or None}
        self.online = None      # list of online entries once fetched
        self.q = queue.Queue()
        self._busy = False
        self._prev_photo = None
        self._remote_prev = {}
        pad = dict(bg=PANEL)

        tk.Label(self, text=tr("Themes"), font=("Segoe UI Semibold", 13), fg=TEXT, **pad).pack(anchor="w", padx=16, pady=(12, 0))
        tk.Label(self, text=tr("A theme changes the colours, the icon of each function, the decorations, and can add a "
                               "frame to the screenshots you copy or export."),
                 font=UI, fg=MUTED, wraplength=int(760 * self.k), justify="left", **pad).pack(anchor="w", padx=16, pady=(2, 8))

        body = tk.Frame(self, **pad)
        body.pack(fill="both", expand=True, padx=16)
        lf = tk.Frame(body, bg=BORDER, padx=1, pady=1)
        lf.pack(side="left", fill="y")
        self.lb = tk.Listbox(lf, width=34, height=16, font=UI, activestyle="none", relief="flat", bd=0,
                             highlightthickness=0, bg=FIELD[0], fg=TEXT, selectbackground=ACCENT_L,
                             selectforeground=TEXT, exportselection=False)
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.lb.yview)
        self.lb.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.lb.pack(side="left", fill="y")
        self.lb.bind("<<ListboxSelect>>", lambda e: self._show())
        self.lb.bind("<Double-Button-1>", lambda e: self._use())

        rf = tk.Frame(body, **pad)
        rf.pack(side="left", fill="both", expand=True, padx=(14, 0))
        self.pw, self.ph = int(520 * self.k), int(330 * self.k)
        self.prev = tk.Label(rf, bg=CANVAS_BG, width=self.pw, height=self.ph, bd=0)
        self.prev.pack(anchor="w")
        self.name_lbl = tk.Label(rf, text="", font=UI_BIG, fg=TEXT, anchor="w", **pad)
        self.name_lbl.pack(fill="x", pady=(8, 0))
        self.meta_lbl = tk.Label(rf, text="", font=UI_S, fg=MUTED, anchor="w", **pad)
        self.meta_lbl.pack(fill="x")
        self.desc_lbl = tk.Label(rf, text="", font=UI, fg=TEXT, anchor="w", justify="left",
                                 wraplength=self.pw, **pad)
        self.desc_lbl.pack(fill="x", pady=(2, 6))
        br = tk.Frame(rf, **pad)
        br.pack(fill="x")
        self.use_btn = FlatButton(br, tr("Use this theme"), self._use, bg=ACCENT, fg="white", hover=ACCENT_D,
                                  padx=12, pady=5)
        self.use_btn.pack(side="left")
        self.inst_btn = FlatButton(br, tr("Download and install"), self._install, bg=ACCENT, fg="white",
                                   hover=ACCENT_D, padx=12, pady=5)
        self.new_btn = FlatButton(br, tr("Make my own from this…"), self._new_from, bg=BTN, hover=BTN_H, padx=10, pady=5,
                                  tip=tr("Copies this theme into your themes folder so you can change its pictures and colours"))
        self.new_btn.pack(side="left", padx=(6, 0))
        self.exp_btn = FlatButton(br, tr("Export .zip…"), self._export, bg=BTN, hover=BTN_H, padx=10, pady=5,
                                  tip=tr("Pack this theme into one file to share it"))
        self.exp_btn.pack(side="left", padx=(6, 0))
        self.del_btn = FlatButton(br, tr("Remove"), self._remove, bg=BTN, hover=BTN_H, padx=10, pady=5)
        self.del_btn.pack(side="left", padx=(6, 0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", pady=(12, 0))
        rnd = tk.Frame(self, **pad)
        rnd.pack(fill="x", padx=16, pady=(10, 0))
        FlatButton(rnd, "🎲  " + tr("Random theme now"), self._random_now, bg=BTN, hover=BTN_H, padx=10, pady=5,
                   tip=tr("Picks one of your installed themes at random")).pack(side="left")
        ttk.Checkbutton(rnd, text=tr("Use a random theme each time the app starts"), variable=app.theme_random,
                        command=app._opts_changed).pack(side="left", padx=(12, 0))
        bot = tk.Frame(self, **pad)
        bot.pack(fill="x", padx=16, pady=10)
        self.get_btn = FlatButton(bot, "☁  " + tr("Get online themes"), self._fetch, bg=BTN, hover=BTN_H, padx=10, pady=5,
                                  tip=tr("Looks for new themes on GitHub. This is the only time the app goes online."))
        self.get_btn.pack(side="left")
        FlatButton(bot, tr("Import .zip…"), self._import, bg=BTN, hover=BTN_H, padx=10, pady=5,
                   tip=tr("Install a theme someone sent you")).pack(side="left", padx=(6, 0))
        FlatButton(bot, tr("Open themes folder"), self._open_folder, bg=BTN, hover=BTN_H, padx=10, pady=5).pack(side="left", padx=(6, 0))
        FlatButton(bot, tr("How to make a theme"), lambda: self._open_url(THEMES_DOC_URL), bg=BTN, hover=BTN_H,
                   padx=10, pady=5).pack(side="left", padx=(6, 0))
        FlatButton(bot, tr("Close"), self.destroy, bg=ACCENT, fg="white", hover=ACCENT_D, padx=12, pady=5).pack(side="right")
        bot2 = tk.Frame(self, **pad)
        bot2.pack(fill="x", padx=16, pady=(0, 12))
        ttk.Checkbutton(bot2, text=tr("Add the theme frame to copies and exports"), variable=app.theme_frame,
                        command=app._opts_changed).pack(side="left")
        self.status = tk.Label(bot2, text="", font=UI_S, fg=MUTED, anchor="e", **pad)
        self.status.pack(side="right")
        if app.theme_errors:
            self._set_status(tr("{n} theme folder(s) could not be read: {names}", n=len(app.theme_errors),
                                names=", ".join(n for n, _ in app.theme_errors[:3])))

        self._fill(select=app.theme.id)
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(100, self._poll)

    # list ---------------------------------------------------------------
    def _fill(self, select=None):
        app = self.app
        self.rows = [{"theme": t, "local": True, "entry": None} for t in app.sorted_themes()]
        if self.online:
            by_id = {r["theme"].id: r for r in self.rows}
            for e in self.online:
                r = by_id.get(e["id"])
                if r is None:
                    self.rows.append({"theme": e["theme"], "local": False, "entry": e})
                elif themes.version_tuple(e["theme"].version) > themes.version_tuple(r["theme"].version):
                    r["entry"] = e
        self.lb.delete(0, "end")
        active = app.st.get("theme", themes.DEFAULT_ID)
        sel = 0
        for i, r in enumerate(self.rows):
            t = r["theme"]
            mark = "● " if r["local"] and t.id == active else "   "
            src = {"default": "", "builtin": tr("built in"), "user": tr("mine")}.get(t.source, "")
            if not r["local"]:
                src = "☁ " + tr("online")
            elif r["entry"]:
                src += "  ⬆ " + tr("update")
            self.lb.insert("end", f"{mark}{t.name(LANG[0])}" + (f"   ({src.strip()})" if src.strip() else ""))
            if t.id == select:
                sel = i
        self.lb.selection_set(sel)
        self.lb.see(sel)
        self._show()

    def _cur(self):
        s = self.lb.curselection()
        return self.rows[s[0]] if s and s[0] < len(self.rows) else None

    def _show(self):
        r = self._cur()
        if not r:
            return
        t = r["theme"]
        self.name_lbl.configure(text=t.name(LANG[0]))
        bits = [b for b in ((tr("by {a}", a=t.author) if t.author else ""), ("v" + t.version if t.version else ""),
                            (tr("has a frame") if t.frame else tr("no frame")),
                            (tr("in use") if r["local"] and t.id == self.app.theme.id else "")) if b]
        if r["entry"] and r["local"]:
            bits.append(tr("version {v} available online", v=r["entry"]["theme"].version))
        self.meta_lbl.configure(text="  ·  ".join(bits))
        self.desc_lbl.configure(text=t.description(LANG[0]))
        if r["local"]:
            self.use_btn.pack(side="left", before=self.new_btn)
            if r["entry"]:
                self.inst_btn.configure(text=tr("Update"))
                self.inst_btn.pack(side="left", padx=(6, 0), after=self.use_btn)
            else:
                self.inst_btn.pack_forget()
            self.new_btn.pack(side="left", padx=(6, 0))
            for b in (self.exp_btn, self.del_btn):
                b.pack_forget()
            if t.path:
                self.exp_btn.pack(side="left", padx=(6, 0))
            if t.source == "user":
                self.del_btn.pack(side="left", padx=(6, 0))
            self._set_preview(self._render_preview(t))
        else:
            for b in (self.use_btn, self.new_btn, self.exp_btn, self.del_btn):
                b.pack_forget()
            self.inst_btn.configure(text=tr("Download and install"))
            self.inst_btn.pack(side="left")
            if t.id in self._remote_prev:
                self._set_preview(self._remote_prev[t.id] or self._render_preview(t))
            else:
                self._set_preview(self._render_preview(t))
                self._remote_prev[t.id] = None
                e = r["entry"]
                self._run(lambda: ("preview", t.id, themes.fetch_preview(e)))

    def _render_preview(self, t):
        prev = t.preview()
        if prev is None:
            try:
                prev = themes.make_preview(t, theme_icon, (520, 330), frame_font, lang=LANG[0])
            except Exception:
                prev = Image.new("RGBA", (520, 330), themes.parse_color(t.colors["canvas"]))
        return prev

    def _set_preview(self, im):
        im = im.copy()
        im.thumbnail((self.pw, self.ph), Image.LANCZOS)
        box = Image.new("RGBA", (self.pw, self.ph), themes.parse_color(CANVAS_BG))
        box.alpha_composite(im.convert("RGBA"), ((self.pw - im.width) // 2, (self.ph - im.height) // 2))
        self._prev_photo = ImageTk.PhotoImage(box)
        self.prev.configure(image=self._prev_photo, width=self.pw, height=self.ph)

    def _set_status(self, text, error=False):
        self.status.configure(text=text, fg="#B91C1C" if error else MUTED)

    # background work -------------------------------------------------------
    def _run(self, fn):
        def work():
            try:
                self.q.put(fn())
            except Exception as ex:
                self.q.put(("error", ex))
        threading.Thread(target=work, daemon=True).start()

    def _poll(self):
        try:
            while True:
                m = self.q.get_nowait()
                kind = m[0]
                if kind == "error":
                    self._busy = False
                    ex = m[1]
                    self._set_status(tr("Could not reach GitHub: {e}", e=getattr(ex, "reason", ex)), True)
                elif kind == "catalog":
                    self._busy = False
                    self.online = m[1]
                    cur = self._cur()
                    self._fill(select=cur["theme"].id if cur else None)
                    new = sum(1 for r in self.rows if not r["local"] or r["entry"])
                    self._set_status(tr("{n} online theme(s), {k} new or updated", n=len(m[1]), k=new))
                elif kind == "preview":
                    self._remote_prev[m[1]] = m[2]
                    cur = self._cur()
                    if m[2] is not None and cur and cur["theme"].id == m[1] and not cur["local"]:
                        self._set_preview(m[2])
                elif kind == "progress":
                    self._set_status(tr("Downloading… {i}/{n}", i=m[1], n=m[2]))
                elif kind == "installed":
                    self._busy = False
                    t = m[1]
                    self.app.themes, self.app.theme_errors = load_themes()
                    self._fill(select=t.id)
                    self._set_status(tr("Installed “{name}”.", name=t.name(LANG[0])))
        except queue.Empty:
            pass
        try:
            if self.winfo_exists():
                self.after(100, self._poll)
        except tk.TclError:
            pass

    # actions ----------------------------------------------------------------
    def _fetch(self):
        if self._busy:
            return
        self._busy = True
        self._set_status(tr("Looking for themes on GitHub…"))
        self._run(lambda: ("catalog", themes.fetch_catalog(lang=LANG[0])))

    def _install(self):
        r = self._cur()
        if not r or not r["entry"] or self._busy:
            return
        self._busy = True
        e = r["entry"]
        self._set_status(tr("Downloading… {i}/{n}", i=0, n=len(e["files"])))
        self._run(lambda: ("installed", themes.install_remote(
            e, THEMES_USER, progress=lambda i, n: self.q.put(("progress", i, n)))))

    def _use(self):
        r = self._cur()
        if not r:
            return
        if not r["local"]:
            self._install()
            return
        self.app.set_theme(r["theme"].id)
        try:
            if self.winfo_exists():
                self._fill(select=r["theme"].id)
        except tk.TclError:   # the app restarted
            pass

    def _random_now(self):
        tid = pick_random_theme(self.app.themes, self.app.theme.id)
        if not tid or tid == self.app.theme.id:
            self._set_status(tr("Install another theme first."))
            return
        self._fill(select=tid)
        self.app.set_theme(tid)
        try:
            if self.winfo_exists():
                self._fill(select=tid)
        except tk.TclError:   # the app restarted
            pass

    def _import(self):
        p = filedialog.askopenfilename(parent=self, title=tr("Import a theme"),
                                       filetypes=[(tr("Theme package"), "*.zip"), ("*", "*.*")])
        if not p:
            return
        try:
            t = themes.import_zip(p, THEMES_USER)
        except Exception as ex:
            messagebox.showerror(tr("Import failed"), str(ex), parent=self)
            return
        self.app.themes, self.app.theme_errors = load_themes()
        self._fill(select=t.id)
        self._set_status(tr("Installed “{name}”.", name=t.name(LANG[0])))

    def _export(self):
        r = self._cur()
        if not r or not r["theme"].path:
            return
        t = r["theme"]
        p = filedialog.asksaveasfilename(parent=self, defaultextension=".zip", initialfile=f"{t.id}.zip",
                                         filetypes=[(tr("Theme package"), "*.zip")])
        if not p:
            return
        try:
            themes.export_zip(t, p)
        except Exception as ex:
            messagebox.showerror(tr("Save failed"), str(ex), parent=self)
            return
        self._set_status(tr("Saved: {p}", p=p))

    def _remove(self):
        r = self._cur()
        if not r or r["theme"].source != "user":
            return
        t = r["theme"]
        if t.id == self.app.theme.id or t.id == self.app.st.get("theme"):
            messagebox.showinfo(APP_NAME, tr("Choose another theme first, then remove this one."), parent=self)
            return
        if not messagebox.askyesno(APP_NAME, tr("Remove the theme “{name}”?", name=t.name(LANG[0])), parent=self):
            return
        try:
            themes.remove_theme(t, THEMES_USER)
        except Exception as ex:
            messagebox.showerror(APP_NAME, str(ex), parent=self)
            return
        self.app.themes, self.app.theme_errors = load_themes()
        self._fill(select=self.app.theme.id)

    def _new_from(self):
        r = self._cur()
        if not r or not r["local"]:
            return
        base = r["theme"]
        name = simpledialog.askstring(tr("New theme"), tr("Name of your theme:"), parent=self,
                                      initialvalue=tr("My theme"))
        if not name or not name.strip():
            return
        try:
            t = themes.create_from(base, name.strip(), THEMES_USER)
        except Exception as ex:
            messagebox.showerror(APP_NAME, str(ex), parent=self)
            return
        self.app.themes, self.app.theme_errors = load_themes()
        self._fill(select=t.id)
        self._set_status(tr("Created “{name}”. Change its pictures and theme.json, then choose it.", name=name.strip()))
        try:
            os.startfile(t.path)
        except Exception:
            pass

    def _open_folder(self):
        os.makedirs(THEMES_USER, exist_ok=True)
        try:
            os.startfile(THEMES_USER)
        except Exception as ex:
            self._set_status(str(ex), True)

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)


# --------------------------------------------------------------------------- settings
def load_settings():
    s = dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            s.update(json.load(f))
    except Exception:
        pass
    return s


def save_settings(s):
    try:
        os.makedirs(APPDATA, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


# =========================================================================== APP
class App:
    def __init__(self, root):
        self.root = root
        self.st = load_settings()
        if self.st.get("lang") not in ("en", "fr", "zh"):
            self.st["lang"] = detect_lang()
        LANG[0] = self.st["lang"]
        self.restart = False
        _DEC[0] = int(self.st.get("decimals", 2))
        self.themes, self.theme_errors = load_themes()
        if self.st.get("theme_random"):
            tid = pick_random_theme(self.themes, self.st.get("theme"))
            if tid:
                self.st["theme"] = tid
        self.theme = self.themes.get(self.st.get("theme")) or self.themes[themes.DEFAULT_ID]
        apply_theme(self.theme)
        self.theme_random = tk.BooleanVar(value=bool(self.st.get("theme_random", False)))
        self.theme_frame = tk.BooleanVar(value=self.st.get("theme_frame", True))
        self._deco_key = None
        root.title(f"{APP_NAME}")
        root.geometry(self.st.get("geometry", "1440x880"))
        root.minsize(1000, 620)
        root.configure(bg=BG)
        ico = os.path.join(RES_DIR, "multicapture.ico")
        if os.path.exists(ico):
            try:
                root.iconbitmap(default=ico)
            except Exception:
                pass
        self.k = max(1.0, root.winfo_fpixels("1i") / 96.0)

        self.items = []          # history, newest first
        self.board = []          # board order
        self.sel = None          # selected screenshot
        self.sel_obj = None      # selected annotation
        self.drag = None
        self.building = None     # polyline / polygon / angle in progress
        self.editing = None      # text object being edited
        self.edit_widget = None
        self.edit_win = None
        self.edit_new = False
        self.busy = False
        self.last_region = None
        self.s, self.vx, self.vy, self.fit = 1.0, 0.0, 0.0, True
        self._base_key = None
        self._base = None
        self._cells = []
        self._grip = None
        self._edit_moved = False
        self._gdrag = None
        self._jobs = {}
        self._loading = False
        self._render_pending = False
        self._last_prop = (None, None, 0)
        self._notes_loading = False
        self.copy_gen = 0
        self._tick = 0
        self.q = queue.Queue()

        st = self.st
        self.view = tk.StringVar(value=st["view"])
        self.tool = tk.StringVar(value="select")
        self.feat = {k: tk.BooleanVar(value=bool(st.get(k))) for k, _ in FEATURES}
        self.pins = []
        mode = st.get("mode")
        if mode not in MODE_KEYS and not (mode == SCROLL_MODE and self.feat["feat_scroll"].get()):
            mode = "Region"
        self.mode_var = tk.StringVar(value=tr(mode))
        self.delay_var = tk.StringVar(value=tr(st.get("delay") if st.get("delay") in DELAY_KEYS else "No delay"))
        self.autocopy = tk.BooleanVar(value=st["autocopy"])
        self.include_notes = tk.BooleanVar(value=st["include_notes"])
        self.autosave = tk.BooleanVar(value=st["autosave"])
        self.keep_history = tk.BooleanVar(value=st["keep_history"])
        self.ask_close = tk.BooleanVar(value=st.get("ask_on_close", True))
        self.color = st["color"]
        self.width_var = tk.IntVar(value=st["width"])
        self.fill_on = tk.BooleanVar(value=st["fill_on"])
        self.fill_color = st["fill_color"]
        self.fill_alpha = tk.IntVar(value=st["fill_alpha"])
        fams = available_families()
        self.family = tk.StringVar(value=st["family"] if st["family"] in fams else fams[0])
        self.fsize = tk.IntVar(value=st["fsize"])
        self.bold = tk.BooleanVar(value=st["bold"])
        self.italic = tk.BooleanVar(value=st["italic"])
        self.underline = tk.BooleanVar(value=st["underline"])
        self.align = tk.StringVar(value=st["align"])
        self.tbg_on = tk.BooleanVar(value=st["tbg_on"])
        self.tbg_color = st["tbg_color"]
        self.border = tk.BooleanVar(value=st["border"])
        self.stamp = tk.StringVar(value=st["stamp"])
        self.decimals = tk.IntVar(value=st["decimals"])

        self._build_ui()
        self._load_history()
        self._update_panel()
        if not self.st.get("guide_shown"):
            self.st["guide_shown"] = True
            root.after(600, self.show_guide)
        threading.Thread(target=hotkey_thread, args=(self.q,), daemon=True).start()
        root.after(100, self._poll)
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ===================================================================== UI construction
    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure(".", font=UI, background=PANEL)
        style.configure("TCombobox", padding=3, arrowsize=12)
        style.configure("TCheckbutton", background=PANEL)
        style.configure("TSpinbox", padding=2, arrowsize=10)
        if self.theme.id != themes.DEFAULT_ID:
            # widgets that do not set their own colours follow the theme too (dark themes need this)
            style.configure(".", foreground=TEXT, fieldbackground=FIELD[0], bordercolor=BORDER,
                            lightcolor=PANEL, darkcolor=BORDER, troughcolor=BTN, arrowcolor=TEXT,
                            selectbackground=ACCENT_L, selectforeground=TEXT, insertcolor=TEXT)
            style.configure("TCheckbutton", foreground=TEXT, indicatorbackground=FIELD[0], indicatorforeground=ACCENT)
            style.map("TCheckbutton", background=[("active", HOVER)], foreground=[("disabled", MUTED)])
            style.map("TCombobox", fieldbackground=[("readonly", FIELD[0])], foreground=[("readonly", TEXT)],
                      selectbackground=[("readonly", FIELD[0])], selectforeground=[("readonly", TEXT)])
            style.map("TSpinbox", fieldbackground=[("!disabled", FIELD[0])])
            style.configure("Vertical.TScrollbar", lightcolor=BTN_H, darkcolor=BTN_H)
            r = self.root
            for opt, val in (("*foreground", TEXT), ("*Label.foreground", TEXT), ("*Entry.background", FIELD[0]),
                             ("*Entry.insertBackground", TEXT), ("*Listbox.background", FIELD[0]),
                             ("*Listbox.foreground", TEXT), ("*Listbox.selectBackground", ACCENT_L),
                             ("*Listbox.selectForeground", TEXT), ("*Text.background", NOTES_BG),
                             ("*Text.foreground", TEXT), ("*Menu.background", PANEL), ("*Menu.foreground", TEXT),
                             ("*Menu.activeBackground", ACCENT_L), ("*Menu.activeForeground", TEXT),
                             ("*Scale.foreground", TEXT), ("*Radiobutton.foreground", TEXT),
                             ("*Checkbutton.foreground", TEXT), ("*Checkbutton.selectColor", FIELD[0])):
                r.option_add(opt, val)
        style.configure("Vertical.TScrollbar", background=BTN_H, troughcolor=PANEL, bordercolor=PANEL,
                        arrowcolor=MUTED, gripcount=0)
        if self.theme.id == themes.DEFAULT_ID:
            style.map("TCombobox", fieldbackground=[("readonly", "white")])
        self.root.option_add("*TCombobox*Listbox.font", UI)

        # ---------------------------------------------------------- header
        head = tk.Frame(self.root, bg=PANEL, highlightthickness=0)
        head.pack(fill="x")
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x")
        try:
            logo = Image.open(os.path.join(RES_DIR, "multicapture.png")).convert("RGBA")
            self._logo = ImageTk.PhotoImage(logo.resize((int(26 * self.k), int(26 * self.k)), Image.LANCZOS))
            tk.Label(head, image=self._logo, bg=PANEL).pack(side="left", padx=(12, 4), pady=8)
        except Exception:
            pass
        tk.Label(head, text="MultiCapture", font=("Segoe UI Semibold", 12), bg=PANEL, fg=TEXT).pack(side="left", padx=(0, 16))

        self._hicons = {}
        FlatButton(head, command=self.new_capture, bg=ACCENT, fg="white", hover=ACCENT_D,
                   font=UI_BIG, padx=14, pady=6, **self._hbtn("capture", "＋", tr("New capture"), 20),
                   tip=tr("New capture  (Ctrl+N)\nGlobal hotkey from anywhere: Ctrl+Alt+S")).pack(side="left", pady=8)
        cb = ttk.Combobox(head, textvariable=self.mode_var, state="readonly", width=12,
                          values=[tr(k) for k in self._mode_keys()])
        self.mode_cb = cb
        cb.pack(side="left", padx=(8, 4))
        Tooltip(cb, tr("Capture mode"), below=True)
        cb2 = ttk.Combobox(head, textvariable=self.delay_var, state="readonly", width=9,
                           values=[tr(k) for k in DELAY_KEYS])
        cb2.pack(side="left", padx=4)
        Tooltip(cb2, tr("Delay before capture"), below=True)
        for w in (cb, cb2):
            w.bind("<<ComboboxSelected>>", lambda e: self.root.focus_set())
        self.extra_bar = tk.Frame(head, bg=PANEL)     # buttons of the optional features that are switched on
        self.extra_bar.pack(side="left")

        tk.Frame(head, bg=BORDER, width=1).pack(side="left", fill="y", padx=12, pady=10)
        tk.Label(head, text=tr("View"), bg=PANEL, fg=MUTED, font=UI).pack(side="left", padx=(0, 6))
        seg = tk.Frame(head, bg=BORDER, padx=1, pady=1)
        seg.pack(side="left")
        self.view_btns = {}
        for i, (name, n) in enumerate(VIEW_MODES):
            tip = (tr("Show one screenshot  (key {k})", k=i + 1) if n == 1 else
                   tr("Show all screenshots  (key {k})", k=i + 1) if n == 0 else
                   tr("Show the last {n} screenshots  (key {k})", n=n, k=i + 1))
            b = FlatButton(seg, tr(name), lambda nm=name: self.set_view(nm), bg=PANEL, padx=11, pady=4, tip=tip)
            b.pack(side="left", padx=(0, 1))
            self.view_btns[name] = b

        tk.Frame(head, bg=BORDER, width=1).pack(side="left", fill="y", padx=12, pady=10)
        FlatButton(head, command=self.copy_view, **self._hbtn("copy", "⧉", tr("Copy")),
                   tip=tr("Copy the current view to the clipboard  (Ctrl+C)")).pack(side="left")
        self.save_btn = FlatButton(head, command=self._save_menu, **self._hbtn("save", "💾", tr("Save") + " ▾"),
                                   tip=tr("Save / export"))
        self.save_btn.pack(side="left")
        self.del_btn = FlatButton(head, command=self._delete_menu, **self._hbtn("delete", "🗑", tr("Delete") + " ▾"),
                                  tip=tr("Delete screenshots"))
        self.del_btn.pack(side="left")
        self.more_btn = FlatButton(head, command=self._options_menu, **self._hbtn("options", "⚙", tr("Options") + " ▾"),
                                   tip=tr("Options"))
        self.more_btn.pack(side="left")
        FlatButton(head, command=self.show_themes, **self._hbtn("themes", "🎨", tr("Themes")),
                   tip=tr("Choose a theme, get new themes online or import your own")).pack(side="left")
        FlatButton(head, command=self.show_guide, **self._hbtn("help", "?", tr("Help")),
                   tip=tr("User guide  (F1)")).pack(side="left")
        deco = self.theme.decoration("header")
        if deco:   # theme picture on the right end of the header (e.g. moon and stars)
            im = deco[0]
            hh = int(_num_opt(deco[1].get("height"), 44, 8, 120) * self.k)
            im = im.resize((max(1, int(im.width * hh / im.height)), hh), Image.LANCZOS)
            bgc = themes.parse_color(PANEL)
            flat = Image.new("RGBA", im.size, bgc)
            flat.alpha_composite(im)
            self._head_deco = ImageTk.PhotoImage(flat)
            tk.Label(head, image=self._head_deco, bg=PANEL, bd=0).pack(side="right", padx=(0, 4))


        # ---------------------------------------------------------- body
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)

        # left: history
        left = tk.Frame(body, bg=PANEL, width=int(214 * self.k))
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")
        lh = tk.Frame(left, bg=PANEL)
        lh.pack(fill="x", padx=10, pady=(10, 4))
        self.count_lbl = tk.Label(lh, text=tr("HISTORY"), font=UI_H, bg=PANEL, fg=MUTED)
        self.count_lbl.pack(side="left")
        self.list_canvas = tk.Canvas(left, bg=PANEL, highlightthickness=0)
        sb = ttk.Scrollbar(left, orient="vertical", command=self.list_canvas.yview)
        self.list_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.list_frame = tk.Frame(self.list_canvas, bg=PANEL)
        self.list_win = self.list_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>", lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.bind("<Configure>", lambda e: self.list_canvas.itemconfigure(self.list_win, width=e.width))
        self.cards = {}

        # right: properties + notes
        right = tk.Frame(body, bg=PANEL, width=int(292 * self.k))
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Frame(body, bg=BORDER, width=1).pack(side="right", fill="y")
        self._build_right(right)

        # tool strip
        strip = tk.Frame(body, bg=PANEL)
        strip.pack(side="left", fill="y")
        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")
        self.tool_btns = {}
        self._icons = {}
        ipx = int(22 * self.k)
        for t in TOOLS:
            if t is None:
                tk.Frame(strip, bg=BORDER, height=1).pack(fill="x", padx=8, pady=4)
                continue
            key, tip, _ = t
            self._icons[key] = make_tool_icon(key, ipx)
            b = tk.Radiobutton(strip, image=self._icons[key], variable=self.tool, value=key, indicatoron=False,
                               bg=PANEL, activebackground=HOVER, selectcolor=ACCENT_L, relief="flat",
                               offrelief="flat", bd=0, width=int(36 * self.k), height=int(32 * self.k),
                               highlightthickness=0,
                               cursor="hand2", command=self._tool_changed, takefocus=0)
            b.pack(padx=5, pady=1)
            Tooltip(b, tr(tip))
            self.tool_btns[key] = b

        # centre: canvas
        centre = tk.Frame(body, bg=CANVAS_BG)
        centre.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(centre, bg=CANVAS_BG, highlightthickness=0, takefocus=1)
        self.canvas.pack(fill="both", expand=True)
        c = self.canvas
        c.bind("<Configure>", lambda e: self.request_render())
        c.bind("<ButtonPress-1>", self.on_press)
        c.bind("<B1-Motion>", self.on_drag)
        c.bind("<ButtonRelease-1>", self.on_release)
        c.bind("<Double-Button-1>", self.on_double)
        c.bind("<Motion>", self.on_motion)
        c.bind("<ButtonPress-3>", self.on_right)
        c.bind("<ButtonPress-2>", lambda e: setattr(self, "_pan", (e.x, e.y)))
        c.bind("<B2-Motion>", self._pan_move)
        self.root.bind_all("<MouseWheel>", self._wheel)

        # ---------------------------------------------------------- status bar
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", side="bottom")
        bar = tk.Frame(self.root, bg=PANEL)
        bar.pack(fill="x", side="bottom", before=body)
        self.status = tk.Label(bar, text=tr("Ready  ·  Ctrl+Alt+S to capture from anywhere"), bg=PANEL, fg=MUTED,
                               font=UI_S, anchor="w")
        self.status.pack(side="left", padx=10, pady=3)
        zf = tk.Frame(bar, bg=PANEL)
        zf.pack(side="right", padx=6)
        FlatButton(zf, tr("Fit"), self.zoom_fit, padx=6, pady=1, font=UI_S, tip=tr("Fit to window  (Ctrl+0)")).pack(side="left")
        FlatButton(zf, "100%", self.zoom_100, padx=6, pady=1, font=UI_S, tip=tr("Actual size  (Ctrl+1)")).pack(side="left")
        FlatButton(zf, "−", lambda: self.zoom_at(1 / 1.25), padx=6, pady=1, font=UI_S, tip=tr("Zoom out  (Ctrl+−)")).pack(side="left")
        self.zoom_lbl = tk.Label(zf, text="100%", bg=PANEL, fg=TEXT, font=UI_S, width=6)
        self.zoom_lbl.pack(side="left")
        FlatButton(zf, "+", lambda: self.zoom_at(1.25), padx=6, pady=1, font=UI_S,
                   tip=tr("Zoom in  (Ctrl++ / Ctrl+wheel)")).pack(side="left")
        self.flash = tk.Label(bar, text="", bg=PANEL, fg=OK_C, font=UI_B)
        self.flash.pack(side="right", padx=10)
        self.coord_lbl = tk.Label(bar, text="", bg=PANEL, fg=MUTED, font=UI_S)
        self.coord_lbl.pack(side="right", padx=10)
        self.size_lbl = tk.Label(bar, text="", bg=PANEL, fg=MUTED, font=UI_S)
        self.size_lbl.pack(side="right", padx=10)

        self.root.bind("<Key>", self.on_key)
        self._refresh_view_btns()
        self._build_extras()

    def _hbtn(self, key, glyph, text, size=18):
        """Header button contents: the theme's icon when it has one, else the usual symbol."""
        im = self.theme.icon(key)
        if im is None:
            return {"text": f"{glyph}  {text}"}
        px = int(size * self.k)
        ph = ImageTk.PhotoImage(theme_icon(self.theme, key, px))
        self._hicons[key] = ph
        return {"text": "  " + text, "image": ph, "compound": "left"}

    def _section(self, parent, title):
        f = tk.Frame(parent, bg=PANEL)
        tk.Label(f, text=tr(title), font=UI_H, bg=PANEL, fg=MUTED).pack(anchor="w", pady=(8, 4))
        return f

    def _build_right(self, right):
        wrap = tk.Frame(right, bg=PANEL)
        wrap.pack(fill="both", expand=True, padx=12)
        self.props = tk.Frame(wrap, bg=PANEL)
        self.props.pack(fill="x")
        P = self.props

        # selection
        self.sec_sel = self._section(P, "SELECTION")
        self.sel_lbl = tk.Label(self.sec_sel, text=tr("Nothing selected"), bg=PANEL, fg=TEXT, font=UI_B, anchor="w",
                                wraplength=int(265 * self.k), justify="left")
        self.sel_lbl.pack(fill="x")
        row = tk.Frame(self.sec_sel, bg=PANEL)
        row.pack(fill="x", pady=(4, 0))
        for i, (txt, cmd, tip) in enumerate((("⧉ " + tr("Duplicate"), self.dup_obj, "Ctrl+D"),
                                             ("✕ " + tr("Delete"), self.delete_obj, tr("Delete key")),
                                             ("▲ " + tr("Front"), self.obj_front, tr("Bring to front")),
                                             ("▼ " + tr("Back"), self.obj_back, tr("Send to back")))):
            FlatButton(row, txt, cmd, padx=6, pady=2, font=UI_S, bg=BTN, hover=BTN_H, tip=tip,
                       anchor="w").grid(row=i // 2, column=i % 2, padx=(0, 3), pady=(0, 3), sticky="ew")
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        # colour
        self.sec_color = self._section(P, "COLOUR")
        grid = tk.Frame(self.sec_color, bg=PANEL)
        grid.pack(anchor="w")
        self.swatches = []
        sz = int(20 * self.k)
        for i, col in enumerate(PALETTE):
            f = tk.Frame(grid, bg=PANEL, highlightthickness=2, highlightbackground=PANEL, width=sz + 4, height=sz + 4)
            f.grid(row=i // 6, column=i % 6, padx=1, pady=1)
            f.pack_propagate(False)
            sw = tk.Label(f, bg=col, cursor="hand2", relief="solid" if col == "#FFFFFF" else "flat", bd=1 if col == "#FFFFFF" else 0)
            sw.pack(fill="both", expand=True, padx=1, pady=1)
            sw.bind("<Button-1>", lambda e, c=col: self.set_color(c))
            self.swatches.append((f, col))
        cr = tk.Frame(self.sec_color, bg=PANEL)
        cr.pack(fill="x", pady=(4, 0))
        self.cur_sw = tk.Label(cr, bg=self.color, width=3, relief="solid", bd=1)
        self.cur_sw.pack(side="left")
        FlatButton(cr, tr("Custom…"), self.pick_color, padx=6, pady=1, font=UI_S, bg=BTN, hover=BTN_H).pack(side="left", padx=6)

        # stroke
        self.sec_stroke = self._section(P, "LINE WIDTH")
        sr = tk.Frame(self.sec_stroke, bg=PANEL)
        sr.pack(fill="x")
        tk.Scale(sr, from_=1, to=30, orient="horizontal", variable=self.width_var, showvalue=True, bg=PANEL,
                 highlightthickness=0, troughcolor=BTN_H, bd=0, sliderrelief="flat", font=UI_S,
                 activebackground=ACCENT, length=int(250 * self.k),
                 command=lambda v: self.on_prop("width")).pack(side="left", fill="x", expand=True)

        # fill
        self.sec_fill = self._section(P, "FILL")
        fr = tk.Frame(self.sec_fill, bg=PANEL)
        fr.pack(fill="x")
        ttk.Checkbutton(fr, text=tr("Fill shape"), variable=self.fill_on, command=lambda: self.on_prop("fill")).pack(side="left")
        self.fill_sw = tk.Label(fr, bg=self.fill_color, width=3, relief="solid", bd=1, cursor="hand2")
        self.fill_sw.pack(side="left", padx=6)
        self.fill_sw.bind("<Button-1>", lambda e: self.pick_fill())
        tk.Label(fr, text=tr("Opacity"), bg=PANEL, fg=MUTED, font=UI_S).pack(side="left", padx=(6, 0))
        tk.Scale(self.sec_fill, from_=5, to=100, orient="horizontal", variable=self.fill_alpha, bg=PANEL,
                 highlightthickness=0, troughcolor=BTN_H, bd=0, sliderrelief="flat", font=UI_S,
                 length=int(250 * self.k), command=lambda v: self.on_prop("alpha")).pack(fill="x")

        # pseudo-3D
        self.sec_solid = self._section(P, "3D")
        sr3 = tk.Frame(self.sec_solid, bg=PANEL)
        sr3.pack(fill="x")
        self.solid_btn = FlatButton(sr3, "⬛ " + tr("Make 3D"), self.toggle_solid, padx=8, pady=2, font=UI_S,
                                    bg=BTN, hover=BTN_H, tip=tr("Rectangle → box, ellipse → cylinder, polygon → prism"))
        self.solid_btn.pack(side="left")
        self.solid_cut = tk.BooleanVar(value=False)
        self.solid_cut_cb = ttk.Checkbutton(sr3, text=tr("Pocket (cut)"), variable=self.solid_cut,
                                            command=self.toggle_cut)
        self.solid_cut_cb.pack(side="left", padx=8)
        self.solid_hint = tk.Label(self.sec_solid, text=tr("Drag the orange ◆ handle to set depth and angle"),
                                   bg=PANEL, fg=MUTED, font=UI_S, wraplength=int(265 * self.k), justify="left")
        self.solid_hint.pack(anchor="w", pady=(4, 0))

        # text
        self.sec_text = self._section(P, "TEXT")
        r1 = tk.Frame(self.sec_text, bg=PANEL)
        r1.pack(fill="x")
        fc = ttk.Combobox(r1, textvariable=self.family, values=available_families(), state="readonly", width=17)
        fc.pack(side="left")
        fc.bind("<<ComboboxSelected>>", lambda e: (self.on_prop("family"), self._refocus()))
        sp = ttk.Spinbox(r1, from_=6, to=300, textvariable=self.fsize, width=5, command=lambda: self.on_prop("fsize"))
        sp.pack(side="left", padx=6)
        sp.bind("<Return>", lambda e: (self.on_prop("fsize"), self._refocus()))
        sp.bind("<FocusOut>", lambda e: self.on_prop("fsize"))
        r2 = tk.Frame(self.sec_text, bg=PANEL)
        r2.pack(fill="x", pady=(6, 0))
        self.fmt_btns = {}
        for key, txt, fnt in (("bold", "B", ("Segoe UI", 10, "bold")), ("italic", "I", ("Georgia", 10, "italic")),
                              ("underline", "U", ("Segoe UI", 10, "underline"))):
            b = FlatButton(r2, txt, lambda k_=key: self.toggle_fmt(k_), font=fnt, padx=9, pady=1,
                           bg=BTN, hover=BTN_H, tip=tr({"bold": "Bold", "italic": "Italic", "underline": "Underline"}[key]))
            b.pack(side="left", padx=(0, 2))
            self.fmt_btns[key] = b
        tk.Frame(r2, bg=PANEL, width=10).pack(side="left")
        for al, txt in (("left", "≡ L"), ("center", "≡ C"), ("right", "≡ R")):
            b = FlatButton(r2, txt, lambda a=al: self.set_align(a), font=UI_S, padx=6, pady=2, bg=BTN,
                           hover=BTN_H, tip=tr(f"Align {al}"))
            b.pack(side="left", padx=(0, 2))
            self.fmt_btns["al_" + al] = b
        r3 = tk.Frame(self.sec_text, bg=PANEL)
        r3.pack(fill="x", pady=(6, 0))
        ttk.Checkbutton(r3, text=tr("Background"), variable=self.tbg_on, command=lambda: self.on_prop("tbg")).pack(side="left")
        self.tbg_sw = tk.Label(r3, bg=self.tbg_color, width=3, relief="solid", bd=1, cursor="hand2")
        self.tbg_sw.pack(side="left", padx=6)
        self.tbg_sw.bind("<Button-1>", lambda e: self.pick_tbg())
        ttk.Checkbutton(r3, text=tr("Border"), variable=self.border, command=lambda: self.on_prop("border")).pack(side="left", padx=6)
        tk.Label(self.sec_text, text=tr("Double-click a text to edit it · drag to move"), bg=PANEL, fg=MUTED,
                 font=UI_S, wraplength=int(265 * self.k), justify="left").pack(anchor="w", pady=(4, 0))

        # size (markers / stamps / measurement labels)
        self.sec_size = self._section(P, "SIZE")
        ss = ttk.Spinbox(self.sec_size, from_=6, to=300, textvariable=self.fsize, width=6, command=lambda: self.on_prop("fsize"))
        ss.pack(anchor="w")
        ss.bind("<Return>", lambda e: (self.on_prop("fsize"), self._refocus()))
        ss.bind("<FocusOut>", lambda e: self.on_prop("fsize"))

        # stamps
        self.sec_stamp = self._section(P, "SYMBOL")
        st = tk.Frame(self.sec_stamp, bg=PANEL)
        st.pack(anchor="w")
        self.stamp_btns = {}
        for i, sym in enumerate(STAMPS):
            b = FlatButton(st, sym, lambda s_=sym: self.set_stamp(s_), font=("Segoe UI Symbol", 12), padx=6, pady=0,
                           bg=BTN, hover=BTN_H)
            b.grid(row=i // 5, column=i % 5, padx=1, pady=1)
            self.stamp_btns[sym] = b

        # measure
        self.sec_measure = self._section(P, "MEASURE")
        self.scale_lbl = tk.Label(self.sec_measure, text=tr("Scale: pixels (not calibrated)"), bg=PANEL, fg=TEXT, font=UI, anchor="w",
                                  justify="left")
        self.scale_lbl.pack(fill="x")
        mr = tk.Frame(self.sec_measure, bg=PANEL)
        mr.pack(fill="x", pady=(4, 0))
        FlatButton(mr, tr("Set scale…"), self.set_scale_manual, padx=5, pady=2, font=UI_S, bg=BTN, hover=BTN_H,
                   tip=tr("Enter how much one pixel represents")).pack(side="left")
        FlatButton(mr, tr("Calibrate"), lambda: self.set_tool("calib"), padx=5, pady=2, font=UI_S, bg=BTN,
                   hover=BTN_H, tip=tr("Draw a line over a known length")).pack(side="left", padx=3)
        FlatButton(mr, tr("Reset"), self.reset_scale, padx=5, pady=2, font=UI_S, bg=BTN, hover=BTN_H).pack(side="left")
        tk.Label(mr, text=tr("Dec."), bg=PANEL, fg=MUTED, font=UI_S).pack(side="left", padx=(8, 2))
        ds = ttk.Spinbox(mr, from_=0, to=6, textvariable=self.decimals, width=3, command=self._dec_changed)
        ds.pack(side="left")
        ds.bind("<Return>", lambda e: self._dec_changed())

        # notes
        tk.Frame(wrap, bg=BORDER, height=1).pack(fill="x", pady=(12, 0))
        nh = tk.Frame(wrap, bg=PANEL)
        nh.pack(fill="x", pady=(8, 4))
        self.notes_lbl = tk.Label(nh, text=tr("NOTES"), font=UI_H, bg=PANEL, fg=MUTED)
        self.notes_lbl.pack(side="left")
        nf = tk.Frame(wrap, bg=BORDER, padx=1, pady=1)
        nf.pack(fill="both", expand=True)
        self.notes = tk.Text(nf, wrap="word", font=("Segoe UI", 10), relief="flat", bd=0, padx=8, pady=6,
                             undo=True, bg=NOTES_BG, height=6, insertbackground=TEXT,
                             highlightthickness=0, selectbackground=ACCENT_L, selectforeground=TEXT)
        self.notes.pack(fill="both", expand=True)
        self.notes.bind("<<Modified>>", self._notes_modified)
        self.notes.bind("<FocusOut>", lambda e: self._schedule_copy(300))
        ttk.Checkbutton(wrap, text=tr("Include notes when copying / exporting"), variable=self.include_notes,
                        command=self._opts_changed).pack(anchor="w", pady=(6, 10))

    # ===================================================================== helpers
    def later(self, key, ms, fn):
        j = self._jobs.pop(key, None)
        if j:
            self.root.after_cancel(j)

        def run():
            self._jobs.pop(key, None)
            fn()
        self._jobs[key] = self.root.after(ms, run)

    def flush_jobs(self):
        for key, j in list(self._jobs.items()):
            self.root.after_cancel(j)
        jobs = dict(self._jobs)
        self._jobs.clear()
        return jobs

    def set_status(self, text):
        self.status.configure(text=text)

    def flash_msg(self, text):
        self.flash.configure(text=text)
        self.later("flash", 2600, lambda: self.flash.configure(text=""))

    def view_n(self):
        return dict(VIEW_MODES)[self.view.get()]

    def _typing(self):
        w = self.root.focus_get()
        return isinstance(w, (tk.Text, tk.Entry, ttk.Entry, tk.Spinbox))

    def _refocus(self):
        if self.edit_widget:
            self.edit_widget.focus_set()
        else:
            self.canvas.focus_set()

    def scale_of(self, it):
        cal = [o for o in it["objs"] if o["type"] == "calib"]
        if cal:
            o = cal[-1]
            px = math.hypot(o["p"][1][0] - o["p"][0][0], o["p"][1][1] - o["p"][0][1])
            if px > 0:
                return (o["real"] / px, o["unit"])
        if it.get("scale"):
            return tuple(it["scale"])
        if self.st.get("default_scale"):
            return tuple(self.st["default_scale"])
        return (1.0, "px")

    def to_img(self, cx, cy):
        return cx / self.s + self.vx, cy / self.s + self.vy

    def to_canvas(self, x, y):
        return (x - self.vx) * self.s, (y - self.vy) * self.s

    # ===================================================================== items
    def new_item(self, img, **kw):
        it = {"id": uuid.uuid4().hex[:12], "orig": img, "size": img.size, "objs": [], "notes": "", "time": datetime.now(),
              "scale": None, "num": self.st["next_num"], "undo": [], "redo": [], "_final": None, "dirty": True}
        self.st["next_num"] += 1
        it.update(kw)
        return it

    def img_of(self, it):
        """Full-size original of a screenshot, reloaded from the session folder if it was evicted."""
        im = it.get("orig")
        if im is None:
            self._wait_saved(it)
            try:
                with Image.open(os.path.join(SESSION_DIR, it["id"] + ".png")) as f:
                    im = f.convert("RGB")
            except Exception as ex:   # file removed or damaged outside the app
                print("reload", it["id"], ex)
                im = Image.new("RGB", it["size"], "#D1D5DB")
                it["on_disk"] = False
            it["orig"] = im
        self._tick += 1
        it["_used"] = self._tick
        self._evict()
        return im

    def _evict(self):
        loaded = [i for i in self.items if i.get("orig") is not None and i.get("on_disk")]
        if len(loaded) <= MAX_LOADED:
            return
        keep = {id(i) for i in self.board_items()} | {id(self.sel)}
        loaded.sort(key=lambda i: i.get("_used", 0))
        for i in loaded[:len(loaded) - MAX_LOADED]:
            if id(i) not in keep:
                i["orig"] = None
                i["_final"] = None
                i["_gkey"] = None

    def final(self, it):
        if it.get("_final") is None:
            img = self.img_of(it).convert("RGBA")
            draw_objects(img, it["objs"], 1.0, 0, 0, self.scale_of(it))
            it["_final"] = img.convert("RGB")
        return it["_final"]

    def with_notes(self, it, title=False):
        img = self.final(it)
        if self.include_notes.get() and it["notes"].strip():
            img = add_notes_strip(img, it["notes"], f"#{it['num']}  ·  {it['time']:%Y-%m-%d %H:%M}" if title else None)
        return img

    def board_items(self):
        n = self.view_n()
        if n == 1:
            return [self.sel] if self.sel else []
        return self.board[-n:] if n else list(self.board)

    def view_image(self):
        n = self.view_n()
        if n == 1:
            return self.out_image(self.sel) if self.sel else None
        items = self.board_items()
        if not items:
            return None
        if len(items) == 1:
            return self.out_image(items[0])
        return self.framed(compose_grid([self.with_notes(i) for i in items]), None, len(items))

    def out_image(self, it, title=False):
        """Screenshot as it is copied / exported: annotations, notes and the theme frame."""
        return self.framed(self.with_notes(it, title), it)

    def framed(self, img, it=None, count=1):
        th = self.theme
        if not (th.frame and self.theme_frame.get()):
            return img
        t = it["time"] if it else datetime.now()
        ctx = {"title": f"{APP_NAME}  ·  #{it['num']}" if it else APP_NAME, "app": APP_NAME,
               "date": f"{t:%Y-%m-%d}", "time": f"{t:%H:%M}", "num": it["num"] if it else "", "count": count,
               "theme": th.name(LANG[0])}
        try:
            return themes.apply_frame(img, th, ctx, frame_font)
        except Exception as ex:   # a broken theme must never stop a copy or a save
            self.set_status(tr("Theme frame skipped: {e}", e=ex))
            return img

    # ===================================================================== capture
    def new_capture(self):
        if self.busy:
            return
        self.commit_edit()
        self.cancel_building()
        self.busy = True
        d = {"No delay": 0, "3 s": 3, "5 s": 5, "10 s": 10}.get(self._key(self.delay_var, DELAY_KEYS), 0)
        self.root.withdraw()
        self.root.after(280 + d * 1000, self._grab)

    def _grab(self):
        try:
            shot = ImageGrab.grab(all_screens=True)
        except Exception as ex:
            self.busy = False
            self.root.deiconify()
            messagebox.showerror(tr("Capture failed"), str(ex))
            return
        mode = self._key(self.mode_var, self._mode_keys())
        if mode == SCROLL_MODE:
            RegionSelector(self.root, shot, virtual_screen(), self._scroll_region)
        elif mode == "Full screen":
            self._capture_done(shot, None)
        elif (mode == "Last region" and self.last_region and self.last_region[2] <= shot.width
              and self.last_region[3] <= shot.height):
            self._capture_done(shot.crop(self.last_region), self.last_region)
        else:
            RegionSelector(self.root, shot, virtual_screen(), self._capture_done)

    def _capture_done(self, img, box):
        self.busy = False
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        if img is None:
            self.set_status(tr("Capture cancelled"))
            return
        if box:
            self.last_region = box
        it = self.new_item(img.convert("RGB"))
        self.items.insert(0, it)
        self.board.append(it)
        self._persist_new(it)
        self._prune()
        self._rebuild_list()
        self.select_item(it)
        self.set_status(tr("Screenshot #{n} added  ({w} × {h})", n=it["num"], w=img.width, h=img.height))
        if self.autocopy.get():
            self.copy_view(auto=True)
        if self.autosave.get():
            self._export_auto(it)

    def _prune(self):
        lim = int(self.st.get("history_limit", 200))
        while len(self.items) > lim:
            old = self.items.pop()
            if old in self.board:
                self.board.remove(old)
            self._delete_files(old)

    # ===================================================================== persistence
    def _persist_new(self, it):
        if not self.keep_history.get():
            return
        os.makedirs(SESSION_DIR, exist_ok=True)
        img = it["orig"]
        p = os.path.join(SESSION_DIR, it["id"] + ".png")

        def work():
            # write to a temp file first, so an interrupted save never leaves a truncated PNG
            try:
                img.save(p + ".tmp", "PNG", compress_level=3)
                os.replace(p + ".tmp", p)
                it["on_disk"] = True
            except Exception as ex:
                print("png save", ex)
        t = threading.Thread(target=work)
        it["_save_thread"] = t
        t.start()
        self._save_meta(it)
        self._save_board()

    def _wait_saved(self, it):
        t = it.get("_save_thread")
        if t is not None:
            t.join()
            it["_save_thread"] = None

    def _save_meta(self, it):
        if not self.keep_history.get():
            return
        try:
            os.makedirs(SESSION_DIR, exist_ok=True)
            meta = {"id": it["id"], "num": it["num"], "time": it["time"].isoformat(), "objs": it["objs"],
                    "notes": it["notes"], "scale": it["scale"], "dirty": it.get("dirty", False)}
            with open(os.path.join(SESSION_DIR, it["id"] + ".json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False)
        except Exception as ex:
            print("meta save", ex)

    def _save_board(self):
        if not self.keep_history.get():
            return
        try:
            with open(os.path.join(SESSION_DIR, "board.json"), "w", encoding="utf-8") as f:
                json.dump({"order": [i["id"] for i in self.board]}, f)
        except Exception:
            pass

    def _delete_files(self, it):
        self._wait_saved(it)
        for ext in (".png", ".json", ".png.tmp"):
            try:
                os.remove(os.path.join(SESSION_DIR, it["id"] + ext))
            except OSError:
                pass

    def _load_history(self):
        if not self.keep_history.get() or not os.path.isdir(SESSION_DIR):
            self.render()
            return
        metas = []
        for fn in os.listdir(SESSION_DIR):
            if fn.endswith(".json") and fn != "board.json":
                try:
                    with open(os.path.join(SESSION_DIR, fn), encoding="utf-8") as f:
                        metas.append(json.load(f))
                except Exception:
                    pass
        metas = [m for m in metas if isinstance(m, dict) and isinstance(m.get("id"), str)]
        metas.sort(key=lambda m: str(m.get("time", "")))
        byid = {}
        for m in metas:
            p = os.path.join(SESSION_DIR, m["id"] + ".png")
            try:
                with Image.open(p) as im:   # reads only the header; pixels load on demand
                    size = im.size
                t = datetime.fromisoformat(m["time"])
                objs = [o for o in m.get("objs") or [] if isinstance(o, dict) and "type" in o]
            except Exception as ex:
                print("skipping session item", m.get("id"), ex)
                if not os.path.exists(p):   # orphan metadata left by an interrupted save
                    try:
                        os.remove(os.path.join(SESSION_DIR, m["id"] + ".json"))
                    except OSError:
                        pass
                continue
            it = {"id": m["id"], "orig": None, "size": size, "on_disk": True, "objs": objs,
                  "notes": str(m.get("notes") or ""), "time": t, "scale": m.get("scale"),
                  "num": int(m.get("num") or 0), "undo": [], "redo": [], "_final": None,
                  "dirty": bool(m.get("dirty", False))}
            for o in it["objs"]:
                o.setdefault("id", uuid.uuid4().hex[:8])
            self.items.insert(0, it)
            byid[it["id"]] = it
        order = []
        try:
            with open(os.path.join(SESSION_DIR, "board.json"), encoding="utf-8") as f:
                order = json.load(f).get("order", [])
            if not isinstance(order, list):
                order = []
        except Exception:
            pass
        self.board = [byid[i] for i in order if i in byid]
        self.board += [it for it in reversed(self.items) if it not in self.board]
        if self.items:
            self.st["next_num"] = max(self.st["next_num"], max(i["num"] for i in self.items) + 1)
        self._rebuild_list()
        if self.items:
            self.select_item(self.items[0])
            self.set_status(tr("{n} screenshots restored from last session", n=len(self.items)))
        else:
            self.render()

    def _export_auto(self, it):
        d = self.st.get("save_dir") or DEFAULT_SAVE_DIR
        try:
            os.makedirs(d, exist_ok=True)
            p = it.get("export") or os.path.join(d, f"Capture_{it['time']:%Y-%m-%d_%H-%M-%S}_{it['num']}.png")
            it["export"] = p
            self.with_notes(it).save(p)
            it["dirty"] = False
        except Exception as ex:
            self.set_status(tr("Auto-save failed: {e}", e=ex))

    # ===================================================================== history list
    def _rebuild_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.cards = {}
        for it in self.items:
            self._make_card(it)
        self.count_lbl.configure(text=tr("HISTORY  ·  {n}", n=len(self.items)))
        self._update_cards()

    def _thumb(self, it):
        t = self.final(it).copy()
        t.thumbnail((int(180 * self.k), int(112 * self.k)), Image.LANCZOS)
        it["_thumb"] = ImageTk.PhotoImage(t)
        return it["_thumb"]

    def _make_card(self, it):
        fr = tk.Frame(self.list_frame, bg=PANEL, highlightthickness=2, highlightbackground=PANEL, padx=4, pady=4)
        fr.pack(fill="x", padx=6, pady=2)
        img = tk.Label(fr, image=self._thumb(it), bg=PANEL)
        img.pack()
        cap = tk.Label(fr, bg=PANEL, font=UI_S, fg=MUTED, anchor="w")
        cap.pack(fill="x")
        for w in (fr, img, cap):
            w.bind("<Button-1>", lambda e, i=it: self.select_item(i))
            w.bind("<Double-Button-1>", lambda e, i=it: (self.set_view("Single"), self.select_item(i)))
            w.bind("<Button-3>", lambda e, i=it: self._card_menu(e, i))
        self.cards[it["id"]] = (fr, img, cap)
        self._card_caption(it)

    def _card_caption(self, it):
        c = self.cards.get(it["id"])
        if not c:
            return
        on_board = it in self.board_items() and self.view_n() != 1
        marks = ("  ●" if it["objs"] else "") + ("  ¶" if it["notes"].strip() else "") + ("  ▦" if on_board else "")
        c[2].configure(text=f"#{it['num']}  {it['time']:%d/%m %H:%M:%S}   {it['size'][0]}×{it['size'][1]}{marks}")

    def _update_cards(self):
        for it in self.items:
            c = self.cards.get(it["id"])
            if not c:
                continue
            sel = it is self.sel
            bg = ACCENT_L if sel else PANEL
            c[0].configure(bg=bg, highlightbackground=ACCENT if sel else PANEL)
            c[1].configure(bg=bg)
            c[2].configure(bg=bg, fg=ACCENT_D if sel else MUTED)
            self._card_caption(it)

    def _refresh_thumb(self, it):
        c = self.cards.get(it["id"])
        if c:
            c[1].configure(image=self._thumb(it))
            self._card_caption(it)

    def _card_menu(self, e, it):
        m = tk.Menu(self.root, tearoff=0, font=UI)
        m.add_command(label=tr("Open"), command=lambda: (self.set_view("Single"), self.select_item(it)))
        m.add_command(label=tr("Copy this screenshot"), command=lambda: self._copy_img(self.out_image(it), f"#{it['num']}"))
        m.add_command(label=tr("Save this screenshot as…"),
                      command=lambda: self._save_img(self.out_image(it), f"Capture_{it['num']}", [it]))
        if self.feat["feat_pin"].get():
            m.add_command(label=tr("Pin to screen"), command=lambda: self.pin_image(self.final(it)))
        if self.feat["feat_ocr"].get():
            m.add_command(label=tr("Extract text (OCR)"), command=lambda: self.ocr_image(self.final(it)))
        m.add_separator()
        if it in self.board:
            m.add_command(label=tr("Move to end of board (newest position)"), command=lambda: self._board_to_end(it))
        m.add_separator()
        m.add_command(label=tr("Delete"), command=lambda: self.delete_item(it))
        m.add_command(label=tr("Delete ALL screenshots…"), command=lambda: self.delete_many(list(self.items)))
        m.tk_popup(e.x_root, e.y_root)

    def _board_to_end(self, it):
        self.board.remove(it)
        self.board.append(it)
        self._save_board()
        self._update_cards()
        self.render()
        self._schedule_copy()

    def select_item(self, it):
        if it is not self.sel:
            self.commit_edit()
            self.cancel_building()
            self.sel_obj = None
            self.fit = True
        self.sel = it
        self._load_notes()
        self._update_cards()
        self._update_panel()
        self.render()
        c = self.cards.get(it["id"]) if it else None
        if c:
            self.root.after_idle(lambda: self._scroll_to_card(c[0]))

    def _scroll_to_card(self, w):
        try:
            total = self.list_frame.winfo_height()
            if total <= 0:
                return
            y0, h = w.winfo_y(), w.winfo_height()
            top, bot = self.list_canvas.canvasy(0), self.list_canvas.canvasy(self.list_canvas.winfo_height())
            if y0 < top:
                self.list_canvas.yview_moveto(y0 / total)
            elif y0 + h > bot:
                self.list_canvas.yview_moveto((y0 + h - self.list_canvas.winfo_height()) / total)
        except Exception:
            pass

    def delete_item(self, it=None):
        it = it or self.sel
        if not it:
            return
        if not messagebox.askyesno(tr("Delete screenshot"), tr("Delete screenshot #{n} from the history?", n=it["num"]),
                                   parent=self.root):
            return
        idx = self.items.index(it)
        self._forget_jobs(it)
        self.items.remove(it)
        if it in self.board:
            self.board.remove(it)
        self._delete_files(it)
        self._save_board()
        if self.sel is it:
            self.sel = self.items[min(idx, len(self.items) - 1)] if self.items else None
            self.sel_obj = None
            self.editing = None
        self._rebuild_list()
        if self.sel:
            self.select_item(self.sel)
        else:
            self._load_notes()
            self.render()
        self.set_status(tr("Screenshot #{n} deleted", n=it["num"]))
        self._schedule_copy()

    # ===================================================================== notes
    def _load_notes(self):
        self._notes_loading = True
        self.notes.delete("1.0", "end")
        if self.sel:
            self.notes.insert("1.0", self.sel["notes"])
            self.notes.configure(state="normal", bg=NOTES_BG)
            self.notes_lbl.configure(text=tr("NOTES  ·  #{n}", n=self.sel["num"]))
        else:
            self.notes_lbl.configure(text=tr("NOTES"))
        self.notes.edit_reset()
        self.notes.edit_modified(False)
        self._notes_loading = False

    def _notes_modified(self, e=None):
        if not self.notes.edit_modified():
            return
        self.notes.edit_modified(False)
        if self._notes_loading or not self.sel:
            return
        it = self.sel
        it["notes"] = self.notes.get("1.0", "end-1c")
        it["dirty"] = True
        self.later("meta_" + it["id"], 800, lambda: self._save_meta(it))
        self.later("card_" + it["id"], 500, lambda: self._card_caption(it))
        if self.autosave.get():
            self.later("exp_" + it["id"], 1500, lambda: self._export_auto(it))
        if self.view_n() != 1:
            self.later("render_notes", 400, self.render)

    # ===================================================================== view
    def set_view(self, name):
        self.commit_edit()
        self.cancel_building()
        self.view.set(name)
        self.st["view"] = name
        self._refresh_view_btns()
        if self.view_n() != 1 and self.tool.get() != "select":
            self.tool.set("select")
            self._tool_changed()
        self.fit = True
        self._update_cards()
        self.render()
        self._schedule_copy(150)

    def _refresh_view_btns(self):
        for name, b in self.view_btns.items():
            if name == self.view.get():
                b.set_colors(ACCENT, "white", ACCENT_D)
            else:
                b.set_colors(PANEL, TEXT, HOVER)

    def request_render(self):
        if not self._render_pending:
            self._render_pending = True
            self.root.after_idle(self._do_render)

    def _do_render(self):
        self._render_pending = False
        self.render()

    def render(self):
        c = self.canvas
        c.delete("content")
        self._cells = []
        self._grip = None
        cw, ch = max(c.winfo_width(), 50), max(c.winfo_height(), 50)
        self._draw_deco(cw, ch)
        if not self.items:
            self._draw_empty(cw, ch)
            self.zoom_lbl.configure(text="")
            self.size_lbl.configure(text="")
            return
        if self.view_n() != 1:
            self._draw_board(cw, ch)
        else:
            self._draw_single(cw, ch)

    def _draw_deco(self, cw, ch):
        """Theme picture behind the screenshots (e.g. a moon in a corner, or a tiled pattern)."""
        if self._deco_key == (cw, ch):
            return
        self._deco_key = (cw, ch)
        self.canvas.delete("deco")
        deco = self.theme.decoration("canvas")
        if not deco:
            return
        try:
            self._deco_photo = ImageTk.PhotoImage(themes.decoration_image(deco, (cw, ch)))
        except Exception:
            return
        self.canvas.create_image(0, 0, anchor="nw", image=self._deco_photo, tags="deco")
        self.canvas.tag_lower("deco")

    def _draw_empty(self, cw, ch):
        c = self.canvas
        x, y = cw / 2, ch / 2
        c.create_rectangle(x - 270, y - 120, x + 270, y + 120, fill=PANEL, outline=BORDER, tags="content")
        c.create_text(x, y - 68, text=tr("No screenshots yet"), font=("Segoe UI Semibold", 15), fill=TEXT, tags="content")
        c.create_text(x, y - 26, text=tr("Click  ＋ New capture  or press  Ctrl+Alt+S  anywhere."), font=UI, fill=MUTED, tags="content")
        c.create_text(x, y + 4, text=tr("Every capture is kept in the history — nothing is overwritten."), font=UI, fill=MUTED, tags="content")
        c.create_text(x, y + 40, text=tr("The current view (single or grid) is copied automatically —\njust paste it into Outlook, Word or Excel."),
                      font=UI, fill=MUTED, justify="center", tags="content")
        c.create_text(x, y + 86, text=tr("Press F1 for the user guide"), font=UI_B, fill=ACCENT, tags="content")

    # ---------------------------------------------------------------- single
    def _draw_single(self, cw, ch):
        c = self.canvas
        it = self.sel
        if not it:
            return
        W, H = it["size"]
        if self.fit:
            self.s = max(0.02, min((cw - 48) / W, (ch - 48) / H, 1.0))
            self.vx = -(cw / self.s - W) / 2
            self.vy = -(ch / self.s - H) / 2
        s = self.s
        ix0, iy0 = max(0, math.floor(self.vx)), max(0, math.floor(self.vy))
        ix1, iy1 = min(W, math.ceil(self.vx + cw / s)), min(H, math.ceil(self.vy + ch / s))
        self.zoom_lbl.configure(text=f"{s * 100:.0f}%")
        self.size_lbl.configure(text=f"#{it['num']}  ·  {W} × {H} px")
        if ix1 <= ix0 or iy1 <= iy0:
            return
        key = (it["id"], round(s, 6), ix0, iy0, ix1, iy1)
        if self._base_key != key:
            crop = self.img_of(it).crop((ix0, iy0, ix1, iy1))
            dw, dh = max(1, round((ix1 - ix0) * s)), max(1, round((iy1 - iy0) * s))
            rs = Image.LANCZOS if s < 1 else (Image.NEAREST if s >= 3 else Image.BICUBIC)
            self._base = (crop.resize((dw, dh), rs) if (dw, dh) != crop.size else crop).convert("RGBA")
            self._base_key = key
        img = self._base.copy()
        objs = list(it["objs"])
        if self.building:
            objs.append(self.building)
        draw_objects(img, objs, s, ix0, iy0, self.scale_of(it), skip_id=self.editing["id"] if self.editing else None)
        self._photo = ImageTk.PhotoImage(img)
        px, py = (ix0 - self.vx) * s, (iy0 - self.vy) * s
        c.create_rectangle(px + 3, py + 3, px + img.width + 3, py + img.height + 3, fill=SHADOW, outline="",
                           tags="content")
        c.create_image(px, py, anchor="nw", image=self._photo, tags="content")
        self._draw_selection()
        if self.editing and self.edit_win:
            self._place_editor()
            c.tag_raise("editor")

    def _draw_selection(self):
        self._grip = None
        if self.editing:                      # text being typed: grip at the editor's top-left corner
            a, b = self.to_canvas(self.editing["x"], self.editing["y"])
            self._draw_grip(a - 4, b - 4)
            return
        o = self.sel_obj
        if not o or o not in (self.sel["objs"] if self.sel else []):
            return
        c = self.canvas
        x0, y0, x1, y1 = obj_bbox(o)
        a, b = self.to_canvas(x0, y0)
        cc, d = self.to_canvas(x1, y1)
        c.create_rectangle(a - 4, b - 4, cc + 4, d + 4, outline=ACCENT, dash=(4, 3), tags="content")
        hs = handles(o)
        solid = bool(o.get("solid")) and o["type"] in solid3d.SOLID_TYPES
        for i, (hx, hy) in enumerate(hs):
            x, y = self.to_canvas(hx, hy)
            if solid and i == len(hs) - 1:        # depth / angle handle: orange diamond
                c.create_polygon(x, y - 7, x + 7, y, x, y + 7, x - 7, y, fill="#FB8C00", outline="white",
                                 width=2, tags="content")
            else:
                c.create_rectangle(x - 5, y - 5, x + 5, y + 5, fill="white", outline=ACCENT, width=2, tags="content")
        self._draw_grip(a - 4, b - 4)

    def _draw_grip(self, x, y):
        """Blue ✥ move handle just outside the top-left corner - drag it to move the object."""
        c = self.canvas
        cx, cy, r, L = x - 12, y - 12, 11, 7
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=ACCENT, outline="white", width=2, tags="content")
        c.create_line(cx - L, cy, cx + L, cy, fill="white", width=2, arrow="both", arrowshape=(4, 4, 3), tags="content")
        c.create_line(cx, cy - L, cx, cy + L, fill="white", width=2, arrow="both", arrowshape=(4, 4, 3), tags="content")
        self._grip = (cx, cy)

    def _on_grip(self, e):
        return self._grip is not None and math.hypot(e.x - self._grip[0], e.y - self._grip[1]) <= 13

    # ---------------------------------------------------------------- board
    def _draw_board(self, cw, ch, hover=None):
        c = self.canvas
        c.delete("content")
        self._cells = []
        items = self.board_items()
        self.zoom_lbl.configure(text="")
        self.size_lbl.configure(text=tr("Board: {n} screenshot(s)  ·  drag to reorder", n=len(items)))
        if not items:
            return
        cols, rows = grid_shape(len(items))
        gap = 14
        cell_w = (cw - gap * (cols + 1)) / cols
        cell_h = (ch - gap * (rows + 1)) / rows
        for k, it in enumerate(items):
            r, col = divmod(k, cols)
            x0, y0 = gap + col * (cell_w + gap), gap + r * (cell_h + gap)
            sel = it is self.sel
            outline = "#F59E0B" if hover is it else (ACCENT if sel else BORDER)
            c.create_rectangle(x0 + 2, y0 + 2, x0 + cell_w + 2, y0 + cell_h + 2, fill=SHADOW, outline="", tags="content")
            c.create_rectangle(x0, y0, x0 + cell_w, y0 + cell_h, fill=PANEL, outline=outline,
                               width=3 if (sel or hover is it) else 1, tags="content")
            img = self.with_notes(it)
            tw, th = int(cell_w - 12), int(cell_h - 30)
            key = (tw, th, id(img))
            if it.get("_gkey") != key:
                sc = min(tw / img.width, th / img.height, 1.0)
                disp = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))),
                                  Image.LANCZOS if sc < 1 else Image.NEAREST)
                it["_gphoto"] = ImageTk.PhotoImage(disp)
                it["_gkey"] = key
            c.create_image(x0 + cell_w / 2, y0 + 6 + th / 2, image=it["_gphoto"], tags="content")
            c.create_text(x0 + 10, y0 + cell_h - 12, anchor="w", fill=ACCENT if sel else MUTED, font=UI_S, tags="content",
                          text=tr("Position {k}", k=k + 1) + f"   ·   #{it['num']}   {it['time']:%H:%M:%S}"
                               + ("   ·   " + tr("annotated") if it["objs"] else "")
                               + ("   ·   " + tr("notes") if it["notes"].strip() else ""))
            self._cells.append((x0, y0, x0 + cell_w, y0 + cell_h, it))

    def _cell_at(self, x, y):
        for x0, y0, x1, y1, it in self._cells:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return it
        return None

    # ===================================================================== zoom / pan
    def zoom_at(self, f, cx=None, cy=None):
        if self.view_n() != 1 or not self.sel:
            return
        c = self.canvas
        if cx is None:
            cx, cy = c.winfo_width() / 2, c.winfo_height() / 2
        x, y = self.to_img(cx, cy)
        self.s = min(16.0, max(0.03, self.s * f))
        self.fit = False
        self.vx, self.vy = x - cx / self.s, y - cy / self.s
        self.render()

    def zoom_fit(self):
        self.fit = True
        self.render()

    def zoom_100(self):
        if self.view_n() != 1 or not self.sel:
            return
        self.zoom_at(1.0 / self.s)

    def _pan_move(self, e):
        if self.view_n() != 1 or not hasattr(self, "_pan"):
            return
        lx, ly = self._pan
        self.vx -= (e.x - lx) / self.s
        self.vy -= (e.y - ly) / self.s
        self._pan = (e.x, e.y)
        self.fit = False
        self.request_render()

    def _wheel(self, e):
        w = self.root.winfo_containing(e.x_root, e.y_root)
        while w is not None:
            if w is self.list_canvas or w is self.list_frame:
                self.list_canvas.yview_scroll(int(-e.delta / 120), "units")
                return
            if w is self.canvas:
                if self.view_n() != 1 or not self.sel:
                    return
                if e.state & 0x4:
                    self.zoom_at(1.15 if e.delta > 0 else 1 / 1.15, e.x_root - self.canvas.winfo_rootx(),
                                 e.y_root - self.canvas.winfo_rooty())
                elif not self.fit:
                    step = 80 / self.s * (1 if e.delta < 0 else -1)
                    if e.state & 0x1:
                        self.vx += step
                    else:
                        self.vy += step
                    self.request_render()
                return
            w = w.master

    # ===================================================================== tools / panel
    def set_tool(self, key):
        self.tool.set(key)
        self._tool_changed()

    def _tool_changed(self):
        self.commit_edit()
        self.cancel_building()
        t = self.tool.get()
        if t != "select" and self.view_n() != 1:
            self.set_view("Single")
        if t != "select":
            self.sel_obj = None
        cur = {"select": "arrow", "text": "xterm"}.get(t, "crosshair")
        self.canvas.configure(cursor=cur)
        self._update_panel()
        self.render()
        self.set_status(tr("Tool: {name}", name=tr(TOOL_NAMES[t])) + tr({
            "perim": "  ·  click points, double-click / Enter to finish, Esc to cancel",
            "area": "  ·  click points, double-click / Enter to finish, Esc to cancel",
            "angle": "  ·  click 3 points (vertex second)",
            "calib": "  ·  draw a line over a known length",
            "callout": "  ·  press on the target, drag to where the text goes",
            "text": "  ·  click to add text, click an existing text to edit it",
        }.get(t, "")))
        self.canvas.focus_set()

    def _update_panel(self):
        o = self.sel_obj
        kind = o["type"] if o else self.tool.get()
        if o:
            self.sel_lbl.configure(text=tr(TOOL_NAMES.get(kind, kind)) + (tr("  (callout)") if kind == "text" and o.get("leader") else ""))
        else:
            self.sel_lbl.configure(text=tr("Nothing selected  ·  click an annotation") if self.tool.get() == "select"
                                   else tr("New: {name}", name=tr(TOOL_NAMES.get(kind, kind))))
        show = {
            "sec_sel": True,
            "sec_color": kind != "mosaic",
            "sec_stroke": kind in ("pen", "highlight", "line", "arrow", "rect", "ellipse", "mosaic", "dist", "calib",
                                   "perim", "area", "angle", "callout") or (kind == "text" and o and o.get("leader")),
            "sec_fill": kind in ("rect", "ellipse", "area"),
            "sec_solid": bool(o) and kind in solid3d.SOLID_TYPES,
            "sec_text": kind in ("text", "callout"),
            "sec_size": kind in ("marker", "stamp", "dist", "calib", "perim", "area", "angle"),
            "sec_stamp": kind == "stamp",
            "sec_measure": kind in ("dist", "calib", "perim", "area", "angle") or kind == "select",
        }
        for name in ("sec_sel", "sec_color", "sec_stroke", "sec_fill", "sec_solid", "sec_text", "sec_size", "sec_stamp", "sec_measure"):
            getattr(self, name).pack_forget()
        for name in ("sec_sel", "sec_color", "sec_stroke", "sec_fill", "sec_solid", "sec_text", "sec_size", "sec_stamp", "sec_measure"):
            if show[name]:
                getattr(self, name).pack(fill="x")
        self._refresh_swatches()
        self._refresh_fmt_btns()
        if show["sec_solid"]:
            on = bool(o.get("solid"))
            self.solid_btn.configure(text=("▭ " + tr("Make flat")) if on else ("⬛ " + tr("Make 3D")))
            self.solid_cut.set(bool(on and o["solid"].get("cut")))
            self.solid_cut_cb.state(["!disabled"] if on else ["disabled"])
            if on:
                self.solid_hint.pack(anchor="w", pady=(4, 0))
            else:
                self.solid_hint.pack_forget()
        if self.sel:
            k, u = self.scale_of(self.sel)
            src = ("reference line" if any(x["type"] == "calib" for x in self.sel["objs"])
                   else "this screenshot" if self.sel.get("scale") else "default")
            self.scale_lbl.configure(text=tr("Scale: 1 px = {k} {u}\nSource: {src}", k=f"{k:.5g}", u=u, src=tr(src))
                                     if u != "px" else tr("Scale: pixels (not calibrated)"))

    def _refresh_swatches(self):
        for f, col in self.swatches:
            f.configure(highlightbackground=ACCENT if col.lower() == self.color.lower() else PANEL)
        self.cur_sw.configure(bg=self.color)
        self.fill_sw.configure(bg=self.fill_color)
        self.tbg_sw.configure(bg=self.tbg_color)

    def _refresh_fmt_btns(self):
        for k in ("bold", "italic", "underline"):
            on = getattr(self, k).get()
            self.fmt_btns[k].set_colors(ACCENT if on else BTN, "white" if on else TEXT, ACCENT_D if on else BTN_H)
        for al in ("left", "center", "right"):
            on = self.align.get() == al
            self.fmt_btns["al_" + al].set_colors(ACCENT if on else BTN, "white" if on else TEXT,
                                                 ACCENT_D if on else BTN_H)
        for sym, b in self.stamp_btns.items():
            on = self.stamp.get() == sym
            b.set_colors(ACCENT if on else BTN, "white" if on else TEXT, ACCENT_D if on else BTN_H)

    def set_color(self, c):
        self.color = c
        self.st["color"] = c
        self._refresh_swatches()
        self.on_prop("color")

    def pick_color(self):
        c = colorchooser.askcolor(color=self.color, title=tr("Annotation colour"), parent=self.root)[1]
        if c:
            self.set_color(c.upper())
        self._refocus()

    def pick_fill(self):
        c = colorchooser.askcolor(color=self.fill_color, title=tr("Fill colour"), parent=self.root)[1]
        if c:
            self.fill_color = c.upper()
            self.fill_on.set(True)
            self._refresh_swatches()
            self.on_prop("fill")
        self._refocus()

    def pick_tbg(self):
        c = colorchooser.askcolor(color=self.tbg_color, title=tr("Text background"), parent=self.root)[1]
        if c:
            self.tbg_color = c.upper()
            self.tbg_on.set(True)
            self._refresh_swatches()
            self.on_prop("tbg")
        self._refocus()

    def toggle_fmt(self, key):
        v = getattr(self, key)
        v.set(not v.get())
        self._refresh_fmt_btns()
        self.on_prop(key)

    def set_align(self, a):
        self.align.set(a)
        self._refresh_fmt_btns()
        self.on_prop("align")

    def set_stamp(self, sym):
        self.stamp.set(sym)
        self._refresh_fmt_btns()
        if self.tool.get() != "stamp" and not (self.sel_obj and self.sel_obj["type"] == "stamp"):
            self.set_tool("stamp")
        self.on_prop("stamp")

    def _dec_changed(self):
        try:
            _DEC[0] = max(0, min(6, int(self.decimals.get())))
        except (ValueError, tk.TclError):
            return
        self.st["decimals"] = _DEC[0]
        for it in self.items:
            if any(o["type"] in ("dist", "perim", "area") for o in it["objs"]):
                it["_final"] = None
                it["_gkey"] = None
        self.render()

    def _fs(self):
        try:
            return max(6, min(300, int(self.fsize.get())))
        except (ValueError, tk.TclError):
            return 20

    def _w(self):
        try:
            return max(1, int(self.width_var.get()))
        except (ValueError, tk.TclError):
            return 3

    def on_prop(self, key):
        if self._loading:
            return
        st = self.st
        st.update(width=self._w(), fill_on=self.fill_on.get(), fill_color=self.fill_color, fill_alpha=self.fill_alpha.get(),
                  family=self.family.get(), fsize=self._fs(), bold=self.bold.get(), italic=self.italic.get(),
                  underline=self.underline.get(), align=self.align.get(), tbg_on=self.tbg_on.get(),
                  tbg_color=self.tbg_color, border=self.border.get(), stamp=self.stamp.get())
        o = self.sel_obj
        if not o or not self.sel or self.view_n() != 1 or o not in self.sel["objs"]:
            return
        t = o["type"]
        before = json.dumps(o, sort_keys=True)
        snap = json.dumps(self.sel["objs"])
        if key == "color" and t != "mosaic":
            o["color"] = self.color
        elif key == "width":
            if t == "mosaic":
                o["block"] = max(4, self._w() * 3)
            elif t not in ("marker", "stamp"):
                o["width"] = self._w()
        elif key == "fill" and t in ("rect", "ellipse"):
            o["fill"] = self.fill_color if self.fill_on.get() else None
            o["fill_alpha"] = self.fill_alpha.get()
        elif key == "alpha" and t in ("rect", "ellipse", "area"):
            o["fill_alpha"] = self.fill_alpha.get()
            if t != "area" and self.fill_on.get():
                o["fill"] = self.fill_color
        elif key == "fsize":
            if t == "text":
                o["size"] = self._fs()
            elif t in ("marker", "stamp"):
                o["size"] = self._fs()
            elif t in ("dist", "calib", "perim", "area", "angle"):
                o["fs"] = max(8, round(self._fs() * 0.7))
        elif t == "text" and key in ("family", "bold", "italic", "underline", "align", "tbg", "border"):
            o["family"] = self.family.get()
            o["bold"], o["italic"], o["underline"] = self.bold.get(), self.italic.get(), self.underline.get()
            o["align"] = self.align.get()
            o["bg"] = self.tbg_color if self.tbg_on.get() else None
            o["border"] = self.border.get()
        elif key == "stamp" and t == "stamp":
            o["sym"] = self.stamp.get()
        if json.dumps(o, sort_keys=True) == before:
            return
        lid, lkey, lt = self._last_prop
        if not (lid == o["id"] and lkey == key and time.time() - lt < 1.5):
            self._push_undo_snapshot(snap)
        self._last_prop = (o["id"], key, time.time())
        if self.editing is o:
            self._style_editor()
        self.changed()

    def _load_props(self, o):
        self._loading = True
        try:
            if "color" in o:
                self.color = o["color"]
            if "width" in o and o["type"] not in ("marker", "stamp"):
                self.width_var.set(int(round(o["width"])))
            if o["type"] == "mosaic":
                self.width_var.set(max(1, int(o.get("block", 12) / 3)))
            if o["type"] in ("rect", "ellipse"):
                self.fill_on.set(bool(o.get("fill")))
                if o.get("fill"):
                    self.fill_color = o["fill"]
                self.fill_alpha.set(o.get("fill_alpha", 40))
            if o["type"] == "area":
                self.fill_alpha.set(o.get("fill_alpha", 25))
            if o["type"] == "text":
                self.family.set(o.get("family", "Segoe UI"))
                self.fsize.set(int(round(o["size"])))
                self.bold.set(o.get("bold", False))
                self.italic.set(o.get("italic", False))
                self.underline.set(o.get("underline", False))
                self.align.set(o.get("align", "left"))
                self.tbg_on.set(bool(o.get("bg")))
                if o.get("bg"):
                    self.tbg_color = o["bg"]
                self.border.set(o.get("border", False))
            if o["type"] in ("marker", "stamp"):
                self.fsize.set(int(round(o["size"])))
            if o["type"] == "stamp":
                self.stamp.set(o["sym"])
        finally:
            self._loading = False

    # ===================================================================== annotation model
    def _new_obj(self, t, **kw):
        o = {"id": uuid.uuid4().hex[:8], "type": t, "color": self.color, "width": self._w()}
        if t in ("rect", "ellipse"):
            o.update(fill=self.fill_color if self.fill_on.get() else None, fill_alpha=self.fill_alpha.get())
        if t == "area":
            o["fill_alpha"] = 25
        if t == "mosaic":
            o["block"] = max(4, self._w() * 3)
        if t in ("dist", "calib", "perim", "area", "angle"):
            o["fs"] = max(8, round(self._fs() * 0.7))
        if t == "text":
            o.update(text="", family=self.family.get(), size=self._fs(), bold=self.bold.get(),
                     italic=self.italic.get(), underline=self.underline.get(), align=self.align.get(),
                     bg=self.tbg_color if self.tbg_on.get() else None, border=self.border.get(), leader=None)
        if t in ("marker", "stamp"):
            o["size"] = self._fs()
        o.update(kw)
        return o

    def _push_undo_snapshot(self, snap):
        it = self.sel
        it["undo"].append(snap)
        if len(it["undo"]) > 150:
            it["undo"].pop(0)
        it["redo"].clear()

    def push_undo(self):
        if self.sel:
            self._push_undo_snapshot(json.dumps(self.sel["objs"]))

    def pop_undo(self):
        if self.sel and self.sel["undo"]:
            self.sel["undo"].pop()

    def undo(self):
        it = self.sel
        if not it or not it["undo"]:
            return
        self.commit_edit()
        it["redo"].append(json.dumps(it["objs"]))
        it["objs"] = json.loads(it["undo"].pop())
        self.sel_obj = None
        self.changed()
        self.set_status(tr("Undo"))

    def redo(self):
        it = self.sel
        if not it or not it["redo"]:
            return
        self.commit_edit()
        it["undo"].append(json.dumps(it["objs"]))
        it["objs"] = json.loads(it["redo"].pop())
        self.sel_obj = None
        self.changed()
        self.set_status(tr("Redo"))

    def changed(self):
        it = self.sel
        if not it:
            return
        it["dirty"] = True
        it["_final"] = None
        it["_gkey"] = None
        self.request_render()
        self._update_panel()
        self.later("thumb_" + it["id"], 350, lambda: self._refresh_thumb(it))
        self.later("meta_" + it["id"], 800, lambda: self._save_meta(it))
        if self.autosave.get():
            self.later("exp_" + it["id"], 1500, lambda: self._export_auto(it))
        self._schedule_copy()

    def select_obj(self, o):
        self.sel_obj = o
        if o:
            self._load_props(o)
        self._update_panel()

    def hit(self, x, y, types=None):
        tol = 6 / self.s
        for o in reversed(self.sel["objs"]):
            if types and o["type"] not in types:
                continue
            if hit_obj(o, x, y, tol):
                return o
        return None

    def delete_obj(self):
        o = self.sel_obj
        if not o or not self.sel or o not in self.sel["objs"]:
            return
        self.push_undo()
        self.sel["objs"].remove(o)
        self.sel_obj = None
        self.changed()

    def toggle_solid(self):
        """Rectangle / ellipse / polygon <-> pseudo-3D box / cylinder / prism."""
        o = self.sel_obj
        if not o or not self.sel or o not in self.sel["objs"] or o["type"] not in solid3d.SOLID_TYPES:
            return
        if o["type"] == "area" and len(o.get("pts", [])) < 3:
            return
        self.push_undo()
        if o.get("solid"):
            o.pop("solid")
        else:
            solid3d.make_solid(o)
            self._load_props(o)
        self._update_panel()
        self.changed()

    def toggle_cut(self):
        o = self.sel_obj
        if not o or not o.get("solid") or not self.sel or o not in self.sel["objs"]:
            return
        self.push_undo()
        o["solid"]["cut"] = bool(self.solid_cut.get())
        self.changed()
        self._refocus()

    def dup_obj(self):
        o = self.sel_obj
        if not o or not self.sel or o not in self.sel["objs"]:
            return
        self.push_undo()
        n = copy.deepcopy(o)
        n["id"] = uuid.uuid4().hex[:8]
        move_obj(n, 14 / self.s, 14 / self.s)
        if n["type"] == "marker":
            n["n"] = self._next_marker()
        self.sel["objs"].append(n)
        self.select_obj(n)
        self.changed()

    def obj_front(self):
        o = self.sel_obj
        if o and self.sel and o in self.sel["objs"]:
            self.push_undo()
            self.sel["objs"].remove(o)
            self.sel["objs"].append(o)
            self.changed()

    def obj_back(self):
        o = self.sel_obj
        if o and self.sel and o in self.sel["objs"]:
            self.push_undo()
            self.sel["objs"].remove(o)
            self.sel["objs"].insert(0, o)
            self.changed()

    def clear_marks(self):
        if self.sel and self.sel["objs"] and messagebox.askyesno(tr("Clear"), tr("Remove all annotations from this screenshot?"),
                                                                 parent=self.root):
            self.push_undo()
            self.sel["objs"] = []
            self.sel_obj = None
            self.changed()

    def _next_marker(self):
        ns = [o["n"] for o in self.sel["objs"] if o["type"] == "marker"]
        return (max(ns) + 1) if ns else 1

    # ===================================================================== text editing
    def start_edit(self, o, new=False):
        self.commit_edit()
        if not new:
            self.push_undo()
        self.editing = o
        self.edit_new = new
        self._edit_moved = False
        self.sel_obj = o
        self._load_props(o)
        self._update_panel()
        t = tk.Text(self.canvas, wrap="none", undo=True, relief="flat", bd=0, padx=3, pady=2,
                    highlightthickness=2, highlightcolor=ACCENT, highlightbackground=ACCENT)
        t.insert("1.0", o["text"])
        self.edit_widget = t
        self.edit_win = self.canvas.create_window(0, 0, window=t, anchor="nw", tags="editor")
        self._style_editor()
        t.bind("<KeyRelease>", lambda e: self._size_editor())
        t.bind("<Escape>", lambda e: (self.commit_edit(), "break")[1])
        t.bind("<Control-Return>", lambda e: (self.commit_edit(), "break")[1])
        t.focus_set()
        t.mark_set("insert", "end-1c")
        self.render()

    def _style_editor(self):
        o, t = self.editing, self.edit_widget
        if not o or not t:
            return
        px = max(6, int(round(o["size"] * self.s)))
        self._edit_font = tkfont.Font(family=o.get("family", "Segoe UI"), size=-px,
                                      weight="bold" if o.get("bold") else "normal",
                                      slant="italic" if o.get("italic") else "roman",
                                      underline=1 if o.get("underline") else 0)
        bg = o.get("bg") or ("#FFFFFF" if contrast(o["color"]) == "#FFFFFF" else "#333333")
        t.configure(font=self._edit_font, fg=o["color"], bg=bg, insertbackground=o["color"])
        t.tag_configure("al", justify={"left": "left", "center": "center", "right": "right"}[o.get("align", "left")])
        t.tag_add("al", "1.0", "end")
        self._size_editor()

    def _size_editor(self):
        t = self.edit_widget
        if not t:
            return
        lines = t.get("1.0", "end-1c").split("\n")
        f = self._edit_font
        wpx = max(f.measure(l) for l in lines + ["  "]) + f.measure("  ") + 12
        cw = max(f.measure("0"), 1)
        t.configure(width=max(4, int(wpx / cw) + 1), height=max(1, len(lines)))
        t.tag_add("al", "1.0", "end")

    def _place_editor(self):
        o = self.editing
        if not o or not self.edit_win:
            return
        x, y = self.to_canvas(o["x"], o["y"])
        self.canvas.coords(self.edit_win, x - 2, y - 2)
        px = max(6, int(round(o["size"] * self.s)))
        if self._edit_font.cget("size") != -px:
            self._style_editor()

    def commit_edit(self):
        o, t = self.editing, self.edit_widget
        if not o:
            return
        txt = t.get("1.0", "end-1c") if t else o["text"]
        try:
            self.canvas.delete("editor")
            t.destroy()
        except Exception:
            pass
        self.editing, self.edit_widget, self.edit_win = None, None, None
        it = self.sel
        if it is None:
            return
        if not txt.strip():
            if o in it["objs"]:
                it["objs"].remove(o)
            if self.edit_new:
                self.pop_undo()
            self.sel_obj = None
        else:
            if not self.edit_new and txt == o["text"] and not self._edit_moved:
                self.pop_undo()
                o["text"] = txt
                self.request_render()
                self.canvas.focus_set()
                return
            o["text"] = txt
        self.canvas.focus_set()
        self.changed()

    # ===================================================================== measurement building
    def cancel_building(self):
        if self.building:
            self.building = None
            self.request_render()

    def finish_building(self):
        o = self.building
        if not o:
            return
        pts = o["pts"][:-1]  # drop rubber point
        clean = []
        for p in pts:
            if not clean or math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-6:
                clean.append(p)
        need = {"perim": 2, "area": 3, "angle": 3}[o["type"]]
        self.building = None
        if len(clean) < need:
            self.set_status(tr("Need at least {n} points", n=need))
            self.request_render()
            return
        o["pts"] = clean[:3] if o["type"] == "angle" else clean
        self.coord_lbl.configure(text="")
        self.push_undo()
        self.sel["objs"].append(o)
        self.changed()
        self.set_status(tr("{name} measurement added", name=tr(TOOL_NAMES[o["type"]])))

    def _building_click(self, x, y):
        o = self.building
        o["pts"][-1] = [x, y]
        if o["type"] == "area" and len(o["pts"]) > 3:
            fx, fy = o["pts"][0]
            if math.hypot(x - fx, y - fy) * self.s < 9:   # clicked on first point -> close polygon
                self.finish_building()                      # (last point = this click, dropped)
                return
        o["pts"].append([x, y])
        if o["type"] == "angle" and len(o["pts"]) > 3:
            self.finish_building()
            return
        self.request_render()

    # ===================================================================== mouse
    def on_motion(self, e):
        if self.view_n() != 1 or not self.sel:
            self.coord_lbl.configure(text="")
            return
        x, y = self.to_img(e.x, e.y)
        k, u = self.scale_of(self.sel)
        txt = f"X {x:.0f}  Y {y:.0f} px"
        if u != "px":
            txt += f"   ({x * k:.{_DEC[0]}f}, {y * k:.{_DEC[0]}f} {u})"
        if self.building:
            o = self.building
            o["pts"][-1] = [x, y]
            if o["type"] == "perim":
                txt += f"   ·   L = {fmt_len(poly_len(o['pts']), (k, u))}"
            elif o["type"] == "area" and len(o["pts"]) >= 3:
                txt += f"   ·   A = {fmt_area(poly_area(o['pts']), (k, u))}"
            self.request_render()
        self.coord_lbl.configure(text=txt)
        # cursor feedback: ✥ handle or (Select tool) any annotation under the mouse -> move cursor
        want = {"select": "arrow", "text": "xterm"}.get(self.tool.get(), "crosshair")
        if self._on_grip(e) or (self.tool.get() == "select" and not self.building and self.hit(x, y)):
            want = "fleur"
        if str(self.canvas.cget("cursor")) != want:
            self.canvas.configure(cursor=want)

    def on_right(self, e):
        if self.building:
            self.finish_building()
            return
        if self.view_n() != 1 or not self.sel:
            return
        x, y = self.to_img(e.x, e.y)
        o = self.hit(x, y)
        m = tk.Menu(self.root, tearoff=0, font=UI)
        if o:
            self.select_obj(o)
            self.render()
            if o["type"] == "text":
                m.add_command(label=tr("Edit text"), command=lambda: self.start_edit(o))
            if o["type"] in solid3d.SOLID_TYPES:
                m.add_command(label=tr("Make flat") if o.get("solid") else tr("Make 3D"), command=self.toggle_solid)
            m.add_command(label=tr("Duplicate"), command=self.dup_obj, accelerator="Ctrl+D")
            m.add_command(label=tr("Bring to front"), command=self.obj_front)
            m.add_command(label=tr("Send to back"), command=self.obj_back)
            m.add_separator()
            m.add_command(label=tr("Delete"), command=self.delete_obj, accelerator="Del")
        else:
            m.add_command(label=tr("Copy current view"), command=self.copy_view, accelerator="Ctrl+C")
            m.add_command(label=tr("Undo"), command=self.undo, accelerator="Ctrl+Z")
            m.add_command(label=tr("Redo"), command=self.redo, accelerator="Ctrl+Y")
            m.add_separator()
            m.add_command(label=tr("Remove all annotations"), command=self.clear_marks)
        m.tk_popup(e.x_root, e.y_root)

    def on_press(self, e):
        self.canvas.focus_set()
        if self.view_n() != 1:
            self._board_press(e)
            return
        if not self.sel:
            return
        if self._on_grip(e) and (self.editing or self.sel_obj):
            o = self.editing or self.sel_obj
            if not self.editing:
                self.push_undo()
            self.drag = {"mode": "grip", "obj": o, "last": self.to_img(e.x, e.y), "moved": False}
            self.canvas.configure(cursor="fleur")
            return
        if self.editing:
            self.commit_edit()
            return
        x, y = self.to_img(e.x, e.y)
        t = self.tool.get()
        it = self.sel
        if self.building:
            self._building_click(x, y)
            return
        if t == "select":
            if self.sel_obj and self.sel_obj in it["objs"]:
                for i, (hx, hy) in enumerate(handles(self.sel_obj)):
                    cx, cy = self.to_canvas(hx, hy)
                    if abs(cx - e.x) <= 7 and abs(cy - e.y) <= 7:
                        self.push_undo()
                        self.drag = {"mode": "handle", "i": i, "moved": False}
                        return
            o = self.hit(x, y)
            if o:
                self.select_obj(o)
                self.push_undo()
                self.drag = {"mode": "move", "last": (x, y), "moved": False}
                self.canvas.configure(cursor="fleur")
            else:
                self.select_obj(None)
                self.drag = {"mode": "pan", "last": (e.x, e.y)}
            self.render()
            return
        if t in ("pen", "highlight"):
            o = self._new_obj(t, pts=[[x, y]])
        elif t in ("line", "arrow", "dist", "calib"):
            o = self._new_obj(t, p=[[x, y], [x, y]])
        elif t in ("rect", "ellipse", "mosaic"):
            o = self._new_obj(t, box=[x, y, x, y])
        elif t == "text":
            ex = self.hit(x, y, types=("text",))
            if ex:
                self.start_edit(ex)
                return
            o = self._new_obj("text", x=x, y=y - self._fs() * 0.6)
            self.push_undo()
            it["objs"].append(o)
            self.start_edit(o, new=True)
            return
        elif t == "callout":
            o = self._new_obj("text", x=x, y=y, leader=[x, y])
            if not o.get("bg"):
                o["bg"] = "#FFFFFF"
            o["border"] = True
            self.push_undo()
            it["objs"].append(o)
            self.drag = {"mode": "callout", "obj": o, "start": (e.x, e.y)}
            return
        elif t in ("marker", "stamp"):
            o = self._new_obj(t, x=x, y=y, **({"n": self._next_marker()} if t == "marker" else {"sym": self.stamp.get()}))
            self.push_undo()
            it["objs"].append(o)
            self.changed()
            return
        elif t in ("perim", "area", "angle"):
            self.building = self._new_obj(t, pts=[[x, y], [x, y]])
            self.request_render()
            return
        else:
            return
        self.push_undo()
        it["objs"].append(o)
        self.drag = {"mode": "create", "obj": o, "start": (e.x, e.y)}
        self.request_render()

    def on_drag(self, e):
        if self.view_n() != 1:
            self._board_motion(e)
            return
        d = self.drag
        if not d:
            return
        x, y = self.to_img(e.x, e.y)
        m = d["mode"]
        if m == "pan":
            lx, ly = d["last"]
            if not self.fit or abs(e.x - lx) + abs(e.y - ly) > 0:
                self.vx -= (e.x - lx) / self.s
                self.vy -= (e.y - ly) / self.s
                d["last"] = (e.x, e.y)
                self.fit = False
                self.canvas.configure(cursor="fleur")
        elif m == "move":
            lx, ly = d["last"]
            move_obj(self.sel_obj, x - lx, y - ly)
            d["last"] = (x, y)
            d["moved"] = True
        elif m == "grip":
            lx, ly = d["last"]
            move_obj(d["obj"], x - lx, y - ly)
            d["last"] = (x, y)
            d["moved"] = True
            if self.editing is d["obj"]:
                self._place_editor()
        elif m == "handle":
            set_handle(self.sel_obj, d["i"], x, y)
            d["moved"] = True
        elif m == "create":
            o = d["obj"]
            shift = e.state & 0x1
            if o["type"] in ("pen", "highlight"):
                lx, ly = o["pts"][-1]
                if math.hypot(x - lx, y - ly) * self.s >= 1.5:
                    o["pts"].append([x, y])
            elif "p" in o:
                x0, y0 = o["p"][0]
                if shift:
                    ang = round(math.atan2(y - y0, x - x0) / (math.pi / 4)) * (math.pi / 4)
                    L = math.hypot(x - x0, y - y0)
                    x, y = x0 + L * math.cos(ang), y0 + L * math.sin(ang)
                o["p"][1] = [x, y]
            else:
                x0, y0 = o["box"][:2]
                if shift:
                    sd = max(abs(x - x0), abs(y - y0))
                    x, y = x0 + math.copysign(sd, x - x0), y0 + math.copysign(sd, y - y0)
                o["box"][2:] = [x, y]
        elif m == "callout":
            o = d["obj"]
            o["x"], o["y"] = x, y
        self.request_render()

    def on_release(self, e):
        if self.view_n() != 1:
            self._board_release(e)
            return
        d, self.drag = self.drag, None
        cur = {"select": "arrow", "text": "xterm"}.get(self.tool.get(), "crosshair")
        self.canvas.configure(cursor=cur)
        if not d:
            return
        m = d["mode"]
        if m == "grip":
            if self.editing is d["obj"]:
                self._edit_moved = self._edit_moved or d["moved"]
                self.request_render()
                if self.edit_widget:
                    self.edit_widget.focus_set()
            elif d["moved"]:
                self.changed()
            else:
                self.pop_undo()
            return
        if m in ("move", "handle"):
            if not d["moved"]:
                self.pop_undo()
            else:
                if self.sel_obj and "box" in self.sel_obj:
                    self.sel_obj["box"] = norm_box(self.sel_obj["box"])
                self.changed()
            self.render()
        elif m == "pan":
            self.render()
        elif m == "create":
            o = d["obj"]
            sx, sy = d["start"]
            tiny = abs(e.x - sx) + abs(e.y - sy) < 4
            if tiny and o["type"] not in ("pen", "highlight"):
                self.sel["objs"].remove(o)
                self.pop_undo()
                self.render()
                return
            if "box" in o:
                o["box"] = norm_box(o["box"])
            if o["type"] == "calib":
                k, u = self.scale_of(self.sel)
                px = math.hypot(o["p"][1][0] - o["p"][0][0], o["p"][1][1] - o["p"][0][1])
                dlg = ScaleDialog(self.root, tr("Set scale"), tr("This line is {px} px long.\nWhat is its real length?", px=f"{px:.1f}"),
                                  value=f"{px * k:.2f}" if u != "px" else "100", unit=u if u != "px" else "mm")
                if not dlg.result:
                    self.sel["objs"].remove(o)
                    self.pop_undo()
                    self.render()
                    return
                v, unit, all_ = dlg.result
                o["real"], o["unit"] = v, unit
                for other in [x for x in self.sel["objs"] if x["type"] == "calib" and x is not o]:
                    self.sel["objs"].remove(other)
                if all_:
                    self.st["default_scale"] = [v / px, unit]
                    self._invalidate_all()
                self.set_status(tr("Scale set: {px} px = {v} {u}  →  1 px = {k} {u}", px=f"{px:.1f}", v=f"{v:g}",
                                   u=unit, k=f"{v / px:.5g}"))
            self.changed()
        elif m == "callout":
            o = d["obj"]
            sx, sy = d["start"]
            if abs(e.x - sx) + abs(e.y - sy) < 6:
                o["x"] += 40 / self.s
                o["y"] -= 50 / self.s
            self.start_edit(o, new=True)

    def on_double(self, e):
        if self.view_n() != 1:
            it = self._cell_at(e.x, e.y)
            if it:
                self.set_view("Single")
                self.select_item(it)
            return
        if not self.sel:
            return
        if self.building:
            self.finish_building()
            return
        x, y = self.to_img(e.x, e.y)
        if self.tool.get() == "select":
            o = self.hit(x, y, types=("text",))
            if o:
                self.drag = None
                self.start_edit(o)
                return
        self.on_press(e)

    # ---------------------------------------------------------------- board mouse
    def _board_press(self, e):
        it = self._cell_at(e.x, e.y)
        if it:
            self.sel = it
            self._load_notes()
            self._update_cards()
            self._gdrag = {"src": it, "moved": False}
            self.render()

    def _board_motion(self, e):
        if not self._gdrag:
            return
        self._gdrag["moved"] = True
        self.canvas.configure(cursor="fleur")
        c = self.canvas
        self._draw_board(c.winfo_width(), c.winfo_height(), hover=self._cell_at(e.x, e.y))

    def _board_release(self, e):
        g, self._gdrag = self._gdrag, None
        self.canvas.configure(cursor="arrow")
        if not g:
            return
        tgt = self._cell_at(e.x, e.y)
        if g["moved"] and tgt and tgt is not g["src"]:
            i, j = self.board.index(g["src"]), self.board.index(tgt)
            self.board[i], self.board[j] = self.board[j], self.board[i]
            self._save_board()
            self.set_status(tr("Board positions swapped"))
            self._schedule_copy()
        self.render()

    # ===================================================================== keyboard
    def on_key(self, e):
        ctrl = bool(e.state & 0x4)
        shift = bool(e.state & 0x1)
        ks = e.keysym.lower()
        typing = self._typing()
        if ks == "f1":
            self.show_guide()
            return "break"
        if ctrl and ks == "n":
            self.new_capture()
            return "break"
        if ctrl and ks == "s":
            (self.save_all_png if shift else self.save_view)()
            return "break"
        if typing:
            return
        if ctrl:
            if ks == "delete" and shift:
                self.delete_many(list(self.items))
            elif ks == "c":
                self.copy_view()
            elif ks == "z":
                self.undo()
            elif ks == "y":
                self.redo()
            elif ks == "d":
                self.dup_obj()
            elif ks == "p" and self.feat["feat_pin"].get():
                self.pin_current()
            elif ks == "t" and self.feat["feat_ocr"].get():
                self.ocr_current()
            elif ks == "r" and self.feat["feat_record"].get():
                self.start_record()
            elif ks in ("0", "kp_0"):
                self.zoom_fit()
            elif ks in ("1", "kp_1"):
                self.zoom_100()
            elif ks in ("plus", "equal", "kp_add"):
                self.zoom_at(1.25)
            elif ks in ("minus", "kp_subtract"):
                self.zoom_at(1 / 1.25)
            return "break"
        if ks == "escape":
            if self.building:
                self.cancel_building()
            elif self.sel_obj:
                self.select_obj(None)
                self.render()
            elif self.tool.get() != "select":
                self.set_tool("select")
            return "break"
        if ks in ("return", "kp_enter") and self.building:
            self.finish_building()
            return "break"
        if ks == "delete":
            if self.sel_obj and self.view_n() == 1:
                self.delete_obj()
            else:
                self.delete_item()
            return "break"
        if ks in ("left", "right", "up", "down"):
            if self.sel_obj and self.view_n() == 1:
                step = (10 if shift else 1) / self.s
                dx = {"left": -step, "right": step}.get(ks, 0)
                dy = {"up": -step, "down": step}.get(ks, 0)
                lid, lkey, lt = self._last_prop
                if not (lid == self.sel_obj["id"] and lkey == "nudge" and time.time() - lt < 1.5):
                    self.push_undo()
                self._last_prop = (self.sel_obj["id"], "nudge", time.time())
                move_obj(self.sel_obj, dx, dy)
                self.changed()
            elif ks in ("up", "down") and self.sel in self.items:
                i = self.items.index(self.sel) + (-1 if ks == "up" else 1)
                if 0 <= i < len(self.items):
                    self.select_item(self.items[i])
            return "break"
        if ks in "12345" and len(ks) == 1:
            self.set_view(VIEW_MODES[int(ks) - 1][0])
            return "break"
        for t in TOOLS:
            if t and t[2] == ks:
                self.set_tool(t[0])
                return "break"

    # ===================================================================== copy / save
    def _schedule_copy(self, ms=600):
        if self.autocopy.get() and self.items:
            self.later("autocopy", ms, lambda: self.copy_view(auto=True))

    def copy_view(self, auto=False):
        if self.editing:
            return
        img = self.view_image()
        if img is None:
            return
        n = self.view_n()
        label = tr("screenshot") if n == 1 else tr("board ({n} screenshots)", n=len(self.board_items()))
        self._copy_img(img, label, auto)

    def _copy_img(self, img, label, auto=False):
        self.copy_gen += 1
        gen = self.copy_gen

        def work():
            if gen != self.copy_gen:
                return
            ok = set_clipboard_image(img)
            self.q.put(("copied", ok, label, auto, img.size))
        threading.Thread(target=work, daemon=True).start()

    def _mark_saved(self, items):
        for it in items:
            if it.get("dirty"):
                it["dirty"] = False
                self._save_meta(it)

    def _save_img(self, img, base, items=()):
        last = self.st.get("last_dir") or DEFAULT_SAVE_DIR
        p = filedialog.asksaveasfilename(
            parent=self.root, defaultextension=".png", initialdir=last if os.path.isdir(last) else None,
            initialfile=f"{base}_{datetime.now():%Y%m%d_%H%M%S}.png", filetypes=SAVE_FILETYPES)
        if not p:
            return
        try:
            save_image(img, p)
            self.st["last_dir"] = os.path.dirname(p)
            self._mark_saved(items)
            self.set_status(tr("Saved: {p}", p=p))
            self.flash_msg(tr("✓ Saved"))
        except Exception as ex:
            messagebox.showerror(tr("Save failed"), str(ex), parent=self.root)

    def save_view(self):
        self.commit_edit()
        img = self.view_image()
        if img is not None:
            self._save_img(img, "Capture" if self.view_n() == 1 else "Board", self.board_items())

    def save_selected(self):
        if self.sel:
            self._save_img(self.out_image(self.sel), f"Capture_{self.sel['num']}", [self.sel])

    def save_all_png(self):
        if not self.items:
            return
        d = filedialog.askdirectory(parent=self.root, title=tr("Folder for all screenshots"),
                                    initialdir=self.st.get("last_dir") or DEFAULT_SAVE_DIR)
        if not d:
            return
        done = []
        try:
            for it in reversed(self.items):
                save_image(self.out_image(it), os.path.join(d, f"Capture_{it['num']:03d}_{it['time']:%Y%m%d_%H%M%S}.png"))
                done.append(it)
        except Exception as ex:
            self._mark_saved(done)
            messagebox.showerror(tr("Save failed"), str(ex), parent=self.root)
            return
        self.st["last_dir"] = d
        self._mark_saved(self.items)
        self.set_status(tr("{n} screenshots saved to {d}", n=len(self.items), d=d))
        self.flash_msg(tr("✓ Saved"))

    def export_batch(self, what, fmt, folder, prefix):
        """Used by the close dialog. Returns the list of written files."""
        ext = SAVE_FORMATS[fmt]
        os.makedirs(folder, exist_ok=True)
        out = []
        if what == "view":
            img = self.view_image()
            items = self.board_items()
            if img is not None:
                p = unique_path(folder, prefix, ext)
                save_image(img, p)
                out.append(p)
        elif what == "pdf":
            items = list(reversed(self.items))
            pages = [self.out_image(it, title=True).convert("RGB") for it in items]
            if pages:
                p = unique_path(folder, prefix, ".pdf")
                pages[0].save(p, "PDF", resolution=96, save_all=True, append_images=pages[1:])
                out.append(p)
        else:
            items = [it for it in reversed(self.items) if what == "each" or it.get("dirty")]
            for it in items:
                p = unique_path(folder, f"{prefix}_{it['num']:03d}", ext)
                save_image(self.out_image(it), p)
                out.append(p)
        self._mark_saved(items)
        return out

    def save_all_pdf(self, board_only=False):
        items = self.board_items() if board_only else list(reversed(self.items))
        if not items:
            return
        p = filedialog.asksaveasfilename(parent=self.root, defaultextension=".pdf",
                                         initialfile=f"Captures_{datetime.now():%Y%m%d_%H%M}.pdf",
                                         filetypes=[("PDF document", "*.pdf")])
        if not p:
            return
        try:
            pages = [self.out_image(it, title=True).convert("RGB") for it in items]
            pages[0].save(p, "PDF", resolution=96, save_all=True, append_images=pages[1:])
        except Exception as ex:
            messagebox.showerror(tr("Save failed"), str(ex), parent=self.root)
            return
        self.st["last_dir"] = os.path.dirname(p)
        self._mark_saved(items)
        self.set_status(tr("PDF with {n} page(s) saved: {p}", n=len(pages), p=p))
        self.flash_msg(tr("✓ PDF saved"))

    def _save_menu(self):
        m = tk.Menu(self.root, tearoff=0, font=UI)
        m.add_command(label=tr("Save current view as…"), command=self.save_view, accelerator="Ctrl+S")
        m.add_command(label=tr("Save selected screenshot as…"), command=self.save_selected)
        m.add_separator()
        m.add_command(label=tr("Save all screenshots as PNG files…"), command=self.save_all_png, accelerator="Ctrl+Shift+S")
        m.add_command(label=tr("Export all screenshots to one PDF…"), command=self.save_all_pdf)
        m.add_command(label=tr("Export board screenshots to PDF…"), command=lambda: self.save_all_pdf(True))
        b = self.save_btn
        m.tk_popup(b.winfo_rootx(), b.winfo_rooty() + b.winfo_height())

    def _options_menu(self):
        m = tk.Menu(self.root, tearoff=0, font=UI)
        m.add_checkbutton(label=tr("Auto-copy current view to clipboard"), variable=self.autocopy, command=self._opts_changed)
        m.add_checkbutton(label=tr("Include notes when copying / exporting"), variable=self.include_notes, command=self._opts_changed)
        m.add_separator()
        m.add_checkbutton(label=tr("Ask to save when closing"), variable=self.ask_close, command=self._opts_changed)
        m.add_checkbutton(label=tr("Auto-save PNG files to folder"), variable=self.autosave, command=self._opts_changed)
        m.add_command(label=tr("Choose auto-save folder…"), command=self._choose_dir)
        m.add_command(label=tr("Open auto-save folder"), command=self._open_dir)
        m.add_separator()
        m.add_checkbutton(label=tr("Keep history between launches"), variable=self.keep_history, command=self._opts_changed)
        m.add_command(label=tr("Clear history…"), command=self.clear_history)
        m.add_separator()
        m.add_command(label=tr("Remove all annotations on this screenshot"), command=self.clear_marks)
        m.add_command(label=tr("Reset default scale"), command=self._reset_default_scale)
        m.add_separator()
        tm = tk.Menu(m, tearoff=0, font=UI)
        self._theme_var = tk.StringVar(value=self.st.get("theme") if self.st.get("theme") in self.themes else themes.DEFAULT_ID)
        for th in self.sorted_themes():
            tm.add_radiobutton(label=th.name(LANG[0]), value=th.id, variable=self._theme_var,
                               command=lambda t=th.id: self.set_theme(t))
        tm.add_separator()
        tm.add_command(label=tr("Theme manager…"), command=self.show_themes)
        m.add_cascade(label=tr("Theme"), menu=tm)
        m.add_checkbutton(label=tr("Add the theme frame to copies and exports"), variable=self.theme_frame,
                          command=self._opts_changed, state="normal" if self.theme.frame else "disabled")
        fm = tk.Menu(m, tearoff=0, font=UI)
        for k, label in FEATURES:
            fm.add_checkbutton(label=tr(label), variable=self.feat[k], command=self._features_changed)
        if self.feat["feat_record"].get():
            fm.add_separator()
            rm = tk.Menu(fm, tearoff=0, font=UI)
            self._fps_var = tk.IntVar(value=int(self.st.get("rec_fps", 10)))
            for f in REC_FPS:
                rm.add_radiobutton(label=tr("{n} frames / s", n=f), value=f, variable=self._fps_var,
                                   command=lambda: (self.st.update(rec_fps=self._fps_var.get()), save_settings(self.st)))
            fm.add_cascade(label=tr("Recording frame rate"), menu=rm)
            has_mp4, has_audio = extras.find_ffmpeg() is not None, extras.audio_available()
            fmm = tk.Menu(fm, tearoff=0, font=UI)
            self._recfmt_var = tk.StringVar(value=self.st.get("rec_format", "mp4") if has_mp4 else "gif")
            save_fmt = lambda: (self.st.update(rec_format=self._recfmt_var.get()), save_settings(self.st))
            fmm.add_radiobutton(label=tr("MP4 video (no length limit, sound)") if has_mp4 else tr("MP4 video (needs ffmpeg)"),
                                value="mp4", variable=self._recfmt_var, command=save_fmt,
                                state="normal" if has_mp4 else "disabled")
            fmm.add_radiobutton(label=tr("GIF animation (up to 60 s)"), value="gif", variable=self._recfmt_var, command=save_fmt)
            fm.add_cascade(label=tr("Recording format"), menu=fmm)
            snd = "normal" if has_mp4 and has_audio and self._recfmt_var.get() == "mp4" else "disabled"
            for key, label in (("rec_mic", "Record microphone"), ("rec_system", "Record system sound")):
                var = tk.BooleanVar(value=bool(self.st.get(key, False)))
                setattr(self, "_" + key + "_var", var)
                fm.add_checkbutton(label=tr(label) + ("" if has_audio else "  " + tr("(needs PyAudioWPatch)")),
                                   variable=var, state=snd,
                                   command=lambda k=key, v=var: (self.st.update({k: v.get()}), save_settings(self.st)))
        m.add_cascade(label=tr("Extra features"), menu=fm)
        m.add_separator()
        lm = tk.Menu(m, tearoff=0, font=UI)
        self._lang_var = tk.StringVar(value=LANG[0])
        for code, name in LANGS:
            lm.add_radiobutton(label=name, value=code, variable=self._lang_var, command=lambda c=code: self.set_lang(c))
        m.add_cascade(label=tr("Language"), menu=lm)
        m.add_separator()
        m.add_command(label=tr("User guide"), command=self.show_guide, accelerator="F1")
        m.add_command(label=tr("Keyboard shortcuts"), command=self.show_shortcuts)
        m.add_command(label=tr("About {app}", app=APP_NAME), command=lambda: messagebox.showinfo(
            tr("About"), f"{APP_NAME}  v{VERSION}\n\n" + tr(
                "Multi-screenshot board with annotation, measurement and notes.\nHistory folder: {p}", p=SESSION_DIR),
            parent=self.root))
        b = self.more_btn
        m.tk_popup(b.winfo_rootx(), b.winfo_rooty() + b.winfo_height())

    def _key(self, var, keys):
        disp = var.get()
        for k in keys:
            if tr(k) == disp or k == disp:
                return k
        return keys[0]

    def set_lang(self, code):
        if code == LANG[0]:
            return
        self.st["lang"] = code
        save_settings(self.st)
        prev = LANG[0]
        LANG[0] = code  # ask in the newly chosen language
        ok = messagebox.askyesno("Language", tr("The new language is applied after a restart.\nRestart now?"),
                                 parent=self.root)
        LANG[0] = prev
        if ok:
            self.restart = True
            self.on_close()
            try:
                if self.root.winfo_exists():   # close was cancelled in the save dialog
                    self.restart = False
            except tk.TclError:
                pass

    # ---------------------------------------------------------------- themes
    def sorted_themes(self):
        order = {"default": 0, "builtin": 1, "user": 2}
        return sorted(self.themes.values(), key=lambda t: (order.get(t.source, 3), t.name(LANG[0]).lower()))

    def set_theme(self, tid):
        """Remembers the theme; colours and icons are applied after a restart."""
        if tid not in self.themes:
            return
        if tid == self.st.get("theme", themes.DEFAULT_ID) and tid == self.theme.id:
            return
        self.st["theme"] = tid
        self.st["theme_frame"] = bool(self.themes[tid].frame) or self.theme_frame.get()
        self.theme_frame.set(self.st["theme_frame"])
        save_settings(self.st)
        if tid == self.theme.id:
            return
        self.ask_restart(tr("The theme “{name}” is applied after a restart.\nRestart now?",
                            name=self.themes[tid].name(LANG[0])))

    def ask_restart(self, text, parent=None):
        if not messagebox.askyesno(APP_NAME, text, parent=parent or self.root):
            return False
        self.restart = True
        self.on_close()
        try:
            if self.root.winfo_exists():   # close was cancelled in the save dialog
                self.restart = False
        except tk.TclError:
            pass
        return self.restart

    def show_themes(self):
        if getattr(self, "_theme_dlg", None) and self._theme_dlg.winfo_exists():
            self._theme_dlg.lift()
            return
        self._theme_dlg = ThemeDialog(self)

    def show_guide(self):
        if getattr(self, "_guide", None) and self._guide.winfo_exists():
            self._guide.lift()
            return
        w = tk.Toplevel(self.root)
        self._guide = w
        w.title(tr("User guide") + " – " + APP_NAME)
        w.configure(bg=PANEL)
        w.geometry(f"{int(760 * self.k)}x{int(720 * self.k)}+{self.root.winfo_rootx() + 80}+{self.root.winfo_rooty() + 40}")
        w.transient(self.root)
        top = tk.Frame(w, bg=PANEL)
        top.pack(fill="x", padx=16, pady=(10, 0))
        for code, name in LANGS:
            FlatButton(top, name, lambda c=code: fill(c), padx=10, pady=3, bg=BTN, hover=BTN_H).pack(side="left", padx=(0, 4))
        FlatButton(top, tr("Close"), w.destroy, padx=10, pady=3, bg=ACCENT, fg="white", hover=ACCENT_D).pack(side="right")
        fr = tk.Frame(w, bg=PANEL)
        fr.pack(fill="both", expand=True, padx=16, pady=10)
        sb = ttk.Scrollbar(fr, orient="vertical")
        t = tk.Text(fr, wrap="word", relief="flat", bd=0, bg=PANEL, fg=TEXT, font=("Segoe UI", 10), padx=6, pady=4,
                    spacing1=2, spacing3=2, yscrollcommand=sb.set, cursor="arrow")
        sb.configure(command=t.yview)
        sb.pack(side="right", fill="y")
        t.pack(fill="both", expand=True)
        t.tag_configure("h1", font=("Segoe UI Semibold", 16), foreground=ACCENT, spacing3=6)
        t.tag_configure("h2", font=("Segoe UI Semibold", 12), foreground=TEXT, spacing1=14, spacing3=4)
        t.tag_configure("li", lmargin1=14, lmargin2=30)
        t.tag_configure("tip", background=ACCENT_L, lmargin1=10, lmargin2=10, rmargin=10, spacing1=6, spacing3=6)
        t.tag_configure("p", spacing3=4)

        def fill(code):
            prev = LANG[0]
            LANG[0] = code
            txt = guide_text()
            LANG[0] = prev
            t.configure(state="normal")
            t.delete("1.0", "end")
            first = True
            for line in txt.strip("\n").split("\n"):
                if line.startswith("# "):
                    t.insert("end", line[2:] + "\n", "h1" if first else "h2")
                    first = False
                elif line.startswith("- "):
                    t.insert("end", "•  " + line[2:] + "\n", "li")
                elif line.startswith("> "):
                    t.insert("end", "💡  " + line[2:] + "\n", "tip")
                elif line.strip():
                    t.insert("end", line + "\n", "p")
            t.configure(state="disabled")
        fill(LANG[0])
        w.bind("<Escape>", lambda e: w.destroy())

    def _opts_changed(self):
        self.st.update(autocopy=self.autocopy.get(), include_notes=self.include_notes.get(),
                       autosave=self.autosave.get(), keep_history=self.keep_history.get(),
                       ask_on_close=self.ask_close.get(), theme_frame=self.theme_frame.get(),
                       theme_random=self.theme_random.get())
        for it in self.items:
            it["_gkey"] = None
        self.render()
        save_settings(self.st)
        if self.keep_history.get():
            for it in self.items:
                p = os.path.join(SESSION_DIR, it["id"] + ".png")
                if not os.path.exists(p):
                    self._persist_new(it)

    def _choose_dir(self):
        d = filedialog.askdirectory(parent=self.root, initialdir=self.st.get("save_dir"), title=tr("Auto-save folder"))
        if d:
            self.st["save_dir"] = d
            save_settings(self.st)

    def _open_dir(self):
        d = self.st.get("save_dir") or DEFAULT_SAVE_DIR
        os.makedirs(d, exist_ok=True)
        os.startfile(d)

    def _delete_menu(self):
        m = tk.Menu(self.root, tearoff=0, font=UI)
        has = bool(self.items)
        st = "normal" if has else "disabled"
        m.add_command(label=tr("Delete selected screenshot"), command=self.delete_item, accelerator="Del",
                      state="normal" if self.sel else "disabled")
        if self.view_n() != 1:
            m.add_command(label=tr("Delete the {n} screenshots of this board…", n=len(self.board_items())),
                          command=lambda: self.delete_many(self.board_items()), state=st)
        m.add_separator()
        m.add_command(label=tr("Delete ALL screenshots…"), command=lambda: self.delete_many(list(self.items)),
                      accelerator="Ctrl+Shift+Del", state=st)
        m.add_separator()
        m.add_command(label=tr("Remove all annotations on this screenshot"), command=self.clear_marks,
                      state="normal" if self.sel and self.sel["objs"] else "disabled")
        b = self.del_btn
        m.tk_popup(b.winfo_rootx(), b.winfo_rooty() + b.winfo_height())

    def _forget_jobs(self, it):
        for key in [k for k in self._jobs if k.endswith("_" + it["id"])]:
            self.root.after_cancel(self._jobs.pop(key))

    def delete_many(self, items):
        """Delete several (or all) screenshots after one confirmation."""
        items = [it for it in items if it in self.items]
        if not items:
            return
        self.commit_edit()
        self.cancel_building()
        dirty = sum(1 for it in items if it.get("dirty"))
        msg = tr("Delete {n} screenshot(s) from the history?", n=len(items))
        if dirty:
            msg += "\n\n" + tr("⚠ {n} of them have not been saved to a file and will be lost.", n=dirty)
        msg += "\n" + tr("Files you saved yourself are not affected.")
        if not messagebox.askyesno(tr("Delete screenshots"), msg, icon="warning", parent=self.root):
            return
        for it in items:
            self._forget_jobs(it)
            self._delete_files(it)
            self.items.remove(it)
            if it in self.board:
                self.board.remove(it)
        if self.sel not in self.items:
            self.sel = self.items[0] if self.items else None
            self.sel_obj = None
            self.editing = None
        self._save_board()
        if not self.items:
            try:
                os.remove(os.path.join(SESSION_DIR, "board.json"))
            except OSError:
                pass
        self._rebuild_list()
        if self.sel:
            self.select_item(self.sel)
        else:
            self._load_notes()
            self.render()
        self.set_status(tr("{n} screenshot(s) deleted", n=len(items)))
        self._schedule_copy()

    def clear_history(self):
        self.delete_many(list(self.items))

    def _invalidate_all(self):
        for it in self.items:
            it["_final"] = None
            it["_gkey"] = None
        self._update_panel()
        self.render()

    def set_scale_manual(self):
        if not self.sel:
            return
        k, u = self.scale_of(self.sel)
        dlg = ScaleDialog(self.root, tr("Set scale"), tr("1 pixel equals:"), value=f"{k:.6g}" if u != "px" else "0.2645",
                          unit=u if u != "px" else "mm")
        if dlg.result:
            v, unit, all_ = dlg.result
            self.push_undo()
            self.sel["objs"] = [o for o in self.sel["objs"] if o["type"] != "calib"]
            self.sel["scale"] = [v, unit]
            if all_:
                self.st["default_scale"] = [v, unit]
            self._invalidate_all()
            self.changed()

    def reset_scale(self):
        if not self.sel:
            return
        self.push_undo()
        self.sel["objs"] = [o for o in self.sel["objs"] if o["type"] != "calib"]
        self.sel["scale"] = None
        self.changed()

    def _reset_default_scale(self):
        self.st["default_scale"] = None
        self._invalidate_all()

    def show_shortcuts(self):
        txt = shortcuts_text()
        extra = [line for k, line in (("feat_pin", tr("Ctrl+P         pin screenshot to the screen")),
                                       ("feat_ocr", tr("Ctrl+T         extract text (OCR)")),
                                       ("feat_record", tr("Ctrl+R         record screen (GIF / MP4)  ·  Esc stop")))
                 if self.feat[k].get()]
        if extra:
            txt += "\n\n" + "\n".join(extra)
        messagebox.showinfo(tr("Keyboard shortcuts"), txt, parent=self.root)

    # ===================================================================== optional features
    def _mode_keys(self):
        return ALL_MODES if self.feat["feat_scroll"].get() else MODE_KEYS

    def _build_extras(self):
        for w in self.extra_bar.winfo_children():
            w.destroy()
        btns = []
        if self.feat["feat_pin"].get():
            btns.append(("pin", "📌", tr("Pin"), self.pin_current,
                         tr("Pin the screenshot above all windows  (Ctrl+P)\n"
                            "Drag to move · wheel to zoom · Ctrl+wheel opacity · double-click or Esc to close")))
        if self.feat["feat_ocr"].get():
            btns.append(("ocr", "🔤", tr("Text"), self.ocr_current,
                         tr("Extract the text of the screenshot  (Ctrl+T)\nWindows OCR, works offline")))
        if self.feat["feat_record"].get():
            btns.append(("record", "⏺", tr("Record"), self.start_record,
                         tr("Record part of the screen as a GIF or MP4 video  (Ctrl+R)\nEsc or Stop to finish")))
        if btns:
            tk.Frame(self.extra_bar, bg=BORDER, width=1).pack(side="left", fill="y", padx=(12, 6), pady=10)
            for key, glyph, text, cmd, tip in btns:
                FlatButton(self.extra_bar, command=cmd, tip=tip, **self._hbtn(key, glyph, text)).pack(side="left")

    def _features_changed(self):
        for k, _ in FEATURES:
            self.st[k] = self.feat[k].get()
        save_settings(self.st)
        keys = self._mode_keys()
        self.mode_cb.configure(values=[tr(k) for k in keys])
        if self._key(self.mode_var, ALL_MODES) not in keys:
            self.mode_var.set(tr("Region"))
        self._build_extras()

    def _current_image(self):
        """What Pin / OCR act on: the selected screenshot (single view) or the board."""
        self.commit_edit()
        if self.view_n() == 1:
            return self.final(self.sel) if self.sel else None
        items = self.board_items()
        if not items:
            return None
        return self.final(items[0]) if len(items) == 1 else compose_grid([self.final(i) for i in items])

    # ---- pin to screen
    def pin_current(self):
        img = self._current_image()
        if img is None:
            self.set_status(tr("Take or select a screenshot first"))
            return
        self.pin_image(img)

    def pin_image(self, img):
        def closed(p):
            if p is None:                      # "close all"
                for q in list(self.pins):
                    q.on_close = None
                    q.close()
                self.pins.clear()
            elif p in self.pins:
                self.pins.remove(p)
        p = extras.PinWindow(self.root, img, copy_fn=lambda im: self._copy_img(im, tr("pinned image")),
                             save_fn=lambda im: self._save_img(im, "Pinned"), on_close=closed)
        self.pins.append(p)
        self.set_status(tr("Pinned  ·  drag to move, wheel to zoom, Ctrl+wheel opacity, double-click or Esc to close"))

    # ---- OCR
    def ocr_current(self):
        img = self._current_image()
        if img is None:
            self.set_status(tr("Take or select a screenshot first"))
            return
        self.ocr_image(img)

    def ocr_image(self, img):
        def lang_changed(lang):
            self.st["ocr_lang"] = lang
            save_settings(self.st)
        extras.OcrDialog(self.root, img, self.st.get("ocr_lang", ""), lang_changed, self.k)

    # ---- scrolling capture
    def _scroll_region(self, img, box):
        if img is None:
            self._capture_done(None, None)
            return
        vx, vy, _, _ = virtual_screen()
        absbox = (box[0] + vx, box[1] + vy, box[2] + vx, box[3] + vy)

        def done(result, err):
            if err:
                self.busy = False
                self.root.deiconify()
                messagebox.showerror(tr("Capture failed"), err, parent=self.root)
                return
            self._capture_done(result, None)
        extras.ScrollCapture(self.root, absbox, done)

    # ---- screen recording
    def start_record(self):
        if self.busy:
            return
        self.commit_edit()
        self.cancel_building()
        self.busy = True
        self.root.withdraw()
        self.root.after(280, self._record_grab)

    def _record_grab(self):
        try:
            shot = ImageGrab.grab(all_screens=True)
        except Exception as ex:
            self.busy = False
            self.root.deiconify()
            messagebox.showerror(tr("Capture failed"), str(ex))
            return
        vx, vy, vw, vh = virtual_screen()
        if self._key(self.mode_var, self._mode_keys()) == "Full screen":
            self._record_region(shot, (0, 0, vw, vh))
        else:
            RegionSelector(self.root, shot, (vx, vy, vw, vh), self._record_region)

    def _record_region(self, img, box):
        if img is None:
            self.busy = False
            self.root.deiconify()
            self.set_status(tr("Recording cancelled"))
            return
        vx, vy, _, _ = virtual_screen()
        absbox = (box[0] + vx, box[1] + vy, box[2] + vx, box[3] + vy)
        fps = self.st.get("rec_fps", 10)
        ffmpeg = extras.find_ffmpeg() if self.st.get("rec_format", "mp4") == "mp4" else None
        if ffmpeg:
            audio = extras.audio_available()
            try:
                extras.VideoRecorder(self.root, absbox, self._record_done, fps=fps, k=self.k, ffmpeg=ffmpeg,
                                     mic=audio and self.st.get("rec_mic", False),
                                     system=audio and self.st.get("rec_system", False))
                return
            except Exception as ex:
                self.set_status(tr("MP4 recording failed ({e}) - recording a GIF instead", e=ex))
        extras.GifRecorder(self.root, absbox, self._record_done, fps=fps, k=self.k)

    def _record_done(self, rec):
        self.busy = False
        self.root.deiconify()
        self.root.lift()
        if rec is None:
            self.set_status(tr("Recording cancelled"))
            return
        folder = self.st.get("last_dir") or DEFAULT_SAVE_DIR
        video = isinstance(rec, extras.VideoTake)
        ext, label = ("mp4", "MP4") if video else ("gif", "GIF")
        p = filedialog.asksaveasfilename(
            parent=self.root, title=tr("Save recording as"), defaultextension="." + ext,
            initialdir=folder if os.path.isdir(folder) else None,
            initialfile=f"Recording_{datetime.now():%Y%m%d_%H%M%S}.{ext}",
            filetypes=[(tr("MP4 video"), "*.mp4")] if video else [(tr("GIF animation"), "*.gif")])
        if not p:
            if video:
                rec.discard()
            self.set_status(tr("Recording discarded"))
            return
        if not p.lower().endswith("." + ext):
            p += "." + ext
        self.st["last_dir"] = os.path.dirname(p)
        note = tr("  ·  stopped at the length limit") if rec.limit_hit else ""
        if video and rec.notes:
            note += "  ·  " + "  ·  ".join(rec.notes)

        def work():
            try:
                if video:
                    if getattr(rec, "error", None):
                        rec.discard()
                        raise RuntimeError(rec.error)
                    extras.save_video(rec, p)
                else:
                    extras.save_gif(rec, p, lambda pct: self.q.put(("gif_progress", pct, label)))
                self.q.put(("gif_saved", p, None, note, label))
            except Exception as ex:
                self.q.put(("gif_saved", p, str(ex), note, label))
        self.set_status(tr("Saving {f}… {p}%", f=label, p=0) if not video else tr("Saving {f}…", f=label))
        threading.Thread(target=work, daemon=True).start()

    # ===================================================================== loop / exit
    def _poll(self):
        try:
            while True:
                m = self.q.get_nowait()
                if m[0] == "capture":
                    self.new_capture()
                elif m[0] == "hotkey_failed":
                    self.set_status(tr("⚠ Global hotkey Ctrl+Alt+S is used by another program - use the button or Ctrl+N"))
                elif m[0] == "copied":
                    _, ok, label, auto, size = m
                    if ok:
                        self.flash_msg(tr("✓ Copied {label}", label=label))
                        if not auto:
                            self.set_status(tr("Copied {label} to clipboard ({w} × {h})", label=label, w=size[0], h=size[1]))
                    else:
                        self.set_status(tr("⚠ Clipboard busy - try Copy again"))
                elif m[0] == "gif_progress":
                    self.set_status(tr("Saving {f}… {p}%", f=m[2], p=m[1]))
                elif m[0] == "gif_saved":
                    _, p, err, note, label = m
                    if err:
                        messagebox.showerror(tr("Save failed"), err, parent=self.root)
                        self.set_status(tr("Save failed"))
                    else:
                        self.set_status(tr("{f} saved: {p}", f=label, p=p) + note)
                        self.flash_msg(tr("✓ {f} saved", f=label))
        except queue.Empty:
            pass
        self._poll_job = self.root.after(80, self._poll)

    def on_close(self):
        self.commit_edit()
        dirty = [it for it in self.items if it.get("dirty")]
        if dirty and self.ask_close.get():
            dlg = CloseDialog(self.root, len(dirty), self.st, tr(self.view.get()))
            r = dlg.result
            if r is None:           # Cancel -> keep the app open
                return
            self.ask_close.set(r["ask"])
            self.st.update(ask_on_close=r["ask"], open_after_save=r["open"])
            if r["action"] == "save":
                try:
                    paths = self.export_batch(r["what"], r["fmt"], r["folder"], r["prefix"])
                except Exception as ex:
                    messagebox.showerror(tr("Save failed"), str(ex), parent=self.root)
                    return
                self.st.update(last_dir=r["folder"], close_fmt=r["fmt"], close_what=r["what"])
                if r["open"] and paths:
                    try:
                        os.startfile(r["folder"])
                    except Exception:
                        pass
        self._shutdown()

    def _shutdown(self):
        for key in list(self._jobs):
            j = self._jobs.pop(key)
            self.root.after_cancel(j)
        for it in self.items:
            self._wait_saved(it)
        if self.keep_history.get():
            for it in self.items:
                self._save_meta(it)
            self._save_board()
        else:
            for it in self.items:
                self._delete_files(it)
        try:
            self.st["geometry"] = self.root.geometry()
        except Exception:
            pass
        self.st.update(mode=self._key(self.mode_var, self._mode_keys()), delay=self._key(self.delay_var, DELAY_KEYS),
                       view=self.view.get())
        save_settings(self.st)
        try:
            self.root.after_cancel(self._poll_job)
        except Exception:
            pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    if app.restart:
        import subprocess
        args = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, os.path.abspath(__file__)]
        env = dict(os.environ)
        # PyInstaller onefile: make the new process unpack its own copy instead of reusing ours,
        # which is deleted when this process exits.
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        subprocess.Popen(args, close_fds=True, env=env)


if __name__ == "__main__":
    main()
