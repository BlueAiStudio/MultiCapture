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
assert app.theme_random.get() is False
for _ in range(20):
    tid = mc.pick_random_theme(app.themes, "night")
    assert tid in app.themes and tid != "night", tid
assert mc.pick_random_theme({"default": 1}, "default") == "default"
assert mc.pick_random_theme({}, None) is None
print("random theme OK")

img = Image.new("RGB", (640, 200), "white")
ImageDraw.Draw(img).rectangle((20, 20, 300, 80), fill="black")
app._capture_done(img, None)
pump(0.3)
assert app.sel is not None

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

# same-spot recapture on the real screen, then the compare window
first = app.items[0]
first["box"] = [100, 100, 500, 400]
app.st["cmp_after_recapture"] = True
app.recapture(first)
pump(1.5)
assert not app.busy and app.sel is not first, "recapture did not add a screenshot"
assert app.sel["size"] == (400, 300) and app.sel["src"] == first["id"], app.sel
assert app.cmp is not None and app.cmp.b is app.sel
app.cmp.mode.set("side")
app.cmp._mode_changed()
pump(0.3)
assert app.cmp.result_image().width == first["size"][0] + app.cmp.GAP + 400
app.cmp.close()
print("same spot + compare OK")

app._shutdown()
print("ALL OK")
