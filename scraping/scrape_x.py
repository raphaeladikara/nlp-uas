"""Scraping tweet tentang Raffi Ahmad, kuota per hari (22 Okt - 14 Nov 2026), mode Latest.

Kenapa per hari: mode "Top" membuat kurva volume bias ke tweet viral. Dengan since/until harian, tiap hari
punya kuota sendiri sehingga tren sentimen per fase bisa dibandingkan.
Actor: kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest (~$0,25 per 1.000 tweet).
Token: APIFY_API3 (3 run paralel).
Output: data/01_raw/x_raw.json (bisa dilanjutkan; hari+query yang sudah ada dilewati).
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import apify_utils as au  # noqa: E402

ACTOR = "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"
OUT = Path(__file__).resolve().parents[1] / "data" / "01_raw" / "x_raw.json"
MULAI, AKHIR = date(2026, 10, 22), date(2026, 11, 14)
QUERIES = [  # (nama, query, maks per hari)
    ("raffi_ahmad", '"raffi ahmad"', 120),
    ("raffi_isu", "raffi (mahasewa OR bayaran OR bundaran OR deklarasi OR klarifikasi OR boikot OR rans OR icw "
                  "OR kpk OR 14m OR miliar OR utusan OR willie OR carnival)", 120),
    ("rafi_typo", '"rafi ahmad" OR "rafi ahmat" OR "raffi ahmat"', 40),
]


def job(args):
    nama, q, n, d = args
    query = f"{q} since:{d} until:{d + timedelta(days=1)}"
    try:
        items, st, c = au.run_actor(ACTOR, {"twitterContent": query, "maxItems": n, "queryType": "Latest",
                                            "lang": "in"}, max_charge_usd=0.1, key="APIFY_API3")
    except Exception as e:  # noqa: BLE001
        print("GAGAL", nama, d, str(e)[:120], flush=True)
        return None
    real = [dict(t, _query=nama, _day=str(d)) for t in items if t.get("type") == "tweet"]
    print(f"{d} {nama:12} -> {len(real):3} (${c or 0:.3f})", flush=True)
    return (nama, str(d), real)


def main():
    rows = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    done = {(r["_query"], r["_day"]) for r in rows}
    hari = [MULAI + timedelta(days=i) for i in range((AKHIR - MULAI).days + 1)]
    todo = [(n, q, k, d) for d in hari for n, q, k in QUERIES if (n, str(d)) not in done]
    print(f"{len(todo)} run", flush=True)
    with ThreadPoolExecutor(3) as ex:
        for res in ex.map(job, todo):
            if res:
                rows += res[2] or [{"_query": res[0], "_day": res[1], "type": "_kosong"}]
                OUT.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    print("total baris", len(rows), flush=True)


if __name__ == "__main__":
    main()
