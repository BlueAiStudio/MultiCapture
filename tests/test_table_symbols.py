"""Tests for the table annotation and the symbol font fallback."""
import ctypes
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not hasattr(ctypes, "windll"):        # lets the tests run on Linux / macOS too
    class _Any:
        def __getattr__(self, n):
            return _Any()

        def __call__(self, *a, **k):
            return 0
    ctypes.windll = _Any()

from PIL import Image  # noqa: E402

import multicapture as mc  # noqa: E402


def table(rows=3, cols=2):
    return mc.make_table([100, 50, 300, 140], rows, cols, id="t1", color="#E53935", width=2, size=16,
                         family="Segoe UI", align="left")


class TableTest(unittest.TestCase):
    def test_edges_and_cells(self):
        o = table()
        xs, ys = mc.table_edges(o)
        self.assertEqual(xs, [100, 200, 300])
        self.assertEqual(ys, [50, 80, 110, 140])
        self.assertEqual(mc.table_cell_at(o, 150, 60), (0, 0))
        self.assertEqual(mc.table_cell_at(o, 250, 130), (2, 1))
        self.assertIsNone(mc.table_cell_at(o, 99, 60))
        self.assertEqual(mc.table_cell_box(o, 1, 1), (200, 80, 300, 110))

    def test_set_size_keeps_text_and_grows(self):
        o = table()
        o["cells"][0][0] = "A"
        o["cells"][2][1] = "Z"
        mc.table_set_size(o, 4, 3)
        self.assertEqual(len(o["cells"]), 4)
        self.assertTrue(all(len(r) == 3 for r in o["cells"]))
        self.assertEqual(o["cells"][0][0], "A")
        self.assertEqual(o["cells"][2][1], "Z")
        self.assertAlmostEqual(o["box"][2] - o["box"][0], 300)    # one more 100 px column
        self.assertAlmostEqual(o["box"][3] - o["box"][1], 120)
        mc.table_set_size(o, 1, 1)
        self.assertEqual(o["cells"], [["A"]])
        self.assertAlmostEqual(sum(o["cw"]), 1)

    def test_insert_delete(self):
        o = table()
        o["cells"][1] = ["b0", "b1"]
        self.assertTrue(mc.table_insert(o, "row", 1))
        self.assertEqual(o["cells"][1], ["", ""])
        self.assertEqual(o["cells"][2], ["b0", "b1"])
        self.assertTrue(mc.table_insert(o, "col", 0))
        self.assertEqual(o["cells"][2], ["", "b0", "b1"])
        self.assertTrue(mc.table_delete(o, "col", 0))
        self.assertTrue(mc.table_delete(o, "row", 1))
        self.assertEqual(o["cells"][1], ["b0", "b1"])
        one = table(1, 1)
        self.assertFalse(mc.table_delete(one, "row", 0))
        self.assertFalse(mc.table_delete(one, "col", 0))

    def test_inner_line_handle(self):
        o = table()
        hs = mc.handles(o)
        self.assertEqual(len(hs), 4 + 1 + 2)
        mc.set_handle(o, 4, 240, 0)                # first column now 140 px wide
        xs, _ = mc.table_edges(o)
        self.assertAlmostEqual(xs[1], 240)
        self.assertEqual(xs[-1], 300)
        mc.set_handle(o, 4, 1000, 0)               # cannot cross the next line
        self.assertLess(mc.table_edges(o)[0][1], 300)

    def test_fit_grows_only(self):
        o = table()
        before = list(o["box"])
        mc.table_fit(o)
        self.assertEqual(o["box"], before)
        o["cells"][1][0] = "a much longer text that does not fit\nand a second line\nand a third line"
        self.assertTrue(mc.table_fit(o))
        self.assertGreater(o["box"][2] - o["box"][0], 200)
        self.assertGreater(o["box"][3] - o["box"][1], 90)

    def test_draw_and_move(self):
        o = table()
        o["cells"][0] = ["Item", "Ø12 ±0.05"]
        o["cells"][1] = ["OK ✓", "→ ⚠"]
        img = Image.new("RGBA", (400, 200), "white")
        mc.draw_objects(img, [o], 1.0, 0, 0, (1.0, "px"))
        self.assertNotEqual(img.getpixel((100, 95)), (255, 255, 255, 255))     # outer line drawn
        self.assertTrue(mc.hit_obj(o, 150, 100, 2))
        mc.move_obj(o, 10, 5)
        self.assertEqual(o["box"][:2], [110, 55])
        self.assertEqual(mc.obj_bbox(o), [110, 55, 310, 145])


    def test_rotate_keeps_table_upright(self):
        import paint
        o = table()
        out = paint.transform_objs([o], "rot_cw", (400, 200))[0]
        x0, y0, x1, y1 = out["box"]
        self.assertAlmostEqual(x1 - x0, 200)          # same size, not turned on its side
        self.assertAlmostEqual(y1 - y0, 90)
        self.assertAlmostEqual((x0 + x1) / 2, 200 - 95)   # centre (200, 95) -> (H - y, x)
        self.assertAlmostEqual((y0 + y1) / 2, 200)


class SymbolTest(unittest.TestCase):
    def test_runs(self):
        font = mc.pil_font("Segoe UI", 20)[0]
        runs = mc.text_runs("ab → c ✓", font)
        self.assertEqual("".join(t for t, _ in runs), "ab → c ✓")
        self.assertEqual([t for t, f in runs if f is not font], ["→", "✓"])
        self.assertEqual(mc.text_runs("plain ±°Ø", font), [("plain ±°Ø", font)])

    def test_text_with_symbols_renders(self):
        o = {"id": "x1", "type": "text", "x": 5, "y": 5, "text": "Check ✓ → ①", "size": 20, "color": "#000000"}
        img = Image.new("RGBA", (300, 60), "white")
        mc.draw_objects(img, [o], 1.0, 0, 0, (1.0, "px"))
        self.assertIsNotNone(Image.eval(img.convert("L"), lambda v: 255 - v).getbbox())

    def test_symbol_groups_are_single_characters(self):
        for name, syms in mc.SYMBOL_GROUPS:
            self.assertTrue(syms and all(len(ch) == 1 for ch in syms), name)


if __name__ == "__main__":
    unittest.main()
