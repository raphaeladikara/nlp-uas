"""Scraping komentar YouTube tentang Raffi Ahmad lewat YouTube Data API v3 (gratis, YOUTUBE_API_KEY).

1. Cari video (beberapa query, terbit 22 Okt - 14 Nov 2026), judulnya harus menyebut Raffi/RANS/mahasewa.
2. Ambil statistik video, pilih 20 video dengan komentar terbanyak (maks 3 per channel).
3. Ambil sampai 100 komentar teratas (order=relevance) per video.
4. Ambil profil channel tiap pemberi komentar (tanggal dibuat, subscriber, jumlah video) untuk filter buzzer.
Output: data/01_raw/yt_videos.json, yt_comments.json, yt_channels.json
"""
import json
import os
import re
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))
KEY = (os.environ.get("YOUTUBE_API_KEY") or "").strip()
API = "https://www.googleapis.com/youtube/v3"
RAW = Path(__file__).resolve().parents[1] / "data" / "01_raw"
QUERIES = ["raffi ahmad mahasiswa bayaran", "raffi ahmad mahasewa", "raffi ahmad bundaran hi deklarasi",
           "raffi ahmad klarifikasi", "raffi ahmad 14 miliar icw", "boikot rans carnival", "raffi ahmad didemo"]
RELEVAN = re.compile(r"raff?i|\brans\b|mahasewa|mahasiswa bayaran|mahasiswa settingan", re.I)


def get(path, **params):
    r = requests.get(f"{API}/{path}", params=dict(params, key=KEY)).json()
    if "error" in r:
        raise RuntimeError(r["error"].get("message"))
    return r


def main():
    vids = {}
    for q in QUERIES:
        r = get("search", part="snippet", q=q, type="video", maxResults=25, regionCode="ID",
                relevanceLanguage="id", publishedAfter="2026-10-22T00:00:00Z", publishedBefore="2026-11-15T00:00:00Z")
        for it in r["items"]:
            if RELEVAN.search(it["snippet"]["title"]):
                vids[it["id"]["videoId"]] = dict(it["snippet"], videoId=it["id"]["videoId"], _query=q)
        print(f"{q!r:40} -> {len(r['items'])} video", flush=True)
    ids = list(vids)
    for i in range(0, len(ids), 50):
        for it in get("videos", part="statistics", id=",".join(ids[i:i + 50]))["items"]:
            vids[it["id"]]["statistics"] = it["statistics"]
    per_ch, pilih = {}, []
    for v in sorted(vids.values(), key=lambda v: -int(v.get("statistics", {}).get("commentCount", 0))):
        ch = v["channelTitle"]
        if per_ch.get(ch, 0) >= 3 or int(v.get("statistics", {}).get("commentCount", 0)) < 20:
            continue
        per_ch[ch] = per_ch.get(ch, 0) + 1
        pilih.append(v)
    pilih = pilih[:20]
    (RAW / "yt_videos.json").write_text(json.dumps(pilih, ensure_ascii=False), encoding="utf-8")

    com = []
    for v in pilih:
        try:
            r = get("commentThreads", part="snippet", videoId=v["videoId"], maxResults=100, order="relevance",
                    textFormat="plainText")
        except RuntimeError as e:
            print("lewati", v["videoId"], e)
            continue
        for it in r["items"]:
            s = it["snippet"]
            com.append(dict(s["topLevelComment"]["snippet"], commentId=it["id"], totalReplyCount=s["totalReplyCount"]))
        print(f"{v['channelTitle'][:20]:20} {v['publishedAt'][:10]} {v['statistics'].get('commentCount'):>6} "
              f"-> {len(r['items'])} | {v['title'][:60]}", flush=True)
    (RAW / "yt_comments.json").write_text(json.dumps(com, ensure_ascii=False), encoding="utf-8")

    chs = list({c["authorChannelId"]["value"] for c in com if c.get("authorChannelId")})
    prof = []
    for i in range(0, len(chs), 50):
        prof += get("channels", part="snippet,statistics", id=",".join(chs[i:i + 50]))["items"]
    (RAW / "yt_channels.json").write_text(json.dumps(prof, ensure_ascii=False), encoding="utf-8")
    print(f"{len(pilih)} video, {len(com)} komentar, {len(prof)} channel", flush=True)


if __name__ == "__main__":
    main()
