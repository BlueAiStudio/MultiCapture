# Generates multicapture.ico / multicapture.png (app icon) with Pillow.
import os
from PIL import Image, ImageDraw, ImageFilter

S = 1024
HERE = os.path.dirname(os.path.abspath(__file__))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    # diagonal gradient background
    c1, c2 = (37, 99, 235), (124, 58, 237)
    grad = Image.new("RGB", (S, S))
    px = grad.load()
    for y in range(S):
        for x in range(S):
            px[x, y] = lerp(c1, c2, (x + y) / (2 * S))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((40, 40, S - 40, S - 40), radius=220, fill=255)
    icon = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # soft shadow
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((52, 70, S - 28, S - 16), radius=220, fill=(15, 23, 42, 110))
    icon.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    icon.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(icon)
    # glossy highlight
    gl = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((-200, -620, S + 200, 430), fill=(255, 255, 255, 34))
    gm = Image.new("L", (S, S), 0)
    gm.paste(mask, (0, 0))
    icon.alpha_composite(Image.composite(gl, Image.new("RGBA", (S, S), (0, 0, 0, 0)), gm))

    # 2x2 grid of tiles
    x0, y0, t, g = 262, 262, 230, 40
    tiles = [(x0, y0), (x0 + t + g, y0), (x0, y0 + t + g), (x0 + t + g, y0 + t + g)]
    for i, (x, y) in enumerate(tiles):
        fill = (255, 255, 255, 245) if i != 3 else (251, 191, 36, 255)
        d.rounded_rectangle((x, y, x + t, y + t), radius=46, fill=fill)
    # mini "picture" in first tile
    x, y = tiles[0]
    d.polygon([(x + 30, y + 190), (x + 100, y + 95), (x + 150, y + 160), (x + 175, y + 130), (x + 205, y + 190)],
              fill=(37, 99, 235, 255))
    d.ellipse((x + 150, y + 40, x + 192, y + 82), fill=(124, 58, 237, 255))
    # text lines in second tile
    x, y = tiles[1]
    for k, w in enumerate((160, 120, 145)):
        d.rounded_rectangle((x + 35, y + 55 + k * 50, x + 35 + w, y + 80 + k * 50), radius=12, fill=(148, 163, 184, 255))
    # ruler in third tile
    x, y = tiles[2]
    d.rounded_rectangle((x + 28, y + 85, x + 202, y + 145), radius=10, outline=(37, 99, 235, 255), width=12)
    for k in range(7):
        xx = x + 52 + k * 21
        d.line((xx, y + 91, xx, y + (118 if k % 2 else 130)), fill=(37, 99, 235, 255), width=8)
    # check mark in amber tile
    x, y = tiles[3]
    d.line([(x + 55, y + 120), (x + 100, y + 165), (x + 178, y + 70)], fill=(255, 255, 255, 255), width=30, joint="curve")

    # capture corner brackets
    w, L, m = 34, 120, 175
    col = (255, 255, 255, 255)
    for (cx, cy, sx, sy) in ((m, m, 1, 1), (S - m, m, -1, 1), (m, S - m, 1, -1), (S - m, S - m, -1, -1)):
        d.line((cx, cy, cx + sx * L, cy), fill=col, width=w)
        d.line((cx, cy, cx, cy + sy * L), fill=col, width=w)
        d.ellipse((cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2), fill=col)

    big = icon.resize((256, 256), Image.LANCZOS)
    big.save(os.path.join(HERE, "multicapture.png"))
    big.save(os.path.join(HERE, "multicapture.ico"),
             sizes=[(16, 16), (20, 20), (24, 24), (32, 32), (40, 40), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("icon written")


if __name__ == "__main__":
    main()
