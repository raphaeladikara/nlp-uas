"""Bagi kartu review ke beberapa reviewer, satu berkas HTML mandiri per orang.

Pakai : python labeling/review/bagi_review.py Nama1 Nama2 Nama3 Nama4 Nama5
        (tanpa argumen -> Reviewer1 ... Reviewer5)
Input : labeling/review/review_data.js (hasil aggregate.py), labeling/review/review.html (template)
Output: labeling/review/untuk_reviewer/review_<Nama>.html  (kirim berkas ini ke tiap orang)
        labeling/review/untuk_reviewer/pembagian.csv       (id kartu -> reviewer)

Cara bagi:
- KALIBRASI kartu yang sama dikerjakan SEMUA reviewer. Dipilih acak dari kartu review label data utama,
  dengan positif diwakili. Gunanya mengukur kesepakatan antar-manusia (Fleiss' kappa di finalize.py), dan
  label akhirnya diambil dari suara terbanyak reviewer.
- Sisa kartu diurutkan per (kelompok, jenis review, platform, label LLM) lalu dibagikan bergiliran,
  jadi tiap orang mendapat campuran yang seimbang dan bebannya hampir sama.
- Berkas HTML berdiri sendiri (data ditanam di dalamnya), bisa dibuka offline tanpa server.
"""
import json
import random
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "untuk_reviewer"
KALIBRASI = 30
SEED = 42


def main():
    nama = sys.argv[1:] or [f"Reviewer{i}" for i in range(1, 6)]
    if len(set(nama)) != len(nama) or any(not n.replace("_", "").isalnum() for n in nama):
        sys.exit("Nama reviewer harus unik dan hanya huruf/angka/garis bawah (dipakai di nama berkas).")
    teks = (HERE / "review_data.js").read_text(encoding="utf-8")
    data = json.loads(teks[teks.index("=") + 1:].strip().rstrip(";"))
    rng = random.Random(SEED)

    kandidat = [d for d in data if d["kelompok"] == "utama" and d["review_label"]]
    pos = [d for d in kandidat if "positif" in d["votes"].values()]
    lain = [d for d in kandidat if d not in pos]
    rng.shuffle(pos)
    rng.shuffle(lain)
    kal = pos[:KALIBRASI // 5] + lain[:KALIBRASI - KALIBRASI // 5]
    id_kal = {d["id"] for d in kal}

    sisa = [d for d in data if d["id"] not in id_kal]
    rng.shuffle(sisa)
    sisa.sort(key=lambda d: (d["kelompok"], d["review_label"], d["review_buzzer"], d["platform"],
                         d["label"] if isinstance(d["label"], str) else ""))
    bagian = {n: [] for n in nama}
    for i, d in enumerate(sisa):
        bagian[nama[i % len(nama)]].append(d)

    template = (HERE / "review.html").read_text(encoding="utf-8")
    tag = '<script src="review_data.js"></script>'
    assert tag in template, "template review.html berubah, tag review_data.js tidak ditemukan"
    OUT.mkdir(exist_ok=True)
    baris = []
    for n in nama:
        kartu = kal + bagian[n]
        rng.shuffle(kartu)  # kartu kalibrasi tercampur, tidak ditandai, supaya dikerjakan seperti kartu biasa
        js = json.dumps(kartu, ensure_ascii=False).replace("</", "<\\/")
        html = template.replace(tag, f"<script>window.REVIEWER = {json.dumps(n)};\nwindow.REVIEW_DATA = {js};</script>")
        (OUT / f"review_{n}.html").write_text(html, encoding="utf-8")
        baris += [dict(id=d["id"], reviewer=n, kalibrasi=d["id"] in id_kal) for d in kartu]
        print(f"{n:12} {len(kartu):4} kartu ({len(kal)} kalibrasi + {len(bagian[n])} bagian sendiri)")
    pd.DataFrame(baris).to_csv(OUT / "pembagian.csv", index=False, encoding="utf-8-sig")
    print(f"total kartu unik: {len(data)} | berkas di {OUT}")


if __name__ == "__main__":
    main()
