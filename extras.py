# -*- coding: utf-8 -*-
"""
Optional extra features for MultiCapture. Each one is off by default and is switched on in
Options -> Extra features:

* Pin to screen   - a screenshot floats above all windows (move, zoom, opacity)
* Text recognition (OCR) - uses the OCR engine built into Windows 10/11 (offline, no download)
* Scrolling capture - captures a region while it scrolls and stitches the frames into one image
* Screen recording - records a region of the screen to an animated GIF

Nothing here adds a dependency: only Pillow, Tkinter, ctypes and the Windows PowerShell that
ships with Windows (for the OCR bridge). The stitching code is pure Python so it can be tested
on any platform.
"""
import base64
import ctypes
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import zlib
from tkinter import ttk

from PIL import Image, ImageDraw, ImageTk

from i18n import tr

IS_WIN = sys.platform == "win32"

ACCENT = "#2563EB"
BAR_BG = "#111827"
BAR_FG = "#F9FAFB"
BAR_HOVER = "#374151"
REC_RED = "#DC2626"
UI = ("Segoe UI", 9)
UI_B = ("Segoe UI Semibold", 9)

# --------------------------------------------------------------------------- Win32 helpers
if IS_WIN:
    import ctypes.wintypes as wt

    _u32 = ctypes.windll.user32
    _g32 = ctypes.windll.gdi32
    _u32.GetDC.restype = ctypes.c_void_p
    _u32.GetDC.argtypes = [ctypes.c_void_p]
    _u32.ReleaseDC.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _u32.WindowFromPoint.restype = ctypes.c_void_p
    _u32.WindowFromPoint.argtypes = [wt.POINT]
    _u32.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
    _u32.SetWindowDisplayAffinity.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    _u32.GetAsyncKeyState.restype = ctypes.c_short
    _g32.CreateCompatibleDC.restype = ctypes.c_void_p
    _g32.CreateCompatibleDC.argtypes = [ctypes.c_void_p]
    _g32.CreateCompatibleBitmap.restype = ctypes.c_void_p
    _g32.CreateCompatibleBitmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    _g32.SelectObject.restype = ctypes.c_void_p
    _g32.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    _g32.BitBlt.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                            ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    _g32.GetDIBits.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint,
                               ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
    _g32.DeleteObject.argtypes = [ctypes.c_void_p]
    _g32.DeleteDC.argtypes = [ctypes.c_void_p]

    class _BMIH(ctypes.Structure):
        _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD),
                    ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                    ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                    ("biClrImportant", wt.DWORD)]


def grab_box(box):
    """Grabs one screen rectangle (absolute virtual-screen pixels) much faster than grabbing all screens."""
    l, t, r, b = box
    w, h = r - l, b - t
    if not IS_WIN:
        from PIL import ImageGrab
        return ImageGrab.grab(bbox=box).convert("RGB")
    hdc = _u32.GetDC(None)
    mdc = _g32.CreateCompatibleDC(hdc)
    bmp = _g32.CreateCompatibleBitmap(hdc, w, h)
    old = _g32.SelectObject(mdc, bmp)
    try:
        if not _g32.BitBlt(mdc, 0, 0, w, h, hdc, l, t, 0x00CC0020):   # SRCCOPY
            raise OSError("BitBlt failed")
        bi = _BMIH()
        bi.biSize = ctypes.sizeof(_BMIH)
        bi.biWidth, bi.biHeight, bi.biPlanes, bi.biBitCount = w, -h, 1, 32   # top-down, BGRA
        buf = ctypes.create_string_buffer(w * h * 4)
        if not _g32.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bi), 0):
            raise OSError("GetDIBits failed")
        return Image.frombytes("RGB", (w, h), buf.raw, "raw", "BGRX")
    finally:
        _g32.SelectObject(mdc, old)
        _g32.DeleteObject(bmp)
        _g32.DeleteDC(mdc)
        _u32.ReleaseDC(None, hdc)


def virtual_screen():
    if not IS_WIN:
        return 0, 0, 1920, 1080
    return (_u32.GetSystemMetrics(76), _u32.GetSystemMetrics(77),
            _u32.GetSystemMetrics(78), _u32.GetSystemMetrics(79))


