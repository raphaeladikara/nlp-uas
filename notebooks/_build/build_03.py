"""Bangun notebook 03 (fine-tuning transformer di Kaggle) untuk tiga model.

Pakai : python notebooks/_build/build_03.py
Output: notebooks/03_transformer_kaggle.ipynb          (versi yang dikumpulkan, MODEL_KEY = "indobertweet")
        notebooks/_kaggle/<model>/notebook.ipynb + kernel-metadata.json (satu kernel Kaggle per model)
"""
import json
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
NB = HERE.parent
MODELS = {
    "indobertweet": "indolem/indobertweet-base-uncased",
    "indobert": "indobenchmark/indobert-base-p1",
    "xlmr": "FacebookAI/xlm-roberta-base",
}


def md(s):
    return nbf.v4.new_markdown_cell(s.strip("\n"))


def code(s):
    return nbf.v4.new_code_cell(s.strip("\n"))


def cells(model_key):
    return [
        md("""
# Fine-tuning Transformer: Sentimen Publik terhadap Raffi Ahmad

**Nama:** Raphael Angelo Adikara Purnama
**NIM:** 164241055
**Mata kuliah:** Natural Language Processing (UAS)
**Topik:** Klasifikasi sentimen publik terhadap Raffi Ahmad setelah kasus "mahasiswa bayaran" di Bundaran HI (29 Oktober 2026)

Notebook ini melatih model transformer yang membaca kalimat secara utuh, jadi bisa memahami konteks kata di dalam kalimat (siapa yang dibela, siapa yang diserang). Ada tiga model yang dibandingkan, semuanya memakai notebook yang sama dan hanya beda nama model:

- **IndoBERTweet** (`indolem/indobertweet-base-uncased`): BERT yang dilatih dari tweet berbahasa Indonesia, jadi paling dekat dengan gaya tulisan di data ini.
- **IndoBERT** (`indobenchmark/indobert-base-p1`): BERT yang dilatih dari teks Indonesia formal (Wikipedia, berita, dan lain-lain). Gunanya untuk melihat apakah pretraining dari media sosial memang membantu.
- **XLM-RoBERTa** (`FacebookAI/xlm-roberta-base`): model multibahasa yang dilatih dari 100 bahasa termasuk Indonesia. Model ini cased, jadi huruf besar dan kecil dibedakan.

Notebook dijalankan di Kaggle (GPU T4) sebagai tiga kernel terpisah. Versi yang dikumpulkan ini memakai `MODEL_KEY = "indobertweet"`. Hasil ketiga kernel dibandingkan di notebook 05.

Perubahan dari versi sebelumnya (hasil konsultasi dosen): target biner dihapus dan diganti augmentasi kelas positif, teks untuk model BERT tidak lagi dibuat huruf kecil, emoji diubah menjadi kata bahasa Indonesia, dan istilah "konteks" diganti "judul"."""),
        code("""import re
import glob
import time
import random
import numpy as np
import pandas as pd
import torch
from pathlib import Path
from torch.utils.data import DataLoader
from transformers import (AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding,
                          get_linear_schedule_with_warmup)
from transformers.utils import logging as hf_logging
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import f1_score, accuracy_score, balanced_accuracy_score

hf_logging.set_verbosity_error()
pd.set_option("display.max_colwidth", 120)

DI_KAGGLE = Path("/kaggle/input").exists()
if DI_KAGGLE:
    DATA = Path(glob.glob("/kaggle/input/**/dataset_prepro.csv", recursive=True)[0]).parent
    OUT = Path("/kaggle/working")
else:
    ROOT = Path.cwd().parent
    DATA, OUT = ROOT / "data" / "05_final", ROOT / "data" / "07_transformer"
OUT.mkdir(parents=True, exist_ok=True)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("data dari:", DATA, "| device:", DEVICE, torch.cuda.get_device_name(0) if DEVICE.type == "cuda" else "")"""),
        md("""## Pengaturan

Hyperparameter ditentukan di awal dan sama untuk ketiga model, supaya perbedaan hasil datang dari modelnya, bukan dari tuning. Learning rate 2e-5, batch 16, 5 epoch, dan warmup 10% adalah pengaturan yang umum untuk fine-tuning BERT ukuran base. Epoch terbaik dipilih dari data validasi (10% dari data latih, dipisah per grup), bukan dari fold uji."""),
        code(f"""MODEL_KEY = "{model_key}"
MODEL_NAMA = {json.dumps(MODELS)}[MODEL_KEY]
MAX_LEN = {{"teks saja": 128, "teks + judul": 256}}
BATCH, EPOCH, LR, WARMUP, SEED = 16, 5, 2e-5, 0.1, 42
LABEL = ["negatif", "netral", "positif"]

# kombinasi yang dilatih: (input, varian augmentasi)
KONFIG = [("teks saja", "tanpa augmentasi"), ("teks saja", "jalur B + parafrase"),
          ("teks + judul", "tanpa augmentasi"), ("teks + judul", "jalur B"),
          ("teks + judul", "parafrase"), ("teks + judul", "jalur B + parafrase")]
VARIAN = {{"tanpa augmentasi": [], "jalur B": ["jalur_b"], "parafrase": ["bt_utama"],
          "jalur B + parafrase": ["jalur_b", "bt_utama", "bt_jalur_b"]}}


def set_seed(s=SEED):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)
    torch.cuda.manual_seed_all(s)


df = pd.read_csv(DATA / "dataset_prepro.csv", dtype={{"grup": str}}).fillna({{"judul_bert": "", "teks_bert": ""}})
aug = pd.read_csv(DATA / "augmentasi_prepro.csv", dtype={{"grup": str}}).fillna({{"judul_bert": "", "teks_bert": ""}})
print(MODEL_KEY, MODEL_NAMA)
print("data utama:", df.shape, df.label.value_counts().to_dict())
if aug.sumber.eq("terarah").any():
    VARIAN["jalur B + terarah"] = ["jalur_b", "terarah"]
    KONFIG.append(("teks + judul", "jalur B + terarah"))
print("augmentasi:", aug.sumber.value_counts().to_dict())"""),
        md("""## Preprocessing khusus BERT

Kolom `teks_ringan` dan `judul_ringan` sudah melalui preprocessing ringan di notebook 02: URL dibuang, mention jadi `@user`, tanda `#` dibuang, dan huruf berulang dipendekkan. Di versi sebelumnya teks juga dibuat huruf kecil dan emoji diubah ke nama bahasa Inggris. Sesuai saran dosen, dua hal ini saya ubah:

1. **Tidak ada lowercase.** Huruf kapital bisa membawa informasi, misalnya "BOIKOT" yang ditulis kapital semua biasanya lebih marah daripada "boikot". Teks dikirim apa adanya, dan keputusan huruf kecil diserahkan ke tokenizer masing-masing model. Sel di bawah memeriksa apa yang sebenarnya dilakukan tokenizer.
2. **Emoji jadi kata bahasa Indonesia.** 😂 menjadi "wajah gembira berurai air mata" dan 🤮 menjadi "wajah muntah", memakai `emoji.demojize(language="id")`. Ketiga model dilatih dari teks bahasa Indonesia (XLM-R juga mencakup Indonesia), jadi kata Indonesia lebih dekat dengan kosakata yang sudah dikenal model daripada nama emoji bahasa Inggris."""),
        code("""tok = AutoTokenizer.from_pretrained(MODEL_NAMA)
lower = getattr(tok, "do_lower_case", None)
print("do_lower_case di tokenizer:", lower)
for t in ["BOIKOT RANS", "boikot rans"]:
    print(f"{t!r:15} -> {tok.tokenize(t)}")
print("contoh emoji :", df.teks_bert[df.teks_ringan.str.contains("😂", na=False)].iloc[0][:120])"""),
        md("""Sel di atas menjawab pertanyaan apakah model bisa belajar dari pola huruf besar dan kecil. Kalau `do_lower_case` bernilai `True`, tokenizer tetap mengubah teks menjadi huruf kecil walaupun teks yang dikirim tidak di-lowercase, karena kosakatanya memang hanya berisi huruf kecil (model *uncased*). Jadi untuk IndoBERTweet dan IndoBERT, "BOIKOT" dan "boikot" tetap menjadi token yang sama. Hanya XLM-RoBERTa (*cased*) yang benar-benar bisa membedakan kapital. Ini salah satu alasan XLM-R ikut dibandingkan."""),
        md("""## Augmentasi hanya di fold latih

Ada dua sumber data tambahan untuk kelas positif (dibuat di notebook 02):

- **Jalur B**: komentar positif dari akun Instagram Raffi sendiri, rentang waktunya sama (22 Oktober sampai 14 November). Akun atau teks yang juga ada di data utama sudah dibuang, supaya tidak bocor ke fold uji.
- **Parafrase back-translation**: teks positif diterjemahkan ke bahasa Inggris lalu kembali ke Indonesia, sehingga isinya sama tapi kalimatnya berbeda.

Aturannya: data tambahan **hanya** masuk ke data latih. Parafrase dari teks yang sedang menjadi data uji (atau data validasi) tidak dipakai, karena isinya hampir sama dengan teks ujinya. Data uji di semua varian tetap sama, yaitu teks jalur A asli, jadi perbandingan sebelum dan sesudah augmentasi adil."""),
        code("""def ke_tensor(teks, judul, input_):
    if input_ == "teks saja":
        return tok(list(teks), truncation=True, max_length=MAX_LEN[input_])
    return tok(list(teks), list(judul), truncation="longest_first", max_length=MAX_LEN[input_])


semua = pd.concat([df.assign(sumber="utama", id_asal=df.id), aug], ignore_index=True)
y_semua = semua.label.map({c: i for i, c in enumerate(LABEL)}).values
n_utama = len(df)
collator = DataCollatorWithPadding(tok)


def loader(enc, idx, acak):
    data = [{k: enc[k][i] for k in enc.keys()} | {"labels": int(y_semua[i])} for i in idx]
    return DataLoader(data, batch_size=BATCH if acak else BATCH * 2, shuffle=acak, collate_fn=collator)


@torch.no_grad()
def tebak(model, enc, idx):
    model.eval()
    prob = []
    for b in loader(enc, idx, acak=False):
        b = {k: v.to(DEVICE) for k, v in b.items() if k != "labels"}
        with torch.autocast(device_type=DEVICE.type, dtype=torch.float16, enabled=DEVICE.type == "cuda"):
            prob.append(torch.softmax(model(**b).logits.float(), -1).cpu().numpy())
    return np.concatenate(prob)


def indeks_latih(k, varian):
    \"\"\"Indeks data utama untuk latih/validasi, ditambah augmentasi yang aman untuk fold uji k.\"\"\"
    idx_latih = np.where(df.fold != k)[0]
    sgk = StratifiedGroupKFold(n_splits=10, shuffle=True, random_state=SEED)
    a, v = next(sgk.split(idx_latih, y_semua[idx_latih], df.grup.values[idx_latih]))
    idx_tr, idx_val = idx_latih[a], idx_latih[v]
    terlarang = set(df.id.values[np.concatenate([np.where(df.fold == k)[0], idx_val])])
    pakai = semua.index[n_utama:][semua.sumber[n_utama:].isin(VARIAN[varian]).values
                                  & ~semua.id_asal[n_utama:].isin(terlarang).values]
    return np.concatenate([idx_tr, pakai.values]), idx_val, len(pakai)


def latih_satu_fold(enc, k, varian):
    idx_tr, idx_val, n_aug = indeks_latih(k, varian)
    idx_uji = np.where(df.fold == k)[0]
    set_seed()
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAMA, num_labels=3).to(DEVICE)
    bobot = compute_class_weight("balanced", classes=np.arange(3), y=y_semua[idx_tr])
    loss_fn = torch.nn.CrossEntropyLoss(weight=torch.tensor(bobot, dtype=torch.float, device=DEVICE))
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    dl = loader(enc, idx_tr, acak=True)
    total = len(dl) * EPOCH
    sched = get_linear_schedule_with_warmup(opt, int(WARMUP * total), total)
    scaler = torch.amp.GradScaler(enabled=DEVICE.type == "cuda")
    terbaik, simpanan, riwayat = -1.0, None, []
    for ep in range(EPOCH):
        model.train()
        for b in dl:
            b = {kk: v.to(DEVICE) for kk, v in b.items()}
            label = b.pop("labels")
            with torch.autocast(device_type=DEVICE.type, dtype=torch.float16, enabled=DEVICE.type == "cuda"):
                logits = model(**b).logits
            loss = loss_fn(logits.float(), label)
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sched.step()
        f1_val = f1_score(y_semua[idx_val], tebak(model, enc, idx_val).argmax(1), average="macro")
        riwayat.append(round(f1_val, 4))
        if f1_val > terbaik:
            terbaik = f1_val
            simpanan = {kk: t.detach().cpu().clone() for kk, t in model.state_dict().items()}
    model.load_state_dict(simpanan)
    prob = tebak(model, enc, idx_uji)
    del model, opt
    torch.cuda.empty_cache()
    return prob, riwayat, n_aug"""),
        md("""## Training

Setiap kombinasi dilatih dengan grouped 5-fold CV yang sama dengan notebook 02 (kolom `fold`), jadi hasilnya bisa dibandingkan per fold dengan baseline. Class weight seimbang tetap dipakai di semua varian. Hasil per fold dan prediksi disimpan ke CSV, dan kombinasi yang sudah selesai dilewati kalau notebook dijalankan ulang."""),
        code("""hasil = []
for input_, varian in KONFIG:
    nama = f"{MODEL_KEY}|{input_}|{varian}"
    f_pred = OUT / f"prediksi_{MODEL_KEY}_{input_}_{varian}.csv".replace(" ", "_").replace("+", "")
    enc = ke_tensor(semua.teks_bert, semua.judul_bert, input_)
    prob = np.zeros((n_utama, 3))
    for k in range(5):
        mulai = time.time()
        idx_uji = np.where(df.fold == k)[0]
        prob[idx_uji], riwayat, n_aug = latih_satu_fold(enc, k, varian)
        y_uji, p = y_semua[idx_uji], prob[idx_uji].argmax(1)
        f1 = f1_score(y_uji, p, labels=range(3), average=None, zero_division=0)
        hasil.append({"model": MODEL_KEY, "input": input_, "augmentasi": varian, "fold": k, "n_aug": n_aug,
                      "macro_f1": f1.mean(), "akurasi": accuracy_score(y_uji, p),
                      "balanced_acc": balanced_accuracy_score(y_uji, p),
                      **{f"f1_{c}": v for c, v in zip(LABEL, f1)},
                      "epoch_terbaik": int(np.argmax(riwayat)) + 1, "f1_val_per_epoch": str(riwayat)})
        print(f"{nama} | fold {k}: macro-F1 {f1.mean():.3f}, F1 positif {f1[2]:.3f}, "
              f"+{n_aug} augmentasi, epoch {np.argmax(riwayat) + 1}, {time.time() - mulai:.0f} detik", flush=True)
    pd.DataFrame({"id": df.id, "prediksi": np.array(LABEL)[prob.argmax(1)],
                  **{f"prob_{c}": prob[:, i] for i, c in enumerate(LABEL)}}).to_csv(f_pred, index=False)
    pd.DataFrame(hasil).to_csv(OUT / f"hasil_per_fold_{MODEL_KEY}.csv", index=False)"""),
        md("""## Ringkasan

Tabel di bawah merangkum macro-F1 dan F1 per kelas (rata-rata 5 fold ± standar deviasi) untuk setiap kombinasi. Perbandingan dengan model lain, uji per fold, dan analisis kesalahan dibahas di notebook 05."""),
        code("""r = pd.DataFrame(hasil)
ringkas = r.groupby(["input", "augmentasi"], sort=False).agg(
    macro_f1=("macro_f1", "mean"), sd=("macro_f1", "std"), f1_negatif=("f1_negatif", "mean"),
    f1_netral=("f1_netral", "mean"), f1_positif=("f1_positif", "mean"), n_aug=("n_aug", "mean")).round(3)
print(ringkas.to_string())"""),
    ]


def main():
    for key in MODELS:
        nb = nbf.v4.new_notebook()
        nb.cells = cells(key)
        nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}}
        d = NB / "_kaggle" / key
        d.mkdir(parents=True, exist_ok=True)
        nbf.write(nb, d / "notebook.ipynb")
        (d / "kernel-metadata.json").write_text(json.dumps({
            "id": f"raphaeladikara/uas-nlp-raffi-{key}", "title": f"uas-nlp-raffi-{key}",
            "code_file": "notebook.ipynb", "language": "python", "kernel_type": "notebook", "is_private": True,
            "enable_gpu": True, "enable_internet": True,
            "dataset_sources": ["raphaeladikara/uas-nlp-raffi-v2"], "competition_sources": [],
            "kernel_sources": []}, indent=1))
        if key == "indobertweet":
            nbf.write(nb, NB / "03_transformer_kaggle.ipynb")
    print("ok")


if __name__ == "__main__":
    main()
