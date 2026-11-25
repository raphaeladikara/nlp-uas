"""Gambar khusus paper: alur penelitian dan sebaran label (EDA)."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "figures"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

langkah = [
    ("Scraping", "X, Instagram, YouTube, TikTok\n22 Okt - 14 Nov 2026 (7.020 teks)"),
    ("Filter", "kosong, spam, duplikat, relevansi, buzzer\nsetiap kandidat buang dicek manual"),
    ("Sampling", "3.525 teks jalur A, 525 jalur B,\n2.623 teks cadangan"),
    ("Labeling 3 AI", "Claude Opus, Sonnet, Haiku\nterpisah, suara terbanyak"),
    ("Review 3 orang", "teks yang tidak disepakati bulat\nFleiss' kappa"),
    ("Dataset final", "3.329 teks, grouped stratified 5-fold"),
    ("Augmentasi (fold latih)", "jalur B, parafrase back-translation,\npelabelan terarah"),
    ("Pemodelan", "baseline, TF-IDF, embedding + LogReg, BiLSTM,\nfine-tune IndoBERT/IndoBERTweet/XLM-R"),
    ("Evaluasi", "macro-F1, F1 positif, AP, analisis kesalahan"),
]
fig, ax = plt.subplots(figsize=(6.2, 8.2))
ax.set_xlim(0, 10); ax.set_ylim(0, len(langkah) * 1.0 + 0.2); ax.axis("off")
for i, (j, isi) in enumerate(langkah):
    y = len(langkah) - i - 0.6
    ax.add_patch(FancyBboxPatch((1.2, y - 0.33), 7.6, 0.72, boxstyle="round,pad=0.02", fc="#eef2f7", ec="#334155", lw=0.8))
    ax.text(5, y + 0.15, j, ha="center", va="center", fontweight="bold")
    ax.text(5, y - 0.12, isi, ha="center", va="center", fontsize=7.5, linespacing=1.1)
    if i < len(langkah) - 1:
        ax.annotate("", xy=(5, y - 0.6), xytext=(5, y - 0.35), arrowprops=dict(arrowstyle="->", color="#334155", lw=0.8))
fig.tight_layout()
fig.savefig(FIG / "p01_alur_penelitian.png", dpi=200)

def koma(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")


def ribuan(n):
    return f"{int(n):,}".replace(",", ".")


# Sebaran label: angka di dalam segmen negatif dan netral, angka positif dan total di ujung batang
df = pd.read_csv(ROOT / "data" / "05_final" / "dataset_prepro.csv")
LABEL = ["negatif", "netral", "positif"]
warna = {"negatif": "#b91c1c", "netral": "#94a3b8", "positif": "#15803d"}
fig, axs = plt.subplots(1, 2, figsize=(8.2, 3.1))
t = pd.crosstab(df.platform, df.label)[LABEL]
t.plot.barh(stacked=True, ax=axs[0], color=[warna[k] for k in LABEL], width=0.7, legend=False)
for i, (plat, row) in enumerate(t.iterrows()):
    kiri = 0
    for k in ["negatif", "netral"]:
        axs[0].text(kiri + row[k] / 2, i, ribuan(row[k]), ha="center", va="center", fontsize=7.5,
                    color="white" if k == "negatif" else "#1e293b")
        kiri += row[k]
    axs[0].text(row.sum() + 15, i, f"+{row['positif']} positif\n(total {ribuan(row.sum())})", va="center", fontsize=7,
                color="#15803d", linespacing=1.0)
axs[0].set_xlim(0, t.sum(axis=1).max() * 1.32)
axs[0].set_title("Label per platform"); axs[0].set_xlabel("jumlah teks"); axs[0].set_ylabel("")
f = pd.crosstab(df.fase, df.label).reindex(["pra", "puncak", "pasca"])[LABEL]
pr = f.div(f.sum(axis=1), axis=0) * 100
pr.plot.bar(stacked=True, ax=axs[1], color=[warna[k] for k in LABEL], width=0.6, legend=False, rot=0)
for i, (fase, row) in enumerate(pr.iterrows()):
    axs[1].text(i, row["negatif"] / 2, f"{koma(row['negatif'])}%", ha="center", va="center", fontsize=7.5, color="white")
    axs[1].text(i, row["negatif"] + row["netral"] / 2, f"{koma(row['netral'])}%", ha="center", va="center", fontsize=7.5)
    axs[1].text(i, 101.5, f"positif {koma(row['positif'])}%", ha="center", va="bottom", fontsize=7, color="#15803d")
axs[1].set_ylim(0, 110)
axs[1].set_xticks(range(len(pr)), [f"{fase}\n(n = {ribuan(f.loc[fase].sum())})" for fase in pr.index])
axs[1].set_title("Proporsi label per fase (%)", pad=12); axs[1].set_xlabel("")
for a in axs:
    a.spines[["top", "right"]].set_visible(False)
fig.legend(LABEL, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.08, 1, 1))
fig.savefig(FIG / "p02_sebaran_label.png", dpi=200)

# Learning curve kelas positif, nilai ditulis di setiap titik
kurva = pd.read_csv(ROOT / "data" / "09_perbandingan" / "learning_curve_positif.csv")
x = kurva["positif di data latih"]
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.plot(x, kurva["F1 positif"], "o-", color="#3b6ea8", label="F1 positif")
ax.plot(x, kurva["macro-F1"], "s--", color="#9aa5b1", label="macro-F1")
for xi, a, b in zip(x, kurva["F1 positif"], kurva["macro-F1"]):
    ax.annotate(koma(a, 3), (xi, a), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=7.5, color="#3b6ea8")
    ax.annotate(koma(b, 3), (xi, b), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=7.5, color="#64748b")
ax.set_xticks(x, [koma(v) for v in x])
ax.set(xlabel="jumlah teks positif di data latih (rata-rata per fold)", ylabel="skor", ylim=(0, 0.7),
       title="Learning curve kelas positif (TF-IDF + LogReg, teks + judul)")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="lower right", frameon=False)
fig.tight_layout()
fig.savefig(FIG / "p03_learning_curve_positif.png", dpi=200)

# Progres IndoBERT fine-tune dari input paling sederhana sampai konfigurasi akhir (fold yang sama)
hasil = pd.read_csv(ROOT / "data" / "07_transformer" / "hasil_per_fold_indobert.csv")
tahap = [("teks saja", "tanpa augmentasi", "teks saja"),
         ("teks + judul", "tanpa augmentasi", "+ judul"),
         ("teks + judul", "jalur B", "+ judul\n+ jalur B"),
         ("teks + judul", "jalur B + terarah", "+ judul\n+ jalur B\n+ terarah")]
nilai = [hasil[(hasil.input == i) & (hasil.augmentasi == a)][["macro_f1", "f1_positif"]].mean() for i, a, _ in tahap]
fig, ax = plt.subplots(figsize=(6.4, 3.4))
lebar = 0.36
for j, (kol, nama, w) in enumerate([("macro_f1", "macro-F1", "#334155"), ("f1_positif", "F1 positif", "#15803d")]):
    xs = [i + (j - 0.5) * lebar for i in range(len(tahap))]
    ys = [v[kol] for v in nilai]
    ax.bar(xs, ys, lebar, color=w, label=nama)
    for xi, yi in zip(xs, ys):
        ax.text(xi, yi + 0.012, koma(yi, 3), ha="center", va="bottom", fontsize=7.5)
ax.set_xticks(range(len(tahap)), [t[2] for t in tahap], fontsize=8)
ax.set(ylabel="skor (rata-rata 5 fold)", ylim=(0, 0.75), title="IndoBERT fine-tune per tahap perbaikan")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper left")
fig.tight_layout()
fig.savefig(FIG / "p04_progres_indobert.png", dpi=200)
print("ok")
