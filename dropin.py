# -*- coding: utf-8 -*-
"""Images brought in from outside the app (drag & drop from Explorer or a browser, Ctrl+V), and the
pictures placed on top of a screenshot as a movable layer ("overlay" annotations).

Kept free of tkinter so it can be unit-tested anywhere. The drop target itself (tkinterdnd2) is
optional: when it is missing the rest of the app works as before, only dropping is unavailable."""
import base64
import hashlib
import io
import os
import re
import threading
import urllib.parse
import urllib.request

from PIL import Image

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".jpe", ".jfif", ".bmp", ".dib", ".gif", ".tif", ".tiff", ".webp", ".ico"}
MAX_DOWNLOAD = 40 * 1024 * 1024        # bytes, for an image dragged from a web page
MAX_SIDE = 12000                       # refuse absurd images (decompression bombs)

try:                                   # Windows OLE drag & drop for Tk; bundled by PyInstaller's own hook
    from tkinterdnd2 import DND_FILES, DND_TEXT, TkinterDnD
except Exception:                      # not installed: dropping is simply not offered
    TkinterDnD = DND_FILES = DND_TEXT = None


def enable_dnd(root):
    """Load the tkdnd extension into an existing Tk root. True when drag & drop is available."""
    if TkinterDnD is None:
        return False
    try:
        TkinterDnD._require(root)
        return True
    except Exception as ex:
        print("drag & drop unavailable:", ex)
        return False


def register(widget, callback):
    """Make widget accept dropped files and links; callback(items, x_root, y_root)."""
    def on_drop(e):
        items = [str(e.data)]
        if getattr(e, "type", "") == DND_FILES:      # a Tcl list: {C:/with space/a.png} C:/b.png
            try:
                items = list(widget.tk.splitlist(e.data))
            except Exception:
                pass
        callback(items, e.x_root, e.y_root)
        return e.action
    # files first (Explorer, Firefox), then the HTML of a web page (the <img> of a picture dragged
    # from Chrome / Edge), then a plain link
    widget.drop_target_register(DND_FILES, "DND_HTML", "DND_URL", DND_TEXT)
    widget.dnd_bind("<<Drop>>", on_drop)


# --------------------------------------------------------------------------- what was dropped
def split_text(text):
    """A dropped text can hold several links / paths, one per line."""
    out = []
    for line in str(text).replace("\r", "\n").split("\n"):
        line = line.strip().strip('"')
        if line:
            out.append(line)
    return out


def html_images(html):
    """Picture addresses in an HTML fragment (CF_HTML from a browser), made absolute."""
    m = re.search(r"SourceURL:(\S+)", html)
    base = m.group(1) if m else ""
    out = []
    for src in re.findall(r"<img\b[^>]*?\ssrc\s*=\s*[\"']([^\"']+)[\"']", html, re.I | re.S):
        src = src.replace("&amp;", "&").strip()
        if src.startswith("//"):
            src = "https:" + src
        elif base and not re.match(r"(?:https?|data|file):", src, re.I):
            src = urllib.parse.urljoin(base, src)
        out.append(src)
    return out


def expand(items):
    """Dropped data -> list of single paths / links."""
    flat = []
    for it in items:
        it = str(it)
        if re.search(r"<img\b", it, re.I):
            flat += html_images(it)
        elif "\n" in it:
            flat += split_text(it)
        else:
            flat.append(it)
    return flat


def classify(item):
    """('file', path) | ('url', url) | ('data', bytes) | (None, item)."""
    s = str(item).strip().strip('"')
    if s.lower().startswith("data:image/"):
        m = re.match(r"data:image/[\w.+-]+;base64,(.*)", s, re.S | re.I)
        if m:
            try:
                return "data", base64.b64decode(m.group(1))
            except Exception:
                pass
        return None, s
    if s.lower().startswith("file:"):
        p = urllib.parse.urlparse(s)
        path = urllib.request.url2pathname(p.path)
        if p.netloc and p.netloc.lower() != "localhost":
            path = "\\\\" + p.netloc + path        # file://server/share/...
        return "file", path
    if re.match(r"https?://", s, re.I):
        return "url", s
    if os.path.isfile(s):
        return "file", s
    return None, s


def is_image_path(p):
    return os.path.splitext(p)[1].lower() in IMAGE_EXTS


def open_image(data_or_path):
    """Open, check size and convert to RGBA (keeps transparency for overlays)."""
    src = io.BytesIO(data_or_path) if isinstance(data_or_path, (bytes, bytearray)) else data_or_path
    with Image.open(src) as im:
        if im.width > MAX_SIDE or im.height > MAX_SIDE or im.width < 1 or im.height < 1:
            raise ValueError(f"{im.width} × {im.height}")
        try:
            im.seek(0)                           # first frame of a GIF / multi-page TIFF
        except EOFError:
            pass
        return im.convert("RGBA")


