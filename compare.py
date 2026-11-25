"""Finding what changed between two screenshots of the same screen area.

Used by "Capture the same area again": the new screenshot gets a highlight rectangle around
every region that differs from the earlier one. Pure Pillow, no Tk, so it can be unit-tested anywhere.
"""
from PIL import Image, ImageChops

BLOCK = 8          # pixels are grouped into BLOCK x BLOCK cells before the regions are found
THRESHOLD = 28     # colour difference (0-255, largest channel) below which a pixel counts as unchanged
MAX_REGIONS = 60


def diff_mask(a, b, threshold=THRESHOLD):
    """Black/white mask ("L"), white where a and b differ. The images must have the same size."""
    d = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    r, g, bl = d.split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), bl)
    return m.point(lambda v: 255 if v > threshold else 0)


def _components(grid, gw, gh):
    """Bounding boxes (in grid cells, inclusive) of the 4-connected groups of set cells."""
    seen = bytearray(gw * gh)
    out = []
    for start in range(gw * gh):
        if not grid[start] or seen[start]:
            continue
        seen[start] = 1
        stack = [start]
        x0 = x1 = start % gw
        y0 = y1 = start // gw
        while stack:
            i = stack.pop()
            x, y = i % gw, i // gw
            x0, x1, y0, y1 = min(x0, x), max(x1, x), min(y0, y), max(y1, y)
            for j in ((i - 1) if x > 0 else -1, (i + 1) if x < gw - 1 else -1,
                      (i - gw) if y > 0 else -1, (i + gw) if y < gh - 1 else -1):
                if j >= 0 and grid[j] and not seen[j]:
                    seen[j] = 1
                    stack.append(j)
        out.append([x0, y0, x1, y1])
    return out


def _merge(boxes, gap):
    """Merges boxes that overlap or are closer than gap pixels, until none do."""
    boxes = [list(b) for b in boxes]
    changed = True
    while changed:
        changed = False
        out = []
        while boxes:
            b = boxes.pop()
            i = 0
            while i < len(boxes):
                c = boxes[i]
                if (b[0] - gap <= c[2] and c[0] - gap <= b[2] and b[1] - gap <= c[3] and c[1] - gap <= b[3]):
                    b = [min(b[0], c[0]), min(b[1], c[1]), max(b[2], c[2]), max(b[3], c[3])]
                    boxes.pop(i)
                    changed = True
                else:
                    i += 1
            out.append(b)
        boxes = out
    return boxes


def diff_regions(a, b, threshold=THRESHOLD, block=BLOCK, pad=4, gap=12, max_regions=MAX_REGIONS):
    """Rectangles [x0, y0, x1, y1] (pixels of b) around the areas where b differs from a.

    Nearby changes are joined into one rectangle; the result is sorted top-to-bottom, left-to-right.
    Returns [] when the images are identical, None when their sizes differ.
    """
    if a.size != b.size:
        return None
    w, h = a.size
    mask = diff_mask(a, b, threshold)
    if mask.getbbox() is None:
        return []
    # a cell counts as changed when any pixel in it changed (block <= 16 keeps one pixel above 0 in the mean)
    block = max(1, min(16, int(block)))
    gw, gh = max(1, -(-w // block)), max(1, -(-h // block))
    pw, ph = gw * block, gh * block
    if (pw, ph) != (w, h):
        padded = Image.new("L", (pw, ph), 0)
        padded.paste(mask, (0, 0))
        mask = padded
    small = mask.resize((gw, gh), Image.BOX).point(lambda v: 255 if v else 0)
    grid = small.tobytes()
    boxes = []
    for x0, y0, x1, y1 in _components(grid, gw, gh):
        # back to pixels, then shrink to the changed pixels inside the cells
        px0, py0, px1, py1 = x0 * block, y0 * block, min(w, (x1 + 1) * block), min(h, (y1 + 1) * block)
        bb = mask.crop((px0, py0, px1, py1)).getbbox()
        if bb is None:
            continue
        boxes.append([px0 + bb[0], py0 + bb[1], px0 + bb[2], py0 + bb[3]])
    boxes = _merge(boxes, gap)
    if len(boxes) > max_regions:            # very busy change: keep joining until few enough
        g = gap
        while len(boxes) > max_regions:
            g *= 2
            boxes = _merge(boxes, g)
    out = [[max(0, b[0] - pad), max(0, b[1] - pad), min(w, b[2] + pad), min(h, b[3] + pad)] for b in boxes]
    out.sort(key=lambda b: (b[1] // max(1, block * 4), b[0]))
    return out


def changed_fraction(a, b, threshold=THRESHOLD):
    """Share of pixels (0..1) that differ; None when the sizes differ."""
    if a.size != b.size:
        return None
    hist = diff_mask(a, b, threshold).histogram()
    return hist[255] / max(1, a.width * a.height)
