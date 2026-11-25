"""Gabungkan jawaban 3 annotator Claude, ambil suara terbanyak, dan tandai teks yang perlu dicek manusia.

Input : labeling/hasil/{opus,sonnet,haiku}/batch_XX.jsonl, labeling/batches/index.csv, data/03_filtered/*.csv
Output: data/04_labeled/label_llm.csv   (semua teks + 3 suara + label mayoritas + penanda review)
        labeling/review/review_data.js  (data untuk halaman review.html)

Aturan:
- relevan  : suara terbanyak dari 3 annotator.
- sentimen : suara terbanyak dari annotator yang menilai relevan. Kalau ketiganya beda, label kosong.
- perlu_review_label : ketiga annotator TIDAK sepakat bulat soal relevan atau sentimen.
- perlu_review_buzzer: teks di zona batas skor buzzer (2-3) yang dinilai buzzer oleh >= 1 annotator,
                       atau teks lolos filter yang dinilai buzzer oleh >= 2 annotator.
"""
import json
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
H, F, L = ROOT / "labeling" / "hasil", ROOT / "data" / "03_filtered", ROOT / "data" / "04_labeled"
MODELS = ["opus", "sonnet", "haiku"]
SENT = {"negatif", "netral", "positif"}


def baca(model):
    rows = {}
    for f in sorted((H / model).glob("batch_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip().strip(",")
            if not line.startswith("{"):
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows[r["id"]] = r
    return rows


def mayoritas(vals):
    vals = [v for v in vals if v not in (None, "")]
    if not vals:
        return None, 0
    v, n = Counter(vals).most_common(1)[0]
    return (v, n) if n >= 2 else (None, n)


def main():
    idx = pd.read_csv(ROOT / "labeling" / "batches" / "index.csv", dtype=str)
    base = pd.concat([pd.read_csv(F / f, dtype=str) for f in
                      ("dataset_untuk_label.csv", "jalur_b_untuk_label.csv", "buzzer.csv",
                       "kontrol_yt_untuk_label.csv", "kontrol_tt_untuk_label.csv") if (F / f).exists()]
                     ).drop_duplicates("id")
    d = idx.merge(base, on=["id", "platform"], how="left")
    hasil = {m: baca(m) for m in MODELS}
    for m in MODELS:
        print(f"{m:7} {len(hasil[m]):5} jawaban, hilang {len(set(d.id) - set(hasil[m]))}")

    out = []
    for r in d.itertuples():
        votes = {m: hasil[m].get(r.id, {}) for m in MODELS}
        rel = [int(v.get("relevan", 0)) if v else None for v in votes.values()]
        rel_maj, rel_n = mayoritas(rel)
        sen = [v.get("sentimen") if v and int(v.get("relevan", 0)) == 1 and v.get("sentimen") in SENT else
               ("tidak_relevan" if v else None) for v in votes.values()]
        sen_maj, sen_n = mayoritas(sen)
        sub_maj, _ = mayoritas([v.get("sub") for v in votes.values() if v and v.get("sentimen") == sen_maj])
        buz = [int(v.get("buzzer", 0)) for v in votes.values() if v]
        flag = lambda k: sum(int(v.get(k, 0)) for v in votes.values() if v) >= 2  # noqa: E731
        aspek = Counter(a for v in votes.values() if v for a in (v.get("aspek") or []))
        target = Counter(a for v in votes.values() if v for a in (v.get("target_lain") or []))
        lengkap = all(votes.values())
        sepakat = lengkap and len(set(sen)) == 1
        status = r.status_buzzer if isinstance(r.status_buzzer, str) else "lolos"
        out.append(dict(
            id=r.id, kelompok=r.kelompok,
            **{f"sentimen_{m}": s for m, s in zip(MODELS, sen)},
            label=sen_maj if sen_maj else None, n_setuju=sen_n, sepakat_bulat=sepakat,
            sub=sub_maj, aspek=";".join(a for a, n in aspek.items() if n >= 2),
            target_lain=";".join(a for a, n in target.items() if n >= 2 and a != "tidak_ada"),
            sarkasme=flag("sarkasme"), butuh_konteks=flag("butuh_konteks"), buzzer_llm_votes=sum(buz),
            catatan=" | ".join(f"{m}: {v.get('catatan')}" for m, v in votes.items() if v and v.get("catatan")),
            perlu_review_label=not sepakat and r.kelompok != "buzzer",
            perlu_review_buzzer=r.kelompok != "buzzer" and ((status == "batas" and sum(buz) >= 1) or sum(buz) >= 2)))
    lab = pd.DataFrame(out)
    L.mkdir(parents=True, exist_ok=True)
    lab.to_csv(L / "label_llm.csv", index=False, encoding="utf-8-sig")

    sub = d.set_index("id")
    # kelompok kontrol hanya untuk uji bias sampling (catatan_bias_sampel.md), cukup label mayoritas LLM
    rv = lab[(lab.perlu_review_label | lab.perlu_review_buzzer) & ~lab.kelompok.str.startswith("kontrol")].copy()
    data = [dict(id=x.id, platform=sub.at[x.id, "platform"], kelompok=x.kelompok, text=sub.at[x.id, "text"],
                 konteks=sub.at[x.id, "konteks"] if isinstance(sub.at[x.id, "konteks"], str) else "",
                 url=sub.at[x.id, "sumber_url"], votes={m: getattr(x, f"sentimen_{m}") for m in MODELS},
                 label=x.label, review_label=bool(x.perlu_review_label), review_buzzer=bool(x.perlu_review_buzzer),
                 skor_buzzer=sub.at[x.id, "skor_buzzer"], alasan_skor=sub.at[x.id, "alasan_skor"]
                 if isinstance(sub.at[x.id, "alasan_skor"], str) else "", buzzer_votes=int(x.buzzer_llm_votes),
                 catatan=x.catatan) for x in rv.itertuples()]
    (ROOT / "labeling" / "review").mkdir(exist_ok=True)
    (ROOT / "labeling" / "review" / "review_data.js").write_text(
        "window.REVIEW_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")

    print("\nsepakat bulat:", f"{lab.sepakat_bulat.mean():.1%}")
    print(lab.groupby("kelompok").label.value_counts(dropna=False).unstack(fill_value=0))
    print("perlu review label:", int(lab.perlu_review_label.sum()), "| perlu review buzzer:",
          int(lab.perlu_review_buzzer.sum()), "| total kartu review:", len(rv))


if __name__ == "__main__":
    main()
