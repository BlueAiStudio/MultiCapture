"""Platform-independent tests for the before / after comparison (difference mask and boxes)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw  # noqa: E402

try:
    import tkinter  # noqa: F401
except ImportError:   # headless Python without Tk: the tested code does not use it
    import types
    for name in ("tkinter", "tkinter.ttk"):
        sys.modules[name] = types.ModuleType(name)
    sys.modules["tkinter"].ttk = sys.modules["tkinter.ttk"]
    sys.modules["PIL.ImageTk"] = types.ModuleType("PIL.ImageTk")

import compare  # noqa: E402


def screen(w=800, h=500):
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    for y in range(20, h - 20, 24):
        d.rectangle((20, y, w - 60, y + 10), fill=(90, 90, 90))
    return im


class DiffTests(unittest.TestCase):
    def test_identical_images_have_no_differences(self):
        a = screen()
        mask, boxes = compare.compare(a, a.copy())
        self.assertIsNone(mask.getbbox())
        self.assertEqual(boxes, [])

    def test_two_separate_changes_give_two_boxes(self):
        a = screen()
        b = a.copy()
        d = ImageDraw.Draw(b)
        d.rectangle((100, 100, 139, 129), fill=(255, 0, 0))
        d.rectangle((600, 400, 619, 409), fill=(0, 0, 255))
        boxes = compare.compare(a, b)[1]
        self.assertEqual(len(boxes), 2)
        self.assertEqual(boxes[0], [100, 100, 140, 130])     # largest first, tight, x1/y1 exclusive
        self.assertEqual(boxes[1], [600, 400, 620, 410])

    def test_nearby_changes_are_joined(self):
        a = Image.new("RGB", (400, 300), "white")
        b = a.copy()
        d = ImageDraw.Draw(b)
        for x in range(50, 90, 4):            # dotted line: many tiny changes close together
            d.point((x, 60), fill="black")
        self.assertEqual(len(compare.compare(a, b)[1]), 1)

    def test_tolerance_ignores_small_colour_changes(self):
        a = Image.new("RGB", (200, 200), (200, 200, 200))
        b = a.copy()
        ImageDraw.Draw(b).rectangle((10, 10, 50, 50), fill=(208, 200, 200))
        self.assertEqual(compare.compare(a, b, tolerance=16)[1], [])
        self.assertEqual(len(compare.compare(a, b, tolerance=4)[1]), 1)

    def test_single_pixel_on_large_image(self):
        a = Image.new("RGB", (3840, 2160), "white")
        b = a.copy()
        b.putpixel((3000, 2000), (0, 0, 0))
        b.putpixel((3001, 2000), (0, 0, 0))
        b.putpixel((3002, 2000), (0, 0, 0))
        self.assertEqual(compare.compare(a, b)[1], [[3000, 2000, 3003, 2001]])

    def test_size_mismatch_compares_overlap(self):
        a = screen(800, 500)
        b = screen(700, 520)
        mask, boxes = compare.compare(a, b)
        self.assertEqual(mask.size, (700, 500))
        for x0, y0, x1, y1 in boxes:
            self.assertLessEqual(x1, 700)
            self.assertLessEqual(y1, 500)

    def test_highlight_and_side_by_side(self):
        a = screen()
        b = a.copy()
        ImageDraw.Draw(b).rectangle((300, 200, 340, 240), fill=(0, 160, 0))
        mask, boxes = compare.compare(a, b)
        h = compare.highlight(b, mask, boxes)
        self.assertEqual(h.size, b.size)
        self.assertEqual(h.getpixel((300 - 4, 220)), compare.DIFF_RGB)     # red box just outside the change
        self.assertNotEqual(h.getpixel((320, 220)), b.getpixel((320, 220)))   # changed pixels are tinted
        self.assertEqual(h.getpixel((5, 5)), b.getpixel((5, 5)))              # the rest is untouched
        sbs = compare.side_by_side(a, h, 16)
        self.assertEqual(sbs.size, (800 * 2 + 16, 500))
        self.assertEqual(compare.pad_to(Image.new("RGB", (10, 10)), (20, 15)).size, (20, 15))


if __name__ == "__main__":
    unittest.main()
