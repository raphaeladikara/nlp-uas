"""Filter sampel kontrol YouTube (komentar terbaru) dengan aturan yang sama seperti notebooks/01_filter_data.ipynb.

Sengaja dibuat terpisah dari notebook: menjalankan ulang notebook akan menggeser sampel acak yang sudah
dilabeli. Script ini hanya menambah satu set baru dan tidak menyentuh file lain di data/03_filtered/.

Input : data/01_raw/yt_videos.json, yt_comments_kontrol.json, yt_channels_kontrol.json
        data/02_csv/youtube.csv (untuk cek duplikat dan hitung teks per akun lintas kedua sampel)
Output: data/03_filtered/kontrol_yt_untuk_label.csv  (maks PER_VIDEO komentar per video, acak)
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scraping"))
from to_csv import bersih_konteks, h  # noqa: E402

RAW, CSV, OUT = ROOT / "data" / "01_raw", ROOT / "data" / "02_csv", ROOT / "data" / "03_filtered"
PER_VIDEO = 25
SPAM = re.compile(r"\b(?:slot|gacor|maxwin|jackpot|scatter|depo|wd\b|rtp|cek bio|link (?:di )?bio|open (?:order|po)|"
                  r"giveaway|pinjol|dana kaget|follow back|f4f|promo code|kode promo|jual(?:an)? akun)\b", re.I)


def normalisasi(t):
    t = re.sub(r"https?://\S+|www\.\S+", " ", str(t))
    t = re.sub(r"@[\w.]+", "@user", t)
    return re.sub(r"\s+", " ", t).strip()


def kunci(t):
    return " ".join(re.sub(r"[^a-z0-9 ]", "", t.lower().replace("@user", "")).split())


def main():
    vids = {v["videoId"]: v for v in json.loads((RAW / "yt_videos.json").read_text(encoding="utf-8"))}
    ch = {c["id"]: c for c in json.loads((RAW / "yt_channels_kontrol.json").read_text(encoding="utf-8"))}
    rows = []
    for c in json.loads((RAW / "yt_comments_kontrol.json").read_text(encoding="utf-8")):
        v = vids[c["videoId"]]
        cid = (c.get("authorChannelId") or {}).get("value")
        sn = ch.get(cid, {}).get("snippet", {})
        rows.append(dict(
            id="YT_" + c["commentId"], platform="youtube", jalur="A", sumber_id=c["videoId"],
            sumber_url="https://www.youtube.com/watch?v=" + c["videoId"],
            konteks=bersih_konteks(f"Judul video {v['channelTitle']}: {v['title']}"), is_reply=False,
            created_at=c["publishedAt"], text_raw=c.get("textOriginal") or "", like_count=c.get("likeCount") or 0,
            author_hash=h(cid), is_pemilik=cid == v.get("channelId"), author_dibuat=(sn.get("publishedAt") or "")[:10] or None))
    df = pd.DataFrame(rows)
    corong = {"0. mentah": len(df)}
    df["created_at"] = pd.to_datetime(df.created_at, utc=True).dt.tz_convert("Asia/Jakarta")
    df["tanggal"] = df.created_at.dt.date

    df = df[(df.created_at >= "2026-10-22") & (df.created_at < "2026-11-15")]
    corong["1. rentang tanggal"] = len(df)
    df["fase"] = pd.cut(df.created_at.dt.tz_localize(None),
                        bins=pd.to_datetime(["2026-10-22", "2026-10-29", "2026-11-03", "2026-11-15"]),
                        labels=["pra", "puncak", "pasca"], right=False).astype(str)
    df = df[~df.is_pemilik]
    corong["2. pemilik unggahan"] = len(df)

    df["text"] = df.text_raw.map(normalisasi)
    inti = df.text.str.replace("@user", " ", regex=False)
    df = df[inti.str.contains(r"[A-Za-z]{2,}|\d+[A-Za-z]") & (inti.str.count(r"[A-Za-z0-9]") >= 3)]
    corong["3. tanpa isi"] = len(df)
    df = df[~df.text.str.contains(SPAM)]
    corong["4. spam"] = len(df)

    # duplikat: teks sama di dalam kontrol, atau sudah ada di sampel teratas
    lama = pd.read_csv(CSV / "youtube.csv", dtype=str)
    lama["kunci"] = lama.text_raw.fillna("").map(normalisasi).map(kunci)
    df["kunci"] = df.text.map(kunci)
    df["n_kata"] = df.kunci.str.split().str.len()
    gabung = pd.concat([lama[["kunci", "author_hash"]], df[["kunci", "author_hash"]]])
    df["n_akun_teks_mirip"] = df.kunci.map(gabung.groupby("kunci").author_hash.nunique())
    dup = df.duplicated(["kunci", "author_hash"]) | (df.n_kata.ge(5) & df.duplicated("kunci"))
    dup |= df.n_kata.ge(5) & df.kunci.isin(set(lama.kunci))
    df = df[~dup]
    corong["5. duplikat"] = len(df)

    # skor buzzer versi YouTube (profil penonton tidak dipakai, sama seperti notebook)
    df["umur_akun_hari"] = (df.created_at.dt.tz_localize(None) - pd.to_datetime(df.author_dibuat)).dt.days
    df["n_teks_akun"] = df.author_hash.map(gabung.author_hash.value_counts())
    umur = df.umur_akun_hari
    skor = (np.where(umur < 30, 2, 0) + np.where((umur >= 30) & (umur < 90), 2, 0)
            + np.where((umur >= 90) & (umur < 180), 1, 0)
            + np.where(df.n_teks_akun >= 6, 2, np.where(df.n_teks_akun >= 3, 1, 0))
            + np.where((df.n_akun_teks_mirip == 2) & (df.n_kata >= 5), 2, 0)
            + np.where(df.text.str.count(r"#\w+") >= 3, 1, 0))
    keras = df.n_kata.ge(5) & df.n_akun_teks_mirip.ge(3)
    df["skor_buzzer"] = skor
    df["status_buzzer"] = np.select([keras, skor >= 4, skor >= 2], ["keras", "skor_tinggi", "batas"], "lolos")
    df = df[~df.status_buzzer.isin(["keras", "skor_tinggi"])]
    corong["6. buzzer"] = len(df)

    df = df.sample(frac=1, random_state=42).groupby("sumber_id").head(PER_VIDEO)
    corong["7. sampel (maks %d/video)" % PER_VIDEO] = len(df)
    df["sampel"] = "terbaru"
    kolom = ["id", "platform", "jalur", "fase", "tanggal", "created_at", "sumber_id", "sumber_url", "konteks", "text",
             "text_raw", "is_reply", "like_count", "author_hash", "skor_buzzer", "status_buzzer", "n_teks_akun",
             "n_akun_teks_mirip", "sampel"]
    df[kolom].sort_values("created_at").to_csv(OUT / "kontrol_yt_untuk_label.csv", index=False, encoding="utf-8-sig")
    for k, v in corong.items():
        print(f"{k:28} {v}")
    print("per fase:", df.fase.value_counts().to_dict())


if __name__ == "__main__":
    main()
