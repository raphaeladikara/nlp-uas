"""Ambil profil akun pemberi komentar Instagram dan TikTok untuk filter buzzer.

X dan YouTube tidak perlu langkah ini: profil penulis tweet sudah ikut di hasil scraping tweet, dan profil
channel YouTube diambil gratis di scrape_yt.py.

  python scraping/scrape_profiles.py ig  -> data/01_raw/ig_profiles.json  (apify/instagram-profile-scraper)
  python scraping/scrape_profiles.py tt  -> data/01_raw/tt_profiles.json  (clockworks/tiktok-profile-scraper)
Bisa dilanjutkan: akun yang sudah ada di file output dilewati.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import apify_utils as au  # noqa: E402

RAW = Path(__file__).resolve().parents[1] / "data" / "01_raw"


def ig_users():
    d = json.loads((RAW / "ig_comments.json").read_text(encoding="utf-8"))
    u = set()
    for c in d["comments"]:
        if c.get("content_type") == "caption":
            continue
        u.add(c.get("username") or (c.get("user") or {}).get("username"))
        for r in c.get("preview_child_comments") or []:
            u.add(r.get("username") or (r.get("user") or {}).get("username"))
    u.discard(None)
    return sorted(u)


def tt_users():
    d = json.loads((RAW / "tt_comments.json").read_text(encoding="utf-8"))
    return sorted({c.get("uniqueId") for c in d["comments"] if c.get("uniqueId")})


def run(platform):
    out = RAW / f"{platform}_profiles.json"
    lama = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    if platform == "ig":
        done = {p.get("username") for p in lama}
        todo = [u for u in ig_users() if u not in done]
        # dibagi ke dua token supaya kredit satu akun tidak habis
        bagian = [(todo[: len(todo) // 2], "APIFY_API5"), (todo[len(todo) // 2:], "APIFY_API6")]
        for users, key in bagian:
            if not users:
                continue
            items, st, c = au.run_actor("apify~instagram-profile-scraper", {"usernames": users},
                                        max_charge_usd=round(len(users) * 0.003 + 0.5, 2), key=key, timeout_s=5400)
            lama += items
            print(f"{key}: {len(users)} akun -> {len(items)} profil (${c:.3f}, {st})", flush=True)
            out.write_text(json.dumps(lama, ensure_ascii=False), encoding="utf-8")
    else:
        done = {((p.get("authorMeta") or {}).get("name") or "").lower() for p in lama}
        todo = [u for u in tt_users() if u.lower() not in done]
        items, st, c = au.run_actor("clockworks~tiktok-profile-scraper",
                                    {"profiles": todo, "resultsPerPage": 1, "shouldDownloadVideos": False,
                                     "shouldDownloadCovers": False, "profileScrapeSections": ["videos"]},
                                    max_charge_usd=round(len(todo) * 0.006 + 0.5, 2), key="APIFY_API7",
                                    timeout_s=5400)
        lama += items
        print(f"tiktok: {len(todo)} akun -> {len(items)} baris (${c:.3f}, {st})", flush=True)
        out.write_text(json.dumps(lama, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    run(sys.argv[1])
