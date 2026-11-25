"""Gabungkan review 3 orang per teks, ambil suara terbanyak, dan hitung Fleiss' kappa.

Pakai : python labeling/review/gabung_review_3lapis.py
Input : labeling/review/3lapis/hasil review 3 orang.csv  (pemisah ";", kolom reviewer_k, label_k, buzzer_k, k = 1..3)
        labeling/review/3lapis/isian_lengkapi_3lapis.csv (opsional: unduhan lengkapi_3lapis.html, berisi suara yang
                                                          belum diisi, hasil diskusi kartu seri, dan cek buzzer)
        labeling/review/3lapis/koordinator_3lapis.csv    (opsional: id,label,buzzer untuk memutus kartu seri)
        data/04_labeled/review_manusia.csv               (review tahap 1, sudah diputus koordinator; dipakai untuk
                                                           kartu yang masih seri dan untuk keputusan buzzer)
Output: data/04_labeled/review_3lapis.csv  (id, kelompok, label_review, buzzer_review, status, n_reviewer)
        labeling/review/3lapis/seri_perlu_koordinator.csv (kartu yang belum punya suara terbanyak 2 orang)
        labeling/review/3lapis/kappa_per_kartu.csv        (jumlah suara per kategori, bahan tabel Fleiss)
        labeling/review/3lapis/ringkasan_kappa.md

Aturan label:
1. Minimal 2 orang memilih label yang sama -> label itu dipakai (status "mayoritas" kalau 3 orang menilai,
   "dua_sepakat" kalau hanya 2 orang yang mengisi dan keduanya sama).
2. Ketiganya beda -> hasil diskusi tim dari isian_lengkapi_3lapis.csv (status "diskusi") atau koordinator_3lapis.csv.
3. Kalau masih belum ada keputusan, dipakai label review tahap 1 (status "putus_tahap1") dan kartunya tetap
   tercatat di seri_perlu_koordinator.csv.
Aturan buzzer: kolom buzzer_1..3 di berkas hasil isinya sama persis di ketiga slot (disalin, bukan dinilai terpisah),
jadi keputusan buzzer diambil dari cek buzzer di isian_lengkapi_3lapis.csv, atau review tahap 1 kalau belum ada.

Fleiss' kappa butuh jumlah penilai yang sama di setiap kartu, jadi dihitung di kartu yang lengkap dinilai 3 orang.
Sebagai pembanding, Krippendorff's alpha (nominal) dihitung di semua kartu yang dinilai minimal 2 orang, karena
alpha tetap sah walau ada nilai yang kosong.
"""
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "labeling" / "review" / "3lapis"
L = ROOT / "data" / "04_labeled"
LABEL = ["negatif", "netral", "positif", "tidak_relevan"]
SENT = LABEL[:3]
K = (1, 2, 3)


def fleiss_kappa(tabel):
    """tabel: baris = kartu, kolom = kategori, isi = jumlah penilai yang memilih kategori itu."""
    m = np.asarray(tabel, float)
    n = m.sum(1)
    assert (n == n[0]).all(), "Fleiss' kappa butuh jumlah penilai yang sama di semua kartu"
    n = n[0]
    p_i = ((m * (m - 1)).sum(1)) / (n * (n - 1))
    p_j = m.sum(0) / m.sum()
    pe = (p_j ** 2).sum()
    return (p_i.mean() - pe) / (1 - pe), p_i.mean(), pe


def fleiss_per_kategori(tabel):
    """Kappa per kategori (Fleiss 1971): seberapa konsisten orang memakai satu kategori tertentu."""
    m = np.asarray(tabel, float)
    n = m.sum(1)[0]
    p_j = m.sum(0) / m.sum()
    return 1 - (m * (n - m)).sum(0) / (len(m) * n * (n - 1) * p_j * (1 - p_j))


def krippendorff_alpha(tabel):
    """Alpha nominal dari tabel jumlah suara per kartu; kartu dengan < 2 penilai diabaikan."""
    m = np.asarray(tabel, float)
    m = m[m.sum(1) >= 2]
    n_u = m.sum(1)
    o = np.zeros((m.shape[1], m.shape[1]))
    for row, nu in zip(m, n_u):
        o += (np.outer(row, row) - np.diag(row)) / (nu - 1)
    n_c, n = o.sum(0), o.sum()
    d_o = n - np.trace(o)
    d_e = (n * n - (n_c ** 2).sum()) / (n - 1)
    return 1 - d_o / d_e


