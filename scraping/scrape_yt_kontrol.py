"""Sampel kontrol YouTube: komentar TERBARU (order=time) dari 20 video yang sama dengan scrape_yt.py.

Kenapa perlu: scrape_yt.py mengambil komentar order=relevance, yang condong ke komentar paling banyak
disukai. Komentar populer di video yang judulnya soal skandal cenderung paling keras, jadi persentase
negatif bisa terlihat lebih tinggi dari aslinya. Sampel terbaru tidak diurutkan berdasarkan like, jadi
selisih sentimen antara kedua sampel ini adalah ukuran langsung seberapa besar bias "komentar teratas".

Komentar yang sudah ada di yt_comments.json dilewati supaya kedua sampel tidak tumpang tindih.
Output: data/01_raw/yt_comments_kontrol.json, yt_channels_kontrol.json
"""
import json

from scrape_yt import RAW, get

PER_VIDEO = 100


def main():
    vids = json.loads((RAW / "yt_videos.json").read_text(encoding="utf-8"))
    lama = {c["commentId"] for c in json.loads((RAW / "yt_comments.json").read_text(encoding="utf-8"))}
    com = []
    for v in vids:
        try:
            r = get("commentThreads", part="snippet", videoId=v["videoId"], maxResults=PER_VIDEO, order="time",
                    textFormat="plainText")
        except RuntimeError as e:
            print("lewati", v["videoId"], e)
            continue
        baru = [dict(it["snippet"]["topLevelComment"]["snippet"], commentId=it["id"],
                     totalReplyCount=it["snippet"]["totalReplyCount"], _sampel="terbaru")
                for it in r["items"] if it["id"] not in lama]
        com += baru
        print(f"{v['channelTitle'][:20]:20} -> {len(r['items'])} diambil, {len(baru)} baru | {v['title'][:50]}",
              flush=True)
    (RAW / "yt_comments_kontrol.json").write_text(json.dumps(com, ensure_ascii=False), encoding="utf-8")

    chs = list({c["authorChannelId"]["value"] for c in com if c.get("authorChannelId")})
    prof = []
    for i in range(0, len(chs), 50):
        prof += get("channels", part="snippet,statistics", id=",".join(chs[i:i + 50]))["items"]
    (RAW / "yt_channels_kontrol.json").write_text(json.dumps(prof, ensure_ascii=False), encoding="utf-8")
    print(f"{len(com)} komentar kontrol, {len(prof)} channel", flush=True)


if __name__ == "__main__":
    main()
