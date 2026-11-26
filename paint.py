# -*- coding: utf-8 -*-
"""Paint-style tools that work on pixels: fill bucket masks, and rotate / flip / crop / resize of a
screenshot together with its annotations. No Tk here, so it can be tested anywhere."""
import base64
import io
import math

from PIL import Image, ImageChops, ImageDraw

FILL_TOLERANCE = 32      # max difference per colour channel (0-255) that still counts as "same colour"


# --------------------------------------------------------------------------- fill bucket
def flood_mask(img, x, y, tol=FILL_TOLERANCE):
    """Area of similar colour connected to (x, y), like Paint's fill bucket.
    Returns (mask, left, top): an 'L' mask (255 = filled) cropped to its bounding box, or None."""
    rgb = img.convert("RGB")
    W, H = rgb.size
    x, y = int(x), int(y)
    if not (0 <= x < W and 0 <= y < H):
        return None
    seed = rgb.getpixel((x, y))
    diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, seed))
    r, g, b = diff.split()
    near = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 1 if v <= tol else 0)
    a = bytearray(near.tobytes())        # 1 = same colour, 0 = border, 2 = filled
    stack = [(x, y)]
    while stack:
        sx, sy = stack.pop()
        row = sy * W
        i = row + sx
        if a[i] != 1:
            continue
        # extend the run to the left and right (bytearray.find runs in C, so this stays fast)
        left = max(a.rfind(0, row, i), a.rfind(2, row, i), row - 1) + 1
        r0 = [p for p in (a.find(0, i, row + W), a.find(2, i, row + W)) if p != -1]
        right = min(r0) if r0 else row + W
        a[left:right] = b"\x02" * (right - left)
        lx, rx = left - row, right - row
        for ny in (sy - 1, sy + 1):
            if 0 <= ny < H:
                nrow = ny * W
                p = nrow + lx
                end = nrow + rx
                while p < end:
                    p = a.find(1, p, end)
                    if p == -1:
                        break
                    stack.append((p - nrow, ny))
                    q = [v for v in (a.find(0, p, end), a.find(2, p, end)) if v != -1]
                    p = min(q) if q else end
    m = Image.frombytes("L", (W, H), bytes(a)).point(lambda v: 255 if v == 2 else 0)
    box = m.getbbox()
    if not box:
        return None
    return m.crop(box), box[0], box[1]


def mask_to_str(m):
    buf = io.BytesIO()
    m.convert("1").save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


_MASKS = {}


def mask_from_str(s):
    m = _MASKS.get(s)
    if m is None:
        with Image.open(io.BytesIO(base64.b64decode(s))) as f:
            m = f.convert("L")
        if len(_MASKS) > 64:
            _MASKS.clear()
        _MASKS[s] = m
    return m


def draw_fill(img, o, s, tf):
    """Draw a fill object (colour through its mask) on img, at view scale s."""
    m = mask_from_str(o["mask"])
    (a, b), (c, d) = tf(o["x"], o["y"]), tf(o["x"] + m.width, o["y"] + m.height)
    a, b = int(round(a)), int(round(b))
    w, h = max(1, int(round(c)) - a), max(1, int(round(d)) - b)
    # only the part that is visible in img is scaled (the view may show a small zoomed-in piece)
    vx0, vy0, vx1, vy1 = max(0, a), max(0, b), min(img.width, a + w), min(img.height, b + h)
    if vx1 <= vx0 or vy1 <= vy0:
        return
    kx, ky = m.width / w, m.height / h
    src = (int((vx0 - a) * kx), int((vy0 - b) * ky),
           max(int((vx0 - a) * kx) + 1, math.ceil((vx1 - a) * kx)),
           max(int((vy0 - b) * ky) + 1, math.ceil((vy1 - b) * ky)))
    part = m.crop(src).resize((vx1 - vx0, vy1 - vy0), Image.NEAREST if s >= 1 else Image.BILINEAR)
    img.paste(o["color"], (vx0, vy0, vx1, vy1), part)


def fill_hit(o, x, y):
    m = mask_from_str(o["mask"])
    px, py = int(x - o["x"]), int(y - o["y"])
    return 0 <= px < m.width and 0 <= py < m.height and m.getpixel((px, py)) > 0


def erase_fill(o, pts, r):
    """Erase circles of radius r around pts (image coordinates) from a fill object's mask.
    Returns True if something was erased; the object is dropped by the caller when it becomes empty."""
    m = mask_from_str(o["mask"]).copy()
    d = ImageDraw.Draw(m)
    for x, y in pts:
        cx, cy = x - o["x"], y - o["y"]
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=0)
    if ImageChops.difference(m, mask_from_str(o["mask"])).getbbox() is None:
        return False
    box = m.getbbox()
    if not box:
        o["mask"] = None
        return True
    o["x"], o["y"] = o["x"] + box[0], o["y"] + box[1]
    o["mask"] = mask_to_str(m.crop(box))
    return True


