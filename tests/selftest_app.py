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
import report  # noqa: E402
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

# pseudo-3D: rectangle -> box, with a pocket, and back
box = app._new_obj("rect", box=[40, 40, 160, 120])
app.sel["objs"].append(box)
app.select_obj(box)
app.toggle_solid()
assert box.get("solid") and len(mc.handles(box)) == 5
mc.set_handle(box, 4, 200, 10)
assert box["solid"]["depth"] > 0
app.solid_cut.set(True)
app.toggle_cut()
assert box["solid"]["cut"]
app.sel["_final"] = None
exported = app.final(app.sel)
assert exported.getpixel((100, 100))[:3] != (255, 255, 255), "box not flattened into the export"
pump(0.2)
app.toggle_solid()
assert "solid" not in box
app.sel["objs"].remove(box)
app.select_obj(None)
print("3D shapes OK")

class Ev:
    def __init__(self, x, y, state=0):
        self.x, self.y, self.state = x, y, state


class Key:
    def __init__(self, keysym, state=0):
        self.keysym, self.state = keysym, state


def at(x, y, state=0):
    return Ev(*app.to_canvas(x, y), state)


SHIFT, CTRL = 0x1, 0x4


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

# Selecting several annotations: Ctrl / Shift + click, Shift + drag a box, Ctrl+A; move / colour / delete together
it = app.sel
kept = (it["objs"], list(it["undo"]), list(it["redo"]))
it["objs"], it["undo"], it["redo"] = [], [], []
app.set_tool("select")
app.render()
r1 = app._new_obj("rect", box=[20, 20, 60, 60])
r2 = app._new_obj("rect", box=[100, 20, 140, 60])
ln = app._new_obj("line", p=[[200, 30], [260, 30]])
it["objs"] += [r1, r2, ln]
app.on_press(at(20, 40))
app.on_release(at(20, 40))
assert app.selected_objs() == [r1], app.selected_objs()
app.on_press(at(100, 40, CTRL))
app.on_release(at(100, 40, CTRL))
assert app.selected_objs() == [r1, r2]
app.on_press(at(20, 40))                       # plain press on one of them keeps both and drags both
app.on_drag(at(30, 50))
app.on_release(at(30, 50))
assert r1["box"] == [30, 30, 70, 70] and r2["box"] == [110, 30, 150, 70] and ln["p"][0] == [200, 30], (r1, r2)
app.undo()                                      # one undo step for the whole group
r1, r2, ln = it["objs"]
assert r1["box"] == [20, 20, 60, 60] and r2["box"] == [100, 20, 140, 60]
assert app.selected_objs() == []
app.on_press(at(190, 10, SHIFT))                # Shift + drag on empty space: selection box
app.on_drag(at(270, 50, SHIFT))
app.render()
app.on_release(at(270, 50, SHIFT))
assert app.selected_objs() == [ln], app.selected_objs()
app.on_press(at(5, 5, SHIFT))
app.on_drag(at(280, 80, SHIFT))
app.on_release(at(280, 80, SHIFT))
assert app.selected_objs() == [r1, r2, ln]
app.render()
assert "annotations" in app.sel_lbl.cget("text") or "标注" in app.sel_lbl.cget("text"), app.sel_lbl.cget("text")
old = r1["color"]
app.set_color("#123456")
assert all(o["color"] == "#123456" for o in it["objs"])
app.undo()
assert all(o["color"] == old for o in it["objs"])
app.on_key(Key("a", CTRL))                      # Ctrl+A
assert len(app.selected_objs()) == 3
app.on_key(Key("Right"))
assert it["objs"][0]["box"][0] > 20
app.undo()
app.select_all_objs()
app.dup_obj()
assert len(it["objs"]) == 6 and len(app.selected_objs()) == 3 and app.selected_objs()[0] is it["objs"][3]
app.on_key(Key("Delete"))
assert len(it["objs"]) == 3
app.select_all_objs()
r1 = it["objs"][0]
app.on_press(at(20, 40, SHIFT))                 # Shift + click on a selected one takes it out
app.on_release(at(20, 40, SHIFT))
assert len(app.selected_objs()) == 2 and r1 not in app.selected_objs()
app.obj_back()
assert it["objs"][2] is r1
app.on_key(Key("Escape"))
assert app.selected_objs() == []
tb = app._new_table(30, 100)                    # table size through the shared property code
it["objs"].append(tb)
app.select_obj(tb)
rows_before = app.table_rows.get()
app.table_rows.set(5)
app.on_prop("table_size")
assert len(tb["rh"]) == 5, len(tb["rh"])
app.select_obj(None)
app.table_rows.set(rows_before)                 # later tests expect the default table size
app.on_prop("table_size")
assert app.st["table_rows"] == rows_before
it["objs"], it["undo"], it["redo"] = kept
app.changed()
print("multi-select annotations OK")

