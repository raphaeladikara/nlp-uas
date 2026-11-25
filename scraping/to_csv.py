"""Ubah JSON mentah Apify/YouTube API (data/01_raw) menjadi CSV dengan skema yang sama untuk keempat platform.

Output:
  data/02_csv/x.csv, instagram.csv, youtube.csv, tiktok.csv  (satu baris = satu teks)
  data/02_csv/gabungan.csv                                   (keempatnya digabung)

Username diubah jadi hash SHA-256 10 karakter di tahap ini, jadi CSV sudah aman untuk dibagikan. Fitur yang
butuh username asli (pola username generik, apakah penulis = pemilik unggahan) dihitung sebelum di-hash.
Belum ada baris yang dibuang di tahap ini, kecuali ID yang sama persis (tweet yang muncul di beberapa query).
"""
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data" / "01_raw", ROOT / "data" / "02_csv"
OUT.mkdir(parents=True, exist_ok=True)
KOLOM = ["id", "platform", "jalur", "query", "sumber_id", "sumber_url", "konteks", "is_reply", "parent_id",
         "created_at", "text_raw", "like_count", "author_hash", "username_generik", "is_pemilik_sumber",
         "author_followers", "author_following", "author_n_post", "author_dibuat", "author_verified",
         "author_private", "author_bio_kosong", "author_foto_default", "author_bot_flag"]


def h(x):
    return hashlib.sha256(str(x or "").lower().encode()).hexdigest()[:10] if x else None


def username_generik(u):
    """Pola username generik: huruf lalu >= 5 digit, atau campuran huruf-angka acak (contoh: user8273645, ab12cd34)."""
    u = str(u or "").lower()
    return bool(re.search(r"^[a-z_.]+\d{5,}$", u) or re.fullmatch(r"[a-z]{2,8}\d{2,}[a-z]{2,}\d{2,}[a-z0-9]*", u)
                or re.fullmatch(r"user\d+", u))


def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bersih_konteks(t, n=400):
    return re.sub(r"\s+", " ", html.unescape(str(t or ""))).strip()[:n]


def x():
    raw = json.loads((RAW / "x_raw.json").read_text(encoding="utf-8"))
    tweets = {}
    for t in raw:
        if t.get("type") == "tweet" and t["id"] not in tweets:
            tweets[t["id"]] = t
    rows = []
    for t in tweets.values():
        a = t.get("author") or {}
        q = t.get("quoted_tweet") or {}
        parent = tweets.get(t.get("inReplyToId") or "")
        konteks = ""
        if q.get("text"):
            konteks = "Tweet yang dikutip: " + q["text"]
        elif parent:
            konteks = "Membalas tweet: " + parent["text"]
        elif t.get("isReply") and t.get("inReplyToUsername"):
            konteks = "Membalas tweet akun lain (isi tweet induk tidak ikut ter-scrape)"
        dibuat = a.get("createdAt")
        rows.append(dict(
            id="X_" + t["id"], platform="x", jalur="A", query=t["_query"], sumber_id=t.get("conversationId"),
            sumber_url=t.get("url"), konteks=bersih_konteks(konteks), is_reply=bool(t.get("isReply")),
            parent_id=t.get("inReplyToId"),
            created_at=iso(datetime.strptime(t["createdAt"], "%a %b %d %H:%M:%S %z %Y")), text_raw=t.get("text") or "",
            like_count=t.get("likeCount") or 0, author_hash=h(a.get("userName")),
            username_generik=username_generik(a.get("userName")), is_pemilik_sumber=False,
            author_followers=a.get("followers"), author_following=a.get("following"),
            author_n_post=a.get("statusesCount"),
            author_dibuat=iso(datetime.strptime(dibuat, "%a %b %d %H:%M:%S %z %Y"))[:10] if dibuat else None,
            author_verified=bool(a.get("isVerified")), author_private=False,
            author_bio_kosong=not (a.get("description") or "").strip(),
            author_foto_default="default_profile" in str(a.get("profilePicture") or ""),
            author_bot_flag=bool(a.get("isAutomated")), lang=t.get("lang")))
    return pd.DataFrame(rows)


def instagram():
    d = json.loads((RAW / "ig_comments.json").read_text(encoding="utf-8"))
    posts = {p["shortCode"]: p for p in d["posts"]}
    prof = {}
    if (RAW / "ig_profiles.json").exists():
        prof = {p.get("username", "").lower(): p for p in json.loads((RAW / "ig_profiles.json").read_text(encoding="utf-8"))}
    rows, seen = [], set()

    def add(c, sc, parent):
        cid = str(c.get("id") or c.get("pk") or c.get("comment_id"))
        if cid in seen:
            return
        seen.add(cid)
        p = posts[sc]
        u = c.get("username") or (c.get("user") or {}).get("username")
        pr = prof.get((u or "").lower(), {})
        ts = c.get("created_at_utc") or c.get("created_at")
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc) if str(ts).isdigit() else \
            datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        rows.append(dict(
            id="IG_" + cid, platform="instagram", jalur=p["_jalur"], query=p.get("_query"), sumber_id=sc,
            sumber_url=f"https://www.instagram.com/p/{sc}/",
            konteks=bersih_konteks(f"Caption unggahan @{p.get('ownerUsername')}: {p.get('caption') or ''}"),
            is_reply=parent is not None, parent_id=parent, created_at=iso(dt), text_raw=c.get("text") or "",
            like_count=c.get("like_count") or c.get("comment_like_count") or 0, author_hash=h(u),
            username_generik=username_generik(u),
            is_pemilik_sumber=bool(c.get("is_created_by_media_owner")) or (u or "").lower() == (p.get("ownerUsername") or "").lower(),
            author_followers=pr.get("followersCount"), author_following=pr.get("followsCount"),
            author_n_post=pr.get("postsCount"), author_dibuat=None,
            author_verified=bool(pr.get("verified") or (c.get("user") or {}).get("is_verified")),
            author_private=bool(pr.get("private") or (c.get("user") or {}).get("is_private")),
            author_bio_kosong=not (pr.get("biography") or "").strip() if pr else None,
            author_foto_default=None, author_bot_flag=False, lang=None))

    for c in d["comments"]:
        if c.get("content_type") == "caption":  # teks caption dari pemilik unggahan, bukan komentar
            continue
        sc = re.search(r"/p/([^/]+)/", c.get("input_url", "")).group(1)
        add(c, sc, None)
        for r in c.get("preview_child_comments") or []:
            add(r, sc, "IG_" + str(c.get("id")))
    return pd.DataFrame(rows)


