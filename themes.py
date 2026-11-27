# -*- coding: utf-8 -*-
"""Theme packs for MultiCapture.

A theme is a folder with a ``theme.json`` file and some PNG images (see docs/THEMES.md):

    flowers/
        theme.json          name, author, version, colours, decorations, frame
        preview.png         optional, shown in the theme manager
        icons/pen.png       optional, one icon per function (missing ones use the default icon)
        ...                 any other images referenced from theme.json

Themes come from three places, later ones win when two share a folder name (= theme id):
  1. built in  : the ``themes`` folder next to the program (bundled in the exe)
  2. user      : %APPDATA%\\MultiCapture\\themes  (downloaded, imported or self-made)

Nothing here runs code from a theme: theme.json is plain data and images are opened with Pillow.
The app is offline; only ``fetch_catalog`` / ``install_remote`` use the network, and only when the
user clicks "Get online themes".
"""
import json
import math
import os
import re
import shutil
import tempfile
import urllib.parse
import urllib.request
import zipfile

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FORMAT = 1
DEFAULT_ID = "default"
REPO = "Blueaistudio/MultiCapture"
BRANCH = "main"
REMOTE_DIR = "themes"

# Every colour a theme can set. Missing keys keep these defaults (the classic MultiCapture look).
DEFAULT_COLORS = {
    "accent": "#2563EB",        # main buttons, selection, links
    "accent_dark": "#1D4ED8",   # accent button when hovered
    "accent_light": "#E8EFFE",  # selected tool, text selection
    "bg": "#F3F4F6",            # window background
    "panel": "#FFFFFF",         # header, side panels, dialogs
    "border": "#E5E7EB",        # separator lines
    "text": "#111827",
    "muted": "#6B7280",         # secondary text
    "canvas": "#E7EAEE",        # area behind the screenshot
    "button": "#F3F4F6",        # small grey buttons
    "button_hover": "#E5E7EB",
    "hover": "#EEF2F7",         # header buttons when hovered
    "icon": "#374151",          # colour of the built-in tool icons
    "icon_accent": "#2563EB",   # second colour of the built-in tool icons
    "shadow": "#C8CDD5",        # shadow under the screenshot on the canvas
    "notes_bg": "#FBFBFC",      # notes box
    "field": "#FFFFFF",         # drop-down lists and number boxes
    "tooltip_bg": "#111827",
    "tooltip_text": "#FFFFFF",
    "success": "#15803D",       # "✓ Copied" message
}

# Names of the icon files a theme may provide in icons/<key>.png
TOOL_ICON_KEYS = ["select", "pen", "highlight", "line", "arrow", "rect", "ellipse", "text", "callout",
                  "marker", "stamp", "mosaic", "dist", "perim", "area", "angle", "calib",
                  "eraser", "fill", "picker", "crop", "table"]
HEADER_ICON_KEYS = ["capture", "copy", "save", "delete", "options", "help", "themes", "pin", "ocr", "record"]
ICON_KEYS = TOOL_ICON_KEYS + HEADER_ICON_KEYS

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
ALLOWED_EXT = {".json", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".txt", ".md"}
MAX_FILE = 8 * 1024 * 1024
MAX_THEME = 40 * 1024 * 1024
MAX_FILES = 300
MAX_PIXELS = 4096 * 4096
ANCHORS = ("nw", "n", "ne", "e", "se", "s", "sw", "w", "center")


class ThemeError(Exception):
    pass


# --------------------------------------------------------------------------- helpers
def local_text(v, lang="en"):
    """theme.json texts are either a plain string or {"en": ..., "zh": ..., "fr": ...}."""
    if isinstance(v, dict):
        for k in (lang, "en", "zh", "fr"):
            if isinstance(v.get(k), str) and v[k].strip():
                return v[k]
        for x in v.values():
            if isinstance(x, str):
                return x
        return ""
    return v if isinstance(v, str) else ""


def parse_color(v, default=None):
    """'#RGB', '#RRGGBB' or '#RRGGBBAA' -> (r, g, b, a). Anything else -> default."""
    if not isinstance(v, str) or not HEX_RE.match(v.strip()):
        return default
    h = v.strip()[1:]
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 6:
        h += "FF"
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))


def color_hex(v, default):
    """Colour for Tk widgets (no alpha)."""
    c = parse_color(v)
    return "#%02X%02X%02X" % c[:3] if c else default


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v or "0"))[:4]) or (0,)


def _num(v, default, lo=None, hi=None):
    try:
        x = float(v)
        if math.isnan(x):
            raise ValueError
    except (TypeError, ValueError):
        return default
    if lo is not None:
        x = max(lo, x)
    if hi is not None:
        x = min(hi, x)
    return x