# Selecting several screenshots in the history: Ctrl + click toggles, Shift + click takes a range
items = list(app.items)                         # newest first; the capture and the blank canvas
assert len(items) >= 2, len(items)
app.select_item(items[0])
app._card_click(Ev(0, 0, CTRL), items[1])
assert app.picked_items() == items[:2] and app.sel is items[1]
calls = []
real_cmp, app.open_compare = app.open_compare, lambda a, b: calls.append((a, b))
app.compare_selected()                          # two selected: compare exactly those, older one first
app.open_compare = real_cmp
assert calls == [(items[1], items[0])], calls
app._card_click(Ev(0, 0, CTRL), items[0])       # Ctrl + click again takes it out
assert app.picked_items() == [items[1]]
app.select_item(items[0])
app._card_click(Ev(0, 0, SHIFT), items[-1])     # Shift + click: the whole range
assert app.picked_items() == items
board_before = list(app.board)
app._picked_board(app.picked_items())
assert app.board[-len(items):] == list(reversed(items)), [b["num"] for b in app.board]
out = tempfile.mkdtemp(prefix="mc_multi_")
real_dir, mc.filedialog.askdirectory = mc.filedialog.askdirectory, lambda **k: out
app.save_all_png(app.picked_items())
mc.filedialog.askdirectory = real_dir
assert len(os.listdir(out)) == len(items), os.listdir(out)
app.on_key(Key("Escape"))
assert len(app.picked_items()) == 1
app._card_click(Ev(0, 0, CTRL), items[0])
app._card_click(Ev(0, 0), items[1])             # plain click: only that one again
assert app.picked_items() == [items[1]]
app.board[:] = board_before
app._save_board()
pump(0.2)
print("multi-select history OK")

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
assert extras.find_ffmpeg(), "ffmpeg (imageio-ffmpeg) not found"
print("audio package:", extras.audio_available())
for snd in (False, True):          # with sound on, a machine without audio devices must still record
    out = {}
    rec = extras.VideoRecorder(root, (100, 100, 421, 341), lambda t: out.update(take=t), fps=10,
                               mic=snd, system=snd)
    pump(2.0)
    rec.stop()
    take = out["take"]
    assert take is not None and not getattr(take, "error", None), getattr(take, "error", None)
    path = os.path.join(os.environ["APPDATA"], f"test_{snd}.mp4")
    extras.save_video(take, path)
    assert os.path.getsize(path) > 500
    print("MP4 OK", "sound" if snd else "silent", round(take.duration, 1), "s", len(take.audio), "track(s)",
          os.path.getsize(path), "bytes", ascii(take.notes))

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

# board report: PDF, Word and the measurement table
it = app.sel
it["objs"].append({"id": "m1", "type": "dist", "color": "#DC2626", "width": 3, "fs": 14, "p": [[20, 100], [220, 100]]})
it["objs"].append({"id": "m2", "type": "area", "color": "#2563EB", "width": 3, "fs": 14, "fill_alpha": 25,
                   "pts": [[10, 10], [110, 10], [110, 60]]})
