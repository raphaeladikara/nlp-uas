"""Bangun notebook 05 (perbandingan semua model, dampak tiap metode, analisis kesalahan).

Pakai : python notebooks/_build/build_05.py
Sel pembacaan hasil diberi tag "baca-<nama>" dan diisi setelah dijalankan.
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
# Perbandingan Model dan Analisis Kesalahan: Sentimen Publik terhadap Raffi Ahmad

**Nama:** Raphael Angelo Adikara Purnama
**NIM:** 164241055
**Mata kuliah:** Natural Language Processing (UAS)
**Topik:** Klasifikasi sentimen publik terhadap Raffi Ahmad setelah kasus "mahasiswa bayaran" di Bundaran HI (29 Oktober 2026)

Notebook ini menggabungkan hasil semua model dari notebook 02 (baseline dan TF-IDF), 03 (fine-tuning IndoBERTweet, IndoBERT, XLM-RoBERTa), dan 04 (IndoBERT embedding + LogReg, BiLSTM + attention). Semua model dievaluasi di 5 fold yang sama, jadi bisa dibandingkan per fold. Isinya:

1. Rekap semua model.
2. Dampak setiap metode: augmentasi (jalur B, parafrase, keduanya), penambahan judul, dan jenis model.
3. Analisis kesalahan model terbaik: kelas mana yang tertukar, kelompok teks mana yang paling sering salah, dan pola kesalahannya dari contoh nyata."""),
    code("""import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from IPython.display import display
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, f1_score

pd.set_option("display.max_colwidth", 110)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})
ROOT = Path.cwd().parent
D, FIG = ROOT / "data", ROOT / "figures"
OUT = D / "09_perbandingan"
OUT.mkdir(exist_ok=True)
LABEL = ["negatif", "netral", "positif"]
NAMA = {"indobertweet": "IndoBERTweet fine-tune", "indobert": "IndoBERT fine-tune", "xlmr": "XLM-RoBERTa fine-tune"}


def nama_berkas(*bagian):
    return "_".join(bagian).replace(" ", "_").replace("+", "")


r = [pd.read_csv(D / "06_baseline" / "hasil_per_fold.csv").assign(sumber="02")]
for f in sorted((D / "07_transformer").glob("hasil_per_fold_*.csv")):
    t = pd.read_csv(f)
    r.append(t.assign(sumber="03", berkas=[f"prediksi_{nama_berkas(m, i, a)}.csv" for m, i, a in zip(t.model, t.input, t.augmentasi)],
                      model=t.model.map(NAMA)))
f = D / "08_embedding_bilstm" / "hasil_per_fold_embed_bilstm.csv"
if f.exists():
    t = pd.read_csv(f)
    awal = t.model.map({"IndoBERT embedding + LogReg": "embedding", "BiLSTM + attention": "bilstm"})
    r.append(t.assign(sumber="04", berkas=[f"prediksi_{nama_berkas(a, i, v)}.csv" for a, i, v in zip(awal, t.input, t.augmentasi)]))
hasil = pd.concat(r, ignore_index=True)

df = pd.read_csv(D / "05_final" / "dataset_prepro.csv")
oof = pd.read_csv(D / "06_baseline" / "prediksi_oof.csv")


def prediksi(model, input_, augmentasi):
    t = hasil[(hasil.model == model) & (hasil.input == input_) & (hasil.augmentasi == augmentasi)]
    if t.sumber.iloc[0] == "02":
        return oof[f"{model} | {input_} | {augmentasi}"].values
    folder = "07_transformer" if t.sumber.iloc[0] == "03" else "08_embedding_bilstm"
    p = pd.read_csv(D / folder / t.berkas.iloc[0]).set_index("id").prediksi
    return p.reindex(df.id).values


ringkas = (hasil.groupby(["model", "input", "augmentasi"], sort=False)
           .agg(macro_f1=("macro_f1", "mean"), sd=("macro_f1", "std"), f1_negatif=("f1_negatif", "mean"),
                f1_netral=("f1_netral", "mean"), f1_positif=("f1_positif", "mean"), akurasi=("akurasi", "mean"))
           .sort_values("macro_f1", ascending=False).round(3).reset_index())
print("konfigurasi:", len(ringkas), "| model:", ringkas.model.nunique())
ringkas.head(20)"""),
    baca("rekap"),
    md("""## Konfigurasi terbaik per model

Tabel ini mengambil satu konfigurasi terbaik (input dan augmentasi) untuk setiap model, supaya jenis model bisa dibandingkan langsung."""),
    code("""terbaik = ringkas.loc[ringkas.groupby("model").macro_f1.idxmax()].sort_values("macro_f1", ascending=False).reset_index(drop=True)
display(terbaik)

fig, ax = plt.subplots(figsize=(8, 3.8))
t = terbaik.iloc[::-1]
warna = ["#9aa5b1" if m in ("kelas terbanyak", "leksikon InSet") else "#7a9cc6" if "TF-IDF" in m else "#3b6ea8" for m in t.model]
ax.barh(t.model, t.macro_f1, xerr=t.sd, color=warna, capsize=3)
for y, (v, p) in enumerate(zip(t.macro_f1, t.f1_positif)):
    ax.text(v + 0.03, y, f"{v:.3f} (F1 positif {p:.2f})", va="center", fontsize=8)
ax.set(xlim=(0, 1), title="Macro-F1 konfigurasi terbaik tiap model (rata-rata 5 fold ± std)")
plt.tight_layout()
plt.savefig(FIG / "05_model_terbaik.png", bbox_inches="tight")
plt.show()"""),
    baca("terbaik"),
    md("""## Dampak augmentasi

Untuk setiap model dan input, varian augmentasi dibandingkan dengan versi tanpa augmentasi. Kolom "fold membaik" menghitung di berapa fold (dari 5) macro-F1 naik. Kalau kenaikannya hanya terjadi di 2 atau 3 fold, selisih rata-ratanya belum bisa dianggap pasti."""),
    code("""baris = []
for (m, i, a), t in hasil.groupby(["model", "input", "augmentasi"], sort=False):
    dasar = hasil[(hasil.model == m) & (hasil.input == i) & (hasil.augmentasi == "tanpa augmentasi")]
    if a == "tanpa augmentasi" or dasar.empty:
        continue
    t, dasar = t.sort_values("fold"), dasar.sort_values("fold")
    d = t.macro_f1.values - dasar.macro_f1.values
    baris.append({"model": m, "input": i, "augmentasi": a, "data tambahan": int(t.n_aug.mean()),
                  "macro-F1 tanpa": round(dasar.macro_f1.mean(), 3), "macro-F1 dengan": round(t.macro_f1.mean(), 3),
                  "Δ macro-F1": round(d.mean(), 3), "fold membaik": f"{(d > 0).sum()}/5",
                  "Δ F1 positif": round((t.f1_positif.values - dasar.f1_positif.values).mean(), 3),
                  "Δ F1 netral": round((t.f1_netral.values - dasar.f1_netral.values).mean(), 3)})
dampak_aug = pd.DataFrame(baris)
dampak_aug.to_csv(OUT / "dampak_augmentasi.csv", index=False)
dampak_aug"""),
    baca("dampak-aug"),
    code("""rata = dampak_aug.groupby("augmentasi")[["Δ macro-F1", "Δ F1 positif", "Δ F1 netral"]].mean().round(3)
rata["konfigurasi membaik"] = dampak_aug.groupby("augmentasi")["Δ macro-F1"].apply(lambda s: f"{(s > 0).sum()}/{len(s)}")
rata"""),
    baca("dampak-aug-rata"),
    md("""## Dampak judul

Sama seperti augmentasi, di sini setiap model dibandingkan antara input teks saja dan teks + judul, keduanya tanpa augmentasi."""),
    code("""baris = []
for m, t in hasil[hasil.augmentasi == "tanpa augmentasi"].groupby("model", sort=False):
    a, b = t[t.input == "teks saja"].sort_values("fold"), t[t.input == "teks + judul"].sort_values("fold")
    if a.empty or b.empty:
        continue
    d = b.macro_f1.values - a.macro_f1.values
    baris.append({"model": m, "teks saja": round(a.macro_f1.mean(), 3), "teks + judul": round(b.macro_f1.mean(), 3),
                  "Δ macro-F1": round(d.mean(), 3), "fold membaik": f"{(d > 0).sum()}/5",
                  "Δ F1 positif": round((b.f1_positif.values - a.f1_positif.values).mean(), 3)})
pd.DataFrame(baris)"""),
    baca("dampak-judul"),
    md("""## Perbandingan per fold dengan baseline

Model terbaik dibandingkan dengan baseline TF-IDF terbaik di setiap fold. Karena fold ujinya sama, kalau model terbaik unggul di kelima fold, kenaikannya konsisten dan bukan kebetulan dari satu fold."""),
    code("""top = ringkas.iloc[0]
base = ringkas[ringkas.model.str.startswith("TF-IDF")].iloc[0]
ambil = lambda r: hasil[(hasil.model == r.model) & (hasil.input == r.input) & (hasil.augmentasi == r.augmentasi)].sort_values("fold")
a, b = ambil(top), ambil(base)
print("terbaik :", top.model, "|", top.input, "|", top.augmentasi)
print("baseline:", base.model, "|", base.input, "|", base.augmentasi)
pd.DataFrame({"fold": range(5), "terbaik": a.macro_f1.values.round(3), "baseline": b.macro_f1.values.round(3),
              "selisih": (a.macro_f1.values - b.macro_f1.values).round(3),
              "F1 positif terbaik": a.f1_positif.values.round(3), "F1 positif baseline": b.f1_positif.values.round(3)})"""),
    baca("per-fold"),
    md("""## Strategi untuk kelas positif

Kelas positif hanya 84 teks (2,5%), jadi per fold uji hanya ada 16 sampai 17 teks positif. Bagian ini menjawab empat pertanyaan:

1. Seberapa jelek sebenarnya F1 positif di kisaran 0,2 sampai 0,3?
2. Apakah menggabungkan beberapa model (ensemble) atau menggeser ambang keputusan kelas positif bisa menaikkannya?
3. Apakah menambah data positif masih akan menaikkan F1 positif (learning curve)?
4. Kalau perlu tambah data, apakah harus scraping lagi, atau cukup melabeli teks cadangan yang sudah ada?"""),
    code("""y, fold = df.label.values, df.fold.values
prev = (y == "positif").mean()
print(f"porsi positif: {prev:.3f}")
print(f"F1 positif kalau semua teks ditebak positif: {2 * prev / (1 + prev):.3f}")
print(f"average precision (AP) tebakan acak: {prev:.3f}")


def probabilitas(berkas):
    p = pd.read_csv(D / "07_transformer" / berkas).set_index("id").reindex(df.id)
    return p[["prob_negatif", "prob_netral", "prob_positif"]].values


def skor_fold(pred):
    s = np.array([f1_score(y[fold == k], pred[fold == k], labels=LABEL, average=None, zero_division=0) for k in range(5)])
    return s.mean(1), s[:, 2]


from sklearn.metrics import average_precision_score
PROB = {}
for kunci, nama in NAMA.items():
    for inp, aug_ in [("teks + judul", "tanpa augmentasi"), ("teks + judul", "jalur B"), ("teks + judul", "jalur B + terarah")]:
        f = D / "07_transformer" / f"prediksi_{nama_berkas(kunci, inp, aug_)}.csv"
        if f.exists():
            PROB[f"{nama} | {inp} | {aug_}"] = probabilitas(f.name)
pilih = [k for k in PROB if k.endswith("jalur B")]
dua = [k for k in pilih if not k.startswith("XLM")]
PROB["ensemble IndoBERT + IndoBERTweet | teks + judul | jalur B"] = np.mean([PROB[k] for k in dua], axis=0)
if len(pilih) > len(dua):
    PROB[f"ensemble {len(pilih)} model fine-tune | teks + judul | jalur B"] = np.mean([PROB[k] for k in pilih], axis=0)
dua_t = [k for k in PROB if k.endswith("jalur B + terarah") and not k.startswith("XLM")]
if len(dua_t) == 2:
    PROB["ensemble IndoBERT + IndoBERTweet | teks + judul | jalur B + terarah"] = np.mean([PROB[k] for k in dua_t], axis=0)

W = np.array([0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 12])
geser = lambda p, w: np.array(LABEL)[(p * [1, 1, w]).argmax(1)]
baris = []
for nama_, p in PROB.items():
    mac, pos = skor_fold(np.array(LABEL)[p.argmax(1)])
    # bobot kelas positif dipilih dari 4 fold lain, lalu diterapkan ke fold uji
    tuned, bobot = np.empty(len(y), dtype=object), []
    for k in range(5):
        lain = fold != k
        w = W[int(np.argmax([f1_score(y[lain], geser(p[lain], w), labels=LABEL, average="macro") for w in W]))]
        bobot.append(w)
        tuned[fold == k] = geser(p[fold == k], w)
    mac2, pos2 = skor_fold(tuned)
    ap = np.mean([average_precision_score(y[fold == k] == "positif", p[fold == k, 2]) for k in range(5)])
    baris.append({"konfigurasi": nama_, "AP positif": round(ap, 3), "macro-F1": round(mac.mean(), 3),
                  "F1 positif": f"{pos.mean():.3f} ± {pos.std(ddof=1):.3f}",
                  "macro-F1 + ambang": round(mac2.mean(), 3), "F1 positif + ambang": f"{pos2.mean():.3f} ± {pos2.std(ddof=1):.3f}",
                  "bobot positif terpilih": bobot})
strategi = pd.DataFrame(baris)
strategi.to_csv(OUT / "strategi_positif.csv", index=False)
strategi"""),
    baca("strategi"),
    md("""### Learning curve: apakah data positif tambahan masih berguna?

Untuk menjawab apakah perlu menambah data, model TF-IDF + LogReg (teks + judul) dilatih ulang dengan hanya 25%, 50%, 75%, dan 100% teks positif di data latih. Teks negatif dan netral tetap semua, dan fold ujinya tetap sama. Kalau F1 positif masih naik tajam sampai 100%, berarti model belum jenuh dan data positif tambahan kemungkinan besar masih menaikkan skor. TF-IDF dipakai karena bisa dilatih ulang puluhan kali di laptop, sedangkan model transformer butuh GPU."""),
    code("""from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def fitur():
    teks = FeatureUnion([("kata", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
                         ("huruf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True))])
    return ColumnTransformer([("teks", teks, "teks"),
                              ("judul", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True), "judul")],
                             transformer_weights={"teks": 1.0, "judul": 0.5})


X = pd.DataFrame({"teks": df.teks_lengkap.fillna(""), "judul": df.judul_lengkap.fillna("")})
prob_tfidf = np.zeros(len(y))
lc = []
for porsi in [0.25, 0.5, 0.75, 1.0]:
    for seed in ([0, 1, 2] if porsi < 1 else [0]):
        rng = np.random.default_rng(seed)
        for k in range(5):
            latih = np.where(fold != k)[0]
            pos = latih[y[latih] == "positif"]
            latih = np.setdiff1d(latih, rng.choice(pos, int(round(len(pos) * (1 - porsi))), replace=False))
            m = Pipeline([("f", fitur()), ("c", LogisticRegression(class_weight="balanced", C=3, max_iter=3000))]).fit(X.iloc[latih], y[latih])
            uji = fold == k
            if porsi == 1.0:
                prob_tfidf[uji] = m.predict_proba(X[uji])[:, list(m.classes_).index("positif")]
            s = f1_score(y[uji], m.predict(X[uji]), labels=LABEL, average=None, zero_division=0)
            lc.append({"porsi positif": porsi, "positif di data latih": int((y[latih] == "positif").sum()), "seed": seed,
                       "fold": k, "macro-F1": s.mean(), "F1 positif": s[2]})
lc = pd.DataFrame(lc)
kurva = lc.groupby("porsi positif").agg(**{"positif di data latih": ("positif di data latih", "mean"),
                                           "macro-F1": ("macro-F1", "mean"), "F1 positif": ("F1 positif", "mean")}).round(3)
kurva.to_csv(OUT / "learning_curve_positif.csv")
display(kurva)
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.plot(kurva["positif di data latih"], kurva["F1 positif"], "o-", color="#3b6ea8", label="F1 positif")
ax.plot(kurva["positif di data latih"], kurva["macro-F1"], "s--", color="#9aa5b1", label="macro-F1")
ax.set(xlabel="jumlah teks positif di data latih (rata-rata per fold)", ylabel="skor", ylim=(0, 0.7),
       title="Learning curve kelas positif (TF-IDF + LogReg, teks + judul)")
ax.legend()
plt.tight_layout()
plt.savefig(FIG / "05_learning_curve_positif.png", bbox_inches="tight")
plt.show()"""),
    baca("kurva"),
    md("""### Dari mana data positif tambahan bisa didapat?

Ada 2.623 teks cadangan yang sudah lolos filter tapi belum dilabeli (`data/03_filtered/cadangan_belum_dilabel.csv`). Kalau diambil acak, porsi positifnya kira-kira sama dengan dataset (2,5%). Sel berikut mengecek apa yang terjadi kalau teks diurutkan dulu berdasarkan skor positif dari model: berapa banyak positif yang benar-benar ada di urutan teratas. Skor di sini adalah probabilitas positif dari TF-IDF + LogReg saat teks itu menjadi data uji, jadi tidak ada kebocoran."""),
    code("""urut = np.argsort(-prob_tfidf)
peringkat = pd.DataFrame([{"teks teratas": n, "positif": int((y[urut[:n]] == "positif").sum()),
                           "presisi": (y[urut[:n]] == "positif").mean(), "kalau acak": prev * n} for n in [50, 100, 200, 400]])
peringkat.to_csv(OUT / "peringkat_positif.csv", index=False)
peringkat.round(3)"""),
    baca("peringkat"),
    md("""### Hasil pelabelan terarah

Saran dari bagian sebelumnya sudah dijalankan (`labeling/terarah/`). Model mengurutkan teks cadangan, lalu 250 teks dengan skor positif tertinggi dan 50 teks acak sebagai pembanding dilabeli dengan alur yang sama seperti data utama: 3 annotator AI, teks yang tidak disepakati bulat dinilai 3 orang, dan kartu yang ketiganya beda diputus koordinator. Annotator tidak diberi tahu skor atau cara pilih teks. Teks positif yang bukan buzzer dan akunnya tidak ada di dataset final dipakai sebagai augmentasi **jalur B + terarah**, hanya di fold latih.

Sel pertama merangkum hasil pelabelannya. Sel kedua membandingkan langsung jalur B dengan jalur B + terarah di model dan input yang sama."""),
    code("""lt = pd.read_csv(D / "04_labeled" / "label_terarah.csv")
aug_t = pd.read_csv(D / "05_final" / "augmentasi_terarah.csv")
ring = (ROOT / "labeling" / "terarah" / "ringkasan_terarah.md").read_text(encoding="utf-8")
print("sumber label:", lt.sumber_label.value_counts().to_dict())
print("Fleiss' kappa review 3 orang, jumlah kartu:", re.search(r"Fleiss' kappa = ([0-9.]+).*? di (\d+) kartu", ring).groups())
print("positif dipakai untuk augmentasi:", len(aug_t), "| per cara pilih:", aug_t.cara_pilih.value_counts().to_dict())
pd.crosstab(lt.cara_pilih, lt.label.fillna("seri"), margins=True).assign(
    porsi_positif=lambda t: (t.positif / t.All).round(3))"""),
    code("""baris = []
for (m, i), t in hasil[hasil.augmentasi == "jalur B + terarah"].groupby(["model", "input"], sort=False):
    b = hasil[(hasil.model == m) & (hasil.input == i) & (hasil.augmentasi == "jalur B")].sort_values("fold")
    if b.empty:
        continue
    t = t.sort_values("fold")
    d = t.macro_f1.values - b.macro_f1.values
    baris.append({"model": m, "input": i, "macro-F1 jalur B": round(b.macro_f1.mean(), 3),
                  "macro-F1 + terarah": round(t.macro_f1.mean(), 3), "Δ macro-F1": round(d.mean(), 3),
                  "fold membaik": f"{(d > 0).sum()}/5", "F1 positif jalur B": round(b.f1_positif.mean(), 3),
                  "F1 positif + terarah": round(t.f1_positif.mean(), 3),
                  "Δ F1 positif": round((t.f1_positif.values - b.f1_positif.values).mean(), 3)})
dampak_terarah = pd.DataFrame(baris)
dampak_terarah.to_csv(OUT / "dampak_terarah.csv", index=False)
dampak_terarah"""),
    baca("terarah"),
    md("""## Lowercase di model BERT

Notebook 03 mencetak isi `do_lower_case` tokenizer saat dijalankan di Kaggle. Sel ini membaca hasilnya langsung dari log Kaggle, supaya jelas bahwa jawabannya berasal dari tokenizer, bukan dugaan."""),
    code("""for f in sorted((D / "07_transformer").glob("*.log")):
    log = f.read_text(encoding="utf-8")
    print(f.name)
    for pola in [r"do_lower_case di tokenizer: (\\w+)", r"'BOIKOT RANS'\\s+-\\\\u003e (\\[[^\\]]*\\])"]:
        for m in re.findall(pola, log)[:1]:
            print("  ", m)"""),
    baca("lowercase"),
    md("""## Analisis kesalahan

Bagian ini memakai prediksi model terbaik untuk semua 5 fold uji (setiap teks diprediksi tepat sekali saat menjadi data uji). Langkahnya: confusion matrix, lalu akurasi per kelompok teks, lalu membaca contoh kesalahan dan mengelompokkannya."""),
    code("""df["pred"] = prediksi(top.model, top.input, top.augmentasi)
df["pred_base"] = prediksi(base.model, base.input, base.augmentasi)
df["benar"] = df.pred == df.label
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, kol, judul in [(axes[0], "pred_base", f"Baseline: {base.model}"), (axes[1], "pred", f"Terbaik: {top.model}")]:
    cm = confusion_matrix(df.label, df[kol], labels=LABEL)
    ConfusionMatrixDisplay(cm, display_labels=LABEL).plot(ax=ax, cmap="Blues", colorbar=False, values_format="d")
    ax.set(title=judul, xlabel="tebakan", ylabel="label asli")
plt.tight_layout()
plt.savefig(FIG / "05_confusion_matrix.png", bbox_inches="tight")
plt.show()
ct = pd.crosstab(df.label, df.pred, normalize="index").round(3)
ct.to_csv(OUT / "confusion_terbaik.csv")
print(ct)"""),
    baca("cm"),
    code("""def per_kelompok(nama, kolom):
    t = df.groupby(kolom).agg(n=("benar", "size"), akurasi=("benar", "mean"),
                              macro_f1=("label", lambda s: f1_score(s, df.loc[s.index, "pred"], labels=LABEL,
                                                                    average="macro", zero_division=0)))
    return t.round(3).assign(kelompok=nama).reset_index().rename(columns={kolom: "nilai"})


df["panjang"] = pd.cut(df.text.str.split().str.len(), [0, 5, 15, 40, 1000], labels=["1-5 kata", "6-15", "16-40", "> 40"])
df["ada_target_lain"] = df.target_lain.fillna("").ne("")
kel = pd.concat([per_kelompok("platform", "platform"), per_kelompok("sarkasme", "sarkasme"),
           per_kelompok("butuh judul", "butuh_konteks"), per_kelompok("ada pihak lain yang dikritik", "ada_target_lain"),
           per_kelompok("panjang teks", "panjang"), per_kelompok("fase", "fase")])[["kelompok", "nilai", "n", "akurasi", "macro_f1"]]
kel.to_csv(OUT / "akurasi_per_kelompok.csv", index=False)
kel"""),
    baca("kelompok"),
    code("""salah = df[~df.benar]
print("jumlah salah:", len(salah), f"({len(salah) / len(df):.1%})")
print(salah.groupby(["label", "pred"]).size().rename("n").sort_values(ascending=False).to_string())
print()
print("sub-kategori teks positif yang salah:")
sub_pos = df[df.label.eq("positif")].groupby("sub").benar.agg(["size", "mean"]).round(3)
sub_pos.to_csv(OUT / "positif_per_sub.csv")
salah.groupby(["label", "pred"]).size().rename("n").to_csv(OUT / "jenis_salah.csv")
print(sub_pos.to_string())"""),
    baca("jenis-salah"),
    md("""### Contoh kesalahan

Sel berikut menampilkan contoh acak dari tiga jenis kesalahan yang paling penting: positif yang ditebak negatif, netral yang ditebak negatif, dan negatif yang ditebak netral. Contoh ini saya baca satu per satu untuk mencari polanya."""),
    code("""for asli, tebak in [("positif", "negatif"), ("netral", "negatif"), ("negatif", "netral")]:
    s = df[(df.label == asli) & (df.pred == tebak)]
    print(f"\\n{asli} ditebak {tebak} ({len(s)} teks):")
    display(s.sample(min(10, len(s)), random_state=5)[["text", "sub", "target_lain", "sarkasme"]])"""),
    baca("contoh"),
    code("""keduanya = (df.pred != df.label) & (df.pred_base != df.label)
hanya_base = (df.pred == df.label) & (df.pred_base != df.label)
hanya_top = (df.pred != df.label) & (df.pred_base == df.label)
print("salah di kedua model         :", int(keduanya.sum()))
print("baseline salah, terbaik benar:", int(hanya_base.sum()))
print("baseline benar, terbaik salah:", int(hanya_top.sum()))
print()
print("contoh yang diperbaiki model terbaik:")
display(df[hanya_base & df.label.ne("negatif")].sample(8, random_state=2)[["text", "label", "pred_base", "pred"]])"""),
    baca("diperbaiki"),
    md("""## Jejak saran dosen

Tabel ini merangkum setiap saran dari konsultasi dosen, apa yang dikerjakan, dan di berkas mana hasilnya bisa dicek."""),
    baca("saran-dosen"),
    baca("kesimpulan"),
]


def main():
    nb = nbf.v4.new_notebook()
    nb.cells = CELLS
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    nbf.write(nb, NB / "05_perbandingan_analisis_kesalahan.ipynb")
    print("ok")


if __name__ == "__main__":
    main()
