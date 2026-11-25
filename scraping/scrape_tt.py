"""Scraping komentar TikTok tentang Raffi Ahmad (22 Okt - 14 Nov 2026).

1. Cari video lewat clockworks/tiktok-scraper (beberapa query), simpan ke data/01_raw/tt_videos.json.
2. Pilih 14 video relevan dengan komentar terbanyak (maks 2 per kreator), ambil 60 komentar per video
   lewat clockworks/tiktok-comments-scraper -> data/01_raw/tt_comments.json.
Token: APIFY_API8.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import apify_utils as au  # noqa: E402

KEY = "APIFY_API8"
RAW = Path(__file__).resolve().parents[1] / "data" / "01_raw"
QUERIES = ["raffi ahmad mahasiswa bayaran", "raffi ahmad mahasewa", "raffi ahmad bundaran hi",
           "raffi ahmad klarifikasi", "raffi ahmad 14 miliar", "boikot rans carnival"]
RELEVAN = re.compile(r"raff?i|\brans\b|mahasewa|mahasiswa bayaran|nagita", re.I)


def main():
    items, st, c = au.run_actor("clockworks~tiktok-scraper",
                                {"searchQueries": QUERIES, "resultsPerPage": 20, "shouldDownloadVideos": False,
                                 "shouldDownloadCovers": False, "shouldDownloadSubtitles": False},
                                max_charge_usd=1.0, key=KEY)
    print(f"video: {len(items)} (${c:.3f}, {st})", flush=True)
    (RAW / "tt_videos.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    seen, per, pilih = set(), {}, []
    for v in sorted(items, key=lambda v: -(v.get("commentCount") or 0)):
        url, au_ = v.get("webVideoUrl"), (v.get("authorMeta") or {}).get("name")
        if not url or url in seen or not ("2026-10-22" <= (v.get("createTimeISO") or "") < "2026-11-15"):
            continue
        if not RELEVAN.search(v.get("text") or "") or per.get(au_, 0) >= 2 or (v.get("commentCount") or 0) < 30:
            continue
        seen.add(url)
        per[au_] = per.get(au_, 0) + 1
        pilih.append(v)
    pilih = pilih[:14]
    for v in pilih:
        print((v.get("authorMeta") or {}).get("name"), v.get("commentCount"), v.get("createTimeISO", "")[:10],
              re.sub(r"\s+", " ", v.get("text") or "")[:60], flush=True)
    com, st, c = au.run_actor("clockworks~tiktok-comments-scraper",
                              {"postURLs": [v["webVideoUrl"] for v in pilih], "commentsPerPost": 60},
                              max_charge_usd=2.0, key=KEY, timeout_s=3600)
    print(f"komentar: {len(com)} (${c:.3f}, {st})", flush=True)
    (RAW / "tt_comments.json").write_text(json.dumps({"videos": pilih, "comments": com}, ensure_ascii=False),
                                          encoding="utf-8")


if __name__ == "__main__":
    main()