def tafsir(k):
    """Skala Landis & Koch (1977)."""
    for batas, kata in [(0, "buruk"), (0.2, "sedikit"), (0.4, "cukup (fair)"), (0.6, "sedang (moderate)"),
                        (0.8, "kuat (substantial)"), (1.01, "hampir sempurna")]:
        if k < batas:
            return kata
    return "hampir sempurna"


def baca_hasil():
    r = pd.read_csv(D / "hasil review 3 orang.csv", sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    r = r.loc[:, ~r.columns.str.startswith("Unnamed")]
    for k in K:
        r[f"label_{k}"] = r[f"label_{k}"].str.strip().str.lower()
        r.loc[~r[f"label_{k}"].isin(LABEL), f"label_{k}"] = ""   # "(tidak menjawab)" dan sel kosong
    isian = D / "isian_lengkapi_3lapis.csv"
    if isian.exists():
        f = pd.read_csv(isian, dtype=str, encoding="utf-8-sig").fillna("")
        for x in f[f.jenis.eq("suara")].itertuples():
            i = r.index[r.id.eq(x.id)][0]
            assert r.at[i, f"label_{x.slot}"] == "", f"slot {x.slot} kartu {x.id} sudah terisi"
            r.at[i, f"reviewer_{x.slot}"], r.at[i, f"label_{x.slot}"] = x.reviewer, x.label
        print(f"isian: {int(f.jenis.eq('suara').sum())} suara, {int(f.jenis.eq('diskusi').sum())} diskusi, "
              f"{int(f.jenis.eq('buzzer').sum())} cek buzzer")
        diskusi = f[f.jenis.eq("diskusi")].set_index("id")
        buzzer = f[f.jenis.eq("buzzer")].set_index("id").buzzer
    else:
        diskusi, buzzer = pd.DataFrame(columns=["label", "catatan"]), pd.Series(dtype=str)
    return r, diskusi, buzzer


def putuskan(vals):
    vals = [v for v in vals if v]
    if not vals:
        return "", "kosong"
    v, n = Counter(vals).most_common(1)[0]
    if n >= 2:
        return v, "mayoritas" if len(vals) == 3 else "dua_sepakat"
    return "", "seri" if len(vals) == 3 else "dua_beda"


def main():
    r, diskusi, buzzer_isian = baca_hasil()
    tahap1 = pd.read_csv(L / "review_manusia.csv", dtype=str).fillna("").set_index("id")
    kord = pd.read_csv(D / "koordinator_3lapis.csv", dtype=str).fillna("").set_index("id") \
        if (D / "koordinator_3lapis.csv").exists() else pd.DataFrame(columns=["label", "buzzer"])

    out = []
    for x in r.itertuples():
        votes = [getattr(x, f"label_{k}") for k in K]
        lb, st = putuskan(votes)
        if not lb and st == "seri" and x.id in diskusi.index:
            lb, st = diskusi.at[x.id, "label"], "diskusi"
        elif not lb and x.id in kord.index and kord.at[x.id, "label"]:
            lb, st = kord.at[x.id, "label"], "koordinator"
        elif not lb and x.id in tahap1.index and tahap1.at[x.id, "label_review"]:
            lb, st = tahap1.at[x.id, "label_review"], "putus_tahap1"
        bz = tahap1.at[x.id, "buzzer_review"] if x.id in tahap1.index else ""
        if x.id in buzzer_isian.index:
            bz = buzzer_isian[x.id]
        if x.id in kord.index and kord.at[x.id, "buzzer"]:
            bz = kord.at[x.id, "buzzer"]
        out.append(dict(id=x.id, kelompok=x.kelompok, platform=x.platform, label_review=lb, buzzer_review=bz,
                        status=st, n_reviewer=sum(v != "" for v in votes)))
    h = pd.DataFrame(out)
    h.drop(columns="platform").to_csv(L / "review_3lapis.csv", index=False, encoding="utf-8-sig")
    belum = h.status.isin(["seri", "dua_beda", "kosong", "putus_tahap1"])
    r[belum.values].assign(label_dipakai=h.label_review[belum].values, status=h.status[belum].values).to_csv(
        D / "seri_perlu_koordinator.csv", index=False, encoding="utf-8-sig")

    tab = pd.DataFrame([[sum(getattr(x, f"label_{k}") == c for k in K) for c in LABEL] for x in r.itertuples()],
                       columns=LABEL)
    tab.insert(0, "id", r.id.values)
    tab["n"] = tab[LABEL].sum(axis=1)
    tab.to_csv(D / "kappa_per_kartu.csv", index=False, encoding="utf-8-sig")
    lengkap = tab.n.eq(3)

    def baris_kappa(nama, mask, kolom=LABEL):
        t = tab.loc[mask & lengkap, kolom].to_numpy()
        if kolom != LABEL:                       # versi 3 kelas: hanya kartu yang ketiganya menilai relevan
            t = t[t.sum(1) == 3]
        if len(t) < 2:
            return None
        k, po, pe = fleiss_kappa(t)
        bulat = (t.max(1) == 3).mean()
        return dict(kelompok=nama, kartu=len(t), kappa=round(k, 3), tafsir=tafsir(k), p_o=round(po, 3),
                    p_e=round(pe, 3), sepakat_bulat=f"{bulat:.0%}", minimal_2_sama=f"{(t.max(1) >= 2).mean():.0%}")

    semua = pd.Series(True, index=tab.index)
    rows = [baris_kappa("semua kartu, 4 kategori", semua)]
    rows += [baris_kappa(f"kelompok {g}", r.kelompok.eq(g).values) for g in sorted(r.kelompok.unique())]
    rows += [baris_kappa(f"platform {p}", r.platform.eq(p).values) for p in sorted(r.platform.unique())]
    rows += [baris_kappa("3 kelas sentimen (ketiga orang menilai relevan)", semua, SENT)]
    rk = pd.DataFrame([x for x in rows if x])
    rk.to_csv(D / "ringkasan_kappa.csv", index=False, encoding="utf-8-sig")

    per_kat = fleiss_per_kategori(tab.loc[lengkap, LABEL].to_numpy())
    alpha = krippendorff_alpha(tab[LABEL].to_numpy())
    n2 = int(tab.n.ge(2).sum())
    k_utama = rk.iloc[0]
    md = ["# Ringkasan review 3 lapis\n",
          f"- kartu: {len(r)} (utama {int(r.kelompok.eq('utama').sum())}, jalur B {int(r.kelompok.eq('jalur_b').sum())})",
          f"- dinilai lengkap 3 orang: {int(lengkap.sum())}, hanya 2 orang: {int(tab.n.eq(2).sum())}, "
          f"kosong: {int(tab.n.eq(0).sum())}",
          "- keputusan label: " + ", ".join(f"{k} {v}" for k, v in h.status.value_counts().items()),
          "",
          f"**Fleiss' kappa = {k_utama.kappa:.3f}** ({k_utama.tafsir}, skala Landis & Koch) di {k_utama.kartu} kartu "
          f"yang lengkap dinilai 3 orang, 4 kategori (negatif, netral, positif, tidak_relevan). "
          f"Kesepakatan teramati P_o = {k_utama.p_o:.3f}, kesepakatan kebetulan P_e = {k_utama.p_e:.3f}.",
          f"Krippendorff's alpha (nominal) di {n2} kartu yang dinilai minimal 2 orang = {alpha:.3f}.",
          "",
          "## Kappa per kelompok\n", rk.to_markdown(index=False), "",
          "## Kappa per kategori (kartu lengkap)\n",
          pd.DataFrame({"kategori": LABEL, "kappa": per_kat.round(3),
                        "dipilih (%)": (tab.loc[lengkap, LABEL].sum() / tab.loc[lengkap, LABEL].to_numpy().sum()
                                        * 100).round(1).values}).to_markdown(index=False), "",
          "Catatan: kartu ini adalah teks yang TIDAK disepakati bulat oleh 3 LLM, jadi memang teks paling ambigu. "
          "Kappa di sini lebih rendah daripada kalau seluruh dataset dinilai ulang."]
    (D / "ringkasan_kappa.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
