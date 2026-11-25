"""Filter sampel kontrol TikTok (komentar di luar jajaran teratas), aturan sama seperti notebook 01.

Profil akun TikTok tidak di-scrape ulang untuk kontrol, jadi sinyal profil di skor buzzer tidak dipakai.
Sinyal perilaku (teks mirip lintas akun, banyak teks per akun, hashtag) tetap dipakai.

Input : data/01_raw/tt_comments_kontrol.json, data/02_csv/tiktok.csv
Output: data/03_filtered/kontrol_tt_untuk_label.csv  (maks PER_VIDEO komentar acak per video)
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scraping"))
sys.path.insert(0, str(ROOT / "filtering"))
from filter_kontrol_yt import SPAM, kunci, normalisasi  # noqa: E402
from to_csv import bersih_konteks, h  # noqa: E402

RAW, CSV, OUT = ROOT / "data" / "01_raw", ROOT / "data" / "02_csv", ROOT / "data" / "03_filtered"
PER_VIDEO = 30


def main():
    d = json.loads((RAW / "tt_comments_kontrol.json").read_text(encoding="utf-8"))
    vids = {v["webVideoUrl"]: v for v in d["videos"]}
    rows = []
    for c in d["comments"]:
        if not c.get("text"):
            continue
        url = c.get("videoWebUrl") or c.get("submittedVideoUrl")
        v = vids.get(url, {})
        u = c.get("uniqueId")
        rows.append(dict(
            id="TT_" + str(c["cid"]), platform="tiktok", jalur="A", sumber_id=str(v.get("id") or url), sumber_url=url,
            konteks=bersih_konteks(f"Deskripsi video @{(v.get('authorMeta') or {}).get('name')}: {v.get('text') or ''}"),
            is_reply=False, created_at=datetime.fromisoformat(c["createTimeISO"].replace("Z", "+00:00")),
            text_raw=c["text"], like_count=c.get("diggCount") or 0, posisi=c.get("_posisi"), author_hash=h(u),
            is_pemilik=(u or "").lower() == ((v.get("authorMeta") or {}).get("name") or "").lower()))
    df = pd.DataFrame(rows).drop_duplicates("id")
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

    lama = pd.read_csv(CSV / "tiktok.csv", dtype=str)
    lama["kunci"] = lama.text_raw.fillna("").map(normalisasi).map(kunci)
    df["kunci"] = df.text.map(kunci)
    df["n_kata"] = df.kunci.str.split().str.len()
    gabung = pd.concat([lama[["kunci", "author_hash"]], df[["kunci", "author_hash"]]])
    df["n_akun_teks_mirip"] = df.kunci.map(gabung.groupby("kunci").author_hash.nunique())
    dup = df.duplicated(["kunci", "author_hash"]) | (df.n_kata.ge(5) & df.duplicated("kunci"))
    dup |= df.n_kata.ge(5) & df.kunci.isin(set(lama.kunci))
    df = df[~dup]
    corong["5. duplikat"] = len(df)

    df["n_teks_akun"] = df.author_hash.map(gabung.author_hash.value_counts())
    skor = (np.where(df.n_teks_akun >= 6, 2, np.where(df.n_teks_akun >= 3, 1, 0))
            + np.where((df.n_akun_teks_mirip == 2) & (df.n_kata >= 5), 2, 0)
            + np.where(df.text.str.count(r"#\w+") >= 3, 1, 0))
    keras = df.n_kata.ge(5) & df.n_akun_teks_mirip.ge(3)
    df["skor_buzzer"] = skor
    df["status_buzzer"] = np.select([keras, skor >= 4, skor >= 2], ["keras", "skor_tinggi", "batas"], "lolos")
    df = df[~df.status_buzzer.isin(["keras", "skor_tinggi"])]
    corong["6. buzzer"] = len(df)

    df = df.sample(frac=1, random_state=42).groupby("sumber_id").head(PER_VIDEO)
    corong[f"7. sampel (maks {PER_VIDEO}/video)"] = len(df)
    df["sampel"] = "luar_teratas"
    kolom = ["id", "platform", "jalur", "fase", "tanggal", "created_at", "sumber_id", "sumber_url", "konteks", "text",
             "text_raw", "is_reply", "like_count", "posisi", "author_hash", "skor_buzzer", "status_buzzer",
             "n_teks_akun", "n_akun_teks_mirip", "sampel"]
    df[kolom].sort_values("created_at").to_csv(OUT / "kontrol_tt_untuk_label.csv", index=False, encoding="utf-8-sig")
    for k, v in corong.items():
        print(f"{k:28} {v}")
    print("video:", df.sumber_id.nunique(), "| median like:", df.like_count.median())


if __name__ == "__main__":
    main()
