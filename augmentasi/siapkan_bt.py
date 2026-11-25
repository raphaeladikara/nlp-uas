"""Pilih teks yang perlu di-back-translate untuk augmentasi kelas positif.

Pakai : python augmentasi/siapkan_bt.py
Output: augmentasi/kaggle_data/bt_sumber.csv (id, kelompok, text)

Yang dipilih adalah semua teks utama dan jalur B yang pernah dinilai positif oleh minimal satu annotator LLM
atau satu reviewer manusia, bukan hanya yang label akhirnya positif. Alasannya, review 3 lapis masih berjalan,
jadi label akhir bisa berubah. Dengan memilih lebih luas, back-translation cukup dijalankan sekali. Saat training,
hanya parafrase dari teks yang label akhirnya positif (dan berada di fold latih) yang dipakai.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
lab = pd.read_csv(ROOT / "data" / "04_labeled" / "label_llm.csv", dtype=str)
lab = lab[lab.kelompok.isin(["utama", "jalur_b"])]
llm_pos = lab[[f"sentimen_{m}" for m in ("opus", "sonnet", "haiku")]].eq("positif").any(axis=1)
rv = pd.concat([pd.read_csv(f, dtype=str) for f in (ROOT / "labeling" / "review" / "hasil").glob("*.csv")])
manusia_pos = lab.id.isin(rv[rv.label_review.eq("positif")].id)
pilih = lab[llm_pos | manusia_pos]

teks = pd.concat([pd.read_csv(ROOT / "data" / "03_filtered" / f, dtype=str)
                  for f in ("dataset_untuk_label.csv", "jalur_b_untuk_label.csv")])
out = pilih[["id", "kelompok"]].merge(teks[["id", "text"]], on="id", how="left")
out.to_csv(ROOT / "augmentasi" / "kaggle_data" / "bt_sumber.csv", index=False, encoding="utf-8-sig")
print(len(out), out.kelompok.value_counts().to_dict())
