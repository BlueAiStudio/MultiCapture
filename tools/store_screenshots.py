"""Makes the Microsoft Store screenshots (1920 x 1080 PNG) in English, Chinese and French.

Runs the real app on Windows (used in CI), fills it with sample captures and annotations,
grabs the window and puts it on a branded background with a caption.

    python tools/store_screenshots.py [output folder]      (default: dist/store-screenshots)

Each scene runs in its own process, because language and theme are applied at start-up.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080

CAPTIONS = {
    "board": {
        "en": "Every capture is kept — compare them side by side",
        "zh": "每张截图都保留 —— 并排对比，一目了然",
        "fr": "Chaque capture est conservée — comparez-les côte à côte",
    },
    "annotate": {
        "en": "Arrows, boxes, numbered markers and text that stay editable",
        "zh": "箭头、方框、编号和文字，随时可以再修改",
        "fr": "Flèches, cadres, repères numérotés et texte toujours modifiables",
    },
    "themes": {
        "en": "Themes: change the colours, icons and frames",
        "zh": "主题：更换配色、图标和边框",
        "fr": "Thèmes : changez les couleurs, les icônes et les cadres",
    },
}
SCENES = [("board", "default", "2×2"), ("annotate", "default", "Single"), ("themes", "night", "2×2")]
LANGS = ("en", "zh", "fr")


# ----------------------------------------------------------------- sample "captures"
def sample_images():
    from PIL import Image, ImageDraw, ImageFont

    def font(size, bold=False):
        for name in (("segoeuib.ttf" if bold else "segoeui.ttf"), "arial.ttf"):
            try:
                return ImageFont.truetype(os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name), size)
            except OSError:
                pass
        return ImageFont.load_default()

    imgs = []
    # 1. bar chart
    im = Image.new("RGB", (900, 560), "white")
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Monthly sales", fill="#111827", font=font(30, True))
    vals = [42, 65, 51, 88, 73, 96]
    for i, v in enumerate(vals):
        x = 80 + i * 130
        d.rectangle((x, 500 - v * 4, x + 80, 500), fill=["#60A5FA", "#3B82F6", "#2563EB"][i % 3])
        d.text((x + 20, 510), ["Jan", "Feb", "Mar", "Apr", "May", "Jun"][i], fill="#6B7280", font=font(20))
    d.line((60, 500, 860, 500), fill="#9CA3AF", width=2)
    imgs.append(im)
    # 2. line chart
    im = Image.new("RGB", (900, 560), "#F9FAFB")
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Website visits", fill="#111827", font=font(30, True))
    for y in range(120, 520, 80):
        d.line((60, y, 860, y), fill="#E5E7EB", width=1)
    pts = [(60 + i * 80, 460 - int(160 * abs(((i * 7) % 11) / 11 - 0.3)) - i * 18) for i in range(11)]
    d.line(pts, fill="#7C3AED", width=5, joint="curve")
    for p in pts:
        d.ellipse((p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7), fill="white", outline="#7C3AED", width=3)
    imgs.append(im)
    # 3. a form / settings page
    im = Image.new("RGB", (900, 560), "white")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 900, 70), fill="#1F2937")
    d.text((30, 18), "Account settings", fill="white", font=font(28, True))
    for i, lab in enumerate(["Name", "E-mail", "Phone", "Address"]):
        y = 110 + i * 95
        d.text((40, y), lab, fill="#374151", font=font(22))
        d.rounded_rectangle((40, y + 32, 620, y + 76), radius=8, outline="#D1D5DB", width=2)
    d.rounded_rectangle((660, 470, 860, 525), radius=10, fill="#16A34A")
    d.text((722, 482), "Save", fill="white", font=font(24, True))
    imgs.append(im)
    # 4. a "photo": hills and sun
    im = Image.new("RGB", (900, 560))
    d = ImageDraw.Draw(im)
    for y in range(560):
        t = y / 560
        d.line((0, y, 900, y), fill=(int(125 + 120 * t), int(180 + 50 * t), int(250 - 40 * t)))
    d.ellipse((640, 70, 760, 190), fill="#FDE68A")
    d.polygon([(0, 420), (220, 260), (430, 400), (620, 300), (900, 430), (900, 560), (0, 560)], fill="#4D7C0F")
    d.polygon([(0, 480), (300, 380), (600, 470), (900, 400), (900, 560), (0, 560)], fill="#365314")
    imgs.append(im)
    return imgs


# ----------------------------------------------------------------- one scene (child process)
def run_scene(scene, theme, view, lang, out_png):
    appdata = tempfile.mkdtemp(prefix="mc_shots_")
    os.environ["APPDATA"] = appdata
    os.makedirs(os.path.join(appdata, "MultiCapture"))
    with open(os.path.join(appdata, "MultiCapture", "settings.json"), "w", encoding="utf-8") as f:
        json.dump({"guide_shown": True, "ask_on_close": False, "autocopy": False, "lang": lang,
                   "theme": theme, "theme_frame": theme != "default", "view": view,
                   "geometry": "1600x900+40+40", "keep_history": False}, f, ensure_ascii=False)
    sys.path.insert(0, ROOT)
    import tkinter as tk

    from PIL import ImageGrab

    import multicapture as mc

    def pump(seconds):
        end = time.time() + seconds
        while time.time() < end:
            root.update()
            time.sleep(0.02)

    root = tk.Tk()
    app = mc.App(root)
    pump(0.5)
    imgs = sample_images()
    for im in reversed(imgs):
        app._capture_done(im, None)
        pump(0.15)
    it = app.items[0]          # the bar chart
    red = "#EF4444"
    it["objs"] += [
        app._new_obj("rect", box=[455, 105, 575, 505], color=red, width=4, fill=None),
        app._new_obj("arrow", p=[[260, 120], [440, 170]], color=red, width=5),
        app._new_obj("marker", x=600, y=110, n=1, color=red, size=26),
        app._new_obj("text", x=120, y=60, text="Best quarter!", color=red, size=26, bold=True, bg="#FFFFFF",
                     border=True),
    ]
    app.select_item(it)
    app.set_view(view)
    app.changed()
    pump(1.5)
    root.update()
    x, y = root.winfo_rootx(), root.winfo_rooty()
    shot = ImageGrab.grab((x, y, x + root.winfo_width(), y + root.winfo_height()), all_screens=True)
    shot.save(out_png)
    app._shutdown() if hasattr(app, "_shutdown") else root.destroy()


# ----------------------------------------------------------------- framing (parent process)
def compose(window_png, caption, lang, out_png):
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    fonts = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    names = ["msyhbd.ttc", "msyh.ttc", "simhei.ttf"] if lang == "zh" else ["segoeuib.ttf", "arialbd.ttf"]
    fnt = None
    for n in names:
        try:
            fnt = ImageFont.truetype(os.path.join(fonts, n), 54)
            break
        except OSError:
            pass
    fnt = fnt or ImageFont.load_default()

    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    c1, c2 = (37, 99, 235), (124, 58, 237)
    for x in range(W):
        t = x / W
        d.line((x, 0, x, H), fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    tw = d.textlength(caption, font=fnt)
    d.text(((W - tw) / 2, 48), caption, fill="white", font=fnt)

    win = Image.open(window_png).convert("RGB")
    box_w, box_h = W - 160, H - 190
    s = min(box_w / win.width, box_h / win.height, 1.0)
    win = win.resize((int(win.width * s), int(win.height * s)), Image.LANCZOS)
    px, py = (W - win.width) // 2, 150 + (box_h - win.height) // 2
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((px - 6, py + 4, px + win.width + 6, py + win.height + 16),
                                             radius=18, fill=(15, 23, 42, 140))
    bg = Image.alpha_composite(bg.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(18)))
    mask = Image.new("L", win.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, win.width - 1, win.height - 1), radius=12, fill=255)
    bg.paste(win, (px, py), mask)
    bg.convert("RGB").save(out_png)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--scene":
        run_scene(*sys.argv[2:7])
        return
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist", "store-screenshots"))
    raw = os.path.join(out, "raw")
    os.makedirs(raw, exist_ok=True)
    n = 0
    for lang in LANGS:
        os.makedirs(os.path.join(out, lang), exist_ok=True)
        for i, (scene, theme, view) in enumerate(SCENES, 1):
            win = os.path.join(raw, f"{lang}_{scene}.png")
            subprocess.run([sys.executable, os.path.abspath(__file__), "--scene", scene, theme, view, lang, win],
                           check=True, timeout=120)
            dst = os.path.join(out, lang, f"{i}_{scene}.png")
            compose(win, CAPTIONS[scene][lang], lang, dst)
            print("wrote", dst)
            n += 1
    print(f"{n} screenshots in {out}")


if __name__ == "__main__":
    main()