def cursor_pos():
    if not IS_WIN:
        return None
    p = wt.POINT()
    return (p.x, p.y) if _u32.GetCursorPos(ctypes.byref(p)) else None


def esc_pressed():
    """True if Esc was pressed since the last call, whichever window has the focus."""
    return IS_WIN and bool(_u32.GetAsyncKeyState(0x1B) & 0x0001)


def exclude_from_capture(win):
    """Hides our own control windows from screen grabs (Windows 10 2004+; ignored elsewhere)."""
    if not IS_WIN:
        return
    try:
        win.update_idletasks()
        _u32.SetWindowDisplayAffinity(ctypes.c_void_p(int(win.wm_frame(), 16)), 0x11)   # WDA_EXCLUDEFROMCAPTURE
    except Exception:
        pass


def send_wheel(box, notches):
    """Scrolls the window under the region down by a number of wheel notches."""
    if not IS_WIN:
        return
    l, t, r, b = box
    cx, cy = (l + r) // 2, (t + b) // 2
    delta = -120 * notches
    cur = cursor_pos()
    if cur and l <= cur[0] < r and t <= cur[1] < b:
        _u32.mouse_event(0x0800, 0, 0, ctypes.c_uint32(delta & 0xFFFFFFFF), 0)   # MOUSEEVENTF_WHEEL
        return
    hwnd = _u32.WindowFromPoint(wt.POINT(cx, cy))
    if hwnd:
        wparam = (delta & 0xFFFF) << 16
        lparam = ((cy & 0xFFFF) << 16) | (cx & 0xFFFF)
        _u32.PostMessageW(hwnd, 0x020A, wparam, lparam)   # WM_MOUSEWHEEL


def draw_cursor(img, x, y, k=1.0):
    """Draws a simple arrow pointer (screen grabs do not contain the mouse cursor)."""
    s = 1.3 * k
    pts = [(0, 0), (0, 17), (4, 13), (7, 20), (10, 19), (7, 12), (12, 12)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill="white", outline="black")


# --------------------------------------------------------------------------- small UI pieces
def _bar_button(parent, text, cmd, bg=BAR_BG, fg=BAR_FG, hover=BAR_HOVER):
    b = tk.Label(parent, text=text, bg=bg, fg=fg, font=UI_B, padx=10, pady=4, cursor="hand2")
    b.bind("<Button-1>", lambda e: cmd())
    b.bind("<Enter>", lambda e: b.configure(bg=hover))
    b.bind("<Leave>", lambda e: b.configure(bg=bg))
    return b


class RegionFrame:
    """A thin coloured frame drawn just outside a screen rectangle (never inside the grab)."""

    def __init__(self, master, box, color, t=3):
        l, tp, r, b = box
        self.wins = []
        for x, y, w, h in ((l - t, tp - t, r - l + 2 * t, t), (l - t, b, r - l + 2 * t, t),
                           (l - t, tp, t, b - tp), (r, tp, t, b - tp)):
            win = tk.Toplevel(master)
            win.overrideredirect(True)
            win.attributes("-topmost", True)
            win.configure(bg=color)
            win.geometry(f"{max(1, w)}x{max(1, h)}{x:+d}{y:+d}")
            exclude_from_capture(win)
            self.wins.append(win)

    def destroy(self):
        for w in self.wins:
            try:
                w.destroy()
            except tk.TclError:
                pass


