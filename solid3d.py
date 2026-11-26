# -*- coding: utf-8 -*-
"""Pseudo-3D annotations: turn a rectangle, ellipse or polygon into a shaded solid (box, cylinder, prism).

Nothing here is real 3D. The flat shape is the front face; the back face is the same shape moved by a depth
vector (oblique projection). Side faces are the quads between the two, shaded by how much they face a light
from the top-left. An optional "pocket" cuts a hole into the front face. Pure PIL, no 3D libraries.

An object becomes a solid by carrying  o["solid"] = {"depth": px, "ang": degrees, "cut": bool}
(depth in image pixels, angle counter-clockwise from the +x axis, so 45 means up-right).
"""
import math

from PIL import Image, ImageChops, ImageDraw

SOLID_TYPES = ("rect", "ellipse", "area")
_LIGHT = (-0.45, -0.89)          # light from the top-left (screen y points down)
_ELL_N = 72                      # ellipse -> polygon resolution
_CUT_SCALE = 0.5                 # pocket opening relative to the front face
_CUT_DEPTH = 0.55                # pocket depth relative to the solid depth


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(rgb, other, k):
    return tuple(int(round(c + (o - c) * k)) for c, o in zip(rgb, other))


def _shade(rgb, k):
    """k in [-1, 1]: >0 lightens towards white, <0 darkens towards black."""
    return _mix(rgb, (255, 255, 255), 0.5 * k) if k >= 0 else _mix(rgb, (0, 0, 0), -0.45 * k)


def front_pts(o):
    """The flat shape as a polygon in image coordinates."""
    t = o["type"]
    if t == "area":
        return [tuple(p) for p in o["pts"]]
    x0, y0, x1, y1 = o["box"]
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    if t == "rect":
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    return [(cx + rx * math.cos(2 * math.pi * i / _ELL_N), cy + ry * math.sin(2 * math.pi * i / _ELL_N))
            for i in range(_ELL_N)]


def depth_vec(o):
    sd = o["solid"]
    a = math.radians(sd.get("ang", 45))
    return sd.get("depth", 40) * math.cos(a), -sd.get("depth", 40) * math.sin(a)


def centroid(pts):
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def _signed_area(pts):
    return sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
               for i in range(len(pts))) / 2


def _normals(pts):
    """Outward unit normal of each edge i -> i+1 (screen coordinates)."""
    sgn = 1 if _signed_area(pts) > 0 else -1
    out = []
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        out.append((sgn * dy / L, -sgn * dx / L))
    return out


def default_solid(o):
    """Sensible depth / angle for a freshly converted shape."""
    pts = front_pts(o)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if o["type"] == "rect":                  # cube look: top and right faces visible
        return {"depth": max(12, round(min(w, h) * 0.45)), "ang": 40, "cut": False}
    # cylinder / prism standing up: the drawn shape is the top, the body goes down
    return {"depth": max(12, round(max(w, h) * 0.5)), "ang": 270, "cut": False}


def make_solid(o):
    """Turn o into a solid in place (gives it a fill so the faces can be shaded)."""
    o["solid"] = default_solid(o)
    if o["type"] in ("rect", "ellipse") and not o.get("fill"):
        o["fill"] = o.get("color", "#1E88E5")
        o["fill_alpha"] = max(o.get("fill_alpha", 40), 70)
    if o["type"] == "area":
        o["fill_alpha"] = max(o.get("fill_alpha", 25), 70)
    return o


# --------------------------------------------------------------------------- geometry for selection
def solid_bbox(o):
    pts = front_pts(o)
    vx, vy = depth_vec(o)
    allp = pts + [(x + vx, y + vy) for x, y in pts]
    m = o.get("width", 2) / 2
    return [min(p[0] for p in allp) - m, min(p[1] for p in allp) - m,
            max(p[0] for p in allp) + m, max(p[1] for p in allp) + m]


def _in_poly(pts, x, y):
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-9) + x1:
            inside = not inside
    return inside


def solid_hit(o, x, y, tol):
    pts = front_pts(o)
    vx, vy = depth_vec(o)
    back = [(px + vx, py + vy) for px, py in pts]
    if _in_poly(pts, x, y) or _in_poly(back, x, y):
        return True
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        if _in_poly([a, b, back[(i + 1) % n], back[i]], x, y):
            return True
    def seg(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))
    m = tol + o.get("width", 2) / 2
    return any(seg(x, y, *q[i], *q[(i + 1) % n]) <= m for q in (pts, back) for i in range(n))


def solid_handle(o):
    """The depth handle: centre of the back face. Drag it to set depth and angle."""
    cx, cy = centroid(front_pts(o))
    vx, vy = depth_vec(o)
    return cx + vx, cy + vy


def set_solid_handle(o, x, y):
    cx, cy = centroid(front_pts(o))
    dx, dy = x - cx, y - cy
    depth = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(-dy, dx)) % 360
    snap = round(ang / 45) * 45                # gentle snap to 0 / 45 / 90 ...
    if abs(ang - snap) < 4:
        ang = snap % 360
    o["solid"]["depth"] = round(max(2.0, depth), 1)
    o["solid"]["ang"] = round(ang, 1)


