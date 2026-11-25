"""Gabungkan label ground truth (sepakat bulat 3 LLM + review 3 orang) menjadi dataset final, lalu cek kesiapannya.

Input : labeling/review/3lapis/sepakat_bulat_gt.csv  (teks yang disepakati bulat 3 LLM, kolom label_gt)
        data/04_labeled/review_3lapis.csv             (hasil labeling/review/gabung_review_3lapis.py: suara
                                                       terbanyak 3 orang untuk teks yang tidak disepakati LLM)
        data/04_labeled/metadata_llm.csv              (sub, aspek, target_lain, sarkasme, butuh_konteks dari
                                                       labeling LLM; label_llm.csv sudah tidak dipakai)
        data/03_filtered/dataset_untuk_label.csv, jalur_b_untuk_label.csv (teks + metadata)
Output: data/05_final/dataset_model.csv      (siap training: id, text, judul, label, fold, ...)
        data/05_final/augmentasi_jalur_b.csv (komentar positif dari akun Raffi, hanya untuk fold latih)
        data/05_final/laporan_kesiapan.md    (semua angka dan hasil pemeriksaan, dibuat ulang tiap dijalankan)

Aturan (alasan lengkap ada di dokumentasi_data.md):
1. Hanya kelompok `utama` (jalur A lolos filter). jalur_b, buzzer, kontrol_yt, kontrol_tt TIDAK masuk.
2. Label akhir = label_gt kalau 3 LLM sepakat bulat, selain itu suara terbanyak 3 orang (review 3 lapis).
3. Teks review buzzer=1 dikeluarkan dari training (dipindah ke statistik buzzer).
4. Dibuang: tidak_relevan dan teks review yang belum punya label.
5. Grouped stratified 5-fold CV (kolom `fold`). Satu akun atau teks identik selalu berada di fold yang
   sama, jadi tidak bisa muncul di data latih dan data uji sekaligus.
"""
import re
from collections import Counter
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parents[1]
F, L, OUT = ROOT / "data" / "03_filtered", ROOT / "data" / "04_labeled", ROOT / "data" / "05_final"
REVIEW_DIR = ROOT / "labeling" / "review" / "hasil"
SENT = ["negatif", "netral", "positif"]
SEED = 42
N_FOLD = 5


def muat_label():
    """Satu tabel label untuk semua teks utama + jalur B: id, kelompok, label, sumber_label, buzzer_review."""
    gt = pd.read_csv(ROOT / "labeling" / "review" / "3lapis" / "sepakat_bulat_gt.csv", dtype=str).fillna("")
    gt = gt.assign(label=gt.label_gt, sumber_label="llm_bulat", buzzer_review="", status_review="")
    r3 = pd.read_csv(L / "review_3lapis.csv", dtype=str).fillna("")
    r3 = r3.assign(label=r3.label_review, sumber_label="manusia_3_orang", status_review=r3.status)
    kol = ["id", "kelompok", "label", "sumber_label", "buzzer_review", "status_review"]
    lab = pd.concat([gt[kol], r3[kol]], ignore_index=True)
    assert lab.id.is_unique, "ada teks yang muncul di sepakat_bulat_gt dan review 3 orang sekaligus"
    return lab


def kunci(t):
    return " ".join(re.sub(r"[^a-z0-9 ]", "", str(t).lower().replace("@user", "")).split())


def grup(df):
    """Union-find: akun yang sama ATAU teks identik masuk satu grup."""
    induk = {}

    def akar(x):
        induk.setdefault(x, x)
        while induk[x] != x:
            induk[x] = induk[induk[x]]
            x = induk[x]
        return x

    for a, k in zip(df.author_hash.fillna(df.id), df.kunci):
        induk[akar("a:" + a)] = akar("k:" + k)
    return df.author_hash.fillna(df.id).map(lambda a: akar("a:" + a))