def _quad(v, default=(0, 0, 0, 0)):
    """A number or [left, top, right, bottom]."""
    if isinstance(v, (int, float)):
        return (max(0.0, float(v)),) * 4
    if isinstance(v, (list, tuple)) and len(v) == 4:
        return tuple(_num(x, 0, 0, 10000) for x in v)
    return default


def safe_rel(rel):
    """Normalises a path inside a theme folder; raises ThemeError for anything leaving it."""
    if not isinstance(rel, str) or not rel or "\x00" in rel:
        raise ThemeError("bad file name")
    p = rel.replace("\\", "/")
    if p.startswith("/") or re.match(r"^[A-Za-z]:", p):
        raise ThemeError(f"absolute path not allowed: {rel}")
    parts = [x for x in p.split("/") if x not in ("", ".")]
    if not parts or any(x == ".." for x in parts):
        raise ThemeError(f"path leaves the theme folder: {rel}")
    return "/".join(parts)


def check_file_name(rel):
    rel = safe_rel(rel)
    if os.path.splitext(rel)[1].lower() not in ALLOWED_EXT:
        raise ThemeError(f"file type not allowed in a theme: {rel}")
    return rel


def _font(font_fn, size, bold=False, text=""):
    size = max(6, int(round(size)))
    if font_fn:
        try:
            return font_fn(size, bold, text)
        except Exception:
            pass
    return ImageFont.load_default(size)


# --------------------------------------------------------------------------- theme object
class Theme:
    def __init__(self, tid, path, source, meta):
        self.id = tid
        self.path = path            # folder, or None for the built-in default theme
        self.source = source        # "default" | "builtin" | "user"
        self.meta = meta
        self._img_cache = {}
        cols = meta.get("colors") if isinstance(meta.get("colors"), dict) else {}
        self.colors = {k: color_hex(cols.get(k), d) for k, d in DEFAULT_COLORS.items()}
        fr = meta.get("frame")
        self.frame = fr if isinstance(fr, dict) and fr else None
        dec = meta.get("decorations")
        self.decorations = dec if isinstance(dec, dict) else {}

    # display ------------------------------------------------------------
    def name(self, lang="en"):
        return local_text(self.meta.get("name"), lang) or self.id

    def description(self, lang="en"):
        return local_text(self.meta.get("description"), lang)

    @property
    def author(self):
        return local_text(self.meta.get("author")) or ""

    @property
    def version(self):
        return str(self.meta.get("version") or "")

    # files --------------------------------------------------------------
    def file(self, rel):
        """Absolute path of a file inside the theme, or None."""
        if not self.path:
            return None
        try:
            rel = safe_rel(rel)
        except ThemeError:
            return None
        p = os.path.join(self.path, *rel.split("/"))
        return p if os.path.isfile(p) else None

    def image(self, rel):
        """RGBA image from the theme (cached), or None if missing / unreadable."""
        if not rel:
            return None
        if rel in self._img_cache:
            return self._img_cache[rel]
        im = None
        p = self.file(rel)
        if p:
            try:
                with Image.open(p) as f:
                    if f.width * f.height <= MAX_PIXELS:
                        im = f.convert("RGBA")
            except Exception:
                im = None
        self._img_cache[rel] = im
        return im

    def icon(self, key):
        """User-made icon for a function (icons/<key>.png), or None to use the default icon."""
        icons = self.meta.get("icons") if isinstance(self.meta.get("icons"), dict) else {}
        return self.image(icons.get(key) or f"icons/{key}.png")

    def preview(self):
        return self.image(self.meta.get("preview") or "preview.png")

    def decoration(self, where):
        d = self.decorations.get(where)
        if isinstance(d, str):
            d = {"image": d}
        if not isinstance(d, dict):
            return None
        im = self.image(d.get("image"))
        return (im, d) if im is not None else None


def default_theme():
    return Theme(DEFAULT_ID, None, "default", {
        "name": {"en": "Classic", "fr": "Classique", "zh": "经典"},
        "author": "MultiCapture", "version": "1.0",
        "description": {"en": "The original MultiCapture look, without a frame.",
                        "fr": "L'apparence d'origine de MultiCapture, sans cadre.",
                        "zh": "MultiCapture 原本的样子，不加边框。"}})