class FloatBar:
    """Small dark control bar placed next to the region being captured or recorded."""

    def __init__(self, master, box, buttons, dot=None):
        self.win = tk.Toplevel(master)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BAR_BG)
        f = tk.Frame(self.win, bg=BAR_BG, padx=6, pady=4)
        f.pack()
        if dot:
            tk.Label(f, text="●", fg=dot, bg=BAR_BG, font=("Segoe UI", 11)).pack(side="left", padx=(2, 0))
        self.label = tk.Label(f, text="", bg=BAR_BG, fg=BAR_FG, font=UI, padx=6)
        self.label.pack(side="left")
        self.buttons = {}
        for key, text, cmd in buttons:
            b = _bar_button(f, text, cmd)
            b.pack(side="left", padx=2)
            self.buttons[key] = b
        self.win.update_idletasks()
        bw, bh = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        vx, vy, vw, vh = virtual_screen()
        l, t, r, b = box
        x = min(max(vx, r - bw), vx + vw - bw)
        if b + 8 + bh <= vy + vh:
            y = b + 8
        elif t - 8 - bh >= vy:
            y = t - 8 - bh
        else:                       # region covers the screen: sit inside it (hidden from the grab)
            y = b - bh - 12
            x = r - bw - 12
        self.win.geometry(f"{x:+d}{y:+d}")
        exclude_from_capture(self.win)

    def set(self, text):
        self.label.configure(text=text)

    def destroy(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass


# =========================================================================== PIN TO SCREEN
class PinWindow:
    """A screenshot floating above all windows. Drag = move, wheel = zoom, Ctrl+wheel = opacity,
    double-click or Esc = close, right-click = menu."""

    def __init__(self, master, img, copy_fn=None, save_fn=None, on_close=None, pos=None):
        self.img, self.copy_fn, self.save_fn, self.on_close = img, copy_fn, save_fn, on_close
        self.zoom, self.alpha = 1.0, 1.0
        w = self.win = tk.Toplevel(master)
        w.overrideredirect(True)
        w.attributes("-topmost", True)
        w.configure(bg=ACCENT, padx=1, pady=1)
        self.c = tk.Canvas(w, highlightthickness=0, bd=0, cursor="fleur", bg="white")
        self.c.pack()
        self._show()
        vx, vy, vw, vh = virtual_screen()
        if pos is None:
            p = cursor_pos() or (vx + 100, vy + 100)
            pos = (p[0] - 24, p[1] - 24)
        x = min(max(vx, int(pos[0])), vx + vw - 80)
        y = min(max(vy, int(pos[1])), vy + vh - 80)
        w.geometry(f"{x:+d}{y:+d}")
        for seq, fn in (("<ButtonPress-1>", self._press), ("<B1-Motion>", self._drag),
                        ("<Double-Button-1>", lambda e: self.close()), ("<MouseWheel>", self._wheel),
                        ("<ButtonPress-3>", self._menu)):
            self.c.bind(seq, fn)
        w.bind("<Escape>", lambda e: self.close())
        w.bind("<Control-c>", lambda e: self.copy_fn and self.copy_fn(self.img))
        w.after(50, w.focus_force)

    def _show(self):
        iw, ih = self.img.size
        w, h = max(8, int(iw * self.zoom)), max(8, int(ih * self.zoom))
        im = self.img if (w, h) == (iw, ih) else self.img.resize((w, h), Image.LANCZOS if self.zoom < 1 else Image.BILINEAR)
        self.photo = ImageTk.PhotoImage(im)
        self.c.configure(width=w, height=h)
        self.c.delete("all")
        self.c.create_image(0, 0, anchor="nw", image=self.photo)

    def _press(self, e):
        self._off = (e.x_root - self.win.winfo_x(), e.y_root - self.win.winfo_y())
        self.win.focus_force()

    def _drag(self, e):
        self.win.geometry(f"{e.x_root - self._off[0]:+d}{e.y_root - self._off[1]:+d}")

    def _wheel(self, e):
        up = e.delta > 0
        if e.state & 0x4:
            self.set_alpha(self.alpha + (0.1 if up else -0.1))
        else:
            self.set_zoom(self.zoom * (1.1 if up else 1 / 1.1))
        return "break"

    def set_zoom(self, z):
        self.zoom = min(4.0, max(0.1, z))
        self._show()

    def set_alpha(self, a):
        self.alpha = min(1.0, max(0.2, a))
        self.win.attributes("-alpha", self.alpha)

    def _menu(self, e):
        m = tk.Menu(self.win, tearoff=0, font=UI)
        if self.copy_fn:
            m.add_command(label=tr("Copy"), command=lambda: self.copy_fn(self.img), accelerator="Ctrl+C")
        if self.save_fn:
            m.add_command(label=tr("Save as…"), command=lambda: self.save_fn(self.img))
        m.add_separator()
        m.add_command(label=tr("Actual size"), command=lambda: self.set_zoom(1.0))
        om = tk.Menu(m, tearoff=0, font=UI)
        for a in (1.0, 0.8, 0.6, 0.4):
            om.add_command(label=f"{int(a * 100)} %", command=lambda v=a: self.set_alpha(v))
        m.add_cascade(label=tr("Opacity"), menu=om)
        m.add_separator()
        m.add_command(label=tr("Close"), command=self.close, accelerator="Esc")
        if self.on_close:
            m.add_command(label=tr("Close all pinned images"), command=lambda: self.on_close(None))
        m.tk_popup(e.x_root, e.y_root)

    def close(self):
        try:
            self.win.destroy()
        except tk.TclError:
            pass
        if self.on_close:
            self.on_close(self)


# =========================================================================== OCR
# Windows PowerShell 5.1 (part of every Windows 10/11) can call the WinRT OCR engine directly.
# Inputs come in through environment variables, the result is written to a UTF-8 file.
_PS_OCR = r"""
$ErrorActionPreference = 'Stop'
$sb = New-Object System.Text.StringBuilder
try {
  Add-Type -AssemblyName System.Runtime.WindowsRuntime
  $null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
  $null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
  $null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]
  $null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
  $asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' } | Select-Object -First 1
  function Await($op, [Type]$t) {
    $task = $asTask.MakeGenericMethod($t).Invoke($null, @($op))
    $null = $task.Wait(-1)
    $task.Result
  }
  $langs = @([Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages | ForEach-Object { $_.LanguageTag })
  [void]$sb.AppendLine('##LANGS:' + ($langs -join '|'))
  $engine = $null
  if ($env:MC_OCR_LANG) {
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new($env:MC_OCR_LANG))
  }
  if (-not $engine) { $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }
  if (-not $engine -and $langs.Count -gt 0) {
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new($langs[0]))
  }
  if (-not $engine) {
    [void]$sb.AppendLine('##NOLANG')
  } else {
    [void]$sb.AppendLine('##USED:' + $engine.RecognizerLanguage.LanguageTag)
    foreach ($p in ($env:MC_OCR_IMGS -split '\|')) {
      $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($p)) ([Windows.Storage.StorageFile])
      $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
      $dec = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
      $bmp = Await ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
      $res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
      foreach ($l in $res.Lines) { [void]$sb.AppendLine($l.Text) }
      $stream.Dispose()
    }
  }
} catch {
  [void]$sb.AppendLine('##ERROR:' + $_.Exception.Message)
}
[IO.File]::WriteAllText($env:MC_OCR_OUT, $sb.ToString(), (New-Object System.Text.UTF8Encoding $false))
"""

_CJK = "\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef\u3000-\u303f\uac00-\ud7af"
_CJK_GAP = re.compile(f"(?<=[{_CJK}]) +(?=[{_CJK}])")
OCR_MAX_SIDE = 4000


def tidy_ocr_line(line):
    """Windows OCR puts a space between every Chinese / Japanese character - remove those."""
    return _CJK_GAP.sub("", line.strip())


def _blank_row(img, y):
    lo_hi = img.crop((0, y, img.width, y + 1)).getextrema()
    return lo_hi[0] == lo_hi[1]


def ocr_chunks(img):
    """Upscales small images (better accuracy on small UI text) and splits tall ones into pieces
    the OCR engine accepts, cutting on blank rows where possible so no text line is cut in half."""
    img = img.convert("RGB")
    scale = 2.0 if img.width <= 1800 and img.height <= 6000 else 1.0
    if img.width * scale > OCR_MAX_SIDE:
        scale = OCR_MAX_SIDE / img.width
    if scale != 1.0:
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.LANCZOS)
    gray = img.convert("L")
    out, y0 = [], 0
    while img.height - y0 > OCR_MAX_SIDE:
        cut = y0 + OCR_MAX_SIDE
        for y in range(cut - 1, cut - 400, -1):
            if _blank_row(gray, y):
                cut = y
                break
        out.append(img.crop((0, y0, img.width, cut)))
        y0 = cut
    out.append(img.crop((0, y0, img.width, img.height)) if y0 else img)
    return out


