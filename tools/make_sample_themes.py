# -*- coding: utf-8 -*-
"""Draws the pictures of the sample themes in themes/ (flowers, night, card).

You do not need this to make a theme: draw your PNGs in any paint program instead.
It only exists so the sample pictures can be rebuilt.   python tools/make_sample_themes.py
"""
import ctypes
import json
import math
import os
import random
import sys
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
if not hasattr(ctypes, "windll"):          # allow running on Linux / macOS
    ctypes.windll = mock.MagicMock()

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import multicapture as mc  # noqa: E402
import themes  # noqa: E402

OUT = os.path.join(ROOT, "themes")
if sys.platform != "win32":   # no Windows fonts here: use any CJK font for the preview texts
    from PIL import ImageFont
    _CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
    if os.path.exists(_CJK):
        mc.frame_font = lambda size, bold=False, text="": ImageFont.truetype(_CJK, max(6, int(size)))
SS = 4   # supersampling


def rgb(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def save(im, *parts):
    p = os.path.join(OUT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    im.save(p, optimize=True)


def down(im, size):
    return im.resize(size, Image.LANCZOS)


# --------------------------------------------------------------------------- flowers
def flower(px, petal, centre, n=6, petal_len=0.46, petal_w=0.24, rot=0.0, inner=None, centre_r=0.2):
    S = px * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S / 2
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        L, Wd = S * petal_len, S * petal_w
        ld.ellipse((c - Wd / 2, c - L, c + Wd / 2, c), fill=rgb(petal))
        if inner:
            ld.ellipse((c - Wd / 5, c - L * 0.8, c + Wd / 5, c - L * 0.15), fill=rgb(inner, 150))
        layer = layer.rotate(-math.degrees(a), resample=Image.BICUBIC, center=(c, c))
        im.alpha_composite(layer)
    d = ImageDraw.Draw(im)
    r = S * centre_r
    d.ellipse((c - r, c - r, c + r, c + r), fill=rgb(centre))
    return im


def tulip(px, color, dark):
    S = px * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((S * .5, S * .55, S * .5, S * .95), fill=rgb("#4E9A51"), width=int(S * .06))
    d.ellipse((S * .5, S * .62, S * .8, S * .78), fill=rgb("#66BB6A"))
    d.ellipse((S * .22, S * .12, S * .52, S * .62), fill=rgb(dark))
    d.ellipse((S * .48, S * .12, S * .78, S * .62), fill=rgb(dark))
    d.ellipse((S * .33, S * .06, S * .67, S * .62), fill=rgb(color))
    return im


def rose(px, color="#E91E63", dark="#AD1457", light="#F48FB1"):
    S = px * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    # leaves
    for ang in (35, 145):
        lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse((c - S * .1, c, c + S * .1, c + S * .48), fill=rgb("#5DA35F"))
        im.alpha_composite(lay.rotate(ang, resample=Image.BICUBIC, center=(c, c)))
    d.ellipse((c - S * .34, c - S * .34, c + S * .34, c + S * .34), fill=rgb(dark))
    for k, col in enumerate((color, light, color, dark)):
        r = S * (.28 - k * .06)
        o = S * .02 * (1 if k % 2 else -1)
        d.pieslice((c - r + o, c - r, c + r + o, c + r), 200 + k * 40, 520 + k * 40, fill=rgb(col))
    d.ellipse((c - S * .05, c - S * .05, c + S * .05, c + S * .05), fill=rgb(dark))
    return im


FLOWER_TOOLS = {   # petal colour, centre, petals
    "select": ("#F8BBD0", "#FFF3E0", 5), "pen": ("#F48FB1", "#FFF8E1", 6), "highlight": ("#FFE082", "#FFF8E1", 8),
    "line": ("#CE93D8", "#FFF8E1", 5), "arrow": ("#F06292", "#FFF8E1", 6), "rect": ("#90CAF9", "#FFFDE7", 4),
    "ellipse": ("#B39DDB", "#FFFDE7", 7), "text": ("#FFAB91", "#FFFDE7", 6), "callout": ("#A5D6A7", "#FFFDE7", 5),
    "marker": ("#EF9A9A", "#FFFDE7", 8), "stamp": ("#FFCC80", "#FFFDE7", 6), "mosaic": ("#B0BEC5", "#FFFDE7", 5),
    "dist": ("#80DEEA", "#FFFDE7", 6), "perim": ("#C5E1A5", "#FFFDE7", 7), "area": ("#F8BBD0", "#FFFDE7", 8),
    "angle": ("#E1BEE7", "#FFFDE7", 5), "calib": ("#FFE0B2", "#FFFDE7", 6),
}


def flower_icon(key, px=96):
    petal, centre, n = FLOWER_TOOLS[key]
    im = down(flower(px, petal, centre, n=n, petal_len=.48, petal_w=.30 if n < 7 else .22,
                     rot=0.3, centre_r=.30), (px, px))
    glyph = mc.tool_icon_image(key, "#6B2D47", "#C2185B").resize((int(px * .42), int(px * .42)), Image.LANCZOS)
    im.alpha_composite(glyph, ((px - glyph.width) // 2, (px - glyph.height) // 2))
    return im


def make_flowers():
    tid = "flowers"
    for key in themes.TOOL_ICON_KEYS:
        save(flower_icon(key), tid, "icons", f"{key}.png")
    head = {
        "capture": down(flower(96, "#FFD54F", "#8D6E63", n=12, petal_len=.48, petal_w=.16, centre_r=.2), (96, 96)),
        "copy": down(flower(96, "#F8BBD0", "#FFF59D", n=5, petal_w=.34), (96, 96)),
        "save": down(tulip(96, "#EC407A", "#C2185B"), (96, 96)),
        "delete": down(flower(96, "#FF8A65", "#FFF59D", n=10, petal_len=.48, petal_w=.15), (96, 96)),
        "options": down(flower(96, "#B39DDB", "#FFF59D", n=8, petal_w=.2), (96, 96)),
        "themes": down(rose(96), (96, 96)),
        "help": down(tulip(96, "#FFB74D", "#F57C00"), (96, 96)),
    }
    for k, im in head.items():
        save(im, tid, "icons", f"{k}.png")
    # stickers for the frame and the decorations
    save(down(rose(240), (240, 240)), tid, "deco", "rose.png")
    save(down(flower(160, "#F8BBD0", "#FFF176", n=5, petal_w=.36, inner="#F06292"), (160, 160)), tid, "deco", "blossom.png")
    save(down(flower(120, "#FFFFFF", "#FBC02D", n=12, petal_len=.48, petal_w=.14), (120, 120)), tid, "deco", "daisy.png")
    # 9-slice picture frame: pink band with dots, transparent middle
    S, B = 240, 36
    fr = Image.new("RGBA", (S * SS, S * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((0, 0, S * SS - 1, S * SS - 1), radius=22 * SS, fill=rgb("#F8BBD0"))
    d.rounded_rectangle((B * SS, B * SS, (S - B) * SS - 1, (S - B) * SS - 1), radius=6 * SS, fill=(0, 0, 0, 0))
    d.rounded_rectangle((6 * SS, 6 * SS, (S - 6) * SS, (S - 6) * SS), radius=18 * SS, outline=rgb("#FFFFFF", 200), width=2 * SS)
    d.rounded_rectangle(((B - 4) * SS, (B - 4) * SS, (S - B + 4) * SS, (S - B + 4) * SS), radius=8 * SS,
                        outline=rgb("#EC407A"), width=3 * SS)
    for i in range(B + 8, S - B - 4, 16):
        for x, y in ((i, B / 2), (i, S - B / 2), (B / 2, i), (S - B / 2, i)):
            d.ellipse(((x - 3) * SS, (y - 3) * SS, (x + 3) * SS, (y + 3) * SS), fill=rgb("#FFFFFF", 230))
    fr = down(fr, (S, S))
    for x, y in ((B / 2, B / 2), (S - B / 2, B / 2), (B / 2, S - B / 2), (S - B / 2, S - B / 2)):
        f = down(flower(30, "#FFFFFF", "#F06292", n=5, petal_w=.36), (30, 30))
        fr.alpha_composite(f, (int(x - 15), int(y - 15)))
    save(fr, tid, "frame.png")
    # header vine and canvas bouquet
    W, H = 300, 88
    hv = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(hv)
    pts = [(x * SS, (H / 2 + 14 * math.sin(x / 26)) * SS) for x in range(0, W, 2)]
    d.line(pts, fill=rgb("#81C784"), width=3 * SS)
    hv = down(hv, (W, H))
    for i, x in enumerate(range(30, W, 52)):
        y = H / 2 + 14 * math.sin(x / 26)
        col = ("#F48FB1", "#FFD54F", "#CE93D8", "#F06292", "#FFAB91", "#90CAF9")[i % 6]
        f = down(flower(40, col, "#FFF8E1", n=5 + i % 3, petal_w=.32), (40, 40))
        hv.alpha_composite(f, (int(x - 20), int(y - 20)))
    save(hv, tid, "header.png")
    bq = Image.new("RGBA", (420, 300), (0, 0, 0, 0))
    random.seed(4)
    for i in range(14):
        kind = i % 3
        sz = random.randint(70, 130)
        f = rose(sz) if kind == 0 else flower(sz, random.choice(["#F8BBD0", "#FFE082", "#E1BEE7", "#FFFFFF"]),
                                                "#FFF176", n=random.choice([5, 6, 8]), petal_w=.3)
        f = down(f, (sz, sz))
        lay = Image.new("RGBA", bq.size, (0, 0, 0, 0))
        lay.paste(f, (random.randint(-20, 420 - sz + 20), random.randint(60, 300 - sz + 40)))
        bq.alpha_composite(lay)
    a = bq.getchannel("A").point(lambda v: v * 0.55)
    bq.putalpha(a)
    save(bq, tid, "canvas.png")


# --------------------------------------------------------------------------- night
def moon(px, glow=True):
    S = px * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if glow:
        g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((S * .12, S * .12, S * .88, S * .88), fill=rgb("#FFE9A8", 90))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(S * .08)))
    m = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(m)
    md.ellipse((S * .2, S * .2, S * .8, S * .8), fill=255)
    md.ellipse((S * .36, S * .1, S * .92, S * .66), fill=0)
    body = Image.new("RGBA", (S, S), rgb("#FFE38A"))
    body.putalpha(m)
    im.alpha_composite(body)
    return im


def star(px, color="#FFF4C2", points=5, inner=.42):
    S = px * SS
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    c = S / 2
    pts = []
    for i in range(points * 2):
        r = (S * .48) if i % 2 == 0 else (S * .48 * inner)
        a = -math.pi / 2 + i * math.pi / points
        pts.append((c + r * math.cos(a), c + r * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=rgb(color))
    return im


def make_night():
    tid = "night"
    save(down(moon(96, glow=False), (96, 96)), tid, "icons", "capture.png")
    save(down(star(96, "#FFE38A"), (96, 96)), tid, "icons", "themes.png")
    save(down(moon(220), (220, 220)), tid, "deco", "moon.png")
    save(down(star(80), (80, 80)), tid, "deco", "star.png")
    save(down(star(48, "#C9D4FF", 4, .3), (48, 48)), tid, "deco", "sparkle.png")
    random.seed(7)
    W, H = 320, 88
    hd = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for _ in range(26):
        s = random.choice([6, 8, 10, 14])
        st = down(star(s * 2, random.choice(["#FFF4C2", "#C9D4FF", "#FFFFFF"]), random.choice([4, 5]), .38), (s, s))
        hd.alpha_composite(st, (random.randint(0, W - s - 70), random.randint(4, H - s - 4)))
    hd.alpha_composite(down(moon(80), (80, 80)), (W - 82, 4))
    save(hd, tid, "header.png")
    W, H = 520, 400
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for _ in range(60):
        s = random.choice([4, 6, 8, 10, 16])
        st = down(star(s * 2, random.choice(["#FFF4C2", "#C9D4FF", "#FFFFFF"]), random.choice([4, 5]), .38), (s, s))
        x, y = random.randint(0, W - s), random.randint(0, H - s)
        if x > W - 230 and y < 230:
            continue
        cv.alpha_composite(st, (x, y))
    cv.alpha_composite(down(moon(220), (220, 220)), (W - 225, 5))
    cv.putalpha(cv.getchannel("A").point(lambda v: v * 0.8))
    save(cv, tid, "canvas.png")


def write_json(tid, meta):
    with open(os.path.join(OUT, tid, "theme.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")


def make_previews():
    found, errors = themes.discover([(OUT, "builtin")])
    assert not errors, errors
    for tid in ("flowers", "night", "card"):
        t = found[tid]
        im = themes.make_preview(t, mc.theme_icon, (520, 330), mc.frame_font, lang="zh")
        save(im.convert("RGB"), tid, "preview.png")


if __name__ == "__main__":
    make_flowers()
    make_night()
    os.makedirs(os.path.join(OUT, "card"), exist_ok=True)
    make_previews()
    print("sample themes written to", OUT)
