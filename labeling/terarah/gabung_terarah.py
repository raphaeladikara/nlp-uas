"""Gabungkan label kelompok terarah: 3 annotator AI, lalu 3 orang untuk teks yang tidak disepakati bulat.

Pakai : python labeling/terarah/gabung_terarah.py           tahap 1, setelah ketiga AI selesai melabeli
        python labeling/terarah/gabung_terarah.py --final   tahap 2, setelah tim mengisi review 3 orang

Tahap 1
  Input : labeling/terarah/hasil/{opus,sonnet,haiku}/batch_XX.jsonl  (format di labeling/codebook.md)
  Output: labeling/terarah/label_llm_terarah.csv             (3 suara + label mayoritas)
          labeling/terarah/review/perlu_review_3_orang.csv   (kartu yang tidak disepakati bulat, reviewer sudah dibagi)
Tahap 2
  Input : labeling/terarah/review/hasil review 3 orang.csv   (berkas tahap 1 yang sudah diisi tim, pemisah ";")
          labeling/terarah/review/koordinator.csv            (opsional: id,label untuk kartu yang ketiganya beda)
  Output: data/04_labeled/label_terarah.csv                  (label akhir semua teks terarah)
          data/05_final/augmentasi_terarah.csv               (teks positif untuk fold latih, kolom fold_asal)
          labeling/terarah/ringkasan_terarah.md              (presisi peringkat, Fleiss' kappa)

Aturan sama dengan data utama: sepakat bulat 3 AI langsung dipakai, selain itu suara terbanyak 3 orang, ketiganya
beda diputus koordinator. Teks yang dinilai buzzer saat review dikeluarkan. Supaya tidak bocor ke fold uji, teks dari
akun yang juga ada di dataset final dibuang, sama seperti aturan jalur B di finalize.py. Sisanya diberi fold_asal -1
(dipakai di semua fold latih).
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "labeling" / "review"))
from gabung_review_3lapis import fleiss_kappa, fleiss_per_kategori, tafsir, putuskan  # noqa: E402

T = ROOT / "labeling" / "terarah"
R = T / "review"
F = ROOT / "data" / "03_filtered"
MODELS = ["opus", "sonnet", "haiku"]
TIM = ["Adit", "Exsa", "Mikael", "Raphael", "Yasyfa"]
LABEL = ["negatif", "netral", "positif", "tidak_relevan"]


def baca(model):
    rows = {}
    for f in sorted((T / "hasil" / model).glob("batch_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip().strip(",")
            if line.startswith("{"):
                try:
                    r = json.loads(line)
                    rows[r["id"]] = r
                except json.JSONDecodeError:
                    pass
    return rows


def suara(v):
    if not v:
        return None
    if int(v.get("relevan", 0)) != 1:
        return "tidak_relevan"
    return v.get("sentimen") if v.get("sentimen") in LABEL[:3] else None


def tahap1():
    d = pd.read_csv(F / "terarah_untuk_label.csv", dtype=str)
    hasil = {m: baca(m) for m in MODELS}
    for m in MODELS:
        hilang = set(d.id) - set(hasil[m])
        print(f"{m:7} {len(hasil[m]):4} jawaban, hilang {len(hilang)}")
        assert not hilang, f"{m} belum melabeli semua teks"
    out = []
    for r in d.itertuples():
        v = {m: hasil[m][r.id] for m in MODELS}
        s = [suara(v[m]) for m in MODELS]
        n_buz = sum(int(v[m].get("buzzer", 0)) for m in MODELS)
        bulat = len(set(s)) == 1 and s[0] is not None
        maj, n = Counter([x for x in s if x]).most_common(1)[0] if any(s) else (None, 0)
        lab = maj if n >= 2 else None
        sub = Counter(v[m].get("sub") for m in MODELS if suara(v[m]) == lab).most_common(1)
        out.append(dict(id=r.id, cara_pilih=r.cara_pilih, skor_positif=r.skor_positif,
                        **{f"label_{m}": x or "(tidak menjawab)" for m, x in zip(MODELS, s)},
                        label_llm=lab, sepakat_bulat=bulat, sub=sub[0][0] if sub else None, buzzer_llm_votes=n_buz,
                        perlu_review=not bulat or (r.status_buzzer == "batas" and n_buz >= 1) or n_buz >= 2))
    lab = pd.DataFrame(out)
    lab.to_csv(T / "label_llm_terarah.csv", index=False, encoding="utf-8-sig")

    rv = lab[lab.perlu_review].merge(d[["id", "platform", "konteks", "text", "sumber_url"]], on="id")
    rv = rv.rename(columns={"konteks": "judul"}).sample(frac=1, random_state=42).reset_index(drop=True)
    # 3 orang berbeda per kartu, dibagi bergiliran supaya beban rata
    rng = random.Random(42)
    beban = Counter()
    for k in (1, 2, 3):
        rv[f"reviewer_{k}"], rv[f"label_{k}"] = "", ""
    for i in rv.index:
        orang = sorted(TIM, key=lambda o: (beban[o], rng.random()))[:3]
        for k, o in enumerate(orang, 1):
            rv.at[i, f"reviewer_{k}"] = o
            beban[o] += 1
    rv["cek_buzzer"] = (rv.buzzer_llm_votes >= 1).map({True: "ya", False: "tidak"})
    rv["buzzer_1"] = ""
    kol = ["id", "platform", "judul", "text", "sumber_url", "label_opus", "label_sonnet", "label_haiku", "cek_buzzer",
           "reviewer_1", "label_1", "reviewer_2", "label_2", "reviewer_3", "label_3", "buzzer_1"]
    R.mkdir(parents=True, exist_ok=True)
    rv[kol].to_csv(R / "perlu_review_3_orang.csv", sep=";", index=False, encoding="utf-8-sig")
    print(f"sepakat bulat {int(lab.sepakat_bulat.sum())}, perlu review 3 orang {len(rv)}; beban: {dict(beban)}")
    print("label mayoritas AI:", lab.groupby("cara_pilih").label_llm.value_counts().unstack(fill_value=0).to_dict("index"))


def gabung_isian_html():
    """Susun 'hasil review 3 orang.csv' dari unduhan halaman review_terarah.html (isian_terarah_<Nama>.csv)."""
    r = pd.read_csv(R / "perlu_review_3_orang.csv", sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    berkas = sorted(R.glob("isian_terarah_*.csv"))
    for f in berkas:
        isi = pd.read_csv(f, dtype=str, encoding="utf-8-sig").fillna("")
        for x in isi.itertuples():
            i = r.index[r.id == x.id]
            if len(i) and x.label:
                r.loc[i, f"label_{x.slot}"] = x.label
                if x.buzzer == "ya":
                    r.loc[i, "buzzer_1"] = "ya"
        print(f"{f.name}: {int((isi.label != '').sum())} label")
    r.to_csv(R / "hasil review 3 orang.csv", sep=";", index=False, encoding="utf-8-sig")


def tahap2():
    lab = pd.read_csv(T / "label_llm_terarah.csv", dtype=str)
    if list(R.glob("isian_terarah_*.csv")):
        gabung_isian_html()
    r = pd.read_csv(R / "hasil review 3 orang.csv", sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    for k in (1, 2, 3):
        r[f"label_{k}"] = r[f"label_{k}"].str.strip().str.lower().where(lambda s: s.isin(LABEL), "")
    kord = pd.read_csv(R / "koordinator.csv", dtype=str).fillna("").set_index("id") \
        if (R / "koordinator.csv").exists() else pd.DataFrame(columns=["label"])
    keputusan, seri = {}, []
    for x in r.itertuples():
        lb, st = putuskan([getattr(x, f"label_{k}") for k in (1, 2, 3)])
        if not lb and x.id in kord.index and kord.at[x.id, "label"]:
            lb, st = kord.at[x.id, "label"], "koordinator"
        if not lb:
            seri.append(x.id)
        keputusan[x.id] = (lb, st, x.buzzer_1.strip().lower() in ("1", "ya", "y"))
    if seri:
        pd.DataFrame({"id": seri, "label": ""}).to_csv(R / "seri_perlu_koordinator.csv", index=False)
        print(f"{len(seri)} kartu ketiganya beda, isi labeling/terarah/review/koordinator.csv lalu jalankan lagi")

    lab["label"] = lab.label_llm
    lab["sumber_label"] = "llm_bulat"
    lab["buzzer"] = False
    for i, x in lab.iterrows():
        if x.id in keputusan:
            lb, st, bz = keputusan[x.id]
            lab.at[i, "label"], lab.at[i, "sumber_label"], lab.at[i, "buzzer"] = lb or None, f"manusia_{st}", bz
    lab.to_csv(ROOT / "data" / "04_labeled" / "label_terarah.csv", index=False, encoding="utf-8-sig")

    # Fleiss' kappa di kartu yang lengkap dinilai 3 orang
    lengkap = r[(r[["label_1", "label_2", "label_3"]] != "").all(axis=1)]
    tabel = [[sum(getattr(x, f"label_{k}") == c for k in (1, 2, 3)) for c in LABEL] for x in lengkap.itertuples()]
    kappa, po, pe = fleiss_kappa(tabel) if tabel else (float("nan"),) * 3
    per_kat = fleiss_per_kategori(tabel) if tabel else []

    # augmentasi: positif, bukan buzzer, tidak identik dengan teks di dataset final
    d = pd.read_csv(F / "terarah_untuk_label.csv", dtype=str)
    final = pd.read_csv(ROOT / "data" / "05_final" / "dataset_model.csv", dtype=str)
    pos = lab[lab.label.eq("positif") & ~lab.buzzer].merge(d, on="id", suffixes=("", "_d"))
    bocor = pos.author_hash.isin(final.author_hash)
    pos = pos[~bocor].copy()
    pos["fold_asal"] = "-1"
    pos.rename(columns={"konteks": "judul"})[["id", "text", "judul", "label", "fold_asal", "tanggal", "sumber_id",
                                              "author_hash", "platform", "cara_pilih", "skor_positif"]].to_csv(
        ROOT / "data" / "05_final" / "augmentasi_terarah.csv", index=False, encoding="utf-8-sig")

    prs = lab[~lab.buzzer].groupby("cara_pilih").label.apply(lambda s: (s == "positif").mean())
    md = ["# Ringkasan pelabelan terarah\n",
          f"- teks dilabeli: {len(lab)} ({int((lab.cara_pilih == 'skor_tertinggi').sum())} skor tertinggi, "
          f"{int((lab.cara_pilih == 'acak').sum())} acak)",
          f"- sepakat bulat 3 AI: {int((lab.sumber_label == 'llm_bulat').sum())}, review 3 orang: {len(r)}",
          f"- positif dari skor tertinggi: {prs.get('skor_tertinggi', 0):.1%}, dari acak: {prs.get('acak', 0):.1%}",
          f"- positif untuk augmentasi: {len(pos)} (dibuang karena akunnya ada di dataset final: {int(bocor.sum())})",
          f"- dinilai buzzer: {int(lab.buzzer.sum())}, kartu seri belum diputus: {len(seri)}",
          f"\n**Fleiss' kappa = {kappa:.3f}** ({tafsir(kappa)}) di {len(lengkap)} kartu lengkap, P_o {po:.3f}, P_e {pe:.3f}.",
          "", "| kategori | kappa |", "|---|---|"] + [f"| {c} | {k:.3f} |" for c, k in zip(LABEL, per_kat)]
    md += ["", "## Sebaran label\n", lab.groupby("cara_pilih").label.value_counts().unstack(fill_value=0).to_markdown()]
    (T / "ringkasan_terarah.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    tahap2() if "--final" in sys.argv else tahap1()