# --------------------------------------------------------------------------- eraser on strokes
def erase_stroke(pts, ex, ey, r):
    """Pieces of a pen / highlighter stroke that stay after erasing a circle (ex, ey, r).
    Returns None when the circle does not touch the stroke."""
    out, cur, hit = [], [], False
    for p in pts:
        if math.hypot(p[0] - ex, p[1] - ey) <= r:
            hit = True
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(p)
    if not hit:
        return None
    if cur:
        out.append(cur)
    return out


# --------------------------------------------------------------------------- whole-image operations
TRANSPOSE = {"rot_cw": Image.ROTATE_270, "rot_ccw": Image.ROTATE_90, "rot180": Image.ROTATE_180,
             "flip_h": Image.FLIP_LEFT_RIGHT, "flip_v": Image.FLIP_TOP_BOTTOM}


def _point_fn(op, W, H, arg):
    if op == "rot_cw":
        return lambda x, y: (H - y, x)
    if op == "rot_ccw":
        return lambda x, y: (y, W - x)
    if op == "rot180":
        return lambda x, y: (W - x, H - y)
    if op == "flip_h":
        return lambda x, y: (W - x, y)
    if op == "flip_v":
        return lambda x, y: (x, H - y)
    if op == "crop":
        x0, y0 = arg[0], arg[1]
        return lambda x, y: (x - x0, y - y0)
    if op == "resize":
        sx, sy = arg[0] / W, arg[1] / H
        return lambda x, y: (x * sx, y * sy)
    raise ValueError(op)


def transform_image(img, op, arg=None):
    if op in TRANSPOSE:
        return img.transpose(TRANSPOSE[op])
    if op == "crop":
        return img.crop(tuple(int(v) for v in arg))
    if op == "resize":
        return img.resize((int(arg[0]), int(arg[1])), Image.LANCZOS)
    raise ValueError(op)


def transform_objs(objs, op, size, arg=None, text_size=None):
    """Annotations moved along with the picture. size = (W, H) of the image before the operation.
    text_size(o) -> (w, h) of a text box (needed so that text keeps its place but stays upright)."""
    W, H = size
    f = _point_fn(op, W, H, arg)
    k = math.sqrt((arg[0] / W) * (arg[1] / H)) if op == "resize" else 1.0
    out = []
    for o in objs:
        o = dict(o)
        t = o.get("type")
        if t == "text":      # text stays upright: move the centre of its box
            w0, h0 = text_size(o) if text_size else (0, 0)
            centre = f(o["x"] + w0 / 2, o["y"] + h0 / 2)
        if k != 1.0:
            for key in ("width", "size", "fs", "block"):
                if isinstance(o.get(key), (int, float)):
                    o[key] = max(1, round(o[key] * k, 2))
        for key in ("pts", "p"):
            if key in o:
                o[key] = [list(f(*p)) for p in o[key]]
        if t == "table" and op in ("rot_cw", "rot_ccw"):    # tables stay upright too: move the centre
            x0, y0, x1, y1 = o["box"]
            cx, cy = f((x0 + x1) / 2, (y0 + y1) / 2)
            hw, hh = abs(x1 - x0) / 2, abs(y1 - y0) / 2
            o["box"] = [cx - hw, cy - hh, cx + hw, cy + hh]
        elif "box" in o:
            (a, b), (c, d) = f(*o["box"][:2]), f(*o["box"][2:])
            o["box"] = [min(a, c), min(b, d), max(a, c), max(b, d)]
        if o.get("leader"):
            o["leader"] = list(f(*o["leader"]))
        if o.get("solid"):   # pseudo-3D depth vector turns / flips / scales with the picture
            sd = dict(o["solid"])
            a = math.radians(sd.get("ang", 45))
            (x0, y0), (x1, y1) = f(0, 0), f(sd.get("depth", 40) * math.cos(a), -sd.get("depth", 40) * math.sin(a))
            sd["depth"] = round(math.hypot(x1 - x0, y1 - y0), 1)
            sd["ang"] = round(math.degrees(math.atan2(-(y1 - y0), x1 - x0)) % 360, 1)
            o["solid"] = sd
        if t == "text":
            cx, cy = centre
            w1, h1 = text_size(o) if text_size else (0, 0)
            o["x"], o["y"] = cx - w1 / 2, cy - h1 / 2
        elif t == "image" and op in TRANSPOSE:   # a picture laid over the screenshot turns with it
            import dropin
            src = dropin.OVERLAYS.get(o.get("src"))
            if src is not None:
                o["src"] = dropin.OVERLAYS.put(src.transpose(TRANSPOSE[op]))
                if op in ("rot_cw", "rot_ccw"):
                    o["ratio"] = src.height / src.width
        elif t == "fill":
            m = mask_from_str(o["mask"])
            (a, b), (c, d) = f(o["x"], o["y"]), f(o["x"] + m.width, o["y"] + m.height)
            if op in TRANSPOSE:
                m = m.transpose(TRANSPOSE[op])
            elif op == "resize":
                m = m.resize((max(1, round(abs(c - a))), max(1, round(abs(d - b)))), Image.NEAREST)
            o["x"], o["y"] = min(a, c), min(b, d)
            o["mask"] = mask_to_str(m)
        elif "x" in o and "y" in o:
            o["x"], o["y"] = f(o["x"], o["y"])
        out.append(o)
    return out
