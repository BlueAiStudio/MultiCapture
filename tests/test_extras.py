"""Platform-independent tests for the optional features (stitching, OCR text tidy-up, GIF writing)."""
import os
import random
import sys
import tempfile
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
    for mod in ("PIL.ImageTk",):
        sys.modules[mod] = types.ModuleType(mod)

import extras  # noqa: E402


def page(w=500, h=3000, seed=1):
    """A long 'document': text-like blocks of varying width with blank gaps."""
    rnd = random.Random(seed)
    im = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(im)
    y = 10
    while y < h - 20:
        lh = rnd.randint(8, 16)
        x = 10
        while x < w - 60:
            ww = rnd.randint(10, 60)
            d.rectangle((x, y, x + ww, y + lh), fill=(rnd.randint(0, 120),) * 3)
            x += ww + rnd.randint(4, 14)
        y += lh + rnd.randint(4, 20)
    return im


def window(doc, top, view_h, header=0, footer=0):
    """What a scrolled viewport shows: optional fixed header / footer bars."""
    w = doc.width
    out = Image.new("RGB", (w, view_h), "white")
    out.paste(doc.crop((0, top, w, top + view_h - header - footer)), (0, header))
    if header:
        out.paste(Image.new("RGB", (w, header), (30, 60, 200)), (0, 0))
        ImageDraw.Draw(out).text((8, 4), "HEADER", fill="white")
    if footer:
        out.paste(Image.new("RGB", (w, footer), (200, 60, 30)), (0, view_h - footer))
        ImageDraw.Draw(out).text((8, view_h - footer + 4), "FOOTER", fill="white")
    return out


class StitchTest(unittest.TestCase):
    def run_case(self, header, footer, steps):
        doc = page()
        vh = 400
        inner = vh - header - footer
        st = extras.Stitcher(window(doc, 0, vh, header, footer))
        top = 0
        for s in steps:
            top = min(top + s, doc.height - inner)
            r = st.add(window(doc, top, vh, header, footer))
            self.assertIn(r, ("added", "same"))
        res = st.result()
        expect_h = header + top + inner + footer
        self.assertEqual(res.height, expect_h)
        self.assertEqual(res.crop((0, header, doc.width, header + top + inner)).tobytes(),
                         doc.crop((0, 0, doc.width, top + inner)).tobytes())

    def test_plain(self):
        self.run_case(0, 0, [120, 90, 150, 200, 37, 1])

    def test_header_footer(self):
        self.run_case(40, 30, [100, 100, 133, 250, 80])

    def test_end_of_page(self):
        self.run_case(0, 0, [300] * 15)     # last steps hit the bottom and do not move

    def test_identical(self):
        im = page(h=400)
        self.assertEqual(extras.find_shift(extras.row_sigs(im), extras.row_sigs(im))[0], 0)

    def test_lost(self):
        doc = page()
        st = extras.Stitcher(window(doc, 0, 400))
        self.assertEqual(st.add(window(doc, 1500, 400)), "lost")


class OcrTextTest(unittest.TestCase):
    def test_cjk_spaces(self):
        self.assertEqual(extras.tidy_ocr_line("截 图 工 具 MultiCapture v1 . 4"), "截图工具 MultiCapture v1 . 4")

    def test_parse(self):
        r = extras.parse_ocr_output("##LANGS:en-US|zh-Hans-CN\n##USED:zh-Hans-CN\n你 好\nHello world\n")
        self.assertEqual(r["langs"], ["en-US", "zh-Hans-CN"])
        self.assertEqual(r["used"], "zh-Hans-CN")
        self.assertEqual(r["text"], "你好\nHello world")

    def test_chunks(self):
        parts = extras.ocr_chunks(page(w=800, h=9000))
        self.assertTrue(all(p.height <= extras.OCR_MAX_SIDE and p.width <= extras.OCR_MAX_SIDE for p in parts))
        self.assertEqual(sum(p.height for p in parts), 9000)


class GifTest(unittest.TestCase):
    def test_save(self):
        import zlib
        rec = extras.Recording((60, 40))
        for i in range(5):
            rec.frames.append(zlib.compress(Image.new("RGB", (60, 40), (i * 40, 0, 0)).tobytes(), 1))
            rec.times.append(i * 0.1)
        rec.end = 0.5
        p = os.path.join(tempfile.mkdtemp(), "t.gif")
        extras.save_gif(rec, p)
        with Image.open(p) as g:
            self.assertEqual(g.n_frames, 5)
            self.assertEqual(g.size, (60, 40))


if __name__ == "__main__":
    unittest.main()
