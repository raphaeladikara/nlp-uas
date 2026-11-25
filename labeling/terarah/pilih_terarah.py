"""Pilih teks cadangan untuk pelabelan terarah kelas positif, lalu tulis batch untuk 3 annotator.

Pakai : python labeling/terarah/pilih_terarah.py
Input : data/03_filtered/cadangan_belum_dilabel.csv (teks lolos filter yang belum pernah dilabeli)
        data/05_final/dataset_prepro.csv              (data latih untuk model pengurut)
Output: data/03_filtered/terarah_untuk_label.csv     (teks terpilih + skor + cara_pilih)
        labeling/terarah/batches/batch_XX.md          (format sama dengan labeling/batches)
        labeling/terarah/batches/index.csv

Alasan (notebook 05, bagian strategi kelas positif): learning curve kelas positif belum jenuh, dan 100 teks dengan skor
positif tertinggi berisi 26% positif, sedangkan sampel acak hanya 2,5%.

Aturan:
- Model pengurut: TF-IDF + LogReg (teks + judul, class weight balanced, C=3), dilatih di seluruh dataset final.
  Sama dengan model yang dipakai untuk memperkirakan presisi peringkat di notebook 05.
- Teks yang isinya identik dengan teks di dataset final dibuang dulu.
- Diambil N_ATAS teks dengan skor positif tertinggi + N_ACAK teks acak dari sisanya. Teks acak dipakai sebagai
  pembanding (berapa persen positif kalau tidak diurutkan) dan supaya annotator tidak hanya melihat teks yang condong
  positif. Batch diacak, dan annotator tidak diberi tahu skor maupun cara pilihnya.
- Hasil pelabelan ini HANYA untuk data latih (seperti jalur B). Tidak masuk fold uji dan tidak masuk statistik sentimen,
  karena sampelnya sengaja condong positif.
"""
import json
import re
from pathlib import Path

import emoji
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parents[2]
F, RES = ROOT / "data" / "03_filtered", ROOT / "resources"
B = ROOT / "labeling" / "terarah" / "batches"
N_ATAS, N_ACAK, UKURAN, SEED = 250, 50, 150, 42
BATCH_AWAL = 29  # melanjutkan nomor batch utama (batch 01-28)

# preprocessing "lengkap" yang sama dengan notebook 02
slang = json.loads((RES / "slang_map.json").read_text(encoding="utf-8"))
NEGASI = {"tidak", "tdk", "gak", "ga", "nggak", "ngga", "enggak", "gk", "bukan", "jangan", "jgn", "belum", "blm", "tak",
          "kurang"}
stopword = set((RES / "stopwords.txt").read_text(encoding="utf-8").split()) - NEGASI


def bersih_ringan(t):
    t = re.sub(r"https?://\S+|www\.\S+", " ", str(t))
    t = re.sub(r"@\w+", "@user", t)
    t = re.sub(r"#(\w+)", r"\1", t)
    t = re.sub(r"([a-zA-Z])\1{2,}", r"\1", t)
    return re.sub(r"\s+", " ", t).strip()


def bersih_lengkap(t):
    t = emoji.demojize(bersih_ringan(t).lower(), language="id", delimiters=(" emo_", " "))
    t = re.sub(r"\b(?:wk)+w?\b|\b(?:ha){2,}h?\b|\b(?:he){2,}h?\b|\b(?:xi){2,}\b", " tawa ", t)
    t = re.sub(r"[^a-z0-9_@ ]", " ", t)
    return " ".join(w for w in (slang.get(w, w) for w in t.split()) if w not in stopword)


def isi_judul(t):
    return re.sub(r"^[^:]{0,60}:\s*", "", str(t))


def kunci(t):
    return " ".join(re.sub(r"[^a-z0-9 ]", "", str(t).lower().replace("@user", "")).split())


def model():
    teks = FeatureUnion([("kata", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
                         ("huruf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True))])
    fitur = ColumnTransformer([("teks", teks, "teks"),
                               ("judul", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True), "judul")],
                              transformer_weights={"teks": 1.0, "judul": 0.5})
    return Pipeline([("f", fitur), ("c", LogisticRegression(class_weight="balanced", C=3, max_iter=3000))])


def main():
    df = pd.read_csv(ROOT / "data" / "05_final" / "dataset_prepro.csv")
    cad = pd.read_csv(F / "cadangan_belum_dilabel.csv", dtype=str)
    awal = len(cad)
    cad = cad[~cad.text.map(kunci).isin(set(df.text.map(kunci)))].copy()
    cad = cad.drop_duplicates("text")

    m = model().fit(pd.DataFrame({"teks": df.teks_lengkap.fillna(""), "judul": df.judul_lengkap.fillna("")}), df.label)
    X = pd.DataFrame({"teks": cad.text.map(bersih_lengkap), "judul": cad.konteks.fillna("").map(lambda t: bersih_lengkap(isi_judul(t)))})
    cad["skor_positif"] = m.predict_proba(X)[:, list(m.classes_).index("positif")].round(4)

    cad = cad.sort_values("skor_positif", ascending=False)
    atas = cad.head(N_ATAS).assign(cara_pilih="skor_tertinggi")
    acak = cad.iloc[N_ATAS:].sample(N_ACAK, random_state=SEED).assign(cara_pilih="acak")
    pilih = pd.concat([atas, acak]).sample(frac=1, random_state=SEED).reset_index(drop=True)
    pilih["kelompok"] = "terarah"
    pilih.to_csv(F / "terarah_untuk_label.csv", index=False, encoding="utf-8-sig")

    # batch: urutan sudah diacak, teks ditulis satu per satu dengan judulnya (tidak dikelompokkan per sumber,
    # supaya urutan sumber tidak membocorkan teks mana yang skornya tinggi)
    B.mkdir(parents=True, exist_ok=True)
    for f in B.glob("batch_*.md"):
        f.unlink()
    idx = []
    for i, start in enumerate(range(0, len(pilih), UKURAN)):
        no = BATCH_AWAL + i
        bagian = pilih.iloc[start:start + UKURAN]
        isi = [f"# Batch {no:02d} ({len(bagian)} teks)\n",
               "Labeli setiap teks sesuai labeling/codebook.md. Judul unggahan ditulis di belakang tiap teks.\n"]
        for r in bagian.itertuples():
            kon = f" [konteks: {r.konteks}]" if isinstance(r.konteks, str) and r.konteks else ""
            isi.append(f"- {r.id} | {r.text}{kon}")
            idx.append((r.id, no, "terarah", r.platform))
        (B / f"batch_{no:02d}.md").write_text("\n".join(isi) + "\n", encoding="utf-8")
    pd.DataFrame(idx, columns=["id", "batch", "kelompok", "platform"]).to_csv(B / "index.csv", index=False,
                                                                              encoding="utf-8-sig")

    print(f"cadangan {awal}, setelah buang teks identik {len(cad)}")
    print(f"terpilih {len(pilih)}: {N_ATAS} skor tertinggi (skor >= {atas.skor_positif.min():.3f}) + {N_ACAK} acak")
    print("platform:", pilih.platform.value_counts().to_dict())
    print("status buzzer:", pilih.status_buzzer.value_counts().to_dict())
    print(f"batch {BATCH_AWAL}-{BATCH_AWAL + len(range(0, len(pilih), UKURAN)) - 1} di {B.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
