# -*- coding: utf-8 -*-
"""
Before / after comparison of two screenshots:

* a slider view - both images on top of each other, drag the divider to reveal one or the other
* a side-by-side view with one shared zoom and pan
* automatic difference highlighting: changed pixels are tinted and every changed area gets a red box

The pixel code (diff_mask, diff_boxes, highlight, side_by_side) is pure Pillow so it can be tested on
any platform. Images of different sizes are aligned at the top-left corner and only the overlapping
part is compared.
"""
import math
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageTk

from i18n import tr

DIFF_RGB = (229, 57, 53)        # red of the boxes and of the tint
PAD_RGB = (200, 205, 213)       # fills the empty part when the two images differ in size
DEFAULT_TOLERANCE = 16


# --------------------------------------------------------------------------- pixel code
def diff_mask(a, b, tolerance=DEFAULT_TOLERANCE):
    """'L' mask of the overlapping top-left area: 255 where a pixel changed by more than `tolerance`
    (0-255, largest of the R, G, B differences), else 0."""
    w, h = min(a.width, b.width), min(a.height, b.height)
    if w <= 0 or h <= 0:
        return Image.new("L", (max(w, 0), max(h, 0)))
    a = a.convert("RGB").crop((0, 0, w, h))
    b = b.convert("RGB").crop((0, 0, w, h))
    r, g, bl = ImageChops.difference(a, b).split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), bl)
    t = max(0, min(254, int(tolerance)))
    return m.point([0] * (t + 1) + [255] * (255 - t))


def diff_boxes(mask, min_pixels=3, max_boxes=300):
    """Bounding boxes [x0, y0, x1, y1] (x1/y1 exclusive) of the changed areas of a diff mask.
    Changes closer than a few pixels are joined into one box. Largest boxes first."""
    w, h = mask.size
    if w == 0 or h == 0 or not mask.getbbox():
        return []
    bs = min(12, max(2, math.ceil(max(w, h) / 320)))          # grid cell size in pixels
    gw, gh = math.ceil(w / bs), math.ceil(h / bs)
    small = mask.resize((gw, gh), Image.BOX).point(lambda v: 255 if v else 0)
    small = small.filter(ImageFilter.MaxFilter(3))             # join changes one cell apart
    data = small.tobytes()
    seen = bytearray(gw * gh)
    boxes = []
    for start in range(gw * gh):
        if not data[start] or seen[start]:
            continue
        seen[start] = 1
        stack = [start]
        x0 = x1 = start % gw
        y0 = y1 = start // gw
        while stack:
            i = stack.pop()
            cx, cy = i % gw, i // gw
            x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
            for nx in (cx - 1, cx, cx + 1):
                if nx < 0 or nx >= gw:
                    continue
                for ny in (cy - 1, cy, cy + 1):
                    if 0 <= ny < gh:
                        j = ny * gw + nx
                        if data[j] and not seen[j]:
                            seen[j] = 1
                            stack.append(j)
        bx = (x0 * bs, y0 * bs, min(w, (x1 + 1) * bs), min(h, (y1 + 1) * bs))
        part = mask.crop(bx)
        tight = part.getbbox()
        if not tight or part.histogram()[255] < min_pixels:
            continue
        boxes.append([bx[0] + tight[0], bx[1] + tight[1], bx[0] + tight[2], bx[1] + tight[3]])
    boxes = _merge(boxes, gap=bs)
    boxes.sort(key=lambda b: -(b[2] - b[0]) * (b[3] - b[1]))
    return boxes[:max_boxes]


def _merge(boxes, gap=0):
    """Joins boxes that overlap or are less than `gap` pixels apart."""
    boxes = [list(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        out = []
        for b in boxes:
            for o in out:
                if b[0] <= o[2] + gap and o[0] <= b[2] + gap and b[1] <= o[3] + gap and o[1] <= b[3] + gap:
                    o[0], o[1], o[2], o[3] = min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3])
                    changed = True
                    break
            else:
                out.append(b)
        boxes = out
    return boxes


