# -*- coding: utf-8 -*-
"""Checks the theme folders in themes/ (run by the GitHub build, or by hand before uploading a theme).

    python tools/check_themes.py            check every folder in themes/
    python tools/check_themes.py my-theme   check one folder (any path)

Errors (the theme cannot be used) make the script fail. Warnings point at likely typos.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import themes  # noqa: E402

KNOWN_TOP = {"format", "id", "name", "author", "version", "description", "colors", "icons", "preview",
             "decorations", "frame", "min_app", "license", "homepage"}
KNOWN_FRAME = {"image", "slice", "inset", "edges", "scale", "ref_size", "margin", "canvas", "padding",
               "background", "radius", "border", "shadow", "titlebar", "caption", "ornaments"}


def images_in(meta):
    """Every image path theme.json refers to."""
    out = []
    for k in ("preview",):
        if isinstance(meta.get(k), str):
            out.append(meta[k])
    for v in (meta.get("icons") or {}).values():
        out.append(v)
    for v in (meta.get("decorations") or {}).values():
        out.append(v if isinstance(v, str) else (v or {}).get("image"))
    fr = meta.get("frame") or {}
    out.append(fr.get("image"))
    for o in fr.get("ornaments") or []:
        out.append((o or {}).get("image"))
    return [p for p in out if p]


def check(path):
    errors, warnings = [], []
    try:
        t = themes._validate_folder(path) if os.path.isdir(path) else None
        if t is None:
            return [f"not a folder: {path}"], []
    except themes.ThemeError as ex:
        return [str(ex)], []
    m = t.meta
    for k in m:
        if k not in KNOWN_TOP:
            warnings.append(f"unknown key in theme.json: {k!r}")
    if not themes.local_text(m.get("name")):
        warnings.append("no \"name\"")
    if not m.get("version"):
        warnings.append("no \"version\" (needed so the app can offer updates)")
    for k, v in (m.get("colors") or {}).items():
        if k not in themes.DEFAULT_COLORS:
            warnings.append(f"unknown colour name: {k!r}")
        elif themes.parse_color(v) is None:
            errors.append(f"colour {k!r} is not like #RRGGBB: {v!r}")
    for rel in images_in(m):
        if t.file(rel) is None:
            errors.append(f"picture not found: {rel}")
        elif t.image(rel) is None:
            errors.append(f"picture cannot be opened (or is larger than 4096 x 4096): {rel}")
    icons_dir = os.path.join(path, "icons")
    if os.path.isdir(icons_dir):
        for fn in os.listdir(icons_dir):
            stem, ext = os.path.splitext(fn)
            if ext.lower() == ".png" and stem not in themes.ICON_KEYS:
                warnings.append(f"icons/{fn} is not used (known names: {', '.join(themes.ICON_KEYS)})")
    if t.frame:
        for k in t.frame:
            if k not in KNOWN_FRAME:
                warnings.append(f"unknown key in \"frame\": {k!r}")
        try:
            for size in ((1200, 800), (300, 120), (2560, 1440)):
                themes.apply_frame(themes._sample_shot().resize(size), t, {"title": "Test", "date": "2026-01-01"})
        except Exception as ex:
            errors.append(f"frame cannot be drawn: {ex}")
    try:
        themes.make_preview(t, lambda th, key, px: th.icon(key))
    except Exception as ex:
        errors.append(f"preview cannot be drawn: {ex}")
    return errors, warnings


def main(args):
    if args:
        folders = args
    else:
        base = os.path.join(ROOT, "themes")
        folders = [os.path.join(base, n) for n in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, n))]
    bad = 0
    for f in folders:
        errors, warnings = check(f)
        name = os.path.basename(os.path.normpath(f))
        print(("FAIL " if errors else "ok   ") + name)
        for e in errors:
            print("   error:  ", e)
        for w in warnings:
            print("   warning:", w)
        bad += bool(errors)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
