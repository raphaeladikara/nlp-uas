"""Pilot scraping kecil (~100 teks per sumber) untuk menilai kualitas sampel sebelum scraping penuh.

Topik: sentimen publik terhadap Raffi Ahmad pasca deklarasi "mahasiswa bayaran" di Bundaran HI (29 Okt 2026).
Pemakaian:  python scraping/pilot.py x | ig | yt | tt
Output: data/00_pilot/<sumber>.json
"""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
import apify_utils as au  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "00_pilot"
OUT.mkdir(parents=True, exist_ok=True)


def save(name, obj):
    (OUT / f"{name}.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


# X
def x():
    """Uji query harian (since/until) pada 3 hari dari 3 fase berbeda."""
    au.pick_key(0.3)
    actor = "kaitoeasyapi~twitter-x-data-tweet-scraper-pay-per-result-cheapest"
    tests = [("raffi ahmad", "2026-10-26", "2026-10-27"),
             ("raffi ahmad", "2026-10-30", "2026-10-31"),
             ("raffi mahasiswa bayaran OR raffi mahasewa", "2026-10-30", "2026-10-31"),
             ("raffi ahmad", "2026-11-10", "2026-11-11")]
    rows = []
    for q, s, u in tests:
        query = f"{q} since:{s} until:{u}"
        items, st, c = au.run_actor(actor, {"twitterContent": query, "maxItems": 30, "queryType": "Latest",
                                            "lang": "in"}, max_charge_usd=0.05)
        real = [dict(t, _query=query) for t in items if t.get("type") == "tweet"]
        rows += real
        print(f"{query!r:70} -> {len(real)} tweet (${c:.3f}, {st})")
    save("x", rows)


# Instagram
def ig():
    au.pick_key(0.6)
    # 1) unggahan publik lewat keyword search
    posts = []
    cache = OUT / "ig_posts.json"
    for kw in ([] if cache.exists() else ["raffi ahmad mahasiswa bayaran", "raffi ahmad bundaran hi", "raffi ahmad klarifikasi"]):
        items, st, c = au.run_actor("apify~instagram-hashtag-scraper",
                                    {"hashtags": [kw], "keywordSearch": True, "resultsType": "posts",
                                     "resultsLimit": 15}, max_charge_usd=0.1)
        posts += [dict(p, _query=kw) for p in items]
        print(f"keyword {kw!r:35} -> {len(items)} post (${c:.3f})")
    # 2) unggahan akun Raffi sendiri (jalur B)
    if cache.exists():
        posts = json.loads(cache.read_text(encoding="utf-8"))
    else:
      items, st, c = au.run_actor("apify~instagram-scraper",
                                {"directUrls": ["https://www.instagram.com/raffinagita1717/"],
                                 "resultsType": "posts", "resultsLimit": 12,
                                 "onlyPostsNewerThan": "2026-10-22"}, max_charge_usd=0.1)
      posts += [dict(p, _query="@raffinagita1717") for p in items]
      print(f"akun raffi -> {len(items)} post (${c:.3f})")
      save("ig_posts", posts)

    # pilih 2 unggahan publik + 1 unggahan Raffi dengan komentar terbanyak
    def top(ps, n):
        seen, out = set(), []
        for p in sorted(ps, key=lambda p: -(p.get("commentsCount") or 0)):
            if p.get("shortCode") and p["shortCode"] not in seen and "raffi" in (p.get("caption") or "").lower() + p["_query"]:
                seen.add(p["shortCode"])
                out.append(p)
        return out[:n]
    pub = top([p for p in posts if p["_query"] != "@raffinagita1717" and (p.get("timestamp") or "") >= "2026-10-29"], 2)
    own = top([p for p in posts if p["_query"] == "@raffinagita1717"], 1)
    for p in pub + own:
        print("  pilih", p["shortCode"], p.get("ownerUsername"), p.get("commentsCount"), p.get("timestamp"),
              (p.get("caption") or "")[:60].replace("\n", " "))
    urls = [f"https://www.instagram.com/p/{p['shortCode']}/" for p in pub + own]
    items, st, c = au.run_actor("datadoping~instagram-comments-and-replies-scraper",
                                {"code_or_id_or_url": urls, "sort_by": "recent", "max_comments": 40},
                                max_charge_usd=0.4)
    print(f"komentar -> {len(items)} (${c:.3f}, {st})")
    save("ig_comments", {"posts": [{k: p.get(k) for k in ("shortCode", "ownerUsername", "caption", "timestamp",
                                                             "commentsCount", "_query")} for p in pub + own],
                         "comments": items})


# YouTube (Data API v3, gratis)
def yt():
    load_dotenv(find_dotenv(usecwd=True))
    key = (os.environ.get("YOUTUBE_API_KEY") or "").strip()
    base = "https://www.googleapis.com/youtube/v3"
    vids = requests.get(f"{base}/search", params={
        "key": key, "part": "snippet", "q": "raffi ahmad mahasiswa bayaran bundaran hi", "type": "video",
        "publishedAfter": "2026-10-28T00:00:00Z", "maxResults": 10, "regionCode": "ID",
        "relevanceLanguage": "id", "order": "relevance"}).json()
    if "error" in vids:
        print(vids["error"]); return
    out = []
    for v in vids.get("items", [])[:4]:
        vid, sn = v["id"]["videoId"], v["snippet"]
        print(" video", vid, sn["channelTitle"], sn["publishedAt"][:10], sn["title"][:70])
        r = requests.get(f"{base}/commentThreads", params={"key": key, "part": "snippet", "videoId": vid,
                                                           "maxResults": 30, "order": "relevance",
                                                           "textFormat": "plainText"}).json()
        for it in r.get("items", []):
            out.append(dict(it["snippet"]["topLevelComment"]["snippet"], _videoId=vid,
                            _videoTitle=sn["title"], _channel=sn["channelTitle"]))
    print(f"komentar youtube -> {len(out)}")
    save("yt", out)


# TikTok
def tt():
    au.pick_key(0.5)
    items, st, c = au.run_actor("clockworks~tiktok-scraper",
                                {"searchQueries": ["raffi ahmad mahasiswa bayaran"], "resultsPerPage": 10,
                                 "shouldDownloadVideos": False, "shouldDownloadCovers": False},
                                max_charge_usd=0.5)
    print(f"video tiktok -> {len(items)} (${c:.3f}, {st})")
    vids = sorted([v for v in items if v.get("webVideoUrl")], key=lambda v: -(v.get("commentCount") or 0))[:3]
    for v in vids:
        print(" video", v.get("authorMeta", {}).get("name"), v.get("commentCount"), v.get("createTimeISO"),
              (v.get("text") or "")[:60])
    com, st, c = au.run_actor("clockworks~tiktok-comments-scraper",
                              {"postURLs": [v["webVideoUrl"] for v in vids], "commentsPerPost": 35},
                              max_charge_usd=0.5)
    print(f"komentar tiktok -> {len(com)} (${c:.3f}, {st})")
    save("tt", {"videos": vids, "comments": com})


if __name__ == "__main__":
    {"x": x, "ig": ig, "yt": yt, "tt": tt}[sys.argv[1]]()
