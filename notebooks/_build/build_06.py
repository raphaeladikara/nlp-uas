"""Bangun notebook 06 (analisis sentimen dari label: fase, platform, aspek, pembela, akun Raffi, buzzer).

Pakai : python notebooks/_build/build_06.py
Input : data/05_final/semua_label.csv (dibuat labeling/finalize.py)
Sel pembacaan hasil diberi tag "baca-<nama>" dan diisi setelah dijalankan (isi_baca.py + baca_06.md).
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
# Analisis Sentimen Publik terhadap Raffi Ahmad

**Nama:** Raphael Angelo Adikara Purnama
**NIM:** 164241055
**Mata kuliah:** Natural Language Processing (UAS)
**Topik:** Klasifikasi sentimen publik terhadap Raffi Ahmad setelah kasus "mahasiswa bayaran" di Bundaran HI (29 Oktober 2026)

Notebook 02 sampai 05 membahas model. Notebook ini kembali ke pertanyaan awalnya: bagaimana sikap warganet ke Raffi setelah kasus ini, dan apakah masih ada yang membelanya. Yang dipakai di sini adalah label akhir (sepakat bulat 3 AI atau suara terbanyak 3 orang), bukan tebakan model, karena labelnya sudah dicek manusia dan lebih bisa dipercaya daripada model terbaik yang macro-F1-nya masih di bawah 0,7.

Ada tiga kelompok teks yang dianalisis terpisah:

1. **Jalur A (data utama):** komentar di unggahan berita dan kreator, bukan buzzer. Ini dasar semua angka utama.
2. **Jalur B:** komentar di akun Instagram Raffi sendiri. Kelompok ini tidak dipakai untuk training (kecuali positifnya untuk augmentasi), karena yang berkomentar di akun seseorang cenderung penggemarnya. Justru karena itu menarik dilihat apakah di akunnya sendiri dia masih dibela.
3. **Buzzer hasil review:** teks yang menurut tim bunyinya seperti pesan pesanan. Dilaporkan terpisah dan tidak ikut di angka utama."""),
    code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import chi2_contingency

pd.set_option("display.max_colwidth", 120)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})
ROOT = Path.cwd().parent
FIG = ROOT / "figures"
SENT = ["negatif", "netral", "positif"]
WARNA = {"negatif": "#c0504d", "netral": "#9aa5b1", "positif": "#4f81bd"}

s = pd.read_csv(ROOT / "data" / "05_final" / "semua_label.csv", parse_dates=["tanggal"])
s["aspek"] = s.aspek.fillna("umum")
a = s[(s.kelompok == "utama") & ~s.buzzer & s.label.isin(SENT)].copy()
b = s[(s.kelompok == "jalur_b") & ~s.buzzer & s.label.isin(SENT)].copy()
bz = s[s.buzzer].copy()
print("jalur A:", len(a), "| jalur B:", len(b), "| buzzer hasil review:", len(bz),
      "| tidak relevan (dibuang):", int(s.label.eq("tidak_relevan").sum()))
pd.DataFrame({"jalur A": a.label.value_counts(), "jalur B": b.label.value_counts()}).reindex(SENT).assign(
    **{"jalur A (%)": lambda x: (x["jalur A"] / x["jalur A"].sum() * 100).round(1),
       "jalur B (%)": lambda x: (x["jalur B"] / x["jalur B"].sum() * 100).round(1)})"""),
    baca("sebaran"),
    md("""## Sentimen per fase

Fase dibagi tiga: **pra** (22 sampai 28 Oktober), **puncak** (29 Oktober sampai 2 November, dari deklarasi sampai GSI Youth Fest batal mengundang Raffi), dan **pasca** (3 sampai 14 November, termasuk temuan ICW soal kontrak Rp14,7 miliar). Uji chi-square dipakai untuk melihat apakah perbedaan proporsi antarfase lebih besar dari yang bisa terjadi karena kebetulan."""),
    code("""ct = pd.crosstab(a.fase, a.label).reindex(["pra", "puncak", "pasca"])[SENT]
persen = (ct.div(ct.sum(axis=1), axis=0) * 100).round(1)
display(ct.assign(total=ct.sum(axis=1)).join(persen, rsuffix=" (%)"))
chi2, p, dof, _ = chi2_contingency(ct.loc[["puncak", "pasca"]])
print(f"puncak vs pasca: chi2 = {chi2:.2f}, dof = {dof}, p = {p:.4f}")"""),
    baca("fase"),
    code("""harian = a.groupby([a.tanggal.dt.date, "label"]).size().unstack(fill_value=0).reindex(columns=SENT, fill_value=0)
harian = harian[harian.sum(axis=1) >= 20]  # hari dengan < 20 teks terlalu sedikit untuk dihitung proporsinya
prop = harian.div(harian.sum(axis=1), axis=0)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
for c in SENT:
    ax1.plot(prop.index, prop[c] * 100, marker="o", ms=3, color=WARNA[c], label=c)
ax1.set(ylabel="% teks", title="Proporsi sentimen per hari (jalur A, hari dengan minimal 20 teks)")
ax1.legend(frameon=False, ncol=3)
ax2.bar(harian.index, harian.sum(axis=1), color="#9aa5b1")
ax2.set(ylabel="jumlah teks")
for ax in (ax1, ax2):
    for t, nama in [("2026-10-29", "deklarasi"), ("2026-10-31", "klarifikasi"), ("2026-11-09", "ICW 14,7 M")]:
        ax.axvline(pd.Timestamp(t).date(), color="k", lw=0.6, ls="--")
        if ax is ax1:
            ax.text(pd.Timestamp(t).date(), 99, " " + nama, fontsize=8, va="top")
