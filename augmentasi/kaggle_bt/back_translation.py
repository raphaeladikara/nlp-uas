# Back-translation Indonesia -> Inggris -> Indonesia untuk augmentasi kelas positif.
# Dijalankan di Kaggle (GPU T4). Input bt_sumber.csv dari augmentasi/siapkan_bt.py.
# Arah id->en memakai sampling supaya terjemahan Inggrisnya bervariasi, arah en->id memakai beam search
# supaya hasil bahasa Indonesianya tetap rapi. Setiap teks diberi sampai 3 parafrase yang berbeda dari aslinya.
import glob
import re

import pandas as pd
import torch
from transformers import MarianMTModel, MarianTokenizer

torch.manual_seed(42)
dev = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", dev)

# TAMBAHAN = True hanya memproses teks positif baru dari review 3 lapis (bt_sumber_tambahan.csv),
# hasilnya disambung ke parafrase lama. False = proses ulang semua bt_sumber.csv.
TAMBAHAN = True
nama_sumber = "bt_sumber_tambahan.csv" if TAMBAHAN else "bt_sumber.csv"
src = pd.read_csv(glob.glob(f"/kaggle/input/**/{nama_sumber}", recursive=True)[0], dtype=str).fillna("")
print("teks sumber:", len(src))


def muat(nama):
    return MarianTokenizer.from_pretrained(nama), MarianMTModel.from_pretrained(nama).to(dev).eval()


tok_ie, mod_ie = muat("Helsinki-NLP/opus-mt-id-en")
tok_ei, mod_ei = muat("Helsinki-NLP/opus-mt-en-id")


@torch.no_grad()
def terjemah(tok, mod, teks, **gen):
    out = []
    for i in range(0, len(teks), 32):
        x = tok(teks[i:i + 32], return_tensors="pt", padding=True, truncation=True, max_length=256).to(dev)
        y = mod.generate(**x, max_new_tokens=256, **gen)
        out += tok.batch_decode(y, skip_special_tokens=True)
    return out


N = 4
asli = src.text.tolist()
# @user diganti sementara supaya tidak diterjemahkan aneh-aneh
masuk = [re.sub(r"@user", "Budi", t) for t in asli]
inggris = terjemah(tok_ie, mod_ie, masuk, do_sample=True, top_p=0.9, temperature=0.9, num_return_sequences=N)
balik = terjemah(tok_ei, mod_ei, inggris, num_beams=4)

norm = lambda t: " ".join(re.sub(r"[^a-z0-9 ]", " ", t.lower()).split())
baris = []
for i, r in src.iterrows():
    sudah = {norm(r.text)}
    for k in range(N):
        p = re.sub(r"\bBudi\b", "@user", balik[i * N + k]).strip()
        if p and norm(p) not in sudah and len(sudah) <= 3:
            sudah.add(norm(p))
            baris.append(dict(id=r.id, kelompok=r.kelompok, text_asli=r.text, inggris=inggris[i * N + k], parafrase=p))
hasil = pd.DataFrame(baris)
hasil["id_aug"] = hasil.id + "_bt" + hasil.groupby("id").cumcount().astype(str)
hasil.to_csv("/kaggle/working/augmentasi_bt.csv", index=False, encoding="utf-8-sig")
print("parafrase:", len(hasil), "| teks yang dapat parafrase:", hasil.id.nunique())
print(hasil.sample(min(15, len(hasil)), random_state=1)[["text_asli", "parafrase"]].to_string())
