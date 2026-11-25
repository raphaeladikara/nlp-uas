"""Isi output sel notebook 03 dan 04 (versi lokal) dari log Kaggle.

Pakai : python notebooks/_build/isi_output_kaggle.py   (setelah build_03.py dan build_04.py)

Kaggle CLI hanya mengunduh berkas hasil dan log, bukan notebook yang sudah dijalankan. Log berisi semua teks yang
dicetak (stdout) secara berurutan, jadi setiap baris dikembalikan ke sel kode yang mencetaknya: baris dicocokkan dengan
potongan teks tetap di dalam print() sel itu, dan urutan sel tidak pernah mundur. Gambar tidak ada di log.
Di akhir notebook ditambah ringkasan semua model yang dibaca dari CSV hasil Kaggle dan dijalankan di laptop.
"""
import json
import re
from pathlib import Path

import codecs

import nbformat as nbf

codecs.register_error("latin1_fallback", lambda e: (e.object[e.start:e.end].decode("latin-1"), e.end))

NB = Path(__file__).resolve().parents[1]
D = NB.parent / "data"


def baca_log(f):
    # log campuran: sebagian besar UTF-8, tapi tanda ± kadang tertulis sebagai satu byte latin-1
    isi = json.loads(Path(f).read_bytes().decode("utf-8", errors="latin1_fallback"))
    return "".join(x["data"] for x in isi if x["stream_name"] == "stdout").splitlines()


def potongan(src):
    """Potongan teks tetap (minimal 2 huruf) di dalam string print() sebuah sel."""
    out = []
    for m in re.finditer(r"print\((.*?)\)\s*$", src, re.M | re.S):
        for s in re.findall(r"[fr]?\"([^\"]*)\"|[fr]?'([^']*)'", m.group(1)):
            teks = s[0] or s[1]
            for c in re.split(r"\{[^}]*\}", teks):
                c = c.strip()
                if len(c) >= 2:
                    out.append(c)
    return out


def isi(nb, baris, kunci_ringkas="macro_f1"):
    kode = [c for c in nb.cells if c.cell_type == "code"]
    pot = [potongan(c.source) for c in kode]
    hasil = {i: [] for i in range(len(kode))}
    p = 0
    for b in baris:
        if kunci_ringkas in b and "|" not in b:
            p = len(kode) - 1
        else:
            # pilih sel (tidak mundur) yang potongan teks tetapnya paling panjang cocok dengan baris ini
            skor = [(max([len(c) for c in pot[j] if c in b], default=0), -j) for j in range(p, len(kode))]
            terbaik = max(skor)
            if terbaik[0] >= 4 or (terbaik[0] >= 2 and -terbaik[1] > p):
                p = -terbaik[1]
        hasil[p].append(b)
    for i, c in enumerate(kode):
        c.outputs = [nbf.v4.new_output("stream", name="stdout", text="\n".join(hasil[i]) + "\n")] if hasil[i] else []
        c.execution_count = i + 1
    return nb


CATATAN = """> **Catatan cara membaca.** Notebook ini dijalankan di Kaggle (GPU T4) lewat Kaggle CLI. Kaggle CLI hanya mengunduh berkas hasil dan log, bukan notebook yang sudah dijalankan, jadi output setiap sel di sini diisi ulang dari log Kaggle (`{log}`) oleh `notebooks/_build/isi_output_kaggle.py`. Isinya teks yang benar-benar dicetak saat training di Kaggle, tidak diubah. Berkas hasilnya ada di `{folder}`. {lain}"""


def tambah_ringkasan(nb, berkas, judul):
    nb.cells.append(nbf.v4.new_markdown_cell(f"""## Ringkasan semua model (dijalankan di laptop)

{judul} Sel ini membaca CSV hasil Kaggle, jadi bisa dijalankan tanpa GPU."""))
    nb.cells.append(nbf.v4.new_code_cell(f"""import pandas as pd
from pathlib import Path
D = Path.cwd().parent / "data"
r = pd.concat([pd.read_csv(D / f) for f in {berkas!r} if (D / f).exists()])
r.groupby(["model", "input", "augmentasi"], sort=False).agg(
    macro_f1=("macro_f1", "mean"), sd=("macro_f1", "std"), f1_negatif=("f1_negatif", "mean"),
    f1_netral=("f1_netral", "mean"), f1_positif=("f1_positif", "mean"), sd_positif=("f1_positif", "std")).round(3)"""))
    # sel ini dijalankan langsung di sini (di laptop), hasilnya ditempel sebagai output
    import pandas as pd
    r = pd.concat([pd.read_csv(D / f) for f in berkas if (D / f).exists()])
    t = r.groupby(["model", "input", "augmentasi"], sort=False).agg(
        macro_f1=("macro_f1", "mean"), sd=("macro_f1", "std"), f1_negatif=("f1_negatif", "mean"),
        f1_netral=("f1_netral", "mean"), f1_positif=("f1_positif", "mean"), sd_positif=("f1_positif", "std")).round(3)
    nb.cells[-1].outputs = [nbf.v4.new_output("execute_result", data={"text/plain": t.to_string(), "text/html": t.to_html()},
                                              execution_count=99)]
    nb.cells[-1].execution_count = 99
    return nb


def main():
    # notebook 03: kode yang sama untuk ketiga model, versi lokal memakai IndoBERTweet
    nb = nbf.read(NB / "03_transformer_kaggle.ipynb", as_version=4)
    nb = isi(nb, baca_log(D / "07_transformer" / "uas-nlp-raffi-indobertweet.log"))
    lain = ("IndoBERT dan XLM-RoBERTa memakai kode yang sama persis, hanya `MODEL_KEY` yang diganti, dan log-nya ada di "
            "`data/07_transformer/uas-nlp-raffi-indobert.log` dan `uas-nlp-raffi-xlmr.log`. Hasil ketiga model dirangkum "
            "di sel terakhir.")
    nb.cells.insert(1, nbf.v4.new_markdown_cell(CATATAN.format(log="data/07_transformer/uas-nlp-raffi-indobertweet.log",
                                                               folder="data/07_transformer/", lain=lain)))
    nb = tambah_ringkasan(nb, [f"07_transformer/hasil_per_fold_{k}.csv" for k in ["indobertweet", "indobert", "xlmr"]],
                          "Tabel ini menggabungkan hasil IndoBERTweet, IndoBERT, dan XLM-RoBERTa.")
    nbf.write(nb, NB / "03_transformer_kaggle.ipynb")

    nb = nbf.read(NB / "04_embedding_bilstm_kaggle.ipynb", as_version=4)
    nb = isi(nb, baca_log(D / "08_embedding_bilstm" / "uas-nlp-raffi-embedding-bilstm.log"))
    nb.cells.insert(1, nbf.v4.new_markdown_cell(CATATAN.format(log="data/08_embedding_bilstm/uas-nlp-raffi-embedding-bilstm.log",
                                                               folder="data/08_embedding_bilstm/", lain="")))
    nb = tambah_ringkasan(nb, ["08_embedding_bilstm/hasil_per_fold_embed_bilstm.csv"],
                          "Tabel ini merangkum IndoBERT embedding + LogReg dan BiLSTM + attention.")
    nbf.write(nb, NB / "04_embedding_bilstm_kaggle.ipynb")
    print("ok")


if __name__ == "__main__":
    main()