# --------------------------------------------------------------------------- rendering
def _dashed(d, p1, p2, fill, width, dash, phase=None):
    """Dashed segment. Pass the same phase list to consecutive calls so a curve keeps its dash rhythm."""
    phase = phase if phase is not None else [0.0, True]
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    if L == 0:
        return
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    t = 0.0
    while t < L:
        step = min(L - t, dash - phase[0])
        if phase[1]:
            d.line((x1 + ux * t, y1 + uy * t, x1 + ux * (t + step), y1 + uy * (t + step)), fill=fill, width=width)
        t += step
        phase[0] += step
        if phase[0] >= dash - 1e-9:
            phase[0], phase[1] = 0.0, not phase[1]


def _side_faces(pts, v, normals):
    """[(order_key, quad, normal, visible)] for every side face."""
    vx, vy = v
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        nx, ny = normals[i]
        vis = nx * vx + ny * vy > 1e-9
        key = ((a[0] + b[0]) / 2) * vx + ((a[1] + b[1]) / 2) * vy
        out.append((key, [a, b, (b[0] + vx, b[1] + vy), (a[0] + vx, a[1] + vy)], (nx, ny), vis))
    return out


def d_solid(img, o, s, tf, sc=None):
    """Draw o (rect / ellipse / area with o['solid']) on img. tf maps image -> output coordinates."""
    smooth = o["type"] == "ellipse"
    pts = [tf(*p) for p in front_pts(o)]
    if len(pts) < 3 or abs(_signed_area(pts)) < 1:
        return
    vx, vy = depth_vec(o)
    v = (vx * s, vy * s)
    back = [(x + v[0], y + v[1]) for x, y in pts]
    normals = _normals(pts)
    faces = _side_faces(pts, v, normals)
    base = _hex(o.get("fill") or o.get("color", "#1E88E5"))
    alpha = max(0.05, min(1.0, o.get("fill_alpha", 70) / 100))
    stroke = o.get("color", "#000000")
    w = max(1, int(round(o.get("width", 3) * s)))
    lw = max(1, int(round(w * 0.75)))
    lx, ly = _LIGHT

    allp = pts + back
    x0 = max(0, int(math.floor(min(p[0] for p in allp))) - w - 2)
    y0 = max(0, int(math.floor(min(p[1] for p in allp))) - w - 2)
    x1 = min(img.width, int(math.ceil(max(p[0] for p in allp))) + w + 2)
    y1 = min(img.height, int(math.ceil(max(p[1] for p in allp))) + w + 2)
    if x1 <= x0 or y1 <= y0:
        return
    off = lambda q: [(x - x0, y - y0) for x, y in q]  # noqa: E731
    layer = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # side faces, far ones first
    for key, quad, (nx, ny), vis in sorted(faces, key=lambda f: -f[0]):
        if vis:
            col = _shade(base, nx * lx + ny * ly)
            d.polygon(off(quad), fill=col + (255,), outline=col + (255,) if smooth else None)
    # front face
    d.polygon(off(pts), fill=_shade(base, 0.18) + (255,))

    # pocket (cut) in the front face
    if o["solid"].get("cut"):
        cx, cy = centroid(pts)
        inner = [(cx + (x - cx) * _CUT_SCALE, cy + (y - cy) * _CUT_SCALE) for x, y in pts]
        vp = (v[0] * _CUT_DEPTH, v[1] * _CUT_DEPTH)
        floor = [(x + vp[0], y + vp[1]) for x, y in inner]
        pocket = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(pocket)
        inner_n = _normals(inner)
        for key, quad, (nx, ny), vis in sorted(_side_faces(inner, vp, inner_n), key=lambda f: -f[0]):
            col = _shade(base, -0.4 - 0.25 * (nx * lx + ny * ly))   # walls face inwards, stay in shadow
            pd.polygon(off(quad), fill=col + (255,), outline=col + (255,) if smooth else None)
        pd.polygon(off(floor), fill=_shade(base, -0.5) + (255,))
        mask = Image.new("L", layer.size, 0)
        ImageDraw.Draw(mask).polygon(off(inner), fill=255)
        layer.paste(pocket, (0, 0), ImageChops.multiply(mask, pocket.getchannel("A")))

    if alpha < 1:
        layer.putalpha(layer.getchannel("A").point(lambda a: int(a * alpha)))
    img.alpha_composite(layer, (x0, y0))

    if o.get("width", 3) <= 0:
        return
    d = ImageDraw.Draw(img)
    n = len(pts)
    vis = [f[3] for f in faces]
    dash = max(4, 4 * s + w * 2)
    # hidden edges (dashed) show through translucent solids
    if alpha < 0.95:
        ph = [0.0, True]
        for i in range(n):
            if not vis[i]:
                _dashed(d, back[i], back[(i + 1) % n], stroke, lw, dash, ph)
        if not smooth:
            for i in range(n):
                if not vis[i] and not vis[i - 1]:
                    _dashed(d, pts[i], back[i], stroke, lw, dash)
    # visible silhouette
    for i in range(n):
        if vis[i]:
            d.line((back[i], back[(i + 1) % n]), fill=stroke, width=w)
    for i in range(n):
        a, b = vis[i - 1], vis[i]
        if (a != b) or (not smooth and (a or b)):
            d.line((pts[i], back[i]), fill=stroke, width=w)
    d.line(pts + [pts[0]], fill=stroke, width=w, joint="curve")
    if o["solid"].get("cut"):
        cx, cy = centroid(pts)
        inner = [(cx + (x - cx) * _CUT_SCALE, cy + (y - cy) * _CUT_SCALE) for x, y in pts]
        d.line(inner + [inner[0]], fill=stroke, width=lw, joint="curve")
