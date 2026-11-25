"""Buat halaman HTML untuk review 3 orang pelabelan terarah.

Pakai : python labeling/terarah/buat_html_terarah.py
Input : labeling/terarah/review/perlu_review_3_orang.csv
Output: labeling/terarah/review/review_terarah.html

Cara pakai halaman: buka di browser, pilih nama sendiri, beri label pada kartu yang ditugaskan, lalu klik
"Unduh isian saya". Hasilnya isian_terarah_<Nama>.csv, taruh di labeling/terarah/review/. Setelah kelima berkas
terkumpul, jalankan gabung_terarah.py --final (berkas isian digabung otomatis).
Isian tersimpan di browser, jadi halaman boleh ditutup lalu dibuka lagi di browser yang sama.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "labeling" / "terarah" / "review"
TIM = ["Adit", "Exsa", "Mikael", "Raphael", "Yasyfa"]


def main():
    r = pd.read_csv(R / "perlu_review_3_orang.csv", sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    kartu = []
    for x in r.itertuples():
        kartu.append(dict(id=x.id, platform=x.platform, judul=x.judul, text=x.text, url=x.sumber_url,
                          ai=[x.label_opus, x.label_sonnet, x.label_haiku], cek_buzzer=x.cek_buzzer == "ya",
                          reviewer={getattr(x, f"reviewer_{k}"): k for k in (1, 2, 3)}))
    data = json.dumps(dict(tim=TIM, kartu=kartu), ensure_ascii=False)
    html = TEMPLATE.replace("/*DATA*/", data.replace("</", "<\\/"))
    (R / "review_terarah.html").write_text(html, encoding="utf-8")
    beban = {n: sum(n in c["reviewer"] for c in kartu) for n in TIM}
    print(f"{len(kartu)} kartu, beban: {beban}")


TEMPLATE = r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Review Pelabelan Terarah</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1d1d1b;--mute:#6b6a66;--line:#e3e1db;--acc:#2f5bd3;
--neg:#c4392f;--net:#6b6a66;--pos:#21844a;--tr:#9a6b12;--ok:#21844a;--warn:#b5560b}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#1f1f1d;--ink:#ecebe7;--mute:#9c9a94;--line:#33322f;
--acc:#7d9bff;--neg:#ef6d62;--net:#a9a7a1;--pos:#4fc282;--tr:#d9a23d;--ok:#4fc282;--warn:#f0954a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px}
.wrap{max-width:860px;margin:0 auto}
h1{font-size:18px;margin:0 0 8px}
.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin:6px 0 10px}
.bar i{display:block;height:100%;background:var(--ok);width:0;transition:width .2s}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.tab{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:6px 12px;
cursor:pointer;font:inherit;font-size:14px}
.tab.on{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.spacer{flex:1}
.btn{border:0;background:var(--acc);color:#fff;border-radius:8px;padding:8px 14px;font:inherit;font-weight:600;cursor:pointer}
.btn:disabled{opacity:.4;cursor:default}
label.chk{font-size:13px;color:var(--mute);display:flex;gap:6px;align-items:center;cursor:pointer}
main{padding:14px 16px 80px}
.help{color:var(--mute);font-size:14px;margin:0 0 14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:12px}
.card.done{opacity:.55}
.meta{font-size:12px;color:var(--mute);display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px;align-items:center}
.meta a{color:var(--acc)}
.badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;background:var(--line);color:var(--ink)}
.badge.ok{background:var(--ok);color:#fff}.badge.warn{background:var(--warn);color:#fff}
details{font-size:13px;color:var(--mute);margin-bottom:6px}
.teks{font-size:16px;margin:4px 0 12px;white-space:pre-wrap;word-break:break-word}
.q{font-size:13px;color:var(--mute);margin:8px 0 4px}
.pick{display:flex;gap:6px;flex-wrap:wrap}
.pick button{font:inherit;font-size:13px;padding:6px 12px;border-radius:8px;border:1.5px solid var(--line);
background:transparent;color:var(--ink);cursor:pointer}
.pick button[data-v=negatif].on{background:var(--neg);border-color:var(--neg);color:#fff}
.pick button[data-v=netral].on{background:var(--net);border-color:var(--net);color:#fff}
.pick button[data-v=positif].on{background:var(--pos);border-color:var(--pos);color:#fff}
.pick button[data-v=tidak_relevan].on{background:var(--tr);border-color:var(--tr);color:#fff}
.pick button[data-v=ya].on{background:var(--neg);border-color:var(--neg);color:#fff}
.pick button[data-v=tidak].on{background:var(--pos);border-color:var(--pos);color:#fff}
.empty{text-align:center;color:var(--mute);padding:40px 0}
.pilih{max-width:420px;margin:60px auto;text-align:center}
.pilih .row{justify-content:center;margin-top:14px}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>Review Pelabelan Terarah</h1>
  <div class="row" style="font-size:13px;color:var(--mute)"><span id="prog"></span></div>
  <div class="bar"><i id="barfill"></i></div>
  <div class="row">
    <span style="font-size:14px">Reviewer:</span><span id="namaTabs" class="row"></span>
    <span class="spacer"></span>
    <label class="chk"><input type="checkbox" id="sembunyi"> sembunyikan yang selesai</label>
    <button class="btn" id="unduh" disabled>Unduh isian saya</button>
  </div>
</div></header>
<main><div class="wrap">
  <p class="help">Beri label sentimen <b>terhadap Raffi Ahmad</b> sesuai <code>labeling/codebook.md</code>. Nilai sendiri dulu,
  jangan berdiskusi. Isian tersimpan otomatis di browser ini. Kalau sudah selesai, klik <b>Unduh isian saya</b> lalu kirim
  berkas <code>isian_terarah_&lt;Nama&gt;.csv</code> ke folder <code>labeling/terarah/review/</code>.</p>
  <div id="list"></div>
</div></main>
<script>
const DATA = /*DATA*/;
const LB = {negatif:"Negatif", netral:"Netral", positif:"Positif", tidak_relevan:"Tidak relevan"};
const KEY = "reviewTerarah.v1";
let S = {nama:"", isi:{}};      // isi[nama][id] = {label, buzzer}
try { S = JSON.parse(localStorage.getItem(KEY)) || S; } catch(e) {}
const simpan = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch(e) {} };
const isian = (id) => ((S.isi[S.nama] = S.isi[S.nama] || {})[id] = S.isi[S.nama][id] || {label:"", buzzer:""});
const milik = () => DATA.kartu.filter(c => S.nama in c.reviewer);
const selesai = c => { const u = (S.isi[S.nama] || {})[c.id] || {}; return !!u.label && (!c.cek_buzzer || !!u.buzzer); };

function el(tag, attrs, ...kids){
  const e = document.createElement(tag);
  for (const k in attrs || {}) { if (k === "class") e.className = attrs[k]; else if (k.startsWith("on")) e[k] = attrs[k]; else e.setAttribute(k, attrs[k]); }
  kids.flat().forEach(k => k != null && e.append(k));
  return e;
}
function picker(opts, val, onPick){
  return el("div", {class:"pick"}, opts.map(([v, txt]) =>
    el("button", {"data-v":v, class: val === v ? "on" : "", type:"button", onclick:() => onPick(v)}, txt)));
}
function kartuEl(c, i){
  const u = (S.isi[S.nama] || {})[c.id] || {}, done = selesai(c);
  const kids = [el("div", {class:"meta"}, el("b", {}, "#" + (i + 1)), el("span", {class:"badge"}, c.platform),
    c.url ? el("a", {href:c.url, target:"_blank", rel:"noopener"}, "buka sumber") : null,
    done ? el("span", {class:"badge ok"}, "selesai") : null)];
  if (c.judul) kids.push(el("details", {}, el("summary", {}, "judul / konteks"), c.judul));
  kids.push(el("div", {class:"teks"}, c.text));
  kids.push(el("div", {class:"q"}, "Sentimen terhadap Raffi:"));
  kids.push(picker(Object.entries(LB), u.label || "", v => { const x = isian(c.id); x.label = x.label === v ? "" : v; simpan(); render(); }));
  if (c.cek_buzzer) {
    kids.push(el("div", {class:"q"}, el("span", {class:"badge warn"}, "cek buzzer"), " Akun ini buzzer? (buka sumber untuk melihat profilnya)"));
    kids.push(picker([["ya","Ya, buzzer"],["tidak","Bukan buzzer"]], u.buzzer || "", v => { const x = isian(c.id); x.buzzer = x.buzzer === v ? "" : v; simpan(); render(); }));
  }
  kids.push(el("details", {}, el("summary", {}, "suara 3 AI (lihat setelah memilih)"), c.ai.map(a => LB[a] || a).join(" · ")));
  return el("div", {class:"card" + (done ? " done" : "")}, kids);
}
function render(){
  const tabs = document.getElementById("namaTabs");
  tabs.replaceChildren(...DATA.tim.map(n => el("button", {class:"tab" + (n === S.nama ? " on" : ""), type:"button",
    onclick:() => { S.nama = n; simpan(); window.scrollTo(0,0); render(); }}, n)));
  const list = document.getElementById("list"), y = window.scrollY;
  document.getElementById("unduh").disabled = !S.nama;
  if (!S.nama) {
    list.replaceChildren(el("div", {class:"empty"}, "Pilih nama kamu di atas untuk melihat kartu yang ditugaskan."));
    document.getElementById("prog").textContent = ""; document.getElementById("barfill").style.width = "0";
    return;
  }
  const M = milik(), n = M.filter(selesai).length;
  const hide = document.getElementById("sembunyi").checked;
  const L = M.map((c, i) => [c, i]).filter(([c]) => !(hide && selesai(c)));
  list.replaceChildren(...(L.length ? L.map(([c, i]) => kartuEl(c, i)) : [el("div", {class:"empty"}, "Semua kartu sudah selesai.")]));
  document.getElementById("prog").textContent = `${S.nama}: ${n} dari ${M.length} kartu selesai` + (n === M.length ? " · siap diunduh" : "");
  document.getElementById("barfill").style.width = (M.length ? n / M.length * 100 : 0) + "%";
  window.scrollTo(0, y);
}
document.getElementById("sembunyi").onchange = render;
document.getElementById("unduh").onclick = () => {
  const M = milik(), kurang = M.length - M.filter(selesai).length;
  if (kurang && !confirm(`Masih ada ${kurang} kartu yang belum lengkap. Tetap unduh?`)) return;
  const q = s => '"' + String(s ?? "").replace(/"/g, '""') + '"';
  const rows = [["id","slot","reviewer","label","buzzer"]];
  M.forEach(c => { const u = (S.isi[S.nama] || {})[c.id] || {}; rows.push([c.id, c.reviewer[S.nama], S.nama, u.label || "", u.buzzer || ""]); });
  const blob = new Blob(["﻿" + rows.map(r => r.map(q).join(",")).join("\r\n")], {type:"text/csv;charset=utf-8"});
  const a = el("a", {href:URL.createObjectURL(blob), download:`isian_terarah_${S.nama}.csv`});
  document.body.append(a); a.click(); a.remove();
};
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