ax1.set_ylim(0, 100)
import matplotlib.dates as mdates
ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.tight_layout()
plt.savefig(FIG / "06_tren_harian.png", bbox_inches="tight")
plt.show()"""),
    baca("tren"),
    md("""## Sentimen per platform"""),
    code("""ct = pd.crosstab(a.platform, a.label)[SENT]
display(ct.assign(total=ct.sum(axis=1)).join((ct.div(ct.sum(axis=1), axis=0) * 100).round(1), rsuffix=" (%)"))
chi2, p, dof, _ = chi2_contingency(ct)
print(f"antarplatform: chi2 = {chi2:.2f}, dof = {dof}, p = {p:.2e}")"""),
    baca("platform"),
    md("""## Apa yang dibahas

Setiap teks punya kolom aspek dari labeling (boleh lebih dari satu): mahasewa, klarifikasi, jabatan utusan khusus, kontrak Rp14,7 miliar, boikot RANS, kehidupan pribadi, atau umum. Tabel ini menghitung berapa persen teks negatif di setiap aspek dan bagaimana porsinya berubah dari fase puncak ke pasca."""),
    code("""asp = a.assign(aspek=a.aspek.str.split(";")).explode("aspek").reset_index(drop=True)
t = asp.groupby("aspek").agg(n=("id", "size"), negatif=("label", lambda x: (x == "negatif").mean() * 100),
                             positif=("label", lambda x: (x == "positif").mean() * 100)).round(1)
porsi = (pd.crosstab(asp.aspek, asp.fase, normalize="columns") * 100).round(1)[["puncak", "pasca"]]
t.join(porsi.add_prefix("porsi di fase ")).sort_values("n", ascending=False)"""),
    baca("aspek"),
    md("""## Siapa yang masih membela

Teks positif dibagi tiga sub-kategori di codebook: **membela** (dengan argumen, misalnya "dia cuma diundang"), **simpati** (kasihan), dan **dukungan** (pujian atau doa tanpa argumen). Sub-kategori negatif juga ditampilkan supaya kelihatan bentuk kritiknya."""),
    code("""sub = pd.crosstab(a["sub"].fillna("(tidak diisi)"), a.label)[SENT]
display(sub[sub.sum(axis=1) > 0].sort_values(SENT, ascending=False))
print("contoh teks positif (jalur A):")
display(a[a.label == "positif"].sample(10, random_state=3)[["platform", "fase", "sub", "text"]])"""),
    baca("pembela"),
    md("""## Akun Raffi sendiri (jalur B)

Komentar jalur B diambil dari unggahan akun Instagram Raffi di rentang waktu yang sama. Dugaan awal saya, kelompok ini akan jauh lebih positif karena yang berkomentar di akun seseorang biasanya pengikutnya."""),
    code("""ct = pd.DataFrame({"jalur A (IG)": a[a.platform == "instagram"].label.value_counts(),
                   "jalur B (akun Raffi)": b.label.value_counts()}).reindex(SENT)
display(ct.join((ct / ct.sum() * 100).round(1), rsuffix=" (%)"))
chi2, p, dof, _ = chi2_contingency(ct.T)
print(f"IG jalur A vs jalur B: chi2 = {chi2:.2f}, p = {p:.4f}")
print(pd.crosstab(b.fase, b.label)[SENT].to_string())
print("\\ncontoh komentar negatif di akun Raffi:")
display(b[b.label == "negatif"].sample(8, random_state=1)[["fase", "text"]])"""),
    baca("jalur-b"),
    md("""## Buzzer

Teks yang ditandai buzzer oleh tim saat review tidak ikut di angka di atas. Yang ditampilkan di sini adalah sikap teks-teks itu, untuk melihat apakah buzzer yang tertangkap condong membela atau menyerang."""),
    code("""print(bz.groupby(["kelompok", "label"]).size().to_string())
bz[["platform", "label", "text"]]"""),
    baca("buzzer"),
    md("""## Sentimen yang ditimbang like

Satu komentar dengan 2.000 like mewakili lebih banyak orang daripada komentar tanpa like. Sebagai pembanding, proporsi sentimen juga dihitung dengan bobot 1 + jumlah like (supaya komentar tanpa like tetap terhitung satu). Angka ini hanya pelengkap, karena like juga dipengaruhi jam unggah dan posisi komentar."""),
    code("""a["like"] = pd.to_numeric(a.like_count, errors="coerce").fillna(0)
w = a.groupby("label").like.apply(lambda x: (1 + x).sum()).reindex(SENT)
pd.DataFrame({"tanpa bobot (%)": (a.label.value_counts(normalize=True).reindex(SENT) * 100).round(1),
              "bobot 1 + like (%)": (w / w.sum() * 100).round(1),
              "median like": a.groupby("label").like.median().reindex(SENT)})"""),
    baca("like"),
    baca("kesimpulan"),
]


def main():
    nb = nbf.v4.new_notebook()
    nb.cells = CELLS
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}}
    nbf.write(nb, NB / "06_analisis_sentimen.ipynb")
    print("ok")


if __name__ == "__main__":
    main()
