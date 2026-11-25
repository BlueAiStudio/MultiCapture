"""Checks the Windows-only parts of the optional features on a real Windows machine (used in CI).
Run:  python tests/selftest_windows.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import extras  # noqa: E402

im = extras.grab_box((0, 0, 320, 200))
assert im.size == (320, 200), im.size
print("grab_box OK", im.size, "virtual screen", extras.virtual_screen())

img = Image.new("RGB", (900, 160), "white")
d = ImageDraw.Draw(img)
font = ImageFont.truetype(os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "arial.ttf"), 40)
d.text((20, 20), "Hello MultiCapture 2026", fill="black", font=font)
d.text((20, 90), "Optical character test", fill="black", font=font)
r = extras.run_ocr(img)
print("OCR result:", r)
if r["error"] or r["nolang"]:
    print("OCR not usable on this machine (no OCR language or no WinRT) - skipped")
else:
    assert "MultiCapture" in r["text"], r["text"]
    print("OCR OK")