def highlight(img, mask, boxes, tint=110, width=None):
    """Copy of `img` with the changed pixels tinted red and a red box around every changed area."""
    out = img.convert("RGB").copy()
    if mask is not None and mask.getbbox():
        red = Image.new("RGB", mask.size, DIFF_RGB)
        region = out.crop((0, 0) + mask.size)
        tinted = Image.blend(region, red, tint / 255)
        region.paste(tinted, (0, 0), mask)
        out.paste(region, (0, 0))
    if boxes:
        lw = width or max(2, round(max(out.size) / 500))
        pad = lw + 2
        d = ImageDraw.Draw(out)
        for x0, y0, x1, y1 in boxes:
            d.rectangle((max(0, x0 - pad), max(0, y0 - pad), min(out.width - 1, x1 + pad - 1),
                         min(out.height - 1, y1 + pad - 1)), outline=DIFF_RGB, width=lw)
    return out


def pad_to(img, size):
    if img.size == tuple(size):
        return img
    out = Image.new("RGB", size, PAD_RGB)
    out.paste(img, (0, 0))
    return out


def side_by_side(a, b, gap=16, bg=(255, 255, 255)):
    w, h = a.width + gap + b.width, max(a.height, b.height)
    out = Image.new("RGB", (w, h), bg)
    out.paste(a, (0, 0))
    out.paste(b, (a.width + gap, 0))
    return out


def _rgb(color, default=(230, 230, 230)):
    try:
        return ImageColor.getrgb(color)[:3]
    except (ValueError, TypeError):
        return default


def compare(a, b, tolerance=DEFAULT_TOLERANCE):
    """(mask, boxes) of the differences between a and b."""
    m = diff_mask(a, b, tolerance)
    return m, diff_boxes(m)


