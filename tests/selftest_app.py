"""Starts the real app on Windows with every extra feature switched on and drives each feature once
(used in CI). Run:  python tests/selftest_app.py"""
import json
import os
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["APPDATA"] = tempfile.mkdtemp(prefix="mc_selftest_")       # keep the real settings untouched
os.makedirs(os.path.join(os.environ["APPDATA"], "MultiCapture"))
with open(os.path.join(os.environ["APPDATA"], "MultiCapture", "settings.json"), "w", encoding="utf-8") as f:
    json.dump({"guide_shown": True, "ask_on_close": False, "autocopy": False, "lang": "zh", "mode": "Scrolling",
               "feat_pin": True, "feat_ocr": True, "feat_scroll": True, "feat_record": True,
               "theme": "night"}, f)

import tkinter as tk  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

import extras  # noqa: E402
import multicapture as mc  # noqa: E402


def pump(seconds):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.02)


root = tk.Tk()
app = mc.App(root)
pump(0.5)
assert app._key(app.mode_var, app._mode_keys()) == mc.SCROLL_MODE, app.mode_var.get()
assert len(app.extra_bar.winfo_children()) == 4, "separator + 3 buttons expected"
print("extra buttons OK")
assert app.theme.id == "night" and app.theme.frame, "night theme expected"
framed = app.framed(Image.new("RGB", (400, 300), "white"))
assert framed.width > 400 and framed.height > 300, framed.size
print("theme OK")

img = Image.new("RGB", (640, 200), "white")
ImageDraw.Draw(img).rectangle((20, 20, 300, 80), fill="black")
app._capture_done(img, None)
pump(0.3)
assert app.sel is not None


class Ev:
    def __init__(self, x, y):
        self.x, self.y, self.state = x, y, 0


def at(x, y):
    return Ev(*app.to_canvas(x, y))


# Paint-style tools: fill, picker, eraser, rotate / crop with undo, blank canvas
app.set_color("#43A047")
app.set_tool("fill")
app.on_press(at(10, 10))
app.on_release(at(10, 10))
assert app.final(app.sel).getpixel((10, 10)) == (0x43, 0xA0, 0x47)
app.set_tool("pen")
app.set_tool("picker")
app.on_press(at(100, 50))
app.on_release(at(100, 50))
assert app.color == "#000000" and app.tool.get() == "pen", (app.color, app.tool.get())
app.set_tool("eraser")
app.on_press(at(10, 10))
app.on_drag(at(14, 10))
app.on_release(at(14, 10))
assert app.final(app.sel).getpixel((10, 10)) == (255, 255, 255)
app.image_op("rot_cw")
assert app.sel["size"] == (200, 640)
app.undo()
assert app.sel["size"] == (640, 200)
app.set_tool("crop")
app.on_press(at(10, 10))
app.on_drag(at(310, 90))
app.on_release(at(310, 90))
assert app.sel["size"] == (300, 80), app.sel["size"]
app.undo()


class FakeBlank:
    def __init__(self, *a, **k):
        self.result = (500, 400, "#FFFFFF")


real_blank, mc.BlankDialog = mc.BlankDialog, FakeBlank
app.new_blank()
mc.BlankDialog = real_blank
assert app.sel["size"] == (500, 400) and app.tool.get() == "pen"
app.set_tool("select")
app.select_item(app.items[1])
pump(0.3)
print("paint tools OK")

app.pin_current()
pump(0.3)
assert len(app.pins) == 1
p = app.pins[0]
p.set_zoom(1.5)
p.set_alpha(0.6)
pump(0.2)
p.close()
assert not app.pins
print("pin OK")

d = extras.OcrDialog(root, img)
t0 = time.time()
while d.result is None and time.time() - t0 < 60:
    pump(0.2)
pump(0.3)
print("OCR dialog result:", d.result)
d.win.destroy()

res = {}
sc = extras.ScrollCapture(root, (100, 100, 500, 400), lambda im, err: res.update(im=im, err=err), auto=False)
pump(1.5)
sc.finish()
assert res.get("im") is not None and res["im"].width == 400, res
print("scrolling capture OK", res["im"].size)

out = {}
rec = extras.GifRecorder(root, (100, 100, 420, 340), lambda r: out.update(rec=r), fps=10)
pump(1.5)
rec.stop()
r = out["rec"]
assert r is not None and r.frames, "no frames recorded"
path = os.path.join(os.environ["APPDATA"], "test.gif")
extras.save_gif(r, path)
with Image.open(path) as g:
    print("recording OK", g.size, g.n_frames, "frames")

app.feat["feat_scroll"].set(False)
app._features_changed()
assert app._key(app.mode_var, mc.ALL_MODES) == "Region"
for k, _ in mc.FEATURES:
    app.feat[k].set(False)
app._features_changed()
assert not app.extra_bar.winfo_children(), "features off -> no extra buttons"
print("switching features off OK")

app._shutdown()
print("ALL OK")