def load_theme_dir(path, source="user"):
    """Reads one theme folder. Raises ThemeError when theme.json is missing or invalid."""
    tid = os.path.basename(os.path.normpath(path)).lower()
    if not ID_RE.match(tid) or tid == DEFAULT_ID:
        raise ThemeError(f"bad theme folder name: {tid!r} (use a-z, 0-9, - and _)")
    jp = os.path.join(path, "theme.json")
    if not os.path.isfile(jp):
        raise ThemeError("theme.json not found")
    if os.path.getsize(jp) > 1024 * 1024:
        raise ThemeError("theme.json is too large")
    try:
        with open(jp, encoding="utf-8-sig") as f:
            meta = json.load(f)
    except (OSError, ValueError) as ex:
        raise ThemeError(f"theme.json is not valid JSON: {ex}")
    if not isinstance(meta, dict):
        raise ThemeError("theme.json must contain an object { ... }")
    fmt = meta.get("format", FORMAT)
    if not isinstance(fmt, int) or fmt > FORMAT:
        raise ThemeError(f"theme format {fmt!r} needs a newer MultiCapture")
    return Theme(tid, path, source, meta)


def discover(dirs):
    """dirs: [(folder, source), ...] in increasing priority. Returns (themes dict, errors list)."""
    themes = {DEFAULT_ID: default_theme()}
    errors = []
    for base, source in dirs:
        if not base or not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            p = os.path.join(base, name)
            if not os.path.isdir(p) or name.startswith((".", "_")):
                continue
            try:
                t = load_theme_dir(p, source)
                themes[t.id] = t
            except ThemeError as ex:
                errors.append((name, str(ex)))
    return themes, errors


# --------------------------------------------------------------------------- frames
def frame_scale(fr, w, h):
    s = fr.get("scale", "auto")
    if isinstance(s, (int, float)):
        return _num(s, 1.0, 0.1, 10)
    ref = _num(fr.get("ref_size"), 1200, 100, 10000)
    return max(0.5, min(2.5, max(w, h) / ref))


