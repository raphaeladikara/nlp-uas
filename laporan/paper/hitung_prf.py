"""Hitung macro precision, recall, F1 per fold untuk konfigurasi terbaik tiap model (tabel pembanding paper)."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data"
LABEL = ["negatif", "netral", "positif"]
df = pd.read_csv(D / "05_final" / "dataset_prepro.csv")
oof = pd.read_csv(D / "06_baseline" / "prediksi_oof.csv").set_index("id").reindex(df.id)


def berkas(folder, awal, inp, aug):
    nama = "_".join([awal, inp, aug]).replace(" ", "_").replace("+", "")
    return pd.read_csv(D / folder / f"prediksi_{nama}.csv").set_index("id").reindex(df.id)


def pred_tfidf(m, inp, aug):
    return oof[f"{m} | {inp} | {aug}"].values


def pred_file(folder, awal, inp, aug):
    return berkas(folder, awal, inp, aug).prediksi.values


def pred_ens(aug):
    p = [berkas("07_transformer", m, "teks + judul", aug)[[f"prob_{k}" for k in LABEL]].values
         for m in ["indobert", "indobertweet"]]
    return np.array(LABEL)[np.mean(p, axis=0).argmax(1)]


KONFIG = [
    ("Kelas terbanyak", "teks saja", "tanpa augmentasi", lambda: pred_tfidf("kelas terbanyak", "teks saja", "tanpa augmentasi")),
    ("Leksikon InSet", "teks saja", "tanpa augmentasi", lambda: pred_tfidf("leksikon InSet", "teks saja", "tanpa augmentasi")),
    ("TF-IDF + LinearSVM", "teks + judul", "jalur B + parafrase", lambda: pred_tfidf("TF-IDF + LinearSVM", "teks + judul", "jalur B + parafrase")),
    ("TF-IDF + LogReg", "teks + judul", "jalur B + terarah", lambda: pred_tfidf("TF-IDF + LogReg", "teks + judul", "jalur B + terarah")),
    ("BiLSTM + attention", "teks saja", "jalur B", lambda: pred_file("08_embedding_bilstm", "bilstm", "teks saja", "jalur B")),
    ("IndoBERT embedding + LogReg", "teks + judul", "jalur B", lambda: pred_file("08_embedding_bilstm", "embedding", "teks + judul", "jalur B")),
    ("XLM-RoBERTa fine-tune", "teks + judul", "jalur B + parafrase", lambda: pred_file("07_transformer", "xlmr", "teks + judul", "jalur B + parafrase")),
    ("IndoBERTweet fine-tune", "teks + judul", "jalur B + terarah", lambda: pred_file("07_transformer", "indobertweet", "teks + judul", "jalur B + terarah")),
    ("IndoBERT fine-tune", "teks + judul", "jalur B + terarah", lambda: pred_file("07_transformer", "indobert", "teks + judul", "jalur B + terarah")),
    ("Ensemble IndoBERT + IndoBERTweet", "teks + judul", "jalur B + terarah", lambda: pred_ens("jalur B + terarah")),
]

baris = []
for m, inp, aug, f in KONFIG:
    p = f()
    per = []
    for k in sorted(df.fold.unique()):
        s = df.fold.values == k
        pr, rc, f1, _ = precision_recall_fscore_support(df.label.values[s], p[s], labels=LABEL, average="macro", zero_division=0)
        _, _, f1c, _ = precision_recall_fscore_support(df.label.values[s], p[s], labels=LABEL, average=None, zero_division=0)
        per.append((pr, rc, f1, f1c[2]))
    a = np.array(per)
    baris.append({"model": m, "input": inp, "augmentasi": aug, "P": a[:, 0].mean(), "R": a[:, 1].mean(),
                  "F1": a[:, 2].mean(), "F1_sd": a[:, 2].std(ddof=1), "F1_positif": a[:, 3].mean()})
t = pd.DataFrame(baris)
t.to_csv(D / "09_perbandingan" / "perbandingan_prf.csv", index=False)
print(t.round(3).to_string())
