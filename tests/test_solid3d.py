"""Unit tests for the pseudo-3D shapes (pure geometry + PIL, runs anywhere)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

import solid3d  # noqa: E402


def ident(x, y):
    return x, y


class SolidTests(unittest.TestCase):
    def test_box_render_and_hit(self):
        o = solid3d.make_solid({"type": "rect", "box": [50, 80, 150, 160], "color": "#1E88E5", "width": 3})
        self.assertEqual(o["fill"], "#1E88E5")
        img = Image.new("RGBA", (300, 250), "white")
        solid3d.d_solid(img, o, 1, ident)
        self.assertNotEqual(img.getpixel((100, 120))[:3], (255, 255, 255))     # front face
        hx, hy = solid3d.solid_handle(o)
        self.assertTrue(hx > 100 and hy < 120)                                   # default: up-right
        self.assertTrue(solid3d.solid_hit(o, hx, hy, 2))                         # back face hits too
        self.assertFalse(solid3d.solid_hit(o, 280, 240, 2))

    def test_handle_sets_depth_and_angle(self):
        o = solid3d.make_solid({"type": "ellipse", "box": [0, 0, 100, 40], "color": "#E53935", "width": 2})
        self.assertEqual(o["solid"]["ang"], 270)                                 # cylinder stands up
        solid3d.set_solid_handle(o, 50, 20 + 60)                                 # straight down 60 px
        self.assertAlmostEqual(o["solid"]["depth"], 60, delta=0.5)
        self.assertEqual(o["solid"]["ang"], 270)
        solid3d.set_solid_handle(o, 50 + 30, 20 - 31)                            # ~46 deg snaps to 45
        self.assertEqual(o["solid"]["ang"], 45)

    def test_prism_with_pocket(self):
        o = solid3d.make_solid({"type": "area", "pts": [[40, 40], [140, 50], [120, 140], [30, 120]],
                                "color": "#43A047", "width": 2, "fill_alpha": 25})
        o["solid"]["cut"] = True
        img = Image.new("RGBA", (260, 300), "white")
        solid3d.d_solid(img, o, 2, lambda x, y: (x * 2 - 40, y * 2 - 40))       # zoomed view
        self.assertGreater(len(set(img.getdata())), 5)
        bb = solid3d.solid_bbox(o)
        self.assertLess(bb[1], 41)
        self.assertGreater(bb[3], 140)

    def test_rotate_turns_depth(self):
        import paint
        o = solid3d.make_solid({"type": "rect", "box": [10, 10, 50, 40], "color": "#1E88E5", "width": 2})
        o["solid"].update(depth=20, ang=0)                                       # depth points right
        r = paint.transform_objs([o], "rot_cw", (100, 80))[0]
        self.assertAlmostEqual(r["solid"]["ang"], 270, delta=0.1)                # now points down
        self.assertEqual(o["solid"]["ang"], 0)                                   # original untouched
        f = paint.transform_objs([o], "flip_h", (100, 80))[0]
        self.assertAlmostEqual(f["solid"]["ang"], 180, delta=0.1)


if __name__ == "__main__":
    unittest.main()
