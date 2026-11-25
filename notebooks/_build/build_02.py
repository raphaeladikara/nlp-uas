"""Bangun notebook 02 (preprocessing, augmentasi, baseline). Sel markdown pembacaan hasil diberi tag "baca-<nama>"
supaya bisa diisi angka setelah notebook dijalankan (lihat isi_baca_02.py).

Pakai : python notebooks/_build/build_02.py
"""
from pathlib import Path

import nbformat as nbf

NB = Path(__file__).resolve().parents[1]


def md(s, tag=None):
    c = nbf.v4.new_markdown_cell(s.strip("\n"))
    if tag:
        c.metadata["tags"] = [tag]
    return c


def code(s):
    return nbf.v4.new_code_cell(s.strip("\n"))


def baca(nama):
    return md("(dibaca setelah dijalankan)", f"baca-{nama}")


CELLS = [
    md("""
# Preprocessing, Augmentasi, dan Baseline: Sentimen Publik terhadap Raffi Ahmad

**Nama:** Raphael Angelo Adikara Purnama
**NIM:** 164241055
**Mata kuliah:** Natural Language Processing (UAS)
**Topik:** Klasifikasi sentimen publik terhadap Raffi Ahmad setelah kasus "mahasiswa bayaran" di Bundaran HI (29 Oktober 2026)

Notebook ini menyiapkan teks untuk semua model, membuat data augmentasi untuk kelas positif, lalu melatih baseline. Datanya `data/05_final/dataset_model.csv` dari `labeling/finalize.py`, yang sudah punya label akhir dan pembagian 5 fold.

Ada beberapa perubahan dari versi sebelumnya setelah konsultasi dosen:

1. **Target biner dihapus.** Sebelumnya saya juga melatih target negatif lawan bukan negatif, karena kelas positif sangat sedikit. Dosen menyarankan tetap 3 kelas dan menambah data positif lewat augmentasi.
2. **Augmentasi kelas positif** dari dua sumber: komentar positif di akun Instagram Raffi sendiri (jalur B) pada rentang waktu yang sama, dan parafrase hasil back-translation. Setiap model dibandingkan sebelum dan sesudah augmentasi.
3. **Istilah "konteks" diganti "judul"**, dan contoh datanya ditampilkan supaya jelas apa yang dibaca model.
4. **Preprocessing untuk model BERT tidak lagi memakai lowercase**, dan emoji diubah menjadi kata bahasa Indonesia, bukan bahasa Inggris."""),
    code("""import re
import sys
import json
import warnings
import emoji
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from IPython.display import display
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold
from sklearn.metrics import f1_score, accuracy_score, balanced_accuracy_score

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*converge.*")
pd.set_option("display.max_colwidth", 110)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})

ROOT = Path.cwd().parent
RES, FIG, FINAL = ROOT / "resources", ROOT / "figures", ROOT / "data" / "05_final"
HASIL = ROOT / "data" / "06_baseline"
HASIL.mkdir(parents=True, exist_ok=True)

# fungsi pengelompokan yang sama dengan yang dipakai finalize.py saat membuat fold
sys.path.insert(0, str(ROOT / "labeling"))
from finalize import kunci, grup

df = pd.read_csv(FINAL / "dataset_model.csv", dtype={"sumber_id": str})
df["judul"] = df.judul.fillna("")
df["kunci"] = df.text.map(kunci)
df["grup"] = grup(df)
print(df.shape)
print(df.label.value_counts().to_string())
pd.crosstab(df.fold, df.label, margins=True)"""),
    baca("data"),
    md("""## Apa yang dimaksud "judul"

Di versi sebelumnya saya menyebutnya "konteks". Isinya adalah teks unggahan tempat sebuah komentar ditulis, jadi istilah "judul" lebih tepat. Isi kolom `judul` berbeda per platform karena tiap platform punya bentuk unggahan yang berbeda:

| platform | isi kolom `judul` |
|---|---|
| YouTube | judul video, diawali nama channel |
| Instagram | caption unggahan, diawali nama akun pemilik |
| TikTok | deskripsi video, diawali nama kreator |
| X | isi tweet yang dikutip atau dibalas. Kalau tweet induknya tidak ikut ter-scrape, judulnya hanya keterangan bahwa tweet ini membalas akun lain. Tweet yang berdiri sendiri tidak punya judul |

Judul perlu karena banyak komentar yang baru jelas maknanya kalau tahu unggahannya. "14 M" atau "pantes aja" tidak berarti apa-apa tanpa tahu bahwa videonya membahas kontrak Rp14,7 miliar. Tabel di bawah memperlihatkan contoh data per platform, persis seperti yang dibaca annotator dan model."""),
    code("""contoh_judul = pd.concat([g[g.butuh_konteks].sample(2, random_state=3)
                          for _, g in df[df.judul.str.len() > 0].groupby("platform")])
contoh_judul[["platform", "judul", "text", "label"]].assign(judul=lambda x: x.judul.str[:110])"""),
    baca("judul"),
    code("""print("teks yang punya judul:", f"{df.judul.str.len().gt(0).mean():.1%}")
print(df.assign(punya_judul=df.judul.str.len().gt(0)).groupby("platform").punya_judul.mean().round(3).to_string())"""),
    baca("punya-judul"),
    code("""panjang = df.text.str.split().str.len()
print("jumlah kata per teks:")
print(panjang.describe(percentiles=[.25, .5, .75, .95]).round(1).to_string())
print()
print("teks yang memuat mention :", round(df.text.str.contains("@").mean() * 100, 1), "%")
print("teks yang memuat emoji   :", round(df.text.map(lambda t: emoji.emoji_count(t) > 0).mean() * 100, 1), "%")
print("teks yang memuat hashtag :", round(df.text.str.contains("#").mean() * 100, 1), "%")
print("teks dengan kata KAPITAL :", round(df.text.str.contains(r"\\b[A-Z]{4,}\\b").mean() * 100, 1), "%")
print("ditandai butuh judul     :", round(df.butuh_konteks.mean() * 100, 1), "%")"""),
    baca("statistik"),
    md("""## Preprocessing

Model yang berbeda butuh teks yang berbeda, jadi preprocessing dibagi tiga tingkat:

1. **Ringan**, dipakai semua model: mention jadi `@user`, URL dibuang, tanda `#` dibuang tapi katanya tetap, huruf yang diulang tiga kali atau lebih dipendekkan ("bangettt" jadi "banget"). Huruf besar dan emoji tidak diubah.
2. **Lengkap**, khusus TF-IDF: ringan + huruf kecil, emoji jadi token (`emo_wajah_muntah`), variasi tawa ("wkwk", "hahaha") disamakan jadi `tawa`, slang dinormalisasi dengan kamus 711 kata, lalu stopword dibuang dengan kata negasi tetap disimpan. TF-IDF hanya menghitung kata, jadi "Boikot", "boikot", dan "BOIKOT" harus disamakan supaya terhitung sebagai kata yang sama.
3. **BERT**, untuk IndoBERTweet, IndoBERT, XLM-R, embedding, dan BiLSTM: ringan + emoji diubah menjadi kata bahasa Indonesia (😂 jadi "wajah gembira berurai air mata"). **Tidak ada lowercase**. Model transformer membaca kalimat utuh dan punya tokenizer sendiri, jadi teks dikirim sedekat mungkin dengan aslinya. Kalau model-nya *cased* (XLM-R), huruf kapital bisa dipakai sebagai sinyal, misalnya "MAMPUS LU" yang ditulis kapital. Kalau model-nya *uncased*, tokenizer-nya sendiri yang mengubah ke huruf kecil. Emoji diubah ke bahasa Indonesia karena modelnya dilatih dari teks Indonesia, jadi kata Indonesia lebih mungkin sudah dikenal."""),
    code("""slang = json.load(open(RES / "slang_map.json", encoding="utf-8"))
NEGASI = {"tidak", "tdk", "gak", "ga", "gk", "nggak", "ngga", "enggak", "engga", "g", "bukan", "bkn",
          "jangan", "jgn", "belum", "blm", "tak", "kurang"}
stopword = set(open(RES / "stopwords.txt", encoding="utf-8").read().split()) - NEGASI
print("kamus slang:", len(slang), "| stopword:", len(stopword))


def bersih_ringan(t):
    t = str(t)
    t = re.sub(r"https?://\\S+|www\\.\\S+", " ", t)
    t = re.sub(r"@\\w+", "@user", t)
    t = re.sub(r"#(\\w+)", r"\\1", t)
    t = re.sub(r"([a-zA-Z])\\1{2,}", r"\\1", t)
    return re.sub(r"\\s+", " ", t).strip()


def untuk_bert(t):
    \"\"\"Ringan + emoji jadi kata bahasa Indonesia. Huruf besar tidak diubah.\"\"\"
    t = emoji.demojize(bersih_ringan(t), language="id", delimiters=(" ", " "))
    return re.sub(r"\\s+", " ", t.replace("_", " ")).strip()


def ke_token(t):
    t = bersih_ringan(t).lower()
    t = emoji.demojize(t, language="id", delimiters=(" emo_", " "))
    t = re.sub(r"\\b(?:wk)+w?\\b|\\b(?:ha){2,}h?\\b|\\b(?:he){2,}h?\\b|\\b(?:xi){2,}\\b", " tawa ", t)
    t = re.sub(r"[^a-z0-9_@ ]", " ", t)
    return " ".join(slang.get(w, w) for w in t.split()).split()


stemmer = StemmerFactory().create_stemmer()
_cache = {}


def stem(w):
    if w.startswith("emo_") or w == "@user":
        return w
    if w not in _cache:
        _cache[w] = stemmer.stem(w)
    return _cache[w]


def bersih_lengkap(t, buang_stop=True, pakai_stem=False):
    tok = ke_token(t)
    if buang_stop:
        tok = [w for w in tok if w not in stopword]
    if pakai_stem:
        tok = [stem(w) for w in tok]
    return " ".join(tok)


def isi_judul(t):
    # buang awalan "Caption unggahan @akun:" atau "Judul video channel:" supaya yang tersisa isinya saja
    return re.sub(r"^[^:]{0,60}:\\s*", "", str(t))


def siapkan(d):
    d = d.copy()
    d["teks_ringan"] = d.text.map(bersih_ringan)
    d["teks_bert"] = d.text.map(untuk_bert)
    d["teks_lengkap"] = d.text.map(bersih_lengkap)
    d["judul_ringan"] = d.judul.fillna("").map(lambda t: bersih_ringan(isi_judul(t)))
    d["judul_bert"] = d.judul.fillna("").map(lambda t: untuk_bert(isi_judul(t)))
    d["judul_lengkap"] = d.judul.fillna("").map(lambda t: bersih_lengkap(isi_judul(t)))
    return d


df = siapkan(df)
contoh = df[df.text.str.contains("😂|🤮|😭") & df.text.str.contains(r"[A-Z]{3,}")].head(3)
contoh = pd.concat([contoh, df[df.text.str.len().between(40, 90)].sample(2, random_state=7)])
contoh[["text", "teks_bert", "teks_lengkap"]]"""),
    baca("prepro"),
    md("""Sel berikut menunjukkan apa yang benar-benar diterima model untuk input **teks + judul**. TF-IDF membuat dua vektor terpisah (satu dari teks, satu dari judul) lalu menggabungkannya, dengan bobot judul setengah dari teks. Model BERT menerima keduanya sebagai pasangan kalimat: `[CLS] teks [SEP] judul [SEP]`, jadi model tahu mana komentar dan mana unggahannya."""),
    code("""r = df[df.butuh_konteks & df.platform.eq("youtube")].iloc[0]
print("teks asli        :", r.text)
print("judul asli       :", r.judul)
print()
print("TF-IDF teks      :", r.teks_lengkap)
print("TF-IDF judul     :", r.judul_lengkap)
print()
print("BERT (pasangan)  : [CLS]", r.teks_bert, "[SEP]", r.judul_bert[:150], "[SEP]")
print("label            :", r.label)"""),
    baca("contoh-input"),
    code("""def ukuran_kosakata(kolom):
    return len(set(" ".join(kolom).split()))


df["teks_tanpa_stop"] = df.text.map(lambda t: bersih_lengkap(t, buang_stop=False))
df["teks_stem"] = df.text.map(lambda t: bersih_lengkap(t, pakai_stem=True))
df["teks_lower"] = df.text.map(lambda t: bersih_ringan(t).lower())
versi = {"ringan + lowercase": "teks_lower", "+ emoji, tawa, slang": "teks_tanpa_stop",
         "+ buang stopword (versi utama)": "teks_lengkap", "+ stemming": "teks_stem"}
pd.DataFrame([{"versi": v, "ukuran kosakata": ukuran_kosakata(df[k]),
               "rata2 token per teks": round(df[k].str.split().str.len().mean(), 1)} for v, k in versi.items()])"""),
    baca("kosakata"),
    md("""## Augmentasi kelas positif

Kelas positif hanya 84 teks, jadi tiap fold uji hanya punya 16 atau 17 teks positif. Model sulit belajar dari contoh sesedikit itu. Saran dosen adalah menambah data positif, bukan mengubah target menjadi biner. Ada dua sumber:

**1. Komentar positif dari akun Raffi (jalur B).** Bu Mar menyarankan komentar dari akun Raffi sendiri boleh dipakai untuk menambah contoh positif, selama rentang waktunya sesuai. Komentar ini sudah ada (jalur B, 22 Oktober sampai 14 November) dan sudah dilabeli dengan cara yang sama. Di `finalize.py` saya hanya mengambil yang label akhirnya positif, bukan buzzer, dan akun maupun teksnya tidak muncul di data utama. Syarat terakhir penting: kalau akun yang sama ada di data uji, model bisa terlihat bagus karena hafal gaya akun itu.

**2. Parafrase back-translation.** Teks positif diterjemahkan ke bahasa Inggris dengan model MarianMT `Helsinki-NLP/opus-mt-id-en` (dengan sampling supaya hasilnya bervariasi), lalu diterjemahkan kembali dengan `opus-mt-en-id`. Hasilnya kalimat dengan makna yang sama tapi susunan kata berbeda. Prosesnya dijalankan di Kaggle (`augmentasi/kaggle_bt/back_translation.py`) untuk semua teks yang pernah dinilai positif oleh minimal satu annotator atau reviewer, supaya tidak perlu diulang kalau label berubah setelah review 3 lapis. Yang dipakai saat training hanya parafrase dari teks yang label akhirnya positif.

Kedua sumber **hanya dipakai di fold latih**. Data uji tetap teks jalur A asli, supaya skor sebelum dan sesudah augmentasi diukur di data yang sama."""),
    code("""bt = pd.read_csv(FINAL / "augmentasi_bt_mentah.csv")


def alasan_buang(r):
    a, p = r.text_asli, str(r.parafrase)
    if re.search(r"[♪▪]", p):
        return "simbol aneh dari model"
    if re.search(r"(\\w-){4,}|(\\w)\\2{5,}", p):
        return "pengulangan karakter"
    if ("@user" in a and "@user" not in p) or re.search(r"\\bBu\\w*di\\b", p):
        return "mention @user rusak"
    na, npar = len(a.split()), len(p.split())
    if na >= 6 and npar < 0.5 * na:
        return "terpotong lebih dari separuh"
    if npar < 2:
        return "terlalu pendek"
    return ""


bt["alasan_buang"] = bt.apply(alasan_buang, axis=1)
print("parafrase mentah:", len(bt), "dari", bt.id.nunique(), "teks")
print(bt.alasan_buang.replace("", "lolos").value_counts().to_string())
cek = pd.read_csv(ROOT / "augmentasi" / "cek_manual_bt.csv")
print("\\ncek manual 40 sampel acak yang lolos saringan:", cek.makna_tetap.value_counts().to_dict())
cek[cek.makna_tetap.eq("tidak")][["text_asli", "parafrase", "catatan"]]"""),
    baca("bt-saring"),
    code("""bt = bt[bt.alasan_buang.eq("")]
jb = pd.read_csv(FINAL / "augmentasi_jalur_b.csv").fillna({"judul": ""})
label_akhir = pd.concat([df.set_index("id").label, jb.set_index("id").label])
judul_asal = pd.concat([df.set_index("id").judul, jb.set_index("id").judul])
fold_asal = df.set_index("id").fold
grup_asal = pd.concat([df.set_index("id").grup, ("b_" + jb.author_hash.fillna(jb.id)).set_axis(jb.id)])

bt = bt[bt.id.map(label_akhir).eq("positif")]  # hanya parafrase dari teks yang label akhirnya positif
aug = pd.concat([
    pd.DataFrame({"id": jb.id, "id_asal": jb.id, "sumber": "jalur_b", "text": jb.text, "judul": jb.judul}),
    pd.DataFrame({"id": bt.id_aug, "id_asal": bt.id, "sumber": np.where(bt.kelompok.eq("utama"), "bt_utama", "bt_jalur_b"),
                  "text": bt.parafrase, "judul": bt.id.map(judul_asal)}),
], ignore_index=True)
# pelabelan terarah dari teks cadangan (labeling/terarah/), hanya kalau labelnya sudah final
f_terarah = FINAL / "augmentasi_terarah.csv"
if f_terarah.exists():
    tr = pd.read_csv(f_terarah).fillna({"judul": ""})
    aug = pd.concat([aug, pd.DataFrame({"id": tr.id, "id_asal": tr.id, "sumber": "terarah", "text": tr.text,
                                        "judul": tr.judul})], ignore_index=True)
    grup_asal = pd.concat([grup_asal, ("t_" + tr.author_hash.fillna(tr.id)).set_axis(tr.id)])
aug["label"] = "positif"
aug["fold_asal"] = aug.id_asal.map(fold_asal).fillna(-1).astype(int)  # -1: berasal dari jalur B, aman untuk semua fold
aug["grup"] = aug.id_asal.map(grup_asal)
aug = siapkan(aug)
print(aug.sumber.value_counts().to_string())
aug.groupby("sumber").sample(2, random_state=1)[["sumber", "text", "judul"]].assign(judul=lambda x: x.judul.str[:60])"""),
    baca("aug"),
    code("""simpan = ["id", "text", "judul", "teks_ringan", "teks_bert", "teks_lengkap", "judul_ringan", "judul_bert",
          "judul_lengkap", "label", "fold", "grup", "platform", "fase", "sub", "sarkasme", "butuh_konteks", "target_lain"]
df[simpan].to_csv(FINAL / "dataset_prepro.csv", index=False, encoding="utf-8-sig")
kolom_aug = ["id", "id_asal", "sumber", "text", "judul", "teks_ringan", "teks_bert", "teks_lengkap", "judul_ringan",
             "judul_bert", "judul_lengkap", "label", "fold_asal", "grup"]
aug[kolom_aug].to_csv(FINAL / "augmentasi_prepro.csv", index=False, encoding="utf-8-sig")
# salinan untuk dataset Kaggle (notebook 03 dan 04)
for f in ("dataset_prepro.csv", "augmentasi_prepro.csv"):
    (ROOT / "augmentasi" / "kaggle_data" / f).write_bytes((FINAL / f).read_bytes())
print(df[simpan].shape, aug[kolom_aug].shape)"""),
    md("""Hasil preprocessing disimpan ke `data/05_final/dataset_prepro.csv` dan data augmentasi ke `augmentasi_prepro.csv`. Kedua berkas ini juga diunggah ke dataset Kaggle privat `raphaeladikara/uas-nlp-raffi-v2`, jadi notebook 03 dan 04 memakai preprocessing yang sama persis.

## Cara evaluasi

Targetnya 3 kelas (negatif, netral, positif). Metrik utamanya **macro-F1**, yaitu rata-rata F1 ketiga kelas dengan bobot sama. Akurasi tidak dipakai sebagai patokan, karena model yang selalu menebak negatif sudah mendapat akurasi sekitar 67%. F1 positif juga selalu dilaporkan, karena kelas inilah yang paling sulit dan yang menjadi alasan augmentasi.

Evaluasinya grouped 5-fold CV memakai kolom `fold`: latih di 4 fold, uji di 1 fold, ulang 5 kali. Satu akun dan teks identik selalu berada di fold yang sama. Hyperparameter dipilih dengan 3-fold CV di dalam fold latih saja (nested CV). Untuk varian augmentasi, data tambahan dimasukkan ke fold latih sebelum tuning, dan parafrase dari teks yang ada di fold uji dibuang."""),
    code("""LABEL = ["negatif", "netral", "positif"]
VARIAN = {"tanpa augmentasi": [], "jalur B": ["jalur_b"], "parafrase": ["bt_utama"],
          "jalur B + parafrase": ["jalur_b", "bt_utama", "bt_jalur_b"]}
if aug.sumber.eq("terarah").any():
    VARIAN["jalur B + terarah"] = ["jalur_b", "terarah"]


def evaluasi(buat_model, X, X_aug=None, varian="tanpa augmentasi", grid=None):
    pred = pd.Series(index=df.index, dtype=object)
    baris = []
    for k in range(5):
        latih, uji = (df.fold != k).values, (df.fold == k).values
        Xl, yl, gl = X[latih], df.label[latih], df.grup[latih]
        n_aug = 0
        if VARIAN[varian]:
            pilih = (aug.sumber.isin(VARIAN[varian]) & aug.fold_asal.ne(k)).values
            Xl, yl, gl = pd.concat([Xl, X_aug[pilih]]), pd.concat([yl, aug.label[pilih]]), pd.concat([gl, aug.grup[pilih]])
            n_aug = int(pilih.sum())
        model = buat_model()
        if grid:
            model = GridSearchCV(model, grid, scoring="f1_macro", n_jobs=-1,
                                 cv=StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42))
            model.fit(Xl, yl, groups=gl)
        else:
            model.fit(Xl, yl)
        p = model.predict(X[uji])
        pred[uji] = p
        f1 = f1_score(df.label[uji], p, labels=LABEL, average=None, zero_division=0)
        baris.append({"fold": k, "n_aug": n_aug, "macro_f1": f1.mean(), "akurasi": accuracy_score(df.label[uji], p),
                      "balanced_acc": balanced_accuracy_score(df.label[uji], p),
                      **{f"f1_{c}": v for c, v in zip(LABEL, f1)}, "param": model.best_params_ if grid else None})
    return pd.DataFrame(baris), pred


hasil, prediksi = {}, {}


def catat(nama, input_, varian, tabel, pred):
    hasil[(nama, input_, varian)] = tabel
    prediksi[(nama, input_, varian)] = pred
    print(f"{nama:20s} | {input_:12s} | {varian:20s} | macro-F1 {tabel.macro_f1.mean():.3f} ± {tabel.macro_f1.std():.3f}"
          f" | F1 positif {tabel.f1_positif.mean():.3f}")


X = pd.DataFrame({"teks": df.teks_lengkap, "judul": df.judul_lengkap, "text": df.text})
X_aug = pd.DataFrame({"teks": aug.teks_lengkap, "judul": aug.judul_lengkap, "text": aug.text})"""),
    md("""## Baseline 1 dan 2: tebak kelas terbanyak dan leksikon InSet

Dua baseline tanpa pembelajaran ini menjadi batas bawah. Yang pertama selalu menebak negatif. Yang kedua memakai leksikon InSet (Indonesia Sentiment Lexicon): skor kata positif dan negatif dijumlah, lalu skor di bawah 0 jadi negatif, di atas 0 jadi positif, dan 0 jadi netral. Kata negasi sebelum kata berbobot membalik tandanya. Keduanya tidak dilatih, jadi augmentasi tidak berpengaruh."""),
    code("""tabel, pred = evaluasi(lambda: DummyClassifier(strategy="most_frequent"), X)
catat("kelas terbanyak", "teks saja", "tanpa augmentasi", tabel, pred)

inset = pd.concat([pd.read_csv(RES / "inset_positive.tsv", sep="\\t"), pd.read_csv(RES / "inset_negative.tsv", sep="\\t")])
inset = inset.groupby("word").weight.sum().to_dict()
PEMBALIK = {"tidak", "enggak", "bukan", "jangan", "belum", "kurang", "tak"}


def skor_inset(teks):
    tok, skor, i = ke_token(teks), 0, 0
    while i < len(tok):
        for n in (3, 2, 1):
            frasa = " ".join(tok[i:i + n])
            if len(tok[i:i + n]) == n and frasa in inset:
                skor += -inset[frasa] if i > 0 and tok[i - 1] in PEMBALIK else inset[frasa]
                i += n
                break
        else:
            i += 1
    return skor


class Leksikon:
    def fit(self, X, y):
        return self

    def predict(self, X):
        s = X.text.map(skor_inset).values
        return np.select([s < 0, s > 0], ["negatif", "positif"], "netral")


tabel, pred = evaluasi(Leksikon, X)
catat("leksikon InSet", "teks saja", "tanpa augmentasi", tabel, pred)
df.assign(skor=df.text.map(skor_inset)).groupby("label").skor.describe().round(2)"""),
    baca("baseline-awal"),
    md("""## Baseline 3: TF-IDF dengan Logistic Regression dan Linear SVM

Setiap teks diubah jadi vektor TF-IDF dari n-gram kata (1 sampai 2) dan n-gram huruf (3 sampai 5). N-gram huruf membantu untuk salah ketik dan slang ("rafi", "raffi", "raffy"). Untuk input teks + judul, judul dibuat vektor sendiri dengan bobot 0,5, karena isi komentar tetap yang utama. Klasifikasinya Logistic Regression dan Linear SVM dengan class weight seimbang.

Logistic Regression dijalankan untuk kedua input dan keempat varian augmentasi. Linear SVM hanya untuk tanpa augmentasi dan augmentasi lengkap, karena tujuannya hanya pembanding."""),
    code("""def fitur(pakai_judul):
    teks = FeatureUnion([
        ("kata", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ("huruf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
    ])
    kolom, bobot = [("teks", teks, "teks")], {"teks": 1.0}
    if pakai_judul:
        kolom.append(("judul", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True), "judul"))
        bobot["judul"] = 0.5
    return ColumnTransformer(kolom, transformer_weights=bobot)


MODEL = {
    "TF-IDF + LogReg": (lambda: LogisticRegression(class_weight="balanced", max_iter=3000), {"clf__C": [0.3, 1, 3, 10]},
                        list(VARIAN)),
    "TF-IDF + LinearSVM": (lambda: LinearSVC(class_weight="balanced", random_state=42), {"clf__C": [0.03, 0.1, 0.3, 1]},
                           ["tanpa augmentasi", "jalur B + parafrase"]),
}
for nama, (clf, grid, daftar) in MODEL.items():
    for input_, pj in [("teks saja", False), ("teks + judul", True)]:
        for varian in daftar:
            buat = lambda clf=clf, pj=pj: Pipeline([("fitur", fitur(pj)), ("clf", clf())])
            tabel, pred = evaluasi(buat, X, X_aug, varian, grid)
            catat(nama, input_, varian, tabel, pred)"""),
    baca("tfidf"),
    md("""## Rekap dan dampak augmentasi

Tabel pertama mengurutkan semua konfigurasi dari macro-F1 tertinggi. Tabel kedua menghitung **selisih** setiap varian augmentasi terhadap versi tanpa augmentasi untuk model dan input yang sama, beserta berapa fold (dari 5) yang membaik. Karena fold ujinya sama persis, selisih per fold bisa dibandingkan langsung."""),
    code("""def rekap():
    baris = []
    for (nama, input_, varian), t in hasil.items():
        baris.append({"model": nama, "input": input_, "augmentasi": varian, "_urut": t.macro_f1.mean(),
                      "macro-F1": f"{t.macro_f1.mean():.3f} ± {t.macro_f1.std():.3f}",
                      **{f"F1 {c}": f"{t[f'f1_{c}'].mean():.3f} ± {t[f'f1_{c}'].std():.3f}" for c in LABEL},
                      "akurasi": round(t.akurasi.mean(), 3)})
    return pd.DataFrame(baris).sort_values("_urut", ascending=False).drop(columns="_urut").reset_index(drop=True)


def dampak():
    baris = []
    for (nama, input_, varian), t in hasil.items():
        dasar = hasil.get((nama, input_, "tanpa augmentasi"))
        if varian == "tanpa augmentasi" or dasar is None:
            continue
        d = t.macro_f1.values - dasar.macro_f1.values
        dp = t.f1_positif.values - dasar.f1_positif.values
        baris.append({"model": nama, "input": input_, "augmentasi": varian, "rata2 data tambahan": int(t.n_aug.mean()),
                      "Δ macro-F1": round(d.mean(), 3), "fold membaik": f"{(d > 0).sum()}/5",
                      "Δ F1 positif": round(dp.mean(), 3), "Δ F1 netral": round((t.f1_netral - dasar.f1_netral).mean(), 3)})
    return pd.DataFrame(baris)


display(rekap())
dampak()"""),
    baca("rekap"),
    code("""data = sorted([(f"{n} | {i} | {v}", t.macro_f1.mean(), t.macro_f1.std()) for (n, i, v), t in hasil.items()],
              key=lambda x: x[1])
fig, ax = plt.subplots(figsize=(9, 0.32 * len(data) + 1))
nama, rata, sd = zip(*data)
warna = ["#9aa5b1" if "terbanyak" in n or "InSet" in n else "#d08c3a" if "tanpa augmentasi" not in n else "#3b6ea8"
         for n in nama]
ax.barh(nama, rata, xerr=sd, color=warna, capsize=2)
for y, v in enumerate(rata):
    ax.text(v + 0.04, y, f"{v:.3f}", va="center", fontsize=7)
ax.set(title="Macro-F1 baseline (rata-rata 5 fold ± std); oranye = dengan augmentasi", xlim=(0, 1))
ax.tick_params(axis="y", labelsize=7)
plt.tight_layout()
plt.savefig(FIG / "02_macro_f1_baseline.png", bbox_inches="tight")
plt.show()"""),
    baca("grafik"),
    md("""## Ablation: dampak tiap langkah preprocessing

Selain augmentasi, setiap langkah preprocessing juga perlu dicek dampaknya. Modelnya dibuat tetap (TF-IDF + LogReg, teks saja, tanpa augmentasi), lalu langkah preprocessing ditambah satu per satu. Baris terakhir menghapus class weight untuk melihat dampaknya."""),
    code("""clf, grid, _ = MODEL["TF-IDF + LogReg"]
baris = []
for nama_v, kolom in versi.items():
    Xa = pd.DataFrame({"teks": df[kolom], "judul": df.judul_lengkap})
    t, _ = evaluasi(lambda: Pipeline([("fitur", fitur(False)), ("clf", clf())]), Xa, grid=grid)
    baris.append({"preprocessing": nama_v, "macro-F1": f"{t.macro_f1.mean():.3f} ± {t.macro_f1.std():.3f}",
                  "F1 positif": round(t.f1_positif.mean(), 3), "F1 netral": round(t.f1_netral.mean(), 3)})
t, _ = evaluasi(lambda: Pipeline([("fitur", fitur(False)), ("clf", LogisticRegression(max_iter=3000))]), X, grid=grid)
baris.append({"preprocessing": "versi utama, TANPA class weight", "macro-F1": f"{t.macro_f1.mean():.3f} ± {t.macro_f1.std():.3f}",
              "F1 positif": round(t.f1_positif.mean(), 3), "F1 netral": round(t.f1_netral.mean(), 3)})
pd.DataFrame(baris)"""),
    baca("ablasi"),
    code("""semua = [t.assign(model=n, input=i, augmentasi=v) for (n, i, v), t in hasil.items()]
pd.concat(semua, ignore_index=True).to_csv(HASIL / "hasil_per_fold.csv", index=False)
pd.DataFrame({"id": df.id, "label": df.label, **{f"{n} | {i} | {v}": p.values for (n, i, v), p in prediksi.items()}}
             ).to_csv(HASIL / "prediksi_oof.csv", index=False)
print("tersimpan:", len(hasil), "konfigurasi")"""),
    md("""Semua hasil disimpan di `data/06_baseline/`. `hasil_per_fold.csv` berisi skor tiap konfigurasi di tiap fold, dan `prediksi_oof.csv` berisi prediksi setiap konfigurasi untuk semua teks (setiap teks diprediksi saat menjadi data uji). Berkas ini dipakai notebook 05 untuk membandingkan semua model dan menganalisis kesalahan."""),
    baca("kesimpulan"),
]


def main():
    nb = nbf.v4.new_notebook()
    nb.cells = CELLS
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    nbf.write(nb, NB / "02_preprocessing_baseline.ipynb")
    print("ok")


if __name__ == "__main__":
    main()