# --------------------------------------------------------------------------- window
class CompareWindow:
    """Compares two screenshots of the app. `app` provides items, img_of(it), copy and marking."""
    GAP = 16

    def __init__(self, app, a, b, pal):
        self.app, self.pal = app, pal
        self.a, self.b = a, b
        self.mode = tk.StringVar(value=app.st.get("cmp_mode", "slider"))
        self.hl = tk.BooleanVar(value=app.st.get("cmp_highlight", True))
        self.tol = tk.IntVar(value=int(app.st.get("cmp_tolerance", DEFAULT_TOLERANCE)))
        self.auto = tk.BooleanVar(value=app.st.get("cmp_after_recapture", True))
        self.split = 0.5
        self.s, self.vx, self.vy, self.fit = 1.0, 0.0, 0.0, True
        self._pan = None
        self._job = None
        self.boxes, self.mask = [], None
        self.ia = self.ib = None        # full-size images shown (highlighted if switched on)

        w = self.win = tk.Toplevel(app.root)
        w.title(tr("Compare screenshots"))
        w.configure(bg=pal["panel"])
        w.geometry(app.st.get("cmp_geometry", "1100x720"))
        w.minsize(640, 420)
        w.protocol("WM_DELETE_WINDOW", self.close)

        top = tk.Frame(w, bg=pal["panel"])
        top.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(top, text=tr("Before"), bg=pal["panel"], fg=pal["muted"]).pack(side="left")
        self.cb_a = ttk.Combobox(top, state="readonly", width=24)
        self.cb_a.pack(side="left", padx=(4, 4))
        ttk.Button(top, text="⇄", width=3, command=self.swap).pack(side="left")
        tk.Label(top, text=tr("After"), bg=pal["panel"], fg=pal["muted"]).pack(side="left", padx=(4, 0))
        self.cb_b = ttk.Combobox(top, state="readonly", width=24)
        self.cb_b.pack(side="left", padx=(4, 12))
        for cb in (self.cb_a, self.cb_b):
            cb.bind("<<ComboboxSelected>>", self._picked)
        for val, txt in (("slider", tr("Slider")), ("side", tr("Side by side"))):
            ttk.Radiobutton(top, text=txt, value=val, variable=self.mode, command=self._mode_changed).pack(side="left")
        top2 = tk.Frame(w, bg=pal["panel"])
        top2.pack(fill="x", padx=10, pady=(0, 6))
        ttk.Checkbutton(top2, text=tr("Highlight differences"), variable=self.hl,
                        command=self._settings_changed).pack(side="left", padx=(0, 4))
        tk.Label(top2, text=tr("Tolerance"), bg=pal["panel"], fg=pal["muted"]).pack(side="left", padx=(6, 2))
        sc = ttk.Scale(top2, from_=0, to=120, orient="horizontal", length=110,
                       command=lambda v: (self.tol.set(int(float(v))), self._debounce()))
        sc.set(self.tol.get())
        sc.pack(side="left")
        self.tol_lbl = tk.Label(top2, textvariable=self.tol, bg=pal["panel"], fg=pal["text"], width=3)
        self.tol_lbl.pack(side="left")
        ttk.Checkbutton(top2, text=tr("Open after each recapture"), variable=self.auto,
                        command=self._settings_changed).pack(side="right")

        bot = tk.Frame(w, bg=pal["panel"])
        bot.pack(fill="x", side="bottom", padx=10, pady=(2, 8))
        self.info = tk.Label(w, text="", bg=pal["panel"], fg=pal["text"], anchor="w", justify="left")
        self.info.pack(fill="x", side="bottom", padx=10, pady=(6, 0))
        tk.Label(bot, text=tr("Wheel: zoom · middle/right-drag: pan · double-click: fit"), bg=pal["panel"],
                 fg=pal["muted"], anchor="w").pack(side="left")
        ttk.Button(bot, text=tr("Close"), command=self.close).pack(side="right")
        ttk.Button(bot, text=tr("Copy comparison"), command=self.copy).pack(side="right", padx=4)
        ttk.Button(bot, text=tr("Mark differences on 'After'"), command=self.mark).pack(side="right", padx=4)

        self.c = tk.Canvas(w, bg=pal["canvas"], highlightthickness=0)
        self.c.pack(fill="both", expand=True)
        c = self.c
        c.bind("<Configure>", lambda e: self.render())
        c.bind("<ButtonPress-1>", self._press)
        c.bind("<B1-Motion>", self._drag)
        c.bind("<ButtonRelease-1>", lambda e: setattr(self, "_pan", None))
        for btn in ("2", "3"):
            c.bind(f"<ButtonPress-{btn}>", lambda e: setattr(self, "_pan", (e.x, e.y)))
            c.bind(f"<B{btn}-Motion>", self._pan_move)
        c.bind("<Double-Button-1>", lambda e: self.zoom_fit())
        c.bind("<MouseWheel>", self._wheel)
        c.bind("<Button-4>", lambda e: self.zoom_at(1.15, e.x, e.y))
        c.bind("<Button-5>", lambda e: self.zoom_at(1 / 1.15, e.x, e.y))
        w.bind("<Escape>", lambda e: self.close())
        w.bind("<Key>", self._key)
        self.set_pair(a, b)
        w.after(50, w.focus_force)

    # ---------------------------------------------------------------- data
    def _label(self, it):
        return f"#{it['num']}   {it['time']:%d/%m %H:%M:%S}   {it['size'][0]}×{it['size'][1]}"

    def _fill_lists(self):
        self._list = list(self.app.items)
        vals = [self._label(i) for i in self._list]
        for cb, it in ((self.cb_a, self.a), (self.cb_b, self.b)):
            cb.configure(values=vals)
            cb.set(self._label(it))

    def _picked(self, e=None):
        try:
            self.a = self._list[self.cb_a.current()]
            self.b = self._list[self.cb_b.current()]
        except (IndexError, TypeError):
            return
        self.fit = True
        self.recompute()
        self.c.focus_set()

    def set_pair(self, a, b):
        self.a, self.b = a, b
        self.fit = True
        self._fill_lists()
        self.recompute()
        self.show()

    def item_removed(self, it):
        """Called by the app when a screenshot is deleted."""
        if it is self.a or it is self.b:
            self.close()
        else:
            self._fill_lists()

    def swap(self):
        self.a, self.b = self.b, self.a
        self._fill_lists()
        self.recompute()

    def recompute(self):
        A, B = self.app.img_of(self.a), self.app.img_of(self.b)
        size = (max(A.width, B.width), max(A.height, B.height))
        if self.hl.get():
            self.mask, self.boxes = compare(A, B, self.tol.get())
            A2, B2 = highlight(A, self.mask, self.boxes), highlight(B, self.mask, self.boxes)
        else:
            self.mask, self.boxes = None, []
            A2, B2 = A.convert("RGB"), B.convert("RGB")
        if self.mode.get() == "slider":
            self.ia, self.ib = pad_to(A2, size), pad_to(B2, size)
            self.scene = None
        else:
            self.ia, self.ib = A2, B2
            self.scene = side_by_side(A2, B2, self.GAP, _rgb(self.pal["canvas"]))
        self._info(A, B)
        self.render()

    def _info(self, A, B):
        parts = [tr("#{a} → #{b}", a=self.a["num"], b=self.b["num"])]
        if self.hl.get():
            n = len(self.boxes)
            if n == 0:
                parts.append(tr("No differences found"))
            else:
                px = self.mask.histogram()[255] if self.mask else 0
                parts.append(tr("{n} changed area(s), {p} pixels", n=n, p=f"{px:,}"))
        if A.size != B.size:
            parts.append(tr("Sizes differ ({a} vs {b}) - only the overlapping top-left part is compared",
                            a=f"{A.width}×{A.height}", b=f"{B.width}×{B.height}"))
        self.info.configure(text="   ·   ".join(parts))

    def _settings_changed(self):
        st = self.app.st
        st["cmp_mode"], st["cmp_highlight"] = self.mode.get(), self.hl.get()
        st["cmp_tolerance"], st["cmp_after_recapture"] = self.tol.get(), self.auto.get()
        self.recompute()

    def _mode_changed(self):
        self.fit = True
        self._settings_changed()

    def _debounce(self):
        if self._job:
            self.win.after_cancel(self._job)
        self._job = self.win.after(250, self._settings_changed)

    # ---------------------------------------------------------------- view
    def content_size(self):
        if self.scene is not None:
            return self.scene.size
        return self.ia.size if self.ia else (1, 1)

    def to_img(self, x, y):
        return x / self.s + self.vx, y / self.s + self.vy

    def _crop(self, img, ox, cw, ch):
        """Visible part of `img` (placed at content x = ox) resized to the zoom; returns (image, canvas x, y)."""
        s = self.s
        x0, y0 = max(0, math.floor(self.vx - ox)), max(0, math.floor(self.vy))
        x1, y1 = min(img.width, math.ceil(self.vx - ox + cw / s)), min(img.height, math.ceil(self.vy + ch / s))
        if x1 <= x0 or y1 <= y0:
            return None, 0, 0
        crop = img.crop((x0, y0, x1, y1))
        dw, dh = max(1, round((x1 - x0) * s)), max(1, round((y1 - y0) * s))
        if (dw, dh) != crop.size:
            crop = crop.resize((dw, dh), Image.LANCZOS if s < 1 else (Image.NEAREST if s >= 3 else Image.BICUBIC))
        return crop, (x0 + ox - self.vx) * s, (y0 - self.vy) * s

    def render(self):
        c = self.c
        c.delete("all")
        if self.ia is None:
            return
        cw, ch = max(c.winfo_width(), 50), max(c.winfo_height(), 50)
        W, H = self.content_size()
        if self.fit:
            self.s = max(0.02, min((cw - 32) / W, (ch - 32) / H, 1.0))
            self.vx, self.vy = -(cw / self.s - W) / 2, -(ch / self.s - H) / 2
        s = self.s
        self._photos = []
        if self.scene is not None:
            im, x, y = self._crop(self.scene, 0, cw, ch)
            if im is not None:
                self._photos.append(ImageTk.PhotoImage(im))
                c.create_image(x, y, anchor="nw", image=self._photos[-1])
            for txt, ox in ((tr("Before") + f"  #{self.a['num']}", 0),
                            (tr("After") + f"  #{self.b['num']}", self.ia.width + self.GAP)):
                self._tag(txt, (ox - self.vx) * s + 6, max(6, -self.vy * s + 6))
            return
        im, x, y = self._crop(self.ia, 0, cw, ch)
        if im is None:
            return
        dx = (W * self.split - self.vx) * s           # divider position on the canvas
        imb, _, _ = self._crop(self.ib, 0, cw, ch)
        cut = int(round(dx - x))
        if 0 < cut < im.width:
            im = im.copy()
            im.paste(imb.crop((cut, 0, imb.width, imb.height)), (cut, 0))
        elif cut <= 0:
            im = imb
        self._photos.append(ImageTk.PhotoImage(im))
        c.create_image(x, y, anchor="nw", image=self._photos[-1])
        top, bot = max(0, y), min(ch, y + im.height)
        c.create_line(dx, top, dx, bot, fill="white", width=3)
        c.create_line(dx, top, dx, bot, fill=self.pal["accent"], width=1)
        my = (top + bot) / 2
        c.create_oval(dx - 14, my - 14, dx + 14, my + 14, fill=self.pal["accent"], outline="white", width=2)
        c.create_text(dx, my, text="◀▶", fill="white", font=("Segoe UI", 8, "bold"))
        self._tag(tr("Before") + f"  #{self.a['num']}", max(x, 0) + 6, top + 6)
        self._tag(tr("After") + f"  #{self.b['num']}", min(x + im.width, cw) - 6, top + 6, anchor="ne")

    def _tag(self, text, x, y, anchor="nw"):
        t = self.c.create_text(x + (6 if anchor == "nw" else -6), y + 4, text=text, anchor=anchor, fill="white",
                               font=("Segoe UI Semibold", 9))
        bb = self.c.bbox(t)
        r = self.c.create_rectangle(bb[0] - 6, bb[1] - 3, bb[2] + 6, bb[3] + 3, fill="#111827", outline="")
        self.c.tag_raise(t, r)

    def zoom_at(self, f, cx=None, cy=None):
        if cx is None:
            cx, cy = self.c.winfo_width() / 2, self.c.winfo_height() / 2
        x, y = self.to_img(cx, cy)
        self.s = min(16.0, max(0.02, self.s * f))
        self.fit = False
        self.vx, self.vy = x - cx / self.s, y - cy / self.s
        self.render()

    def zoom_fit(self):
        self.fit = True
        self.render()

    def _wheel(self, e):
        self.zoom_at(1.15 if e.delta > 0 else 1 / 1.15, e.x, e.y)

    def _press(self, e):
        if self.scene is None:
            self._set_split(e.x)
        else:
            self._pan = (e.x, e.y)

    def _drag(self, e):
        if self.scene is None:
            self._set_split(e.x)
        else:
            self._pan_move(e)

    def _set_split(self, x):
        W = self.content_size()[0]
        self.split = min(1.0, max(0.0, self.to_img(x, 0)[0] / W))
        self.render()

    def _pan_move(self, e):
        if not self._pan:
            return
        lx, ly = self._pan
        self.vx -= (e.x - lx) / self.s
        self.vy -= (e.y - ly) / self.s
        self._pan = (e.x, e.y)
        self.fit = False
        self.render()

    def _key(self, e):
        ks = e.keysym.lower()
        if ks in ("left", "right") and self.scene is None:
            self.split = min(1.0, max(0.0, self.split + (0.05 if ks == "right" else -0.05)))
            self.render()
        elif ks == "h":
            self.hl.set(not self.hl.get())
            self._settings_changed()
        elif ks == "s":
            self.swap()
        elif ks in ("0", "kp_0"):
            self.zoom_fit()

    # ---------------------------------------------------------------- actions
    def result_image(self):
        """Before | After side by side, with the highlights - what Copy puts on the clipboard."""
        if self.scene is not None:
            return side_by_side(self.ia, self.ib, self.GAP)
        A, B = self.app.img_of(self.a), self.app.img_of(self.b)
        if self.hl.get():
            A, B = highlight(A, self.mask, self.boxes), highlight(B, self.mask, self.boxes)
        return side_by_side(A.convert("RGB"), B.convert("RGB"), self.GAP)

    def copy(self):
        self.app._copy_img(self.result_image(), tr("comparison"))

    def mark(self):
        boxes = self.boxes if self.hl.get() else compare(self.app.img_of(self.a), self.app.img_of(self.b),
                                                       self.tol.get())[1]
        self.app.mark_differences(self.b, boxes)

    def show(self):
        try:
            self.win.deiconify()
            self.win.lift()
        except tk.TclError:
            pass

    def hide(self):
        try:
            self.win.withdraw()
        except tk.TclError:
            pass

    def close(self):
        try:
            if self.win.state() == "normal":
                self.app.st["cmp_geometry"] = self.win.geometry()
        except tk.TclError:
            pass
        self.win.destroy()
        if getattr(self.app, "cmp", None) is self:
            self.app.cmp = None