def main():
    lab = muat_label()
    meta = pd.read_csv(F / "dataset_untuk_label.csv", dtype=str)
    d = lab[lab.kelompok == "utama"].merge(meta, on="id", how="left", validate="one_to_one")
    ml = pd.read_csv(L / "metadata_llm.csv", dtype=str)
    # Output mentah LLM batch 28 (39 teks hasil revisi filter) tidak tersimpan, jadi metadata-nya diisi ulang
    # satu annotator dengan codebook yang sama. Label sentimennya tetap dari review 3 orang.
    isi_ulang = L / "metadata_batch28_isi_ulang.csv"
    if isi_ulang.exists():
        tambah = pd.read_csv(isi_ulang, dtype=str)
        ml = pd.concat([ml, tambah[~tambah.id.isin(ml.id)]], ignore_index=True)
    d = d.merge(ml, on="id", how="left", validate="one_to_one")
    for c in ("sarkasme", "butuh_konteks"):
        d[c] = d[c].eq("True")
    n_awal = len(d)

    r3 = d[d.sumber_label.eq("manusia_3_orang")]
    belum_label = r3.label.eq("")
    ringkas = ROOT / "labeling" / "review" / "3lapis" / "ringkasan_kappa.md"
    info_review = {"ringkas": f"review 3 lapis, {int(lab.sumber_label.eq('manusia_3_orang').sum())} kartu "
                              f"(utama {len(r3)})",
                   "kesepakatan": ringkas.read_text(encoding="utf-8").split("\n", 1)[1] if ringkas.exists() else ""}

    d["label_final"] = d.label
    corong = {"utama (jalur A) dilabeli": n_awal,
              "  - label dari 3 LLM sepakat bulat": int(d.sumber_label.eq("llm_bulat").sum()),
              "  - label dari review 3 orang": len(r3)}
    keluar_buzzer = d.buzzer_review.eq("1")
    d = d[~keluar_buzzer]
    corong["- dikeluarkan: buzzer hasil review"] = int(keluar_buzzer.sum())
    tr = d.label_final.eq("tidak_relevan")
    corong["- dibuang: tidak relevan"] = int(tr.sum())
    kosong = ~d.label_final.isin(SENT) & ~tr
    corong["- dibuang: review belum punya label (seri, belum diputus)"] = int(kosong.sum())
    d = d[d.label_final.isin(SENT)].copy()
    corong["dataset model"] = len(d)

    d["judul"] = d.konteks
    d["kunci"] = d.text.map(kunci)
    # Teks identik di sumber yang sama harus satu label. Kalau review 3 orang memberi label berbeda untuk
    # salinan-salinannya, suara semua penilai di salinan itu digabung dan diambil yang terbanyak.
    suara = pd.read_csv(ROOT / "labeling" / "review" / "3lapis" / "kappa_per_kartu.csv").set_index("id")
    harmonis = []
    for (_, _), g in d.groupby(["kunci", "sumber_id"]):
        if g.label_final.nunique() > 1:
            v = suara.reindex(g.id)[SENT].sum()
            baru = v.idxmax() if (v == v.max()).sum() == 1 else g.label_final.mode().iloc[0]
            harmonis += [(i, d.at[i, "label_final"], baru) for i in g.index]
            d.loc[g.index, "label_final"] = baru
    corong["  (label disamakan: teks identik di sumber yang sama)"] = len(harmonis)
    d["grup"] = grup(d)
    # grouped 5-fold CV: tiap teks jadi data uji tepat sekali, jadi semua teks positif ikut dievaluasi
    d["fold"] = -1
    sgk = StratifiedGroupKFold(n_splits=N_FOLD, shuffle=True, random_state=SEED)
    for k, (_, uji) in enumerate(sgk.split(d, d.label_final, d.grup)):
        d.iloc[uji, d.columns.get_loc("fold")] = k

    cek = []

    def periksa(nama, ok, detail=""):
        cek.append((nama, bool(ok), detail))

    kelompok_lain = set(lab[lab.kelompok != "utama"].id)
    periksa("tidak ada teks jalur B / buzzer / kontrol di dataset", not d.id.isin(kelompok_lain).any())
    periksa("id unik", d.id.is_unique)
    periksa("semua label di {negatif, netral, positif}", d.label_final.isin(SENT).all())
    periksa("teks tidak kosong", d.text.fillna("").str.strip().ne("").all())
    periksa("semua teks punya fold", d.fold.between(0, N_FOLD - 1).all())
    periksa("tidak ada akun yang muncul di dua fold", d.dropna(subset=["author_hash"])
            .groupby("author_hash").fold.nunique().max() == 1)
    periksa("tidak ada teks identik di dua fold", d.groupby("kunci").fold.nunique().max() == 1)
    periksa("tiap fold punya ketiga kelas", d.groupby("fold").label_final.nunique().min() == 3)
    # teks sama di sumber berbeda boleh beda label (konteksnya beda); di sumber yang sama harus konsisten
    konflik = d.groupby(["kunci", "sumber_id"]).label_final.nunique().gt(1)
    contoh = ", ".join(konflik[konflik].index.get_level_values(0)[:3])
    periksa("teks identik di sumber yang sama berlabel konsisten", not konflik.any(),
            f"{int(konflik.sum())} kelompok: {contoh}" if konflik.any() else "")
    periksa("setiap teks review 3 lapis punya label akhir", not belum_label.any(),
            f"{int(belum_label.sum())} kartu dibuang: {', '.join(r3.id[belum_label])}" if belum_label.any() else "")
    st = r3.status_review.value_counts()
    periksa("kartu review dinilai minimal 2 orang", not st.get("kosong", 0),
            ", ".join(f"{k} {v}" for k, v in st.items()))
    periksa("metadata LLM (sarkasme, butuh judul) tersedia", d.id.isin(ml.id).all(),
            f"{int((~d.id.isin(ml.id)).sum())} teks tanpa metadata, dianggap False" if not d.id.isin(ml.id).all() else "")
    INFO = ("kartu review", "metadata", "setiap teks review")
    siap = all(ok for n, ok, _ in cek if not n.startswith(INFO))

    kolom = ["id", "text", "judul", "label_final", "fold", "platform", "fase", "tanggal", "sumber_id",
             "author_hash", "is_media", "status_buzzer", "sumber_label", "sub", "aspek", "target_lain",
             "sarkasme", "butuh_konteks", "like_count"]
    OUT.mkdir(parents=True, exist_ok=True)
    d[kolom].rename(columns={"label_final": "label"}).to_csv(OUT / "dataset_model.csv", index=False,
                                                              encoding="utf-8-sig")

    # semua teks berlabel (utama termasuk buzzer dan tidak relevan, plus jalur B) untuk notebook analisis sentimen
    mb_all = pd.read_csv(F / "jalur_b_untuk_label.csv", dtype=str)
    teks_all = pd.concat([meta, mb_all]).drop_duplicates("id")
    semua = lab.merge(teks_all[["id", "platform", "fase", "tanggal", "text", "konteks", "like_count", "is_media",
                                "status_buzzer", "author_hash"]], on="id", how="left").merge(ml, on="id", how="left")
    semua = semua.rename(columns={"konteks": "judul"})
    semua["buzzer"] = semua.buzzer_review.eq("1")
    semua.drop(columns="buzzer_review").to_csv(OUT / "semua_label.csv", index=False, encoding="utf-8-sig")

    # positif dari akun Raffi (jalur B), rentang waktunya sama (22 Okt - 14 Nov). Hanya untuk fold latih.
    # Akun atau teks yang juga ada di data utama dibuang supaya tidak bocor ke fold uji.
    mb = pd.read_csv(F / "jalur_b_untuk_label.csv", dtype=str)
    b = lab[lab.kelompok == "jalur_b"].merge(mb, on="id", how="left")
    b["label_final"] = b.label
    b = b[b.label_final.eq("positif") & b.buzzer_review.ne("1")].copy()
    b["kunci"] = b.text.map(kunci)
    bocor = b.author_hash.isin(d.author_hash) | b.kunci.isin(d.kunci)
    b = b[~bocor].drop_duplicates("kunci")
    b.drop(columns="label").rename(columns={"konteks": "judul", "label_final": "label"})[
        ["id", "text", "judul", "label", "tanggal", "sumber_id", "author_hash"]].to_csv(
        OUT / "augmentasi_jalur_b.csv", index=False, encoding="utf-8-sig")
    corong["(augmentasi) positif jalur B untuk fold latih"] = len(b)
    corong["(augmentasi) positif jalur B dibuang karena akun/teks ada di data utama"] = int(bocor.sum())

    tab = pd.crosstab(d.fold, d.label_final, margins=True)
    pct = (d.label_final.value_counts(normalize=True) * 100).round(1)
    md = [f"# Laporan kesiapan dataset model\n",
          f"**Status: {'SIAP' if siap else 'DRAFT, belum siap'}**  ",
          f"Review manusia: {info_review['ringkas']} (`labeling/review/3lapis/`)\n",
          "## Corong label\n", "| tahap | jumlah |", "|---|---|"]
    md += [f"| {k} | {v} |" for k, v in corong.items()]
    md += ["\n## Distribusi kelas\n", "| label | n | % |", "|---|---|---|"]
    md += [f"| {k} | {int((d.label_final == k).sum())} | {pct.get(k, 0)} |" for k in SENT]
    md += ["\n## Fold CV (grouped by akun + teks identik, stratified)\n", tab.to_markdown(), "",
           "## Kesepakatan reviewer manusia (review 3 lapis, Fleiss' kappa)\n", info_review["kesepakatan"], "",
           "## Sumber label\n", d.sumber_label.value_counts().to_frame("n").to_markdown(), "",
           "## Pemeriksaan\n", "| cek | hasil | detail |", "|---|---|---|"]
    md += [f"| {n} | {'OK' if ok else ('CATATAN' if n.startswith(INFO) else 'GAGAL')} | {det} |" for n, ok, det in cek]
    md += ["\n## Catatan untuk modeling\n",
           f"- Kelas positif hanya {pct.get('positif', 0)}%. Pakai class weight / oversampling di train saja, "
           "dan laporkan macro-F1 serta F1 per kelas, bukan akurasi.",
           f"- {d.butuh_konteks.mean():.0%} teks ditandai butuh konteks. Bandingkan model teks saja vs teks + konteks.",
           f"- {int(d.is_media.eq('True').sum())} teks dari akun media X ikut training (label sesuai isi), "
           "tapi dikeluarkan dari statistik opini publik.",
           f"- Evaluasi memakai grouped {N_FOLD}-fold CV dengan kolom `fold`: latih di 4 fold, uji di 1 fold, "
           "ulangi 5 kali, laporkan rata-rata dan standar deviasi. Tuning hyperparameter dilakukan di dalam "
           "fold latih saja (nested), jangan memakai fold uji. Jangan membuat split acak baru, supaya tidak bocor."]
    (OUT / "laporan_kesiapan.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n".join(f"{'OK   ' if ok else 'GAGAL'} {n} {det}" for n, ok, det in cek))
    print(tab)
    print("STATUS:", "SIAP" if siap else "DRAFT")
    return 0 if siap else 1


if __name__ == "__main__":
    sys.exit(main())
