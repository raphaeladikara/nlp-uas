"""Pecah teks yang lolos filter menjadi batch untuk 3 annotator Claude (Opus, Sonnet, Haiku).

Input : data/03_filtered/dataset_untuk_label.csv, jalur_b_untuk_label.csv, buzzer.csv
        (--kontrol: sampel kontrol bias, --tambahan: teks baru dari revisi gerbang filter)
Output: labeling/batches/batch_XX.md   (teks dikelompokkan per sumber, konteks ditulis sekali per sumber)
        labeling/batches/index.csv     (id -> batch)
Ketiga annotator membaca batch yang sama persis, lalu menulis jawabannya ke
labeling/hasil/<model>/batch_XX.jsonl sesuai format di labeling/codebook.md.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
F, B = ROOT / "data" / "03_filtered", ROOT / "labeling" / "batches"
UKURAN = 180


def main():
    kontrol = "--kontrol" in sys.argv
    tambahan = "--tambahan" in sys.argv
    if tambahan:
        # teks yang baru lolos setelah revisi gerbang filter (notebook 01 versi 2), ditulis sebagai batch baru
        d = pd.read_csv(F / "audit" / "perlu_label_v2.csv", dtype=str)
        lama = pd.read_csv(B / "index.csv", dtype=str)
        d = d[~d.id.isin(lama.id)]
        mulai = int(lama.batch.astype(int).max()) + 1
        kontrol = True  # sisanya sama dengan mode kontrol: batch lama tidak disentuh
    elif kontrol:
        # sampel kontrol YouTube (komentar terbaru) ditambahkan sebagai batch baru di belakang,
        # supaya batch lama yang sudah dilabeli tidak bergeser
        d = pd.concat([pd.read_csv(f, dtype=str).assign(kelompok=f.name.replace("_untuk_label.csv", ""))
                       for f in sorted(F.glob("kontrol_*_untuk_label.csv"))], ignore_index=True)
        lama = pd.read_csv(B / "index.csv", dtype=str)
        d = d[~d.id.isin(lama.id)]
        mulai = int(lama.batch.astype(int).max()) + 1
    else:
        parts = []
        for nama, kelompok in (("dataset_untuk_label.csv", "utama"), ("jalur_b_untuk_label.csv", "jalur_b"),
                               ("buzzer.csv", "buzzer")):
            d = pd.read_csv(F / nama, dtype=str)
            d["kelompok"] = kelompok
            parts.append(d)
        d = pd.concat(parts, ignore_index=True).drop_duplicates("id")
        mulai = 1
    # urut per sumber supaya konteks cukup ditulis sekali; batch tidak memotong di tengah sumber kalau bisa
    d = d.sort_values(["platform", "sumber_id", "created_at"]).reset_index(drop=True)
    B.mkdir(parents=True, exist_ok=True)
    if not kontrol:
        for f in B.glob("batch_*.md"):
            f.unlink()

    batch, isi, n, idx = mulai, [], 0, []

    def tulis():
        nonlocal batch, isi, n
        if not isi:
            return
        kepala = (f"# Batch {batch:02d} ({n} teks)\n\nLabeli setiap teks sesuai labeling/codebook.md. "
                  "Konteks di atas tiap kelompok berlaku untuk semua teks di bawahnya.\n")
        (B / f"batch_{batch:02d}.md").write_text(kepala + "\n".join(isi) + "\n", encoding="utf-8")
        batch, isi, n = batch + 1, [], 0

    for (plat, sid), g in d.groupby(["platform", "sumber_id"], sort=False):
        if n and n + len(g) > UKURAN * 1.15:
            tulis()
        for start in range(0, len(g), UKURAN):
            potong = g.iloc[start:start + UKURAN]
            if n and n + len(potong) > UKURAN * 1.15:
                tulis()
            if plat == "x":
                for r in potong.itertuples():
                    kon = f" [konteks: {r.konteks}]" if isinstance(r.konteks, str) and r.konteks else ""
                    isi.append(f"- {r.id} | {r.text}{kon}")
                    idx.append((r.id, batch))
            else:
                isi.append(f"\n## Sumber {plat} {sid}\nKonteks: {potong.konteks.iloc[0]}\n")
                for r in potong.itertuples():
                    isi.append(f"- {r.id} | {r.text}")
                    idx.append((r.id, batch))
            n += len(potong)
    tulis()
    baru = pd.DataFrame(idx, columns=["id", "batch"]).merge(d[["id", "kelompok", "platform"]])
    if kontrol:
        baru = pd.concat([lama, baru.astype(str)], ignore_index=True)
    baru.to_csv(B / "index.csv", index=False, encoding="utf-8-sig")
    print(f"{len(d)} teks -> batch {mulai:02d}-{batch - 1:02d}", d.kelompok.value_counts().to_dict())


if __name__ == "__main__":
    main()
