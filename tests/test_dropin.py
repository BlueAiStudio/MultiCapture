"""Platform-independent tests for pictures brought in from outside (drag & drop) and laid over a screenshot."""
import base64
import io
import os
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

import dropin  # noqa: E402


def write(p, data):
    with open(p, "wb") as f:
        f.write(data)


def png_bytes(size=(40, 20), color=(255, 0, 0, 255)):
    b = io.BytesIO()
    Image.new("RGBA", size, color).save(b, "PNG")
    return b.getvalue()


class DropTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="mc_drop_")

    def test_classify(self):
        p = os.path.join(self.dir, "a.png")
        write(p, png_bytes())
        self.assertEqual(dropin.classify(p), ("file", p))
        self.assertEqual(dropin.classify("https://example.com/x.png")[0], "url")
        kind, data = dropin.classify("data:image/png;base64," + base64.b64encode(png_bytes()).decode())
        self.assertEqual(kind, "data")
        self.assertTrue(data.startswith(b"\x89PNG"))
        self.assertEqual(dropin.classify("just some text")[0], None)
        if os.name == "nt":
            self.assertEqual(dropin.classify("file:///C:/Users/x/a%20b.png"), ("file", r"C:\Users\x\a b.png"))

    def test_html(self):
        html = ("Version:0.9\r\nSourceURL:https://example.com/a/page.html\r\n<html><body><!--StartFragment-->"
                '<a href="/x"><img alt="" src="pics/p.png?a=1&amp;b=2"></a><img src=\'//cdn.example.com/q.jpg\'>'
                "<!--EndFragment--></body></html>")
        self.assertEqual(dropin.expand([html]), ["https://example.com/a/pics/p.png?a=1&b=2", "https://cdn.example.com/q.jpg"])
        self.assertEqual(dropin.expand(["a.png\r\nb.png"]), ["a.png", "b.png"])

    def test_load_items(self):
        p = os.path.join(self.dir, "a.png")
        write(p, png_bytes((30, 10)))
        bad = os.path.join(self.dir, "b.png")
        write(bad, b"not a picture")
        uri = "data:image/png;base64," + base64.b64encode(png_bytes((5, 5))).decode()
        out = {}
        done = threading.Event()
        dropin.load_items([p, p, bad, uri, self.dir], lambda i, e: (out.update(i=i, e=e), done.set()))
        self.assertTrue(done.wait(10))
        self.assertEqual([im.size for _, im in out["i"]], [(30, 10), (5, 5)])   # duplicate and folder skipped
        self.assertEqual(len(out["e"]), 1)
        self.assertEqual(out["i"][0][1].mode, "RGBA")

    def test_clipboard(self):
        imgs, errs = dropin.from_clipboard(Image.new("RGB", (3, 4)))
        self.assertEqual(imgs[0][1].size, (3, 4))
        self.assertEqual(dropin.from_clipboard(None), ([], []))

    def test_fit_box(self):
        b = dropin.fit_box(2000, 1000, 1000, 800, 500, 400)
        self.assertAlmostEqual(b[2] - b[0], 450)              # 45 % of the screenshot width
        self.assertAlmostEqual((b[2] - b[0]) / (b[3] - b[1]), 2)
        b = dropin.fit_box(100, 50, 1000, 800, 990, 790)       # small: not enlarged, kept inside
        self.assertEqual(b, [900, 750, 1000, 800])

    def test_keep_ratio(self):
        box = [100, 100, 300, 200]                              # ratio 2
        b = dropin.keep_ratio(box, 2, 500, 210, 2.0)            # bottom-right, top-left fixed
        self.assertEqual(b[:2], [100, 100])
        self.assertAlmostEqual((b[2] - b[0]) / (b[3] - b[1]), 2)
        b = dropin.keep_ratio(box, 0, 500, 500, 2.0)            # dragged past the fixed corner: no flip
        self.assertEqual(b[2:], [300, 200])
        self.assertGreater(b[2] - b[0], 0)

    def test_store(self):
        st = dropin.OverlayStore()
        im = Image.new("RGBA", (64, 32), (0, 128, 255, 255))
        key = st.put(im)                                        # memory only
        self.assertIs(st.get(key), st.mem[key])
        folder = os.path.join(self.dir, "ov")
        st.set_folder(folder)                                   # written once a folder is set
        self.assertTrue(os.path.exists(os.path.join(folder, key + ".png")))
        st2 = dropin.OverlayStore()
        st2.set_folder(folder)
        self.assertEqual(st2.get(key).size, (64, 32))           # reloaded from disk
        half = st2.scaled(key, (16, 16), (0, 0, 32, 32), 50)
        self.assertEqual(half.size, (16, 16))
        self.assertEqual(half.getpixel((5, 5))[3], 127)
        st2.cleanup(set())
        self.assertFalse(os.listdir(folder))
        self.assertEqual(dropin.overlay_keys([{"objs": [{"type": "image", "src": "k"}, {"type": "pen"}]}]), {"k"})


if __name__ == "__main__":
    unittest.main()
