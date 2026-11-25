"""Helper Apify. Token dibaca dari NLP/.env.

Ada 8 akun: APIFY_API, APIFY_API2 ... APIFY_API8. `pick_key(butuh_usd)` memilih akun pertama
yang kreditnya masih cukup, jadi scraping tidak berhenti di tengah kalau akun utama habis.
"""
import os
import time

import requests
from dotenv import find_dotenv, load_dotenv

BASE = "https://api.apify.com/v2"
KEYS = [f"APIFY_API{i}" if i > 1 else "APIFY_API" for i in range(1, 9)]
_aktif = KEYS[0]


def _token(name):
    load_dotenv(find_dotenv(usecwd=True))
    # di .env ada spasi sebelum "=", jadi nama variabelnya bisa ikut berakhiran spasi
    return (os.environ.get(name) or os.environ.get(name + " ") or "").strip()


def _headers(name=None):
    return {"Authorization": "Bearer " + _token(name or _aktif)}


def use_key(name):
    global _aktif
    _aktif = name


def credit_left(name=None):
    l = requests.get(f"{BASE}/users/me/limits", headers=_headers(name)).json()["data"]
    return l["limits"]["maxMonthlyUsageUsd"] - l["current"]["monthlyUsageUsd"]


def pick_key(butuh_usd):
    """Pakai akun pertama yang sisa kreditnya >= butuh_usd. Kembalikan nama akun yang dipakai."""
    for k in KEYS:
        if _token(k) and credit_left(k) >= butuh_usd:
            use_key(k)
            return k
    raise RuntimeError(f"Tidak ada akun Apify dengan kredit >= ${butuh_usd:.2f}")


def run_actor(actor, run_input, timeout_s=1800, max_charge_usd=None, key=None, retry=4):
    """Jalankan actor, tunggu selesai, kembalikan (items, status, biaya_usd).

    `key` memilih token tertentu (tiap platform pakai token sendiri supaya tidak kena batas run bersamaan).
    Kalau ditolak karena batas run bersamaan, tunggu lalu coba lagi.
    """
    hd = _headers(key)
    params = {"maxTotalChargeUsd": max_charge_usd} if max_charge_usd else {}
    for i in range(retry + 1):
        r = requests.post(f"{BASE}/acts/{actor}/runs", headers=hd, json=run_input, params=params)
        if r.status_code < 400:
            break
        if "concurrent-runs-limit" in r.text and i < retry:
            time.sleep(30 * (i + 1))
            continue
        raise RuntimeError(r.text[:500])
    run = r.json()["data"]
    t0 = time.time()
    while run["status"] in ("READY", "RUNNING") and time.time() - t0 < timeout_s:
        time.sleep(10)
        run = requests.get(f"{BASE}/actor-runs/{run['id']}", headers=hd).json()["data"]
    items = requests.get(f"{BASE}/datasets/{run['defaultDatasetId']}/items",
                         headers=hd, params={"clean": "true", "format": "json"}).json()
    return items, run["status"], run.get("usageTotalUsd", 0)