def nine_slice(src, cuts, size, k, edges="stretch"):
    """Draws a 9-slice image at `size`. cuts = (left, top, right, bottom) in source pixels;
    corners are scaled by k, edges are stretched or tiled, the centre is stretched."""
    W, H = size
    sw, sh = src.size
    l, t, r, b = (int(round(x)) for x in cuts)
    l, r = min(l, sw // 2), min(r, sw // 2)
    t, b = min(t, sh // 2), min(b, sh // 2)
    L, T, R, B = (max(0, int(round(x * k))) for x in (l, t, r, b))
    if L + R > W:
        L = R = W // 2
    if T + B > H:
        T = B = H // 2
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xs_src = [(0, l), (l, sw - r), (sw - r, sw)]
    ys_src = [(0, t), (t, sh - b), (sh - b, sh)]
    xs_dst = [(0, L), (L, W - R), (W - R, W)]
    ys_dst = [(0, T), (T, H - B), (H - B, H)]
    for j in range(3):
        for i in range(3):
            sx0, sx1 = xs_src[i]
            sy0, sy1 = ys_src[j]
            dx0, dx1 = xs_dst[i]
            dy0, dy1 = ys_dst[j]
            if sx1 <= sx0 or sy1 <= sy0 or dx1 <= dx0 or dy1 <= dy0:
                continue
            piece = src.crop((sx0, sy0, sx1, sy1))
            dw, dh = dx1 - dx0, dy1 - dy0
            tile = edges == "tile" and (i == 1) != (j == 1)
            if tile:
                # keep the pattern's proportions: scale the thickness by k, repeat along the edge
                if i == 1:
                    pw = max(1, int(round(piece.width * dh / piece.height)))
                    piece = piece.resize((pw, dh), Image.LANCZOS)
                    strip = Image.new("RGBA", (dw, dh))
                    for x in range(0, dw, pw):
                        strip.paste(piece, (x, 0))
                else:
                    ph = max(1, int(round(piece.height * dw / piece.width)))
                    piece = piece.resize((dw, ph), Image.LANCZOS)
                    strip = Image.new("RGBA", (dw, dh))
                    for y in range(0, dh, ph):
                        strip.paste(piece, (0, y))
                out.alpha_composite(strip, (dx0, dy0))
            else:
                out.alpha_composite(piece.resize((dw, dh), Image.LANCZOS), (dx0, dy0))
    return out


def _rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=max(0, int(radius)), fill=255)
    return m


def _fill_template(tpl, ctx):
    if not isinstance(tpl, str):
        return ""

    class D(dict):
        def __missing__(self, key):
            return ""
    try:
        return tpl.format_map(D({k: v for k, v in ctx.items() if isinstance(v, (str, int, float))}))
    except (ValueError, IndexError, AttributeError):
        return tpl


def _anchor_xy(anchor, box, w, h, off):
    """Top-left corner for a w x h picture centred on a box point (nw, n, ne, e, se, s, sw, w, center)."""
    x0, y0, x1, y1 = box
    a = anchor if anchor in ANCHORS else "nw"
    ax = x0 if a in ("nw", "w", "sw") else x1 if a in ("ne", "e", "se") else (x0 + x1) / 2
    ay = y0 if a in ("nw", "n", "ne") else y1 if a in ("sw", "s", "se") else (y0 + y1) / 2
    return int(round(ax - w / 2 + off[0])), int(round(ay - h / 2 + off[1]))


def apply_frame(img, theme, ctx=None, font_fn=None):
    """Returns `img` (RGB) inside the theme's frame. ctx gives the caption values
    (title, date, time, num). font_fn(size, bold, text) -> ImageFont."""
    fr = theme.frame if theme else None
    if not fr:
        return img
    ctx = ctx or {}
    src = img.convert("RGBA")
    w, h = src.size
    k = frame_scale(fr, w, h)

    def px(key, default=0, hi=2000):
        return int(round(_num(fr.get(key), default, 0, hi) * k))

    border_img = theme.image(fr.get("image"))
    cuts = _quad(fr.get("slice"), (0, 0, 0, 0)) if border_img is not None else (0, 0, 0, 0)
    inset = _quad(fr.get("inset"), cuts) if border_img is not None else (0, 0, 0, 0)
    il, it_, ir, ib = (int(round(x * k)) for x in inset)
    pad = px("padding", 0)
    margin = px("margin", 0)
    radius = px("radius", 0, 500)

    tb = fr.get("titlebar") if isinstance(fr.get("titlebar"), dict) else None
    cap = fr.get("caption") if isinstance(fr.get("caption"), dict) else None
    tb_h = int(round(_num(tb.get("height"), 34, 0, 400) * k)) if tb else 0
    cap_h = int(round(_num(cap.get("height"), 56, 0, 600) * k)) if cap else 0

    cw = il + pad + w + pad + ir
    ch = it_ + tb_h + pad + h + pad + cap_h + ib
    W, H = cw + 2 * margin, ch + 2 * margin
    canvas_c = parse_color(fr.get("canvas"), (255, 255, 255, 0))
    out = Image.new("RGBA", (W, H), canvas_c)
    card = (margin, margin, margin + cw, margin + ch)

    # ornaments that sit behind the card
    orns = fr.get("ornaments") if isinstance(fr.get("ornaments"), list) else []
    _draw_ornaments(out, theme, [o for o in orns if isinstance(o, dict) and o.get("layer") == "back"], card, k)

    # shadow
    sh = fr.get("shadow") if isinstance(fr.get("shadow"), dict) else None
    if sh:
        col = parse_color(sh.get("color"), (0, 0, 0, 70))
        blur = _num(sh.get("blur"), 16, 0, 200) * k
        off = sh.get("offset") if isinstance(sh.get("offset"), list) and len(sh.get("offset")) == 2 else [0, 6]
        ox, oy = (int(round(_num(v, 0, -500, 500) * k)) for v in off)
        f = 4  # blur a small mask, then scale it up: fast even for 4K screenshots
        sm = Image.new("L", (max(1, W // f), max(1, H // f)), 0)
        ImageDraw.Draw(sm).rounded_rectangle(((card[0] + ox) / f, (card[1] + oy) / f, (card[2] + ox) / f, (card[3] + oy) / f),
                                             radius=radius / f, fill=col[3])
        if blur > 0:
            sm = sm.filter(ImageFilter.GaussianBlur(blur / f))
        layer = Image.new("RGBA", (W, H), col[:3] + (0,))
        layer.putalpha(sm.resize((W, H), Image.BILINEAR))
        out.alpha_composite(layer)

    # card background
    bg = parse_color(fr.get("background"), (255, 255, 255, 255) if (pad or tb or cap or radius) else (0, 0, 0, 0))
    if bg[3]:
        layer = Image.new("RGBA", (cw, ch), bg)
        out.paste(layer, card[:2], _rounded_mask((cw, ch), radius))

    d = ImageDraw.Draw(out)
    # title bar
    if tb and tb_h:
        tcol = parse_color(tb.get("color"), (229, 231, 235, 255))
        y0 = card[1] + it_
        bar = Image.new("RGBA", (cw - il - ir, tb_h), tcol)
        m = Image.new("L", bar.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, bar.width - 1, bar.height + radius), radius=radius, fill=255)
        out.paste(bar, (card[0] + il, y0), m)
        x = card[0] + il + int(14 * k)
        if tb.get("dots", True):
            r = max(2, int(tb_h * 0.17))
            for c in ("#FF5F57", "#FEBC2E", "#28C840"):
                d.ellipse((x, y0 + tb_h / 2 - r, x + 2 * r, y0 + tb_h / 2 + r), fill=parse_color(c))
                x += int(2 * r + r * 1.1)
        text = _fill_template(tb.get("text", "{title}"), ctx)
        if text:
            fnt = _font(font_fn, tb_h * 0.42, True, text)
            d.text((card[0] + cw / 2, y0 + tb_h / 2), text, font=fnt, anchor="mm",
                   fill=parse_color(tb.get("text_color"), (55, 65, 81, 255)))

    # the screenshot
    sx, sy = card[0] + il + pad, card[1] + it_ + tb_h + pad
    if radius and not pad and not tb and not border_img:
        out.paste(src, (sx, sy), ImageChops.multiply(src.getchannel("A"), _rounded_mask((w, h), radius)))
    else:
        out.alpha_composite(src, (sx, sy))
    bd = fr.get("border") if isinstance(fr.get("border"), dict) else None
    if bd:
        bw = int(round(_num(bd.get("width"), 1, 0, 200) * k))
        if bw:
            d.rounded_rectangle((card[0], card[1], card[2] - 1, card[3] - 1), radius=radius,
                                outline=parse_color(bd.get("color"), (208, 213, 221, 255)), width=bw)

    # caption under the screenshot
    if cap and cap_h:
        text = _fill_template(cap.get("text", "{date}"), ctx)
        if text:
            size = _num(cap.get("size"), 20, 4, 300) * k
            fnt = _font(font_fn, size, bool(cap.get("bold")), text)
            al = cap.get("align", "center")
            y = card[1] + it_ + tb_h + pad + h + pad + cap_h / 2
            if al == "left":
                xy, anchor = (card[0] + il + pad + int(4 * k), y), "lm"
            elif al == "right":
                xy, anchor = (card[2] - ir - pad - int(4 * k), y), "rm"
            else:
                xy, anchor = (card[0] + cw / 2, y), "mm"
            d.text(xy, text, font=fnt, anchor=anchor, fill=parse_color(cap.get("color"), (55, 65, 81, 255)))

    # 9-slice picture frame on top
    if border_img is not None:
        out.alpha_composite(nine_slice(border_img, cuts, (cw, ch), k, fr.get("edges", "stretch")), card[:2])

    _draw_ornaments(out, theme, [o for o in orns if isinstance(o, dict) and o.get("layer") != "back"], card, k)

    flat = Image.new("RGB", out.size, canvas_c[:3] if canvas_c[3] else (255, 255, 255))
    flat.paste(out, (0, 0), out)
    return flat


def _composite_at(out, piece, x, y):
    """alpha_composite that accepts positions partly (or fully) outside the image."""
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(out.width, x + piece.width), min(out.height, y + piece.height)
    if x1 <= x0 or y1 <= y0:
        return
    out.alpha_composite(piece.crop((x0 - x, y0 - y, x1 - x, y1 - y)), (x0, y0))


def _draw_ornaments(out, theme, orns, card, k):
    for o in orns[:40]:
        im = theme.image(o.get("image"))
        if im is None:
            continue
        size = _num(o.get("size"), im.width, 1, 4000) * k
        sc = size / max(1, im.width)
        tw, th = max(1, int(im.width * sc)), max(1, int(im.height * sc))
        piece = im.resize((tw, th), Image.LANCZOS)
        off = o.get("offset") if isinstance(o.get("offset"), list) and len(o.get("offset")) == 2 else [0, 0]
        off = [_num(v, 0, -4000, 4000) * k for v in off]
        x, y = _anchor_xy(o.get("anchor", "nw"), card, tw, th, off)
        _composite_at(out, piece, x, y)


# --------------------------------------------------------------------------- preview
def make_preview(theme, icon_fn, size=(520, 330), font_fn=None, sample=None, lang="en"):
    """Mock-up of the main window in this theme. icon_fn(theme, key, px) -> RGBA icon."""
    W, H = size
    c = theme.colors
    out = Image.new("RGBA", (W, H), parse_color(c["bg"]))
    d = ImageDraw.Draw(out)
    hh = 40
    d.rectangle((0, 0, W, hh), fill=c["panel"])
    d.line((0, hh, W, hh), fill=c["border"])
    deco = theme.decoration("header")
    if deco:
        im = deco[0]
        th = hh - 2
        piece = im.resize((max(1, int(im.width * th / im.height)), th), Image.LANCZOS)
        out.alpha_composite(piece, (W - piece.width, 1))
    d.rounded_rectangle((12, 9, 104, 31), radius=4, fill=c["accent"])
    label = "+ " + theme.name(lang)[:10]
    d.text((58, 20), label, font=_font(font_fn, 11, True, label), fill="#FFFFFF", anchor="mm")
    for i in range(3):
        d.rounded_rectangle((118 + i * 46, 12, 158 + i * 46, 28), radius=3, fill=c["button"])
    lw, tw_, rw = 92, 34, 96
    d.rectangle((0, hh + 1, lw, H), fill=c["panel"])
    d.line((lw, hh, lw, H), fill=c["border"])
    for i in range(4):
        y = hh + 10 + i * 52
        d.rounded_rectangle((8, y, lw - 8, y + 44), radius=4, fill=c["canvas"],
                            outline=c["accent"] if i == 0 else c["border"], width=2 if i == 0 else 1)
    d.rectangle((W - rw, hh + 1, W, H), fill=c["panel"])
    d.line((W - rw, hh, W - rw, H), fill=c["border"])
    for i in range(5):
        d.rounded_rectangle((W - rw + 10, hh + 14 + i * 22, W - 12 - (i % 3) * 14, hh + 24 + i * 22), radius=3,
                            fill=c["button"])
    d.rectangle((lw + 1, hh + 1, lw + tw_, H), fill=c["panel"])
    d.line((lw + tw_, hh, lw + tw_, H), fill=c["border"])
    for i, key in enumerate(TOOL_ICON_KEYS[:min(len(TOOL_ICON_KEYS), (H - hh - 8) // 26)]):
        y = hh + 6 + i * 26
        if i == 1:
            d.rounded_rectangle((lw + 4, y - 2, lw + tw_ - 4, y + 22), radius=4, fill=c["accent_light"])
        ic = icon_fn(theme, key, 20)
        if ic is not None:
            out.alpha_composite(ic, (lw + (tw_ - 20) // 2 + 1, y))
    cx0, cy0, cx1, cy1 = lw + tw_ + 1, hh + 1, W - rw, H
    d.rectangle((cx0, cy0, cx1, cy1), fill=c["canvas"])
    deco = theme.decoration("canvas")
    if deco:
        _paste_deco(out, deco, (cx0, cy0, cx1, cy1), 0.45)
    shot = sample or _sample_shot()
    if theme.frame:
        shot = apply_frame(shot, theme, {"title": "MultiCapture", "date": "2026-11-25", "time": "09:30", "num": 1},
                           font_fn)
    aw, ah = cx1 - cx0 - 24, cy1 - cy0 - 24
    s = min(aw / shot.width, ah / shot.height)
    shot = shot.convert("RGBA").resize((max(1, int(shot.width * s)), max(1, int(shot.height * s))), Image.LANCZOS)
    x, y = cx0 + (cx1 - cx0 - shot.width) // 2, cy0 + (cy1 - cy0 - shot.height) // 2
    if not theme.frame:
        d.rectangle((x + 3, y + 3, x + shot.width + 3, y + shot.height + 3), fill=c["shadow"])
    out.alpha_composite(shot, (x, y))
    return out


def _sample_shot():
    im = Image.new("RGB", (900, 600), "#FFFFFF")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 900, 70), fill="#E8EEF7")
    d.rectangle((40, 110, 520, 140), fill="#CBD5E1")
    for i in range(6):
        d.rectangle((40, 180 + i * 50, 840 - (i % 3) * 120, 200 + i * 50), fill="#E2E8F0")
    d.rectangle((600, 100, 860, 300), fill="#DBEAFE")
    d.ellipse((560, 330, 760, 470), outline="#E53935", width=10)
    return im


def _paste_deco(out, deco, box, max_frac=0.45):
    """Decoration image in a box. options: anchor (nw/ne/sw/se/n/s/e/w/center/tile), size (px), margin."""
    im, opt = deco
    x0, y0, x1, y1 = (int(v) for v in box)
    bw, bh = x1 - x0, y1 - y0
    if bw < 4 or bh < 4:
        return
    anchor = opt.get("anchor", "se")
    if anchor == "tile":
        layer = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        for yy in range(0, bh, max(1, im.height)):
            for xx in range(0, bw, max(1, im.width)):
                layer.paste(im, (xx, yy))
        out.alpha_composite(layer, (x0, y0))
        return
    s = min(1.0, max_frac * bw / im.width, max_frac * bh / im.height)
    if opt.get("size"):
        s = min(s, _num(opt.get("size"), im.width, 1, 4000) / im.width)
    piece = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS) if s != 1 else im
    m = int(_num(opt.get("margin"), 12, 0, 500))
    px, py = _anchor_xy(anchor, (x0 + m, y0 + m, x1 - m, y1 - m), piece.width, piece.height, (0, 0))
    a = anchor if anchor in ANCHORS else "se"
    # keep the picture inside the box (the anchor names a corner / side of the box)
    px = x0 + m if "w" in a else (x1 - m - piece.width if "e" in a else px)
    py = y0 + m if "n" in a else (y1 - m - piece.height if "s" in a else py)
    _composite_at(out, piece, px, py)


def decoration_image(deco, box_size, max_frac=0.45):
    """Renders a decoration into a transparent image of box_size (used for the Tk canvas)."""
    out = Image.new("RGBA", box_size, (0, 0, 0, 0))
    _paste_deco(out, deco, (0, 0) + tuple(box_size), max_frac)
    return out


# --------------------------------------------------------------------------- install / import
def _validate_folder(path):
    """Checks every file of an unpacked theme; returns the loaded Theme."""
    total, count = 0, 0
    for root, dirs, files in os.walk(path):
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, path).replace(os.sep, "/")
            check_file_name(rel)
            if os.path.islink(p):
                raise ThemeError(f"links are not allowed: {rel}")
            sz = os.path.getsize(p)
            if sz > MAX_FILE:
                raise ThemeError(f"file too large: {rel}")
            total += sz
            count += 1
    if count > MAX_FILES or total > MAX_THEME:
        raise ThemeError("theme is too large")
    return load_theme_dir(path)


def _move_into(tmp_theme_dir, user_dir, tid):
    os.makedirs(user_dir, exist_ok=True)
    dest = os.path.join(user_dir, tid)
    old = None
    if os.path.exists(dest):
        old = dest + ".old"
        shutil.rmtree(old, ignore_errors=True)
        os.rename(dest, old)
    shutil.move(tmp_theme_dir, dest)
    if old:
        shutil.rmtree(old, ignore_errors=True)
    return load_theme_dir(dest, "user")


def import_zip(zip_path, user_dir):
    """Installs a theme shared as a .zip (theme.json at the top, or inside one folder)."""
    try:
        zf = zipfile.ZipFile(zip_path)
    except (OSError, zipfile.BadZipFile) as ex:
        raise ThemeError(f"not a zip file: {ex}")
    with zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        names = [safe_rel(i.filename) for i in infos]
        roots = {n.split("/")[0] for n in names}
        if "theme.json" in names:
            prefix = ""
            tid = os.path.splitext(os.path.basename(zip_path))[0]
        elif len(roots) == 1 and f"{next(iter(roots))}/theme.json" in names:
            prefix = next(iter(roots)) + "/"
            tid = next(iter(roots))
        else:
            raise ThemeError("theme.json not found in the zip")
        try:
            meta = json.loads(zf.read(infos[names.index(prefix + "theme.json")]).decode("utf-8-sig"))
            if isinstance(meta, dict) and isinstance(meta.get("id"), str):
                tid = meta["id"]
        except ValueError:
            pass
        tid = re.sub(r"[^a-z0-9_-]+", "-", tid.strip().lower()).strip("-_")[:48]
        if not ID_RE.match(tid or "") or tid == DEFAULT_ID:
            raise ThemeError(f"bad theme name: {tid!r}")
        if sum(i.file_size for i in infos) > MAX_THEME or len(infos) > MAX_FILES:
            raise ThemeError("theme is too large")
        tmp = tempfile.mkdtemp(prefix="mc_theme_")
        try:
            dst = os.path.join(tmp, tid)
            os.makedirs(dst)
            for info, n in zip(infos, names):
                if not n.startswith(prefix):
                    continue
                rel = check_file_name(n[len(prefix):])
                if info.file_size > MAX_FILE:
                    raise ThemeError(f"file too large: {rel}")
                p = os.path.join(dst, *rel.split("/"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with zf.open(info) as fi, open(p, "wb") as fo:
                    data = fi.read(MAX_FILE + 1)
                    if len(data) > MAX_FILE:
                        raise ThemeError(f"file too large: {rel}")
                    fo.write(data)
            _validate_folder(dst)
            return _move_into(dst, user_dir, tid)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


def export_zip(theme, zip_path):
    """Packs a theme folder into a .zip that others can import."""
    if not theme.path:
        raise ThemeError("the classic theme has no files")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(theme.path):
            for fn in files:
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, theme.path).replace(os.sep, "/")
                zf.write(p, f"{theme.id}/{rel}")


def remove_theme(theme, user_dir):
    if theme.source != "user" or not theme.path:
        raise ThemeError("only downloaded or imported themes can be removed")
    if os.path.normcase(os.path.dirname(os.path.abspath(theme.path))) != os.path.normcase(os.path.abspath(user_dir)):
        raise ThemeError("theme is not in the user themes folder")
    shutil.rmtree(theme.path)


# --------------------------------------------------------------------------- online catalog
UA = "MultiCapture-theme-browser"


def _get(url, timeout=20, limit=MAX_FILE):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(limit + 1)
    if len(data) > limit:
        raise ThemeError("download too large")
    return data


def raw_url(path, repo=REPO, branch=BRANCH):
    return f"https://raw.githubusercontent.com/{repo}/{branch}/" + urllib.parse.quote(path)


def fetch_catalog(repo=REPO, branch=BRANCH, folder=REMOTE_DIR, timeout=20, lang="en"):
    """Lists the themes in the GitHub repository's themes/ folder.
    One GitHub API call for the file list, then one theme.json download per theme.
    Returns [{"id", "meta", "files": [(rel, size)], "theme": Theme-like (for name/version)}]."""
    url = f"https://api.github.com/repos/{repo}/git/trees/{urllib.parse.quote(branch)}?recursive=1"
    tree = json.loads(_get(url, timeout, 30 * 1024 * 1024).decode("utf-8"))
    groups = {}
    pre = folder.strip("/") + "/"
    for node in tree.get("tree", []):
        p = node.get("path", "")
        if node.get("type") != "blob" or not p.startswith(pre):
            continue
        rest = p[len(pre):]
        if "/" not in rest:
            continue
        tid, rel = rest.split("/", 1)
        if not ID_RE.match(tid) or tid == DEFAULT_ID:
            continue
        g = groups.setdefault(tid, {"files": [], "bad": False})
        try:
            rel = check_file_name(rel)
        except ThemeError:
            g["bad"] = True
            continue
        g["files"].append((rel, int(node.get("size") or 0)))
    out = []
    for tid, g in sorted(groups.items()):
        if g["bad"] or not any(r == "theme.json" for r, _ in g["files"]):
            continue
        if len(g["files"]) > MAX_FILES or sum(s for _, s in g["files"]) > MAX_THEME:
            continue
        try:
            meta = json.loads(_get(raw_url(f"{pre}{tid}/theme.json", repo, branch), timeout, 1024 * 1024)
                              .decode("utf-8-sig"))
        except Exception:
            continue
        if not isinstance(meta, dict) or not isinstance(meta.get("format", FORMAT), int) or meta.get("format", FORMAT) > FORMAT:
            continue
        out.append({"id": tid, "meta": meta, "files": g["files"], "repo": repo, "branch": branch,
                    "folder": pre, "theme": Theme(tid, None, "online", meta)})
    return out


def fetch_preview(entry, timeout=20):
    """Downloads only the preview image of an online theme (None if it has none)."""
    rel = entry["meta"].get("preview") or "preview.png"
    if not any(r == rel for r, _ in entry["files"]):
        return None
    import io
    data = _get(raw_url(entry["folder"] + entry["id"] + "/" + rel, entry["repo"], entry["branch"]), timeout)
    with Image.open(io.BytesIO(data)) as im:
        if im.width * im.height > MAX_PIXELS:
            return None
        return im.convert("RGBA")


def install_remote(entry, user_dir, timeout=30, progress=None):
    """Downloads every file of an online theme into the user themes folder."""
    tid = entry["id"]
    tmp = tempfile.mkdtemp(prefix="mc_theme_")
    try:
        dst = os.path.join(tmp, tid)
        os.makedirs(dst)
        n = len(entry["files"])
        for i, (rel, _size) in enumerate(entry["files"]):
            rel = check_file_name(rel)
            data = _get(raw_url(entry["folder"] + tid + "/" + rel, entry["repo"], entry["branch"]), timeout)
            p = os.path.join(dst, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(data)
            if progress:
                progress(i + 1, n)
        _validate_folder(dst)
        return _move_into(dst, user_dir, tid)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


ICON_README = """Put one PNG per function in this folder to replace its icon (square, transparent background,
64 x 64 px or larger). Missing files keep the normal icon.

Tools:   {tools}
Header:  {header}
"""


def create_from(base, name, user_dir):
    """Starts a new theme in the user folder from an existing one (or from the classic look),
    with every colour written out so it is easy to edit."""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "my-theme"
    tid, n = slug, 2
    while os.path.exists(os.path.join(user_dir, tid)) or tid == DEFAULT_ID:
        tid, n = f"{slug}-{n}", n + 1
    os.makedirs(user_dir, exist_ok=True)
    dest = os.path.join(user_dir, tid)
    if base.path:
        shutil.copytree(base.path, dest)
    else:
        os.makedirs(dest)
    meta = dict(base.meta) if base.path else {}
    meta.update({"format": FORMAT, "name": name, "author": "", "version": "1.0",
                 "description": "", "colors": dict(base.colors)})
    meta.pop("id", None)
    meta.pop("preview", None)
    pv = os.path.join(dest, "preview.png")
    if os.path.exists(pv):
        os.remove(pv)   # the copied preview would show the old theme
    with open(os.path.join(dest, "theme.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    os.makedirs(os.path.join(dest, "icons"), exist_ok=True)
    with open(os.path.join(dest, "icons", "README.txt"), "w", encoding="utf-8") as f:
        f.write(ICON_README.format(tools=", ".join(TOOL_ICON_KEYS), header=", ".join(HEADER_ICON_KEYS)))
    return load_theme_dir(dest, "user")