def download(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise ValueError("too large")
    return data


def load_items(items, on_done):
    """Turn dropped items into images in a worker thread. on_done(images, errors) runs in that thread,
    so the caller passes it back to the Tk thread (e.g. through a queue)."""
    flat = expand(items)

    def work():
        images, errors = [], []
        seen = set()
        for it in flat:
            kind, v = classify(it)
            key = v if kind != "data" else hashlib.sha1(v).hexdigest()
            if kind is None or key in seen:
                continue
            seen.add(key)
            try:
                if kind == "file":
                    if os.path.isdir(v):
                        continue
                    images.append((os.path.basename(v), open_image(v)))
                elif kind == "url":
                    name = os.path.basename(urllib.parse.urlparse(v).path) or "image"
                    images.append((name, open_image(download(v))))
                else:
                    images.append(("image", open_image(v)))
            except Exception as ex:
                errors.append((os.path.basename(str(v))[:60] if kind != "data" else "image", str(ex)[:120]))
        on_done(images, errors)
    t = threading.Thread(target=work, daemon=True)
    t.start()
    return t


def from_clipboard(grab):
    """grab = ImageGrab.grabclipboard result: an image, a list of file paths, or None."""
    if grab is None:
        return [], []
    if isinstance(grab, Image.Image):
        return [("clipboard", grab.convert("RGBA"))], []
    images, errors = [], []
    for p in grab if isinstance(grab, (list, tuple)) else []:
        try:
            images.append((os.path.basename(p), open_image(p)))
        except Exception as ex:
            errors.append((os.path.basename(p), str(ex)[:120]))
    return images, errors


# --------------------------------------------------------------------------- overlay pictures
class OverlayStore:
    """Pictures used by "image" annotations, by content hash. Kept as PNG files next to the session
    (so undo snapshots and the metadata only carry the short key) and cached in memory."""

    def __init__(self):
        self.folder = None
        self.mem = {}
        self._scaled = {}

    def set_folder(self, folder):
        """Where the picture files go (None: memory only). Pictures added meanwhile are written now."""
        self.folder = folder
        if folder:
            for im in list(self.mem.values()):
                self.put(im)

    def _path(self, key):
        return os.path.join(self.folder, key + ".png") if self.folder else None

    def put(self, img):
        img = img.convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, "PNG", compress_level=3)
        data = buf.getvalue()
        key = hashlib.sha1(data).hexdigest()[:20]
        self.mem[key] = img
        p = self._path(key)
        if p and not os.path.exists(p):
            try:
                os.makedirs(self.folder, exist_ok=True)
                with open(p + ".tmp", "wb") as f:
                    f.write(data)
                os.replace(p + ".tmp", p)
            except OSError as ex:
                print("overlay save", ex)
        return key

    def get(self, key):
        im = self.mem.get(key)
        if im is None:
            p = self._path(key)
            if p and os.path.exists(p):
                try:
                    with Image.open(p) as f:
                        im = f.convert("RGBA")
                    self.mem[key] = im
                except Exception as ex:
                    print("overlay load", key, ex)
        return im

    def scaled(self, key, size, box, alpha):
        """The visible part `box` (in source pixels) of picture `key` resized to `size`, with opacity."""
        k = (key, size, tuple(round(v, 2) for v in box), alpha)
        im = self._scaled.get(k)
        if im is None:
            src = self.get(key)
            if src is None:
                return None
            im = src.resize(size, Image.LANCZOS if size[0] < box[2] - box[0] else Image.BICUBIC, box=box)
            if alpha < 100:
                a = im.getchannel("A").point(lambda v: v * alpha // 100)
                im.putalpha(a)
            if len(self._scaled) > 24:
                self._scaled.clear()
            self._scaled[k] = im
        return im

    def cleanup(self, used):
        """Remove picture files no annotation refers to any more."""
        if not self.folder or not os.path.isdir(self.folder):
            return
        for fn in os.listdir(self.folder):
            key = fn.split(".")[0]
            if key not in used:
                try:
                    os.remove(os.path.join(self.folder, fn))
                except OSError:
                    pass
                self.mem.pop(key, None)


OVERLAYS = OverlayStore()


def overlay_keys(items):
    return {o.get("src") for it in items for o in it.get("objs", []) if o.get("type") == "image"}


def fit_box(img_w, img_h, base_w, base_h, cx, cy, frac=0.45):
    """Initial place of a picture laid over a screenshot: at most `frac` of the screenshot, never
    enlarged, centred on (cx, cy) and kept inside the screenshot."""
    k = min(1.0, frac * base_w / img_w, frac * base_h / img_h)
    w, h = max(8.0, img_w * k), max(8.0, img_h * k)
    x0 = min(max(0.0, cx - w / 2), max(0.0, base_w - w))
    y0 = min(max(0.0, cy - h / 2), max(0.0, base_h - h))
    return [x0, y0, x0 + w, y0 + h]


def keep_ratio(box, i, x, y, ratio):
    """Move corner i (0 tl, 1 tr, 2 br, 3 bl) of box towards (x, y) keeping width / height = ratio,
    with the opposite corner fixed. The box never flips over its fixed corner."""
    x0, y0, x1, y1 = box
    ax, ay = [(x1, y1), (x0, y1), (x0, y0), (x1, y0)][i]
    sx, sy = [(-1, -1), (1, -1), (1, 1), (-1, 1)][i]
    w, h = max(0.0, sx * (x - ax)), max(0.0, sy * (y - ay))
    if w / max(h, 1e-6) > ratio:
        h = w / ratio
    else:
        w = h * ratio
    if w < 8:
        w, h = 8.0, 8.0 / ratio
    bx, by = ax + sx * w, ay + sy * h
    return [min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)]
