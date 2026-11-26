"""Tests for the Paint-style tools (fill bucket, eraser, rotate / flip / crop / resize with annotations)."""
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw  # noqa: E402

import paint  # noqa: E402


def picture():
    im = Image.new("RGB", (400, 300), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((50, 50, 250, 200), outline="black", width=3)
    d.ellipse((100, 90, 180, 150), outline="red", width=2)
    return im


class FloodFill(unittest.TestCase):
    def test_inside_rectangle_stops_at_borders(self):
        m, x, y = paint.flood_mask(picture(), 60, 60)
        self.assertEqual((x, y), (53, 53))                 # just inside the 3 px border
        self.assertEqual(m.size, (195, 145))
        self.assertEqual(m.getpixel((140 - x, 120 - y)), 0)   # inside the ellipse: a separate area
        self.assertEqual(m.getpixel((60 - x, 60 - y)), 255)

    def test_outside_and_on_line(self):
        m, x, y = paint.flood_mask(picture(), 5, 5)
        self.assertEqual((x, y, m.size), (0, 0, (400, 300)))
        self.assertEqual(m.getpixel((150, 120)), 0)
        m, x, y = paint.flood_mask(picture(), 51, 120)    # on the black border: only the border
        self.assertEqual(m.getpixel((51 - x, 120 - y)), 255)
        self.assertLessEqual(m.size[0], 201)

    def test_tolerance_and_outside_point(self):
        im = Image.new("RGB", (50, 50), (200, 200, 200))
        ImageDraw.Draw(im).rectangle((0, 0, 24, 49), fill=(210, 205, 200))
        self.assertEqual(paint.flood_mask(im, 40, 10)[0].size, (50, 50))       # small differences are filled
        self.assertEqual(paint.flood_mask(im, 40, 10, tol=0)[0].size, (25, 50))
        self.assertIsNone(paint.flood_mask(im, 80, 10))

    def test_fast_on_full_hd(self):
        im = Image.new("RGB", (1920, 1080), "white")
        d = ImageDraw.Draw(im)
        for i in range(0, 1920, 40):
            d.line((i, 0, i + 30, 1079), fill="blue")
        t = time.time()
        paint.flood_mask(im, 1900, 5)
        paint.flood_mask(im, 2, 1075)
        self.assertLess(time.time() - t, 3)

    def test_mask_round_trip_and_hit(self):
        m, x, y = paint.flood_mask(picture(), 60, 60)
        s = paint.mask_to_str(m)
        self.assertEqual(paint.mask_from_str(s).tobytes(), m.tobytes())
        o = {"type": "fill", "x": x, "y": y, "mask": s, "color": "#FF0000"}
        self.assertTrue(paint.fill_hit(o, 60, 60))
        self.assertFalse(paint.fill_hit(o, 140, 120))
        self.assertFalse(paint.fill_hit(o, 5, 5))

    def test_draw_fill_scaled(self):
        m, x, y = paint.flood_mask(picture(), 60, 60)
        o = {"type": "fill", "x": x, "y": y, "mask": paint.mask_to_str(m), "color": "#FF0000"}
        for s in (1.0, 0.5, 2.0):
            img = Image.new("RGBA", (int(400 * s), int(300 * s)), "white")
            paint.draw_fill(img, o, s, lambda a, b: (a * s, b * s))
            self.assertEqual(img.getpixel((int(60 * s), int(60 * s)))[:3], (255, 0, 0))
            self.assertEqual(img.getpixel((int(140 * s), int(120 * s)))[:3], (255, 255, 255))
        # a zoomed-in view that shows only a piece of the fill, offset by (100, 80)
        img = Image.new("RGBA", (100, 100), "white")
        paint.draw_fill(img, o, 4.0, lambda a, b: ((a - 190) * 4, (b - 160) * 4))
        self.assertEqual(img.getpixel((50, 50))[:3], (255, 0, 0))


class Eraser(unittest.TestCase):
    def test_stroke_split(self):
        pts = [[x, 10] for x in range(0, 101, 5)]
        self.assertIsNone(paint.erase_stroke(pts, 50, 50, 8))
        pieces = paint.erase_stroke(pts, 50, 10, 8)
        self.assertEqual(len(pieces), 2)
        self.assertEqual(pieces[0][-1], [40, 10])
        self.assertEqual(pieces[1][0], [60, 10])
        self.assertEqual(paint.erase_stroke([[0, 0]], 0, 0, 3), [])

    def test_erase_fill(self):
        m, x, y = paint.flood_mask(picture(), 60, 60)
        o = {"type": "fill", "x": x, "y": y, "mask": paint.mask_to_str(m), "color": "#FF0000"}
        self.assertFalse(paint.erase_fill(o, [(5, 5)], 3))
        self.assertTrue(paint.erase_fill(o, [(60, 60)], 4))
        self.assertFalse(paint.fill_hit(o, 60, 60))
        self.assertTrue(paint.fill_hit(o, 200, 180))
        tiny = {"type": "fill", "x": 0, "y": 0, "mask": paint.mask_to_str(Image.new("L", (4, 4), 255)), "color": "#000"}
        self.assertTrue(paint.erase_fill(tiny, [(2, 2)], 10))
        self.assertIsNone(tiny["mask"])


class ImageOps(unittest.TestCase):
    objs = [{"type": "rect", "box": [10, 20, 50, 40], "width": 3},
            {"type": "arrow", "p": [[0, 0], [100, 50]], "width": 3},
            {"type": "marker", "x": 30, "y": 30, "size": 20, "n": 1},
            {"type": "text", "x": 10, "y": 10, "size": 20, "leader": [5, 5]}]

    @staticmethod
    def size(o):
        return 40 * o["size"] / 20, 20 * o["size"] / 20

    def run_op(self, op, arg=None):
        return paint.transform_objs(self.objs, op, (200, 100), arg, self.size)

    def test_rotate_cw(self):
        img = paint.transform_image(Image.new("RGB", (200, 100)), "rot_cw")
        self.assertEqual(img.size, (100, 200))
        r, a, mk, t = self.run_op("rot_cw")
        self.assertEqual(r["box"], [60, 10, 80, 50])
        self.assertEqual(a["p"], [[100, 0], [50, 100]])
        self.assertEqual((mk["x"], mk["y"]), (70, 30))
        # text centre (30, 20) -> (80, 30); box stays upright 40 x 20
        self.assertEqual((t["x"], t["y"]), (60, 20))
        self.assertEqual(t["leader"], [95, 5])
        self.assertEqual(self.objs[0]["box"], [10, 20, 50, 40], "input must not change")

    def test_rotate_pixels_match_points(self):
        im = Image.new("RGB", (200, 100), "white")
        im.putpixel((30, 10), (255, 0, 0))
        for op in ("rot_cw", "rot_ccw", "rot180", "flip_h", "flip_v"):
            out = paint.transform_image(im, op)
            o = paint.transform_objs([{"type": "marker", "x": 30.5, "y": 10.5}], op, im.size)[0]
            self.assertEqual(out.getpixel((int(o["x"]), int(o["y"]))), (255, 0, 0), op)

    def test_rotate_four_times_is_identity(self):
        objs = self.objs
        size = (200, 100)
        for _ in range(4):
            objs = paint.transform_objs(objs, "rot_ccw", size, None, self.size)
            size = size[::-1]
        for a, b in zip(objs, self.objs):
            self.assertEqual(a, b)

    def test_crop_and_resize(self):
        r, a, mk, t = self.run_op("crop", (10, 10, 110, 60))
        self.assertEqual(r["box"], [0, 10, 40, 30])
        self.assertEqual((mk["x"], mk["y"]), (20, 20))
        r, a, mk, t = self.run_op("resize", (100, 50))
        self.assertEqual(r["box"], [5, 10, 25, 20])
        self.assertEqual(r["width"], 1.5)
        self.assertEqual(mk["size"], 10)
        self.assertEqual((t["x"], t["y"]), (5, 5))       # centre (30, 20) -> (15, 10), size 20 x 10

    def test_fill_follows(self):
        im = picture()
        m, x, y = paint.flood_mask(im, 60, 60)
        fill = {"type": "fill", "x": x, "y": y, "mask": paint.mask_to_str(m), "color": "#00F"}
        for op, arg in (("rot_cw", None), ("flip_h", None), ("crop", (40, 40, 300, 250)), ("resize", (200, 150))):
            out = paint.transform_image(im, op, arg)
            o = paint.transform_objs([fill], op, im.size, arg)[0]
            px, py = (60, 60)
            q = paint.transform_objs([{"type": "marker", "x": px, "y": py}], op, im.size, arg)[0]
            self.assertTrue(paint.fill_hit(o, q["x"], q["y"]), op)
            self.assertEqual(out.size[0] >= paint.mask_from_str(o["mask"]).width, True)


if __name__ == "__main__":
    unittest.main()
