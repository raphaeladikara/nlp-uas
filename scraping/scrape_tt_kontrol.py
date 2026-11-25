"""Sampel kontrol TikTok: komentar DI LUAR jajaran teratas dari 14 video yang sama dengan scrape_tt.py.

Actor clockworks/tiktok-comments-scraper tidak punya opsi urut terbaru, jadi caranya: ambil lebih dalam
(PER_VIDEO komentar per video, urutan bawaan TikTok yang condong ke komentar populer), lalu buang komentar
yang sudah ada di tt_comments.json (60 teratas). Sisanya adalah komentar yang tidak masuk jajaran teratas.
Kalau persentase negatifnya jauh lebih rendah dari sampel teratas, berarti bias like memang ada.

Token: APIFY_API8. Output: data/01_raw/tt_comments_kontrol.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import apify_utils as au  # noqa: E402

KEY = "APIFY_API8"
RAW = Path(__file__).resolve().parents[1] / "data" / "01_raw"
PER_VIDEO = 110


def main():
    lama = json.loads((RAW / "tt_comments.json").read_text(encoding="utf-8"))
    sudah = {str(c.get("cid")) for c in lama["comments"]}
    urls = [v["webVideoUrl"] for v in lama["videos"]]
    com, st, c = au.run_actor("clockworks~tiktok-comments-scraper",
                              {"postURLs": urls, "commentsPerPost": PER_VIDEO, "maxRepliesPerComment": 0},
                              max_charge_usd=2.0, key=KEY, timeout_s=3600)
    print(f"diambil: {len(com)} (${c:.3f}, {st})", flush=True)
    posisi = {}
    baru = []
    for x in com:
        u = x.get("videoWebUrl") or x.get("submittedVideoUrl")
        posisi[u] = posisi.get(u, 0) + 1
        if str(x.get("cid")) in sudah or x.get("repliesToId"):
            continue
        baru.append(dict(x, _posisi=posisi[u], _sampel="luar_teratas"))
    (RAW / "tt_comments_kontrol.json").write_text(
        json.dumps({"videos": lama["videos"], "comments": baru}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(baru)} komentar baru (di luar sampel teratas)", flush=True)


if __name__ == "__main__":
    main()
