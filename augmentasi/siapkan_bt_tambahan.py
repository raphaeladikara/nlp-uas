"""Cari teks yang label akhirnya positif tapi belum pernah di-back-translate.

Pakai : python augmentasi/siapkan_bt_tambahan.py
Output: augmentasi/kaggle_data/bt_sumber_tambahan.csv (id, kelompok, text)

Setelah review 3 lapis selesai, beberapa teks bisa berubah jadi positif padahal tidak ada di bt_sumber.csv.
Berkas tambahan ini dijalankan di kernel back-translation yang sama (mode TAMBAHAN=1), lalu hasilnya
disambung ke data/05_final/augmentasi_bt_mentah.csv.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "data" / "05_final"
d = pd.read_csv(FINAL / "dataset_model.csv", dtype=str)
jb = pd.read_csv(FINAL / "augmentasi_jalur_b.csv", dtype=str)
sumber = pd.read_csv(ROOT / "augmentasi" / "kaggle_data" / "bt_sumber.csv", dtype=str)
sudah = set(pd.read_csv(FINAL / "augmentasi_bt_mentah.csv", dtype=str).id) | set(sumber.id)

pos = pd.concat([d[d.label == "positif"].assign(kelompok="utama")[["id", "kelompok", "text"]],
                 jb.assign(kelompok="jalur_b")[["id", "kelompok", "text"]]])
baru = pos[~pos.id.isin(sudah)].drop_duplicates("id")
baru.to_csv(ROOT / "augmentasi" / "kaggle_data" / "bt_sumber_tambahan.csv", index=False, encoding="utf-8-sig")
print(len(baru), "teks positif baru perlu back-translation")
print(baru.to_string())
