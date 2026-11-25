"""Siapkan review manusia 3 lapis: setiap teks yang tidak disepakati bulat oleh 3 annotator LLM dilabeli 3 orang.

Pakai : python labeling/review/buat_review_3lapis.py
Input : data/04_labeled/label_llm.csv (hasil aggregate.py), data/03_filtered/*.csv (teks dan judul),
        labeling/review/hasil/*.csv (review 1 orang yang sudah dikerjakan sebelumnya)
Output: labeling/review/3lapis/sepakat_bulat_gt.csv     teks yang disepakati bulat 3 LLM, labelnya langsung GT
        labeling/review/3lapis/perlu_review_3_orang.csv teks yang belum disepakati, diisi 3 orang
        labeling/review/3lapis/tugas_<Nama>.csv         potongan berkas di atas untuk tiap orang

Aturan:
- Hanya kelompok utama (jalur A) dan jalur_b. Buzzer dan kontrol tidak direview.
- Slot reviewer 1 diisi review lama (satu orang) kalau ada. Kartu kalibrasi yang dulu dikerjakan 5 orang
  diambil 3 reviewernya secara acak (seed 42), supaya setiap kartu punya tepat 3 penilai dan Fleiss' kappa
  bisa dihitung dengan jumlah penilai yang sama di semua kartu.
- Slot yang masih kosong dibagi bergiliran ke 5 orang. Satu orang tidak pernah mendapat kartu yang sama dua kali.
"""
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
F, L = ROOT / "data" / "03_filtered", ROOT / "data" / "04_labeled"
HASIL, OUT = ROOT / "labeling" / "review" / "hasil", ROOT / "labeling" / "review" / "3lapis"
TIM = ["Adit", "Exsa", "Mikael", "Raphael", "Yasyfa"]
MODELS = ["opus", "sonnet", "haiku"]
SEED = 42


def main():
    lab = pd.read_csv(L / "label_llm.csv", dtype=str)
    lab = lab[lab.kelompok.isin(["utama", "jalur_b"])]
    teks = pd.concat([pd.read_csv(F / f, dtype=str) for f in ("dataset_untuk_label.csv", "jalur_b_untuk_label.csv")])
    d = lab.merge(teks[["id", "platform", "konteks", "text", "sumber_url", "skor_buzzer", "alasan_skor"]], on="id",
                  how="left", validate="one_to_one").rename(columns={"konteks": "judul"})
    for m in MODELS:
        d[f"label_{m}"] = d[f"sentimen_{m}"].fillna("(tidak menjawab)")
    perlu = d.perlu_review_label.eq("True") | d.perlu_review_buzzer.eq("True")

    OUT.mkdir(parents=True, exist_ok=True)
    gt = d[~perlu].assign(label_gt=lambda x: x.label)
    gt[["id", "kelompok", "platform", "judul", "text"] + [f"label_{m}" for m in MODELS] + ["label_gt"]].to_csv(
        OUT / "sepakat_bulat_gt.csv", index=False, encoding="utf-8-sig")

    r = d[perlu].copy()
    r["cek_buzzer"] = r.perlu_review_buzzer.eq("True").map({True: "ya", False: "tidak"})
    r["label_mayoritas_llm"] = r.label.fillna("(tidak ada mayoritas)")

    lama = pd.concat([pd.read_csv(f, dtype=str) for f in sorted(HASIL.glob("hasil_review_*.csv"))]).fillna("")
    lama = lama.drop_duplicates(["id", "reviewer"], keep="last")
    rng = random.Random(SEED)
    slot = {}
    for i, g in lama.groupby("id"):
        g = g.sort_values("reviewer")
        pilih = g if len(g) <= 3 else g.iloc[sorted(rng.sample(range(len(g)), 3))]
        slot[i] = list(pilih.itertuples(index=False))

    beban = {n: 0 for n in TIM}
    baris = []
    # kartu diurutkan seperti bagi_review.py supaya tiap orang dapat campuran kelompok dan platform yang seimbang
    r = r.sort_values(["kelompok", "cek_buzzer", "platform", "label_mayoritas_llm", "id"])
    for x in r.itertuples():
        isi = slot.get(x.id, [])
        nama = [s.reviewer for s in isi]
        for _ in range(3 - len(isi)):
            calon = sorted((n for n in TIM if n not in nama), key=lambda n: (beban[n], TIM.index(n)))
            nama.append(calon[0])
            beban[calon[0]] += 1
        row = dict(id=x.id, kelompok=x.kelompok, platform=x.platform, judul=x.judul, text=x.text,
                   sumber_url=x.sumber_url, label_opus=x.label_opus, label_sonnet=x.label_sonnet,
                   label_haiku=x.label_haiku, label_mayoritas_llm=x.label_mayoritas_llm, catatan_llm=x.catatan,
                   cek_buzzer=x.cek_buzzer, skor_buzzer=x.skor_buzzer, alasan_skor_buzzer=x.alasan_skor)
        for k in range(3):
            s = isi[k] if k < len(isi) else None
            row[f"reviewer_{k + 1}"] = nama[k]
            row[f"label_{k + 1}"] = s.label_review if s else ""
            row[f"buzzer_{k + 1}"] = s.buzzer_review if s else ""
        baris.append(row)
    out = pd.DataFrame(baris)
    out.to_csv(OUT / "perlu_review_3_orang.csv", index=False, encoding="utf-8-sig")

    for n in TIM:
        mine = [(k, row) for _, row in out.iterrows() for k in (1, 2, 3)
                if row[f"reviewer_{k}"] == n and row[f"label_{k}"] == ""]
        t = pd.DataFrame([{**{c: row[c] for c in ("id", "kelompok", "platform", "judul", "text", "sumber_url",
                                                    "label_opus", "label_sonnet", "label_haiku", "cek_buzzer",
                                                    "skor_buzzer", "alasan_skor_buzzer")},
                           "slot": k, "label": "", "buzzer": ""} for k, row in mine])
        t.to_csv(OUT / f"tugas_{n}.csv", index=False, encoding="utf-8-sig")

    terisi = sum(out[f"label_{k}"].ne("").sum() for k in (1, 2, 3))
    print(f"sepakat bulat (GT langsung): {len(gt)}  {gt.kelompok.value_counts().to_dict()}")
    print(f"perlu review 3 orang: {len(out)}  {out.kelompok.value_counts().to_dict()}")
    print(f"slot terisi dari review lama: {terisi} dari {3 * len(out)}")
    print("slot baru per orang:", beban)


if __name__ == "__main__":
    main()