it["notes"] = "报告测试 report test"
it["_final"] = None
rows = app.measure_rows(it)
assert [r[0] for r in rows] == ["距离", "面积", "周长"], rows
assert rows[0][1:3] == ("200", "px"), rows
entries = app.report_entries([it])
rp = os.path.join(os.environ["APPDATA"], "report.pdf")
report.write_pdf(rp, report.pdf_pages("测试报告", entries, app.report_labels(), font=mc.frame_font))
report.write_docx(rp[:-4] + ".docx", "测试报告", entries, app.report_labels())
assert os.path.getsize(rp) > 1000 and os.path.getsize(rp[:-4] + ".docx") > 1000
app.copy_measure_table()
assert root.clipboard_get().splitlines()[0].split("\t") == list(app.table_header())
print("board report OK")

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

# table: create, type into two cells, Tab adds a row in the last cell
app.set_view("Single")
app.select_item(app.items[-1])
app.set_tool("table")
o = app._new_table(30, 30)
app.push_undo()
app.sel["objs"].append(o)
o["box"] = [30, 30, 230, 120]
app.select_obj(o)
app.start_cell_edit(o, 0, 0)
app.cell_edit["w"].insert("1.0", "项目 Ø12")
app._cell_step(1)
app.insert_symbol("✓")
for _ in range(len(o["rh"]) * len(o["cw"]) - 1):
    app._cell_step(1)
app.commit_edit()
pump(0.2)
assert o["cells"][0] == ["项目 Ø12", "✓"], o["cells"]
assert len(o["rh"]) == 4, len(o["rh"])
app.final(app.sel)
app.show_symbols()
pump(0.3)
app.sym_win.destroy()
app.set_tool("select")
print("table OK")

# Undo / redo buttons in the top bar: greyed when there is nothing to undo / redo
it = app.sel
n = len(it["objs"])
it["redo"].clear()
app._update_undo_btns()
assert app.undo_btn._enabled and not app.redo_btn._enabled
app.undo_btn._click(None)
pump(0.1)
assert app.redo_btn._enabled
app.redo_btn._click(None)
pump(0.1)
assert len(it["objs"]) == n and not app.redo_btn._enabled
it["undo"].clear()
app._update_undo_btns()
assert not app.undo_btn._enabled
app.undo_btn._click(None)       # greyed: does nothing
assert len(it["objs"]) == n
print("undo / redo buttons OK")

root.state("zoomed")              # a maximized window stays maximized after a capture
pump(0.3)
app._hide_windows()
pump(0.3)
app._capture_done(None, None)
pump(0.5)
assert root.state() == "zoomed", root.state()
root.state("normal")
pump(0.3)
app._hide_windows()
pump(0.3)
app._capture_done(None, None)
pump(0.5)
assert root.state() == "normal", root.state()
print("stays maximized after capture OK")

# a window saved on a bigger screen is pulled back inside the work area
assert mc.fit_geometry("1440x880+600+400", (0, 0, 1366, 728)) == "1366x696+0+0", mc.fit_geometry("1440x880+600+400", (0, 0, 1366, 728))
assert mc.fit_geometry("1000x600+100+50", (0, 0, 1920, 1040)) == "1000x600+100+50"
assert mc.fit_geometry("1000x600+-8+-8", (0, 0, 1920, 1040)) == "1000x600+0+0"
assert mc.fit_geometry("1000x600+2500+50", (1920, 0, 3840, 1040)) == "1000x600+2500+50"
assert mc.fit_geometry("garbage", (0, 0, 100, 100)) == "garbage"
print("window kept on screen OK")

# the header switches to icons only when it does not fit, and back
full = {w: w.cget("text") for w in app._head_labels()}
app._set_head_compact(True)
pump(0.2)
assert app.save_btn.cget("text") != full[app.save_btn]
app._set_head_compact(False)
pump(0.2)
assert all(w.cget("text") == t for w, t in full.items())
root.geometry(f"{root.minsize()[0]}x700")
pump(0.5)
app._fit_header()
pump(0.3)
assert app.head.winfo_reqwidth() <= app.head.winfo_width() + 2, (app.head.winfo_reqwidth(), app.head.winfo_width())
print("header fits a narrow window OK", "compact" if app._head_compact else "full")

app._shutdown()
print("ALL OK")
