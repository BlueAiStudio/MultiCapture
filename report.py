# -*- coding: utf-8 -*-
"""
Board report: the screenshots of the board with their notes and measurements, as a PDF
(drawn with Pillow) or a Word .docx file (written directly as Office Open XML), plus a
measurement summary table that can be pasted into Excel (tab separated).

No extra dependency: only Pillow and the standard library, so the PyInstaller exe and the
Store package keep working. Nothing here imports Tkinter, so it can be tested on any platform.

An entry is a dict:
    {"title": "#3  ·  2026-11-25 14:02", "image": PIL.Image, "notes": "text",
     "measures": [("Distance", "12.40", "mm"), ...]}
"""
import io
import re
import zipfile
from datetime import datetime
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

ACCENT = "#2563EB"
TEXT = "#1F2937"
MUTED = "#6B7280"
LINE = "#D0D5DD"


def _default_font(size, bold=False, text=""):
    return ImageFont.load_default(size)


# --------------------------------------------------------------------------- table
def table_rows(entries):
    """One row per measured value: (screenshot, measurement number, type, value, unit)."""
    rows = []
    for e in entries:
        shot = e["title"].split("  ")[0]
        for k, m in enumerate(e["measures"], 1):
            rows.append((shot, str(m[3]) if len(m) > 3 else str(k), m[0], m[1], m[2]))
    return rows


def table_tsv(rows, header):
    def cell(s):
        return str(s).replace("\t", " ").replace("\r", " ").replace("\n", " ")
    return "\r\n".join("\t".join(cell(c) for c in r) for r in [tuple(header)] + list(rows)) + "\r\n"


