"""Bangun notebook 04 (IndoBERT embedding + LogReg dan BiLSTM + attention, dijalankan di Kaggle).

Pakai : python notebooks/_build/build_04.py
Output: notebooks/04_embedding_bilstm_kaggle.ipynb, notebooks/_kaggle/embed_bilstm/{notebook.ipynb, kernel-metadata.json}
"""
import json
from pathlib import Path

import nbformat as nbf

NB = Path(__file__).resolve().parents[1]


def md(s):
    return nbf.v4.new_markdown_cell(s.strip("\n"))


def code(s):
    return nbf.v4.new_code_cell(s.strip("\n"))


CELLS = [
    md("""
# IndoBERT sebagai Embedding + Logistic Regression, dan BiLSTM + Attention

**Nama:** Raphael Angelo Adikara Purnama
**NIM:** 164241055
**Mata kuliah:** Natural Language Processing (UAS)
**Topik:** Klasifikasi sentimen publik terhadap Raffi Ahmad setelah kasus "mahasiswa bayaran" di Bundaran HI (29 Oktober 2026)

Notebook ini menambah dua metode di antara TF-IDF (notebook 02) dan fine-tuning transformer (notebook 03), sesuai saran dosen:

1. **IndoBERT sebagai embedding lalu Logistic Regression.** IndoBERT tidak dilatih ulang. Setiap teks dilewatkan ke IndoBERT sekali, lalu vektor kontekstual per token dirata-rata menjadi satu vektor 768 dimensi. Vektor ini dipakai sebagai fitur untuk Logistic Regression. Bedanya dengan TF-IDF, vektor ini sudah membawa makna kata sesuai kalimatnya. Bedanya dengan fine-tuning, bobot IndoBERT tidak ikut diubah, jadi kita bisa melihat seberapa banyak kenaikan yang datang dari representasinya saja dan seberapa banyak dari proses fine-tuning.
2. **BiLSTM + attention.** Model sekuensial non-transformer yang membaca teks kata demi kata dari dua arah (kiri ke kanan dan kanan ke kiri), lalu lapisan attention memilih kata yang paling penting untuk keputusan. Ini model yang memahami urutan dan konteks kalimat, tapi jauh lebih kecil dari BERT dan dilatih dari nol (kecuali embedding katanya).

Keduanya dievaluasi dengan grouped 5-fold CV yang sama, dua jenis input (teks saja, teks + judul), dan empat varian augmentasi (tanpa, jalur B, parafrase, keduanya). Notebook dijalankan di Kaggle (GPU T4)."""),
    code("""import glob
import time
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
from transformers.utils import logging as hf_logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score, accuracy_score, balanced_accuracy_score

hf_logging.set_verbosity_error()
DI_KAGGLE = Path("/kaggle/input").exists()
if DI_KAGGLE:
    DATA = Path(glob.glob("/kaggle/input/**/dataset_prepro.csv", recursive=True)[0]).parent
    OUT = Path("/kaggle/working")
else:
    ROOT = Path.cwd().parent
    DATA, OUT = ROOT / "data" / "05_final", ROOT / "data" / "08_embedding_bilstm"
OUT.mkdir(parents=True, exist_ok=True)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 42
LABEL = ["negatif", "netral", "positif"]
MODEL_NAMA = "indobenchmark/indobert-base-p1"
VARIAN = {"tanpa augmentasi": [], "jalur B": ["jalur_b"], "parafrase": ["bt_utama"],
          "jalur B + parafrase": ["jalur_b", "bt_utama", "bt_jalur_b"]}
INPUT = ["teks saja", "teks + judul"]


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


df = pd.read_csv(DATA / "dataset_prepro.csv", dtype={"grup": str}).fillna({"judul_bert": "", "teks_bert": ""})
aug = pd.read_csv(DATA / "augmentasi_prepro.csv", dtype={"grup": str}).fillna({"judul_bert": "", "teks_bert": ""})
semua = pd.concat([df.assign(sumber="utama", id_asal=df.id), aug], ignore_index=True)
y_semua = semua.label.map({c: i for i, c in enumerate(LABEL)}).values
n_utama = len(df)
if aug.sumber.eq("terarah").any():
    VARIAN["jalur B + terarah"] = ["jalur_b", "terarah"]
print("device:", DEVICE, "| data utama:", len(df), "| augmentasi:", aug.sumber.value_counts().to_dict())"""),
    md("""Fungsi di bawah dipakai kedua metode. `indeks_latih()` mengambil data latih untuk fold uji `k` lalu menambahkan data augmentasi sesuai varian. Parafrase dari teks yang sedang menjadi data uji tidak pernah dipakai. Data uji selalu teks jalur A asli, jadi skor semua varian dihitung di data yang sama."""),
    code("""def indeks_latih(k, varian, sisihkan_val=False):
    idx_latih = np.where(df.fold != k)[0]
    idx_val = np.array([], dtype=int)
    if sisihkan_val:
        sgk = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=SEED)
        a, v = next(sgk.split(idx_latih, y_semua[idx_latih], df.grup.values[idx_latih]))
        idx_latih, idx_val = idx_latih[a], idx_latih[v]
    terlarang = set(df.id.values[np.concatenate([np.where(df.fold == k)[0], idx_val])])
    ekor = semua.iloc[n_utama:]
    pakai = np.where(ekor.sumber.isin(VARIAN[varian]).values & ~ekor.id_asal.isin(terlarang).values)[0] + n_utama
    return np.concatenate([idx_latih, pakai]), idx_val, len(pakai)


def skor(k, p, model, input_, varian, n_aug, **lain):
    y_uji = y_semua[np.where(df.fold == k)[0]]
    f1 = f1_score(y_uji, p, labels=range(3), average=None, zero_division=0)
    return {"model": model, "input": input_, "augmentasi": varian, "fold": k, "n_aug": n_aug, "macro_f1": f1.mean(),
            "akurasi": accuracy_score(y_uji, p), "balanced_acc": balanced_accuracy_score(y_uji, p),
            **{f"f1_{c}": v for c, v in zip(LABEL, f1)}, **lain}"""),
    md("""## 1. IndoBERT sebagai embedding

Teks dan judul diubah menjadi vektor secara terpisah (maksimal 128 token masing-masing), lalu untuk input teks + judul kedua vektor digabung menjadi 1.536 dimensi. Saya memakai rata-rata vektor semua token (mean pooling), bukan vektor token `[CLS]` saja. Tanpa fine-tuning, vektor `[CLS]` belum dilatih untuk merangkum kalimat, sedangkan rata-rata token biasanya lebih stabil untuk dipakai sebagai fitur.

Teks yang dipakai adalah `teks_bert` (tanpa lowercase dari notebook kita, emoji sudah jadi kata bahasa Indonesia). IndoBERT p1 adalah model uncased, jadi tokenizer-nya tetap mengubah huruf menjadi kecil."""),
    code("""tok = AutoTokenizer.from_pretrained(MODEL_NAMA)
bert = AutoModel.from_pretrained(MODEL_NAMA).to(DEVICE).eval()


@torch.no_grad()
def embed(teks, batch=64):
    out = []
    teks = list(teks)
    for i in range(0, len(teks), batch):
        x = tok(teks[i:i + batch], truncation=True, max_length=128, padding=True, return_tensors="pt").to(DEVICE)
        with torch.autocast(device_type=DEVICE.type, dtype=torch.float16, enabled=DEVICE.type == "cuda"):
            h = bert(**x).last_hidden_state.float()
        m = x["attention_mask"].unsqueeze(-1).float()
        out.append(((h * m).sum(1) / m.sum(1)).cpu().numpy())
    return np.concatenate(out)


mulai = time.time()
E_teks = embed(semua.teks_bert)
E_judul_unik = semua.judul_bert.drop_duplicates()
peta = dict(zip(E_judul_unik, embed(E_judul_unik)))
E_judul = np.stack([peta[j] for j in semua.judul_bert])
print("embedding:", E_teks.shape, E_judul.shape, f"{time.time() - mulai:.0f} detik")
del bert
torch.cuda.empty_cache()"""),
    md("""Logistic Regression memakai class weight seimbang. Nilai `C` dipilih dengan 3-fold CV di dalam data latih saja (nested CV), dikelompokkan per grup supaya akun yang sama tidak ada di dua sisi. Fitur distandarkan dulu karena skala tiap dimensi embedding berbeda-beda."""),
    code("""hasil = []
grup_semua = semua.grup.fillna(semua.id_asal).values
for input_ in INPUT:
    X = E_teks if input_ == "teks saja" else np.hstack([E_teks, E_judul])
    for varian in VARIAN:
        pred = np.empty(n_utama, dtype=int)
        for k in range(5):
            idx_tr, _, n_aug = indeks_latih(k, varian)
            idx_uji = np.where(df.fold == k)[0]
            model = GridSearchCV(make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=3000)),
                                 {"logisticregression__C": [0.001, 0.003, 0.01, 0.03]}, scoring="f1_macro",
                                 cv=StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=SEED), n_jobs=-1)
            model.fit(X[idx_tr], y_semua[idx_tr], groups=grup_semua[idx_tr])
            pred[idx_uji] = model.predict(X[idx_uji])
            hasil.append(skor(k, pred[idx_uji], "IndoBERT embedding + LogReg", input_, varian, n_aug,
                              param=model.best_params_["logisticregression__C"]))
        r = pd.DataFrame(hasil[-5:])
        print(f"embedding+LogReg | {input_:12} | {varian:20} | macro-F1 {r.macro_f1.mean():.3f} ± {r.macro_f1.std():.3f}"
              f" | F1 positif {r.f1_positif.mean():.3f}", flush=True)
        pd.DataFrame({"id": df.id, "prediksi": np.array(LABEL)[pred]}).to_csv(
            OUT / f"prediksi_embedding_{input_}_{varian}.csv".replace(" ", "_").replace("+", ""), index=False)
pd.DataFrame(hasil).to_csv(OUT / "hasil_per_fold_embed_bilstm.csv", index=False)"""),
    md("""## 2. BiLSTM + attention

Arsitekturnya:

- **Embedding** 768 dimensi, diambil dari lapisan embedding kata IndoBERT dan dibekukan. Dengan data latih sekitar 2.600 teks, melatih embedding dari nol akan overfitting, jadi lebih masuk akal memakai embedding yang sudah ada. Tokenizer-nya juga tokenizer IndoBERT (wordpiece), sehingga kata slang yang tidak dikenal tetap dipecah jadi potongan kata.
- **BiLSTM** 2 arah dengan 128 unit per arah. Untuk teks + judul, keduanya disambung dengan token `[SEP]` dan teks diletakkan di depan, jadi kalau terpotong yang hilang adalah ujung judul.
- **Attention**: setiap posisi diberi skor, lalu output BiLSTM dirata-rata dengan bobot skor tersebut. Padding tidak ikut dihitung.
- **Dropout** 0,3, lalu satu lapisan linear ke 3 kelas.

Dilatih 10 epoch dengan Adam (learning rate 1e-3), batch 32, dan class weight seimbang. Epoch terbaik dipilih dari 10% data latih yang disisihkan per grup, sama seperti notebook 03."""),
    code("""emb_bert = AutoModel.from_pretrained(MODEL_NAMA).embeddings.word_embeddings.weight.detach().clone()


class BiLSTMAttention(nn.Module):
    def __init__(self, emb, hidden=128):
        super().__init__()
        self.emb = nn.Embedding.from_pretrained(emb, freeze=True, padding_idx=tok.pad_token_id)
        self.lstm = nn.LSTM(emb.shape[1], hidden, batch_first=True, bidirectional=True)
        self.att = nn.Linear(2 * hidden, 1)
        self.drop = nn.Dropout(0.3)
        self.out = nn.Linear(2 * hidden, 3)

    def forward(self, ids, mask):
        h, _ = self.lstm(self.drop(self.emb(ids)))
        s = self.att(h).squeeze(-1).masked_fill(mask == 0, -1e4)
        a = torch.softmax(s, -1)
        return self.out(self.drop((h * a.unsqueeze(-1)).sum(1))), a


def ke_id(input_):
    if input_ == "teks saja":
        x = tok(list(semua.teks_bert), truncation=True, max_length=128, padding="max_length", return_tensors="pt")
    else:
        x = tok(list(semua.teks_bert), list(semua.judul_bert), truncation="longest_first", max_length=192,
                padding="max_length", return_tensors="pt")
    return x["input_ids"], x["attention_mask"]


@torch.no_grad()
def tebak(model, ids, mask, idx):
    model.eval()
    out = []
    for i in range(0, len(idx), 256):
        j = idx[i:i + 256]
        out.append(torch.softmax(model(ids[j].to(DEVICE), mask[j].to(DEVICE))[0], -1).cpu().numpy())
    return np.concatenate(out)


def latih_bilstm(ids, mask, k, varian, epoch=10):
    idx_tr, idx_val, n_aug = indeks_latih(k, varian, sisihkan_val=True)
    set_seed()
    model = BiLSTMAttention(emb_bert).to(DEVICE)
    bobot = compute_class_weight("balanced", classes=np.arange(3), y=y_semua[idx_tr])
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor(bobot, dtype=torch.float, device=DEVICE))
    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=1e-3)
    y_t = torch.tensor(y_semua)
    terbaik, simpanan, riwayat = -1, None, []
    for ep in range(epoch):
        model.train()
        acak = np.random.permutation(idx_tr)
        for i in range(0, len(acak), 32):
            j = acak[i:i + 32]
            logit, _ = model(ids[j].to(DEVICE), mask[j].to(DEVICE))
            loss = loss_fn(logit, y_t[j].to(DEVICE))
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        f1_val = f1_score(y_semua[idx_val], tebak(model, ids, mask, idx_val).argmax(1), average="macro")
        riwayat.append(round(f1_val, 4))
        if f1_val > terbaik:
            terbaik, simpanan = f1_val, {kk: v.detach().clone() for kk, v in model.state_dict().items()}
    model.load_state_dict(simpanan)
    return model, riwayat, n_aug"""),
    code("""contoh_att = {}
for input_ in INPUT:
    ids, mask = ke_id(input_)
    for varian in VARIAN:
        pred = np.empty(n_utama, dtype=int)
        mulai = time.time()
        for k in range(5):
            idx_uji = np.where(df.fold == k)[0]
            model, riwayat, n_aug = latih_bilstm(ids, mask, k, varian)
            pred[idx_uji] = tebak(model, ids, mask, idx_uji).argmax(1)
            hasil.append(skor(k, pred[idx_uji], "BiLSTM + attention", input_, varian, n_aug,
                              epoch_terbaik=int(np.argmax(riwayat)) + 1, f1_val_per_epoch=str(riwayat)))
            if input_ == "teks saja" and varian == "tanpa augmentasi" and k == 0:
                contoh_att["model"], contoh_att["idx"] = model, idx_uji
        r = pd.DataFrame(hasil[-5:])
        print(f"BiLSTM+attention | {input_:12} | {varian:20} | macro-F1 {r.macro_f1.mean():.3f} ± {r.macro_f1.std():.3f}"
              f" | F1 positif {r.f1_positif.mean():.3f} | {time.time() - mulai:.0f} detik", flush=True)
        pd.DataFrame({"id": df.id, "prediksi": np.array(LABEL)[pred]}).to_csv(
            OUT / f"prediksi_bilstm_{input_}_{varian}.csv".replace(" ", "_").replace("+", ""), index=False)
        pd.DataFrame(hasil).to_csv(OUT / "hasil_per_fold_embed_bilstm.csv", index=False)"""),
    md("""Bobot attention bisa dipakai untuk melihat kata mana yang paling diperhatikan model. Sel berikut menampilkan 3 kata dengan bobot tertinggi untuk beberapa teks positif di fold 0 (model teks saja, tanpa augmentasi)."""),
    code("""ids, mask = ke_id("teks saja")
model, idx = contoh_att["model"], contoh_att["idx"]
pos = [i for i in idx if y_semua[i] == 2][:8]
with torch.no_grad():
    model.eval()
    _, a = model(ids[pos].to(DEVICE), mask[pos].to(DEVICE))
for n, i in enumerate(pos):
    token = tok.convert_ids_to_tokens(ids[i][mask[i] == 1])
    bobot = a[n][: len(token)].cpu().numpy()
    top = [token[j] for j in bobot.argsort()[::-1][:3]]
    print(f"{semua.teks_bert[i][:80]!r:85} -> {top}")"""),
    md("""## Ringkasan

Tabel di bawah merangkum kedua metode untuk semua kombinasi input dan augmentasi. Perbandingan dengan model lain dan analisis kesalahannya ada di notebook 05."""),
    code("""r = pd.DataFrame(hasil)
print(r.groupby(["model", "input", "augmentasi"], sort=False).agg(
    macro_f1=("macro_f1", "mean"), sd=("macro_f1", "std"), f1_negatif=("f1_negatif", "mean"),
    f1_netral=("f1_netral", "mean"), f1_positif=("f1_positif", "mean")).round(3).to_string())"""),
]


def main():
    nb = nbf.v4.new_notebook()
    nb.cells = CELLS
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    nbf.write(nb, NB / "04_embedding_bilstm_kaggle.ipynb")
    d = NB / "_kaggle" / "embed_bilstm"
    d.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, d / "notebook.ipynb")
    (d / "kernel-metadata.json").write_text(json.dumps({
        "id": "raphaeladikara/uas-nlp-raffi-embedding-bilstm", "title": "uas-nlp-raffi-embedding-bilstm",
        "code_file": "notebook.ipynb", "language": "python", "kernel_type": "notebook", "is_private": True,
        "enable_gpu": True, "enable_internet": True,
        "dataset_sources": ["raphaeladikara/uas-nlp-raffi-v2"], "competition_sources": [], "kernel_sources": []},
        indent=1))
    print("ok")


if __name__ == "__main__":
    main()
