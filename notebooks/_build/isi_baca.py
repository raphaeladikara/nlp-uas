"""Isi sel markdown bertag "baca-<nama>" dengan teks pembacaan hasil.

Pakai : python notebooks/_build/isi_baca.py <notebook.ipynb> <teks.md>
Format teks.md: blok diawali baris "@@ <nama>", isinya sampai blok berikutnya.
"""
import re
import sys

import nbformat as nbf

nb = nbf.read(sys.argv[1], as_version=4)
teks = open(sys.argv[2], encoding="utf-8").read()
blok = {m.group(1): m.group(2).strip() for m in re.finditer(r"^@@ (\S+)\n(.*?)(?=^@@ |\Z)", teks, re.S | re.M)}
terisi = 0
for c in nb.cells:
    for t in c.metadata.get("tags", []):
        if t.startswith("baca-") and t[5:] in blok:
            c.source = blok[t[5:]]
            terisi += 1
kosong = [t for c in nb.cells for t in c.metadata.get("tags", []) if t.startswith("baca-") and c.source.startswith("(dibaca")]
nbf.write(nb, sys.argv[1])
print("terisi:", terisi, "| belum:", kosong)
