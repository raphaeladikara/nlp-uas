"""Bangun laporan revisi dari laporan progress.

Pakai : python laporan/buat_laporan.py
Input : Laporan Progress UAS NLP - Kelompok J.docx (bagian 1 dan 2 dipakai ulang), data hasil pipeline, figures/
Output: Laporan UAS NLP - Kelompok J (Revisi).docx

Bagian 1 (gambaran umum) dan 2 (scraping) diambil dari laporan progress, hanya tabel alur dan istilah yang
diperbarui. Mulai bagian 3 ditulis ulang karena pipeline-nya berubah setelah konsultasi dosen.
Isi teks bagian 3 dan seterusnya ada di laporan/isi_laporan.py.
"""
import copy
import re
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from isi_laporan import ISI, TABEL_ALUR, ISTILAH_BARU  # noqa: E402

SRC = ROOT / "Laporan Progress UAS NLP - Kelompok J.docx"
OUT = ROOT / "Laporan UAS NLP - Kelompok J (Revisi).docx"

d = docx.Document(SRC)
body = d.element.body
anak = list(body.iterchildren())
mulai = next(i for i, el in enumerate(anak) if el.tag == qn("w:p")
             and "".join(t.text or "" for t in el.iter(qn("w:t"))).strip() == "3. Filter")
for el in anak[mulai:]:
    if el.tag != qn("w:sectPr"):
        body.remove(el)
sect = body.find(qn("w:sectPr"))


def _taruh(el):
    sect.addprevious(el)
    return el


def para(teks="", style=None, italic=None, size=None, bold=None, align=None):
    p = d.add_paragraph(style=style)
    _taruh(p._p)
    # **tebal** di dalam teks
    for i, bagian in enumerate(re.split(r"\*\*", teks)):
        if not bagian:
            continue
        r = p.add_run(bagian)
        r.bold = True if i % 2 else bold
        r.italic = italic
        if size:
            r.font.size = Pt(size)
    if align:
        p.alignment = align
    return p


def judul(teks, level):
    return para(teks, style=f"Heading {level}")


_nomor = {}


def caption(teks):
    # Nomor tabel/gambar/kode diurutkan ulang otomatis. Nomor pertama tiap jenis mengikuti yang tertulis
    # (melanjutkan nomor di bagian 1 dan 2 dari laporan progress), sisanya naik satu per satu.
    m = re.match(r"(Tabel|Gambar|Kode) (\d+)\.", teks)
    if m:
        jenis = m.group(1)
        _nomor[jenis] = _nomor[jenis] + 1 if jenis in _nomor else int(m.group(2))
        teks = f"{jenis} {_nomor[jenis]}." + teks[m.end():]
    return para(teks, italic=True, size=10)


def butir(teks):
    return para(teks, style="List Paragraph").__setattr__("style", d.styles["List Paragraph"]) or None


def _shade(cell, warna):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), warna)
    tcPr.append(sh)


def _border(tbl):
    tblPr = tbl._tbl.tblPr
    b = OxmlElement("w:tblBorders")
    for sisi in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{sisi}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:color"), "BFBFBF")
        b.append(e)
    tblPr.append(b)


def tabel(baris, lebar=None, ukuran=9):
    t = d.add_table(rows=len(baris), cols=len(baris[0]))
    _taruh(t._tbl)
    _border(t)
    for i, row in enumerate(baris):
        for j, v in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            p = c.paragraphs[0]
            for k, bagian in enumerate(re.split(r"\*\*", str(v))):
                if bagian:
                    r = p.add_run(bagian)
                    r.font.size = Pt(ukuran)
                    r.bold = True if (i == 0 or k % 2) else None
            if i == 0:
                _shade(c, "E7ECF3")
    if lebar:
        for j, w in enumerate(lebar):
            for row in t.rows:
                row.cells[j].width = Cm(w)
    para()
    return t


def kode(teks):
    for baris in teks.strip("\n").split("\n"):
        p = d.add_paragraph()
        _taruh(p._p)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        r = p.add_run(baris if baris else " ")
        r.font.name = "Consolas"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        r.font.size = Pt(8.5)
        pPr = p._p.get_or_add_pPr()
        sh = OxmlElement("w:shd")
        sh.set(qn("w:val"), "clear")
        sh.set(qn("w:fill"), "F3F3F3")
        pPr.append(sh)
    para()


def gambar(path, lebar_cm=15):
    p = d.add_paragraph()
    _taruh(p._p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Cm(lebar_cm))


# perbarui tabel alur (Tabel 1) dan istilah (Tabel 2) dari bagian 1
alur, istilah = d.tables[0], d.tables[1]
while len(alur.rows) > 1:
    alur._tbl.remove(alur.rows[-1]._tr)
for row in TABEL_ALUR:
    tr = copy.deepcopy(alur.rows[0]._tr) if False else None
    cells = alur.add_row().cells
    for c, v in zip(cells, row):
        c.text = v
        for r in c.paragraphs[0].runs:
            r.font.size = Pt(9)
for k, v in ISTILAH_BARU:
    cells = istilah.add_row().cells
    cells[0].text, cells[1].text = k, v
    for c in cells:
        for r in c.paragraphs[0].runs:
            r.font.size = Pt(9)

# ganti judul dokumen
for p in d.paragraphs[:3]:
    if p.text.startswith("Laporan Penjelasan Pipeline"):
        p.runs[0].text = "Laporan Penjelasan Pipeline, Model, dan Analisis Kesalahan"
        for r in p.runs[1:]:
            r.text = ""

API = dict(para=para, judul=judul, caption=caption, tabel=tabel, kode=kode, gambar=gambar, ROOT=ROOT,
           butir=lambda t: para(t, style="List Paragraph"))
ISI(**API)
d.save(OUT)
print("tersimpan:", OUT.name)