def youtube():
    vids = {v["videoId"]: v for v in json.loads((RAW / "yt_videos.json").read_text(encoding="utf-8"))}
    ch = {c["id"]: c for c in json.loads((RAW / "yt_channels.json").read_text(encoding="utf-8"))}
    rows = []
    for c in json.loads((RAW / "yt_comments.json").read_text(encoding="utf-8")):
        v = vids[c["videoId"]]
        cid = (c.get("authorChannelId") or {}).get("value")
        p = ch.get(cid, {})
        st, sn = p.get("statistics", {}), p.get("snippet", {})
        rows.append(dict(
            id="YT_" + c["commentId"], platform="youtube", jalur="A", query=v.get("_query"), sumber_id=c["videoId"],
            sumber_url="https://www.youtube.com/watch?v=" + c["videoId"],
            konteks=bersih_konteks(f"Judul video {v['channelTitle']}: {v['title']}"), is_reply=False, parent_id=None,
            created_at=c["publishedAt"], text_raw=c.get("textOriginal") or "", like_count=c.get("likeCount") or 0,
            author_hash=h(cid), username_generik=username_generik((c.get("authorDisplayName") or "").lstrip("@")),
            is_pemilik_sumber=cid == v.get("channelId"),
            author_followers=None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0)) if st else None,
            author_following=None, author_n_post=int(st["videoCount"]) if st.get("videoCount") else None,
            author_dibuat=(sn.get("publishedAt") or "")[:10] or None, author_verified=False, author_private=False,
            author_bio_kosong=not (sn.get("description") or "").strip() if sn else None,
            author_foto_default=None, author_bot_flag=False, lang=None))
    return pd.DataFrame(rows)


def tiktok():
    d = json.loads((RAW / "tt_comments.json").read_text(encoding="utf-8"))
    vids = {v["webVideoUrl"]: v for v in d["videos"]}
    prof = {}
    if (RAW / "tt_profiles.json").exists():
        for p in json.loads((RAW / "tt_profiles.json").read_text(encoding="utf-8")):
            m = p.get("authorMeta") or {}
            if m.get("name"):
                prof[m["name"].lower()] = m
    rows, seen = [], set()
    for c in d["comments"]:
        if c.get("cid") in seen or not c.get("text"):
            continue
        seen.add(c.get("cid"))
        v = vids.get(c.get("videoWebUrl") or c.get("submittedVideoUrl"), {})
        u = c.get("uniqueId")
        m = prof.get((u or "").lower(), {})
        rows.append(dict(
            id="TT_" + str(c["cid"]), platform="tiktok", jalur="A", query=None,
            sumber_id=str(v.get("id") or c.get("videoWebUrl")), sumber_url=c.get("videoWebUrl"),
            konteks=bersih_konteks(f"Deskripsi video @{(v.get('authorMeta') or {}).get('name')}: {v.get('text') or ''}"),
            is_reply=bool(c.get("repliesToId")), parent_id=("TT_" + str(c["repliesToId"])) if c.get("repliesToId") else None,
            created_at=iso(datetime.fromisoformat(c["createTimeISO"].replace("Z", "+00:00"))), text_raw=c.get("text") or "", like_count=c.get("diggCount") or 0,
            author_hash=h(u), username_generik=username_generik(u),
            is_pemilik_sumber=(u or "").lower() == ((v.get("authorMeta") or {}).get("name") or "").lower(),
            author_followers=m.get("fans"), author_following=m.get("following"), author_n_post=m.get("video"),
            author_dibuat=None, author_verified=bool(m.get("verified")), author_private=bool(m.get("privateAccount")),
            author_bio_kosong=not (m.get("signature") or "").strip() if m else None,
            author_foto_default=None, author_bot_flag=False, lang=None))
    return pd.DataFrame(rows)


def main():
    semua = []
    for nama, f in (("x", x), ("instagram", instagram), ("youtube", youtube), ("tiktok", tiktok)):
        df = f()
        df = df[KOLOM + ["lang"]]
        df.to_csv(OUT / f"{nama}.csv", index=False, encoding="utf-8-sig")
        print(f"{nama:10} {len(df):5} baris, {df.author_hash.nunique():5} akun, profil terisi "
              f"{df.author_followers.notna().mean():.0%}")
        semua.append(df)
    g = pd.concat(semua, ignore_index=True)
    g.to_csv(OUT / "gabungan.csv", index=False, encoding="utf-8-sig")
    print("gabungan", len(g))


if __name__ == "__main__":
    main()
