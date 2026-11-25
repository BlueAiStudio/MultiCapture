"""Platform-independent tests for the board report (PDF pages, Word .docx, Excel table)."""
import os
import sys
import tempfile
import unittest
import zipfile
from datetime import datetime
from xml.dom import minidom

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw  # noqa: E402

import report  # noqa: E402

L = {"created": "Created {d}", "shots": "{n} screenshot(s)", "notes": "Notes", "measures": "Measurements",
     "summary": "Measurement summary", "header": ("Screenshot", "No.", "Type", "Value", "Unit"),
     "page": "Page {i} / {n}"}


def entries():
    out = []
    for n, (w, h) in enumerate([(800, 500), (300, 200), (1600, 2400)], 1):
        im = Image.new("RGB", (w, h), "white")
        ImageDraw.Draw(im).rectangle((10, 10, w // 2, h // 2), fill="#2563EB")
        out.append({"title": f"#{n}  ·  2026-11-25 10:0{n}", "image": im,
                    "notes": "" if n == 2 else "Line one\nnote <with> & special \x01 chars 中文",
                    "measures": [] if n == 2 else [("Distance", "12.40", "mm", 1), ("Area", "3.10", "mm²", 2),
                                                   ("Perimeter", "7.00", "mm", 2), ("Angle", "45.0", "°", 3)]})
    return out


class ReportTests(unittest.TestCase):
    def test_table(self):
        rows = report.table_rows(entries())
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0], ("#1", "1", "Distance", "12.40", "mm"))
        self.assertEqual(rows[2][1], "2")          # area and its perimeter share a number
        tsv = report.table_tsv(rows, L["header"])
        lines = tsv.split("\r\n")
        self.assertEqual(lines[0], "Screenshot\tNo.\tType\tValue\tUnit")
        self.assertEqual(len(lines), 10)           # header + 8 rows + trailing empty
        self.assertTrue(all(l.count("\t") == 4 for l in lines[:-1]))

    def test_pdf(self):
        pages = report.pdf_pages("Report", entries(), L, when=datetime(2026, 11, 25, 9, 30))
        self.assertGreaterEqual(len(pages), 3)
        self.assertTrue(all(p.size == (1240, 1754) for p in pages))
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.pdf")
            report.write_pdf(p, pages)
            with open(p, "rb") as f:
                self.assertTrue(f.read(5) == b"%PDF-")

    def test_docx(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.docx")
            report.write_docx(p, "Report & <title>", entries(), L)
            with zipfile.ZipFile(p) as z:
                names = set(z.namelist())
                for n in ("[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/styles.xml",
                          "word/_rels/document.xml.rels", "docProps/core.xml",
                          "word/media/image1.png", "word/media/image3.png"):
                    self.assertIn(n, names)
                for n in names - {x for x in names if x.endswith(".png")}:
                    minidom.parseString(z.read(n))       # every XML part is well-formed
                doc = z.read("word/document.xml").decode("utf-8")
                self.assertIn("Report &amp; &lt;title&gt;", doc)
                self.assertEqual(doc.count("<w:drawing>"), 3)
                self.assertEqual(doc.count("<w:tr>"), 9)  # header + 8 rows
                self.assertNotIn("\x01", doc)


if __name__ == "__main__":
    unittest.main()
