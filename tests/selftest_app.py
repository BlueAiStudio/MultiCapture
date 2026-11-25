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

# --- pictures dragged in from outside (the OLE drop itself cannot be simulated; everything after it is)
assert app.dnd and app.drop_targets == 3, f"drop targets: dnd={app.dnd} n={app.drop_targets}"
drop_png = os.path.join(os.environ["APPDATA"], "dropped.png")
Image.new("RGBA", (300, 120), (0, 160, 0, 255)).save(drop_png)
choice = ["merge"]


class FakeDrop:   # stands in for the modal DropDialog
    def __init__(self, master, images, can_overlay, label):
        self.result = choice[0]


real_dialog, mc.DropDialog = mc.DropDialog, FakeDrop
app.set_view("Single")
n_items, n_board = len(app.items), len(app.board)
app.on_drop([drop_png])
pump(1.0)
assert len(app.items) == n_items + 1 and len(app.board) == n_board + 1, "merge: added to the board"
assert app.view_n() != 1, "merge switches to a board view"
print("drop merge OK")

choice[0] = "solo"
app.on_drop([drop_png])
pump(1.0)
solo = app.sel
assert solo.get("solo") and solo not in app.board and app.view_n() == 1, "solo: kept out of the board"
print("drop solo OK")

choice[0] = "overlay"
base = app.sel
app.on_drop([drop_png])
pump(1.0)
o = app.sel_obj
assert o and o["type"] == "image" and o in base["objs"], "overlay object expected"
fin = app.final(base)
cx, cy = int((o["box"][0] + o["box"][2]) / 2), int((o["box"][1] + o["box"][3]) / 2)
assert fin.getpixel((cx, cy)) == (0, 160, 0), fin.getpixel((cx, cy))
app.undo()
assert not [x for x in base["objs"] if x["type"] == "image"], "undo removes the overlay"
app.redo()
assert [x for x in base["objs"] if x["type"] == "image"], "redo restores it"
print("drop overlay OK")
mc.DropDialog = real_dialog

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