def parse_ocr_output(raw):
    langs, used, err, nolang, lines = [], "", "", False, []
    for line in raw.splitlines():
        if line.startswith("##LANGS:"):
            langs = [x for x in line[8:].split("|") if x]
        elif line.startswith("##USED:"):
            used = line[7:]
        elif line.startswith("##ERROR:"):
            err = line[8:]
        elif line.startswith("##NOLANG"):
            nolang = True
        else:
            lines.append(tidy_ocr_line(line))
    return {"text": "\n".join(lines).strip(), "langs": langs, "used": used, "error": err, "nolang": nolang}


def run_ocr(img, lang=""):
    """Runs Windows OCR on a PIL image. Returns a dict: text, langs, used, error, nolang."""
    if not IS_WIN:
        return {"text": "", "langs": [], "used": "", "error": "Windows only", "nolang": False}
    tmp = tempfile.mkdtemp(prefix="mc_ocr_")
    try:
        paths = []
        for i, part in enumerate(ocr_chunks(img)):
            p = os.path.join(tmp, f"part{i}.png")
            part.save(p, compress_level=1)
            paths.append(p)
        out = os.path.join(tmp, "out.txt")
        env = dict(os.environ, MC_OCR_IMGS="|".join(paths), MC_OCR_OUT=out, MC_OCR_LANG=lang or "")
        ps = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "WindowsPowerShell", "v1.0",
                          "powershell.exe")
        if not os.path.exists(ps):
            ps = "powershell.exe"
        enc = base64.b64encode(_PS_OCR.encode("utf-16-le")).decode("ascii")
        subprocess.run([ps, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-EncodedCommand", enc],
                       env=env, timeout=120, capture_output=True, creationflags=0x08000000)   # CREATE_NO_WINDOW
        if not os.path.exists(out):
            return {"text": "", "langs": [], "used": "", "error": tr("Windows OCR is not available on this computer."),
                    "nolang": False}
        with open(out, encoding="utf-8-sig") as f:
            return parse_ocr_output(f.read())
    except Exception as ex:
        return {"text": "", "langs": [], "used": "", "error": str(ex), "nolang": False}
    finally:
        for name in os.listdir(tmp):
            try:
                os.remove(os.path.join(tmp, name))
            except OSError:
                pass
        try:
            os.rmdir(tmp)
        except OSError:
            pass


class OcrDialog:
    """Shows the recognised text (editable), copies it to the clipboard, lets you switch language."""

    def __init__(self, master, img, lang="", on_lang=None, k=1.0):
        self.master, self.img, self.on_lang = master, img, on_lang
        self.result = None
        w = self.win = tk.Toplevel(master)
        w.title(tr("Text recognition (OCR)"))
        w.configure(bg="white")
        w.geometry(f"{int(560 * k)}x{int(440 * k)}+{master.winfo_rootx() + 120}+{master.winfo_rooty() + 80}")
        w.transient(master)
        top = tk.Frame(w, bg="white")
        top.pack(fill="x", padx=12, pady=(10, 6))
        tk.Label(top, text=tr("Language"), bg="white", font=UI).pack(side="left")
        self.auto = tr("Auto")
        self.lang_var = tk.StringVar(value=lang or self.auto)
        self.lang_cb = ttk.Combobox(top, textvariable=self.lang_var, state="readonly", width=14,
                                    values=[self.auto] + ([lang] if lang else []))
        self.lang_cb.pack(side="left", padx=6)
        self.lang_cb.bind("<<ComboboxSelected>>", lambda e: self._lang_changed())
        _bar_button(top, tr("Close"), w.destroy, bg="#F3F4F6", fg="#111827", hover="#E5E7EB").pack(side="right")
        _bar_button(top, tr("Copy text"), self.copy, bg=ACCENT, fg="white", hover="#1D4ED8").pack(side="right", padx=6)
        fr = tk.Frame(w, bg="white")
        fr.pack(fill="both", expand=True, padx=12)
        sb = ttk.Scrollbar(fr, orient="vertical")
        self.text = tk.Text(fr, wrap="word", font=("Segoe UI", 10), relief="solid", bd=1, padx=6, pady=4,
                            yscrollcommand=sb.set, undo=True)
        sb.configure(command=self.text.yview)
        sb.pack(side="right", fill="y")
        self.text.pack(fill="both", expand=True)
        self.status = tk.Label(w, text="", bg="white", fg="#6B7280", font=("Segoe UI", 8), anchor="w")
        self.status.pack(fill="x", padx=12, pady=(4, 8))
        w.bind("<Escape>", lambda e: w.destroy())
        self.run()

    def _lang_changed(self):
        v = self.lang_var.get()
        lang = "" if v == self.auto else v
        if self.on_lang:
            self.on_lang(lang)
        self.run()

    def run(self):
        v = self.lang_var.get()
        lang = "" if v == self.auto else v
        self.status.configure(text=tr("Recognising text…"))
        self.text.delete("1.0", "end")
        self.result = None
        threading.Thread(target=lambda: setattr(self, "result", run_ocr(self.img, lang)), daemon=True).start()
        self._wait()

    def _wait(self):
        try:
            if not self.win.winfo_exists():
                return
        except tk.TclError:
            return
        if self.result is None:
            self.win.after(120, self._wait)
            return
        r = self.result
        if r["langs"]:
            self.lang_cb.configure(values=[self.auto] + r["langs"])
        if r["error"]:
            self.status.configure(text=tr("OCR failed: {e}", e=r["error"]), fg="#B91C1C")
        elif r["nolang"]:
            self.status.configure(text=tr("No OCR language is installed. Add one in Windows Settings → Time & language → "
                                          "Language & region (a language with “Optical character recognition”)."),
                                  fg="#B91C1C", wraplength=self.win.winfo_width() - 24, justify="left")
        elif not r["text"]:
            self.status.configure(text=tr("No text found."), fg="#6B7280")
        else:
            self.text.insert("1.0", r["text"])
            self.copy(quiet=True)
            self.status.configure(text=tr("{n} lines · language {lang} · copied to the clipboard",
                                          n=r["text"].count("\n") + 1, lang=r["used"]), fg="#15803D")

    def copy(self, quiet=False):
        txt = self.text.get("1.0", "end-1c")
        if not txt.strip():
            return
        self.win.clipboard_clear()
        self.win.clipboard_append(txt)
        if not quiet:
            self.status.configure(text=tr("✓ Text copied"), fg="#15803D")


# =========================================================================== SCROLLING CAPTURE
def row_sigs(img):
    """One signature per pixel row (ignores the right edge, where the scrollbar thumb moves)."""
    g = img.convert("L")
    if g.width > 120:
        g = g.crop((0, 0, g.width - max(16, g.width // 40), g.height))
    cols = min(64, g.width)
    g = g.resize((cols, g.height), Image.BOX).point(lambda v: v >> 3)
    data = g.tobytes()
    sigs, info = [], []
    for y in range(g.height):
        row = data[y * cols:(y + 1) * cols]
        sigs.append(hash(row))
        info.append(row.count(row[0]) < cols)      # False for blank (single-colour) rows
    return sigs, info


def find_shift(prev, cur):
    """How far the content moved up between two frames.
    Returns (d, lo, hi): d = shift in pixels (0 = no change), rows lo..hi are the part that scrolls
    (rows above lo / below hi stay fixed, e.g. a sticky header or footer). None if no match."""
    ps, pi = prev
    cs, ci = cur
    n = min(len(ps), len(cs))
    top = 0
    while top < n and ps[top] == cs[top]:
        top += 1
    if top == n:
        return 0, 0, n
    bot = 0
    while bot < n - top and ps[n - 1 - bot] == cs[n - 1 - bot]:
        bot += 1
    lo, hi = top, n - bot
    # Vote with row *transitions* (row j differs from row j-1): far more distinctive than single rows,
    # because a line of text or a flat block repeats the same row many times.
    pos = {}
    for j in range(lo + 1, hi):
        if cs[j] != cs[j - 1] and (ci[j] or ci[j - 1]):
            pos.setdefault((cs[j - 1], cs[j]), []).append(j)
    votes = {}
    for i in range(lo + 1, hi):
        if ps[i] == ps[i - 1] or not (pi[i] or pi[i - 1]):
            continue
        js = pos.get((ps[i - 1], ps[i]))
        if not js or len(js) > 8:
            continue
        for j in js:
            d = i - j
            if d > 0:
                votes[d] = votes.get(d, 0) + 1
    m = hi - lo
    for d in sorted(votes, key=lambda x: (-votes[x], x))[:6]:
        if m - d < max(6, m // 12):
            continue
        tot = ok = 0
        for j in range(lo, hi - d):
            if ci[j] or pi[j + d]:
                tot += 1
                ok += cs[j] == ps[j + d]
        if tot >= 4 and ok >= 0.85 * tot:
            return d, lo, hi
    return None


class Stitcher:
    """Builds one tall image from frames of a region that scrolls downwards."""

    def __init__(self, first, max_h=20000):
        self.w = first.width
        self.strips = [first]
        self.last, self.last_sig = first, row_sigs(first)
        self.done = first.height      # rows of the last frame already in the result
        self.height = first.height
        self.matched = False
        self.max_h = max_h

    def add(self, img):
        """Returns 'same', 'added', 'lost' (no overlap found - scroll back / slower) or 'full'."""
        sig = row_sigs(img)
        r = find_shift(self.last_sig, sig)
        if r is None:
            return "lost"
        d, lo, hi = r
        if d == 0:
            return "same"
        if not self.matched:          # now we know where the fixed footer starts
            self.matched = True
            self.strips[0] = self.strips[0].crop((0, 0, self.w, hi))
            self.done = self.height = hi
        start = max(lo, self.done - d)
        end = max(hi, start)
        if end > start:
            self.strips.append(img.crop((0, start, self.w, end)))
            self.height += end - start
        self.done = end
        self.last, self.last_sig = img, sig
        return "full" if self.height >= self.max_h else "added"

    def result(self):
        parts = list(self.strips)
        if self.matched and self.done < self.last.height:
            parts.append(self.last.crop((0, self.done, self.w, self.last.height)))
        h = sum(p.height for p in parts)
        out = Image.new("RGB", (self.w, h))
        y = 0
        for p in parts:
            out.paste(p, (0, y))
            y += p.height
        return out


class ScrollCapture:
    """Grabs a region repeatedly while it scrolls (auto-scroll or by hand) and stitches the frames."""

    def __init__(self, master, box, on_done, auto=True):
        self.master, self.box, self.on_done = master, box, on_done
        self.auto, self.gen, self.closed = auto, 0, False
        self.same = 0
        self.stitch = None
        self.frame = RegionFrame(master, box, ACCENT)
        self.bar = FloatBar(master, box, [("auto", "", self.toggle_auto), ("done", "✓  " + tr("Done"), self.finish),
                                          ("cancel", "✕  " + tr("Cancel"), self.cancel)])
        self._auto_label()
        self.bar.set(tr("Starting…"))
        esc_pressed()
        master.after(300, self._start)

    def _auto_label(self):
        self.bar.buttons["auto"].configure(text=("⏸  " + tr("Pause")) if self.auto else ("▶  " + tr("Auto-scroll")))

    def _start(self):
        if self.closed:
            return
        try:
            self.stitch = Stitcher(grab_box(self.box))
        except Exception as ex:
            self._close()
            self.on_done(None, str(ex))
            return
        self._loop()

    def toggle_auto(self):
        self.auto = not self.auto
        self.same = 0
        self._auto_label()
        self._loop()

    def _loop(self):
        self.gen += 1
        g = self.gen
        if self.auto:
            h = self.box[3] - self.box[1]
            send_wheel(self.box, max(1, min(5, h // 260)))
            self.master.after(380, lambda: self._step(g))
        else:
            self.master.after(150, lambda: self._step(g))

    def _step(self, g):
        if self.closed or g != self.gen:
            return
        if esc_pressed():
            self.finish()
            return
        try:
            r = self.stitch.add(grab_box(self.box))
        except Exception:
            r = "lost"
        h = self.stitch.height
        if r == "full":
            self.finish()
            return
        if r == "lost":
            self.bar.set(tr("⚠ Lost track – scroll back up a little, then more slowly"))
        elif r == "same":
            self.same += 1
            if self.auto and self.same >= 3:      # nothing moves any more: end of the page
                self.finish()
                return
            self.bar.set(tr("{h} px  ·  scroll down (by hand or Auto-scroll)  ·  Esc = done", h=h))
        else:
            self.same = 0
            self.bar.set(tr("{h} px  ·  scroll down (by hand or Auto-scroll)  ·  Esc = done", h=h))
        self._loop()

    def _close(self):
        self.closed = True
        self.frame.destroy()
        self.bar.destroy()

    def finish(self):
        if self.closed:
            return
        self._close()
        self.on_done(self.stitch.result() if self.stitch else None, None)

    def cancel(self):
        if self.closed:
            return
        self._close()
        self.on_done(None, None)


# =========================================================================== SCREEN RECORDING (GIF)
REC_MAX_SECONDS = 60
REC_MAX_SIDE = 1280
REC_PIXEL_BUDGET = 300_000_000   # frames x pixels kept in memory (about 300 MB while saving the GIF)


class Recording:
    def __init__(self, size):
        self.size = size
        self.frames = []     # zlib-compressed RGB bytes, consecutive duplicates removed
        self.times = []      # start time of each frame (s)
        self.end = 0.0
        self.limit_hit = False

    def durations(self):
        ts = self.times + [self.end]
        return [max(20, int(round((ts[i + 1] - ts[i]) * 1000))) for i in range(len(self.frames))]

    def images(self):
        for d in self.frames:
            yield Image.frombytes("RGB", self.size, zlib.decompress(d))


def save_gif(rec, path, progress=None):
    n = len(rec.frames)
    durs = rec.durations()
    it = rec.images()
    first = next(it)

    def rest():
        for i, im in enumerate(it, 2):
            if progress:
                progress(int(i * 100 / n))
            yield im
    first.save(path, save_all=True, append_images=rest(), duration=durs, loop=0, optimize=False)


class GifRecorder:
    def __init__(self, master, box, on_done, fps=10, k=1.0):
        self.master, self.box, self.on_done = master, box, on_done
        self.fps = max(1, min(30, int(fps)))
        self.k = k
        l, t, r, b = box
        w, h = r - l, b - t
        self.scale = min(1.0, REC_MAX_SIDE / max(w, h))
        self.rec = Recording((max(1, int(w * self.scale)), max(1, int(h * self.scale))))
        self.stop_ev = threading.Event()
        self.cancelled = False
        self.closed = False
        self.frame = RegionFrame(master, box, REC_RED)
        self.bar = FloatBar(master, box, [("stop", "■  " + tr("Stop"), self.stop),
                                          ("cancel", "✕  " + tr("Cancel"), self.cancel)], dot=REC_RED)
        self.bar.set("0:00")
        esc_pressed()
        self.t0 = time.perf_counter()
        self.th = threading.Thread(target=self._run, daemon=True)
        self.th.start()
        self._tick()

    def _run(self):
        rec, box, l, t = self.rec, self.box, self.box[0], self.box[1]
        interval = 1.0 / self.fps
        nxt = time.perf_counter()
        last = None
        px = rec.size[0] * rec.size[1]
        while not self.stop_ev.is_set():
            now = time.perf_counter()
            if now - self.t0 > REC_MAX_SECONDS or (len(rec.frames) + 1) * px > REC_PIXEL_BUDGET:
                rec.limit_hit = True
                break
            try:
                im = grab_box(box)
            except Exception:
                im = None
            if im is not None:
                cur = cursor_pos()
                if cur and l <= cur[0] < box[2] and t <= cur[1] < box[3]:
                    draw_cursor(im, cur[0] - l, cur[1] - t, self.k)
                if self.scale < 1:
                    im = im.resize(rec.size, Image.BILINEAR)
                data = zlib.compress(im.tobytes(), 1)
                if data != last:
                    rec.frames.append(data)
                    rec.times.append(now - self.t0)
                    last = data
            nxt += interval
            time.sleep(max(0.0, nxt - time.perf_counter()))
        rec.end = time.perf_counter() - self.t0

    def _tick(self):
        if self.closed:
            return
        if esc_pressed():
            self.stop()
            return
        if not self.th.is_alive():          # length / memory limit reached
            self.stop()
            return
        s = int(time.perf_counter() - self.t0)
        self.bar.set(f"{s // 60}:{s % 60:02d}  ·  " + tr("Esc or Stop to finish"))
        self.master.after(250, self._tick)

    def _finish(self, cancelled):
        if self.closed:
            return
        self.closed = True
        self.stop_ev.set()
        self.th.join(timeout=3)
        self.frame.destroy()
        self.bar.destroy()
        self.on_done(None if cancelled or not self.rec.frames else self.rec)

    def stop(self):
        self._finish(False)

    def cancel(self):
        self._finish(True)