# --------------------------------------------------------------------------- PDF
def wrap(text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if font.getlength(line + ch) <= maxw or not line:
                line += ch
                continue
            sp = line.rfind(" ")
            if sp > 0 and ch != " ":
                out.append(line[:sp])
                line = line[sp + 1:] + ch
            else:
                out.append(line)
                line = ch.lstrip()
        out.append(line)
    return out


class _Pages:
    """Flowing layout on A4 pages at 150 dpi."""
    W, H, M = 1240, 1754, 96

    def __init__(self, font):
        self.font = font
        self.pages = []
        self.new()

    def new(self):
        self.im = Image.new("RGB", (self.W, self.H), "white")
        self.d = ImageDraw.Draw(self.im)
        self.pages.append(self.im)
        self.y = self.M

    @property
    def cw(self):
        return self.W - 2 * self.M

    def room(self, h):
        if self.y + h > self.H - self.M and self.y > self.M:
            self.new()

    def text(self, s, size=22, bold=False, color=TEXT, gap=0.45):
        f = self.font(size, bold, s)
        lh = int(size * 1.5)
        for line in wrap(s, f, self.cw):
            self.room(lh)
            self.d.text((self.M, self.y), line, font=f, fill=color)
            self.y += lh
        self.y += int(size * gap)

    def rule(self, color=LINE, width=2, gap=18):
        self.room(gap * 2)
        self.d.line((self.M, self.y, self.W - self.M, self.y), fill=color, width=width)
        self.y += gap

    def scale(self, img):
        """Screen pixels are 96 dpi, the page is 150 dpi: show at real size when it fits."""
        return min(self.cw / img.width, (self.H - 2 * self.M - 160) / img.height, 150 / 96)

    def image(self, img):
        s = self.scale(img)
        t = img.convert("RGB")
        if abs(s - 1) > 1e-3:
            t = t.resize((max(1, int(t.width * s)), max(1, int(t.height * s))), Image.LANCZOS)
        self.room(t.height + 8)
        self.im.paste(t, (self.M, self.y))
        self.d.rectangle((self.M - 1, self.y - 1, self.M + t.width, self.y + t.height), outline=LINE)
        self.y += t.height + 18

    def table(self, header, rows, widths):
        size = 19
        fb = self.font(size, True, "")
        rh = int(size * 1.9)
        xs = [self.M]
        for w in widths:
            xs.append(xs[-1] + int(self.cw * w))

        def row(cells, head):
            self.room(rh)
            if head:
                self.d.rectangle((self.M, self.y, self.W - self.M, self.y + rh), fill="#EEF2FF")
            for i, c in enumerate(cells):
                c = str(c)
                ff = fb if head else self.font(size, False, c)
                while ff.getlength(c) > xs[i + 1] - xs[i] - 16 and len(c) > 1:
                    c = c[:-2] + "…"
                right = i == 3
                x = xs[i + 1] - 8 - ff.getlength(c) if right else xs[i] + 8
                self.d.text((x, self.y + (rh - size) // 2 - 2), c, font=ff, fill=TEXT)
            self.y += rh
            self.d.line((self.M, self.y, self.W - self.M, self.y), fill=LINE, width=1)

        row(header, True)
        for r in rows:
            if self.y + rh > self.H - self.M:
                self.new()
                row(header, True)
            row(r, False)
        self.y += 24

    def finish(self, footer):
        n = len(self.pages)
        for i, p in enumerate(self.pages, 1):
            d = ImageDraw.Draw(p)
            s = footer(i, n)
            f = self.font(16, False, s)
            d.text((self.W - self.M - f.getlength(s), self.H - self.M // 2 - 10), s, font=f, fill=MUTED)
        return self.pages


def pdf_pages(title, entries, L, when=None, font=None):
    """L: dict of translated labels (created, shots, notes, measures, summary, header, page)."""
    when = when or datetime.now()
    pg = _Pages(font or _default_font)
    pg.text(title, 40, True, ACCENT, 0.2)
    pg.text(L["created"].format(d=f"{when:%Y-%m-%d %H:%M}") + "   ·   " + L["shots"].format(n=len(entries)),
            19, False, MUTED, 0.3)
    pg.rule(ACCENT, 3, 30)
    for e in entries:
        pg.room(int(e["image"].height * pg.scale(e["image"])) + 60)   # keep the heading with its image
        pg.text(e["title"], 25, True, ACCENT, 0.3)
        pg.image(e["image"])
        if e["notes"].strip():
            pg.text(L["notes"], 19, True, MUTED, 0.1)
            pg.text(e["notes"].strip(), 21)
        if e["measures"]:
            pg.text(L["measures"], 19, True, MUTED, 0.1)
            for m in e["measures"]:
                pg.text(f"{m[0]}:  {m[1]} {m[2]}".rstrip(), 21, gap=0.05)
            pg.y += 10
        pg.rule()
    rows = table_rows(entries)
    if rows:
        pg.room(200)
        pg.text(L["summary"], 27, True, ACCENT, 0.3)
        pg.table(L["header"], rows, (0.16, 0.10, 0.34, 0.22, 0.18))
    return pg.finish(lambda i, n: L["page"].format(i=i, n=n))


def write_pdf(path, pages):
    pages[0].save(path, "PDF", resolution=150, save_all=True, append_images=pages[1:])


# --------------------------------------------------------------------------- Word (.docx)
_BAD_XML = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")
EMU = 914400  # per inch


def _x(s):
    return escape(_BAD_XML.sub("", str(s)))


def _run(text, bold=False, size=None, color=None):
    pr = ("<w:b/>" if bold else "") + (f'<w:color w:val="{color.lstrip("#")}"/>' if color else "") \
        + (f'<w:sz w:val="{size * 2}"/><w:szCs w:val="{size * 2}"/>' if size else "")
    parts = str(text).split("\n")
    body = "<w:br/>".join(f'<w:t xml:space="preserve">{_x(p)}</w:t>' for p in parts)
    return f"<w:r>{'<w:rPr>' + pr + '</w:rPr>' if pr else ''}{body}</w:r>"


def _p(runs, after=120, keep_next=False, align=None, border=None):
    ppr = f'<w:spacing w:after="{after}"/>' + ("<w:keepNext/>" if keep_next else "") \
        + (f'<w:jc w:val="{align}"/>' if align else "") \
        + (f'<w:pBdr><w:bottom w:val="single" w:sz="{border[0]}" w:space="4" w:color="{border[1]}"/></w:pBdr>'
           if border else "")
    return f"<w:p><w:pPr>{ppr}</w:pPr>{runs}</w:p>"


def _img(rid, n, w_px, h_px, max_w_in=6.6, max_h_in=8.2):
    s = min(max_w_in * 96 / w_px, max_h_in * 96 / h_px, 1.0)
    cx, cy = int(w_px * s / 96 * EMU), int(h_px * s / 96 * EMU)
    return (
        f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{n}" name="Picture {n}"/>'
        f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{n}" name="image{n}.png"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        f'<a:ln w="9525"><a:solidFill><a:srgbClr val="D0D5DD"/></a:solidFill></a:ln></pic:spPr>'
        f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')


def _table(header, rows, widths):
    total = 9638
    grid = "".join(f'<w:gridCol w:w="{int(total * w)}"/>' for w in widths)
    b = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="D0D5DD"/>'
    borders = "".join(b.format(s) for s in ("top", "left", "bottom", "right", "insideH", "insideV"))

    def tr_(cells, head):
        out = "<w:tr>" + ('<w:trPr><w:tblHeader/></w:trPr>' if head else "")
        for i, c in enumerate(cells):
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="EEF2FF"/>' if head else ""
            out += (f'<w:tc><w:tcPr><w:tcW w:w="{int(total * widths[i])}" w:type="dxa"/>{shade}</w:tcPr>'
                    + _p(_run(c, bold=head, size=10), after=0, align="right" if i == 3 and not head else None)
                    + "</w:tc>")
        return out + "</w:tr>"

    return (f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:tblBorders>{borders}</w:tblBorders>'
            f'<w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar>'
            f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
            + tr_(header, True) + "".join(tr_(r, False) for r in rows) + "</w:tbl>")


_CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
       '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
       '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
       '<Default Extension="xml" ContentType="application/xml"/>'
       '<Default Extension="png" ContentType="image/png"/>'
       '<Override PartName="/word/document.xml" '
       'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
       '<Override PartName="/word/styles.xml" '
       'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
       '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
       '</Types>')
_RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
         '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
         '</Relationships>')
_STYLES = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults>'
           '<w:rPrDefault><w:rPr><w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft YaHei" w:cs="Segoe UI"/>'
           '<w:color w:val="1F2937"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr></w:rPrDefault>'
           '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="264" w:lineRule="auto"/></w:pPr></w:pPrDefault>'
           '</w:docDefaults></w:styles>')
_NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
       'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
       'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
       'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
       'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"')


def write_docx(path, title, entries, L, when=None, app="MultiCapture"):
    when = when or datetime.now()
    body, rels, media = [], [], []
    body.append(_p(_run(title, True, 22, ACCENT), after=60))
    body.append(_p(_run(L["created"].format(d=f"{when:%Y-%m-%d %H:%M}") + "   ·   "
                        + L["shots"].format(n=len(entries)), size=9, color=MUTED),
                   after=240, border=(12, ACCENT.lstrip("#"))))
    for n, e in enumerate(entries, 1):
        buf = io.BytesIO()
        e["image"].convert("RGB").save(buf, "PNG", optimize=True)
        media.append((f"word/media/image{n}.png", buf.getvalue()))
        rid = f"rIdImg{n}"
        rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                    f'relationships/image" Target="media/image{n}.png"/>')
        body.append(_p(_run(e["title"], True, 13, ACCENT), after=80, keep_next=True))
        body.append(_p(_img(rid, n, *e["image"].size), after=160))
        if e["notes"].strip():
            body.append(_p(_run(L["notes"], True, 9, MUTED), after=20, keep_next=True))
            body.append(_p(_run(e["notes"].strip()), after=160))
        if e["measures"]:
            body.append(_p(_run(L["measures"], True, 9, MUTED), after=20, keep_next=True))
            for m in e["measures"]:
                body.append(_p(_run(f"{m[0]}:  ") + _run(f"{m[1]} {m[2]}".rstrip(), True), after=20))
        body.append(_p("", after=200, border=(4, "D0D5DD")))
    rows = table_rows(entries)
    if rows:
        body.append(_p(_run(L["summary"], True, 14, ACCENT), after=120, keep_next=True))
        body.append(_table(L["header"], rows, (0.16, 0.10, 0.34, 0.22, 0.18)))
        body.append(_p(""))
    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/>'
            '</w:sectPr>')
    doc = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {_NS}><w:body>'
           + "".join(body) + sect + "</w:body></w:document>")
    doc_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                + "".join(rels) + "</Relationships>")
    stamp = f"{when:%Y-%m-%dT%H:%M:%S}Z"
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{_x(title)}</dc:title><dc:creator>{_x(app)}</dc:creator>'
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{stamp}</dcterms:created></cp:coreProperties>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CT)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("docProps/core.xml", core)
        z.writestr("word/document.xml", doc)
        z.writestr("word/styles.xml", _STYLES)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        for name, data in media:
            z.writestr(name, data, zipfile.ZIP_STORED)
