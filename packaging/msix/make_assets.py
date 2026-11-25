"""Makes the MSIX tile and icon images from multicapture.png.

Usage: python packaging/msix/make_assets.py <output Assets folder>
Writes scale-100/200/400 tiles plus the targetsize icons (and the "unplated" ones the
taskbar uses), so makepri can pick the right size for each screen.
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ICON = os.path.join(HERE, "..", "..", "multicapture.png")

# name: (width, height) at scale-100
TILES = {
    "Square44x44Logo": (44, 44),
    "Square71x71Logo": (71, 71),
    "Square150x150Logo": (150, 150),
    "Wide310x150Logo": (310, 150),
    "StoreLogo": (50, 50),
}
SCALES = (100, 200, 400)
TARGET_SIZES = (16, 24, 32, 48, 256)


def tile(src, w, h, pad):
    """Icon centred on a transparent w x h canvas, leaving `pad` (fraction) around it."""
    side = int(min(w, h) * (1 - 2 * pad))
    im = src.resize((side, side), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(im, ((w - side) // 2, (h - side) // 2))
    return out


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    src = Image.open(ICON).convert("RGBA")
    for name, (w, h) in TILES.items():
        pad = 0.0 if name in ("Square44x44Logo", "StoreLogo") else 0.18
        for s in SCALES:
            tile(src, w * s // 100, h * s // 100, pad).save(os.path.join(out_dir, f"{name}.scale-{s}.png"))
    for t in TARGET_SIZES:
        im = tile(src, t, t, 0.0)
        im.save(os.path.join(out_dir, f"Square44x44Logo.targetsize-{t}.png"))
        im.save(os.path.join(out_dir, f"Square44x44Logo.targetsize-{t}_altform-unplated.png"))
        im.save(os.path.join(out_dir, f"Square44x44Logo.targetsize-{t}_altform-lightunplated.png"))
    print(f"Assets written to {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "Assets"))
