"""Scraping komentar Instagram tentang Raffi Ahmad (22 Okt - 14 Nov 2026).

Dua jalur:
  A (publik)    : unggahan akun berita/diskusi yang ditemukan lewat keyword + hashtag. Dipakai untuk training
                  dan analisis utama.
  B (akun Raffi): unggahan @ukp_mudaseni_raffiahmad dan @raffinagita1717. Hanya untuk analisis pembanding,
                  TIDAK ikut training (komentar di akun sendiri cenderung bias ke fans/haters yang datang khusus).

Tahap:  python scraping/scrape_ig.py posts     -> data/01_raw/ig_posts.json
        python scraping/scrape_ig.py comments  -> data/01_raw/ig_comments.json
Token: APIFY_API4.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import apify_utils as au  # noqa: E402

KEY = "APIFY_API4"
RAW = Path(__file__).resolve().parents[1] / "data" / "01_raw"
MULAI, AKHIR = "2026-10-22", "2026-11-15"
JALUR_B = ["ukp_mudaseni_raffiahmad", "raffinagita1717"]
KEYWORDS = ["raffi ahmad", "raffi ahmad mahasiswa bayaran", "mahasewa", "raffi ahmad bundaran hi",
            "raffi ahmad klarifikasi", "deklarasi sumpah pemuda mahasiswa", "raffi ahmad 14 miliar",
            "raffi ahmad icw", "rans carnival boikot"]
HASHTAGS = ["raffiahmad", "mahasewa", "mahasiswabayaran", "boikotrans", "boikotraffiahmad"]
TENTANG_RAFFI = re.compile(r"raff?i|\brans\b|nagita|utusan khusus", re.I)


def posts():
    rows = []
    for kw in KEYWORDS:
        items, st, c = au.run_actor("apify~instagram-hashtag-scraper",
                                    {"hashtags": [kw], "keywordSearch": True, "resultsType": "posts",
                                     "resultsLimit": 30}, max_charge_usd=0.2, key=KEY)
        rows += [dict(p, _query=kw, _jalur="A") for p in items]
        print(f"keyword {kw!r:38} -> {len(items)} post (${c:.3f})", flush=True)
    items, st, c = au.run_actor("apify~instagram-hashtag-scraper",
                                {"hashtags": HASHTAGS, "resultsType": "posts", "resultsLimit": 30},
                                max_charge_usd=0.3, key=KEY)
    rows += [dict(p, _query="#" + "/#".join(HASHTAGS), _jalur="A") for p in items]
    print(f"hashtag -> {len(items)} post (${c:.3f})", flush=True)
    items, st, c = au.run_actor("apify~instagram-scraper",
                                {"directUrls": [f"https://www.instagram.com/{u}/" for u in JALUR_B],
                                 "resultsType": "posts", "resultsLimit": 40, "onlyPostsNewerThan": MULAI},
                                max_charge_usd=0.3, key=KEY)
    rows += [dict(p, _query="akun_raffi", _jalur="B") for p in items]
    print(f"akun raffi -> {len(items)} post (${c:.3f})", flush=True)
    (RAW / "ig_posts.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def pilih(rows, jalur, n, per_owner):
    seen, owner, out = set(), {}, []
    for p in sorted(rows, key=lambda p: -(p.get("commentsCount") or 0)):
        sc, own = p.get("shortCode"), (p.get("ownerUsername") or "").lower()
        if not sc or sc in seen or (p.get("commentsCount") or 0) < 30:
            continue
        if not (MULAI <= (p.get("timestamp") or "") < AKHIR):
            continue
        if jalur == "A" and (own in JALUR_B or not TENTANG_RAFFI.search(p.get("caption") or "")):
            continue
        if jalur == "B" and own not in JALUR_B:
            continue
        if owner.get(own, 0) >= per_owner:
            continue
        seen.add(sc)
        owner[own] = owner.get(own, 0) + 1
        out.append(p)
    return out[:n]


def comments():
    rows = json.loads((RAW / "ig_posts.json").read_text(encoding="utf-8"))
    a = pilih([p for p in rows if p["_jalur"] == "A"], "A", 22, 3)
    b = pilih(rows, "B", 8, 8)
    hasil, meta = [], []
    for jalur, ps, n in (("A", a, 100), ("B", b, 80)):
        for p in ps:
            print(jalur, p["shortCode"], p.get("ownerUsername"), p.get("commentsCount"), p.get("timestamp", "")[:10],
                  re.sub(r"\s+", " ", p.get("caption") or "")[:60], flush=True)
            meta.append({k: p.get(k) for k in ("shortCode", "ownerUsername", "caption", "timestamp", "commentsCount",
                                               "likesCount", "_query")} | {"_jalur": jalur})
        items, st, c = au.run_actor("datadoping~instagram-comments-and-replies-scraper",
                                    {"code_or_id_or_url": [f"https://www.instagram.com/p/{p['shortCode']}/" for p in ps],
                                     "sort_by": "popular", "max_comments": n},
                                    max_charge_usd=round(len(ps) * n * 0.002 + 0.5, 2), key=KEY, timeout_s=3600)
        print(f"jalur {jalur}: {len(items)} komentar (${c:.3f}, {st})", flush=True)
        hasil += items
    (RAW / "ig_comments.json").write_text(json.dumps({"posts": meta, "comments": hasil}, ensure_ascii=False),
                                          encoding="utf-8")


if __name__ == "__main__":
    {"posts": posts, "comments": comments}[sys.argv[1]]()
