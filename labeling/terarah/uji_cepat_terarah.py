"""Uji cepat (sementara): apakah positif terarah menaikkan F1 positif TF-IDF + LogReg?

Label terarah di sini masih label AI (sebelum review 3 orang), jadi hasilnya hanya perkiraan awal.
Pakai : python labeling/terarah/uji_cepat_terarah.py
Output: labeling/terarah/uji_cepat_terarah.csv
"""
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import f1_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from pilih_terarah import bersih_lengkap, isi_judul, model  # noqa: E402

FIN = ROOT / "data" / "05_final"
df = pd.read_csv(FIN / "dataset_prepro.csv", dtype=str).fillna("")
final = pd.read_csv(FIN / "dataset_model.csv", dtype=str).fillna("")
aug = pd.read_csv(FIN / "augmentasi_prepro.csv", dtype=str).fillna("")
jb = aug[aug.sumber == "jalur_b"]

lab = pd.read_csv(ROOT / "labeling" / "terarah" / "label_llm_terarah.csv", dtype=str)
d = pd.read_csv(ROOT / "data" / "03_filtered" / "terarah_untuk_label.csv", dtype=str).fillna("")
t = lab.merge(d[["id", "text", "konteks", "author_hash"]], on="id")
t = t[t.label_llm.eq("positif") & ~t.author_hash.isin(final.author_hash)].copy()
t["teks_lengkap"] = t.text.map(bersih_lengkap)
t["judul_lengkap"] = t.konteks.map(lambda s: bersih_lengkap(isi_judul(s)))
t["label"], t["fold_asal"] = "positif", "-1"
bulat = t[t.sepakat_bulat.eq("True")]
print(f"positif terarah: {len(bulat)} sepakat bulat, {len(t)} termasuk mayoritas 2 dari 3")

VARIAN = {"tanpa augmentasi": [], "jalur B": [jb], "jalur B + terarah (bulat)": [jb, bulat],
          "jalur B + terarah (bulat + mayoritas)": [jb, t]}
X = lambda x: pd.DataFrame({"teks": x.teks_lengkap.values, "judul": x.judul_lengkap.values})
hasil = []
for nama, tambah in VARIAN.items():
    pred = pd.Series(index=df.index, dtype=object)
    for f in sorted(df.fold.unique()):
        latih = pd.concat([df[df.fold != f]] + [a[a.fold_asal != f] for a in tambah])
        uji = df[df.fold == f]
        pred[uji.index] = model().fit(X(latih), latih.label).predict(X(uji))
    per = f1_score(df.label, pred, labels=["negatif", "netral", "positif"], average=None)
    hasil.append(dict(varian=nama, macro_f1=f1_score(df.label, pred, average="macro"), f1_negatif=per[0],
                      f1_netral=per[1], f1_positif=per[2], n_pos_latih_tambahan=sum(len(a) for a in tambah)))
    print(hasil[-1])
out = pd.DataFrame(hasil).round(3)
out.to_csv(ROOT / "labeling" / "terarah" / "uji_cepat_terarah.csv", index=False)
print(out.to_string(index=False))
