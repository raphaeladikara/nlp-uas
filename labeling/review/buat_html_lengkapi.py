"""Buat halaman HTML untuk menyelesaikan review 3 lapis: suara yang belum diisi, kartu seri yang perlu diskusi,
dan konfirmasi buzzer.

Pakai : python labeling/review/buat_html_lengkapi.py
Input : labeling/review/3lapis/hasil review 3 orang.csv, data/04_labeled/review_manusia.csv
Output: labeling/review/3lapis/lengkapi_3lapis.html  (buka di browser, klik-klik, lalu "Unduh hasil")
Hasil unduhan (isian_lengkapi_3lapis.csv) ditaruh di labeling/review/3lapis/, lalu jalankan
gabung_review_3lapis.py.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "labeling" / "review" / "3lapis"
TIM = ["Adit", "Exsa", "Mikael", "Raphael", "Yasyfa"]
LABEL = ["negatif", "netral", "positif", "tidak_relevan"]
K = (1, 2, 3)


def main():
    r = pd.read_csv(D / "hasil review 3 orang.csv", sep=";", dtype=str, encoding="utf-8-sig").fillna("")
    for k in K:
        r.loc[~r[f"label_{k}"].isin(LABEL), f"label_{k}"] = ""
    t1 = pd.read_csv(ROOT / "data" / "04_labeled" / "review_manusia.csv", dtype=str).fillna("").set_index("id")

    beban = {n: 0 for n in TIM}
    kartu = []
    for x in r.itertuples():
        slots = [dict(slot=k, reviewer=getattr(x, f"reviewer_{k}"), label=getattr(x, f"label_{k}")) for k in K]
        isi = [s for s in slots if s["label"]]
        kosong = [s for s in slots if not s["label"]]
        seri = len(isi) == 3 and len({s["label"] for s in isi}) == 3
        cek_buzzer = x.buzzer_1 == "ya"
        if not kosong and not seri and not cek_buzzer:
            continue
        # usulan nama untuk slot kosong: orang yang memang ditugasi (kalau namanya ada), kalau tidak, yang paling
        # sedikit bebannya dan belum menilai kartu ini
        dipakai = {s["reviewer"] for s in slots if s["reviewer"]}
        for s in kosong:
            if not s["reviewer"]:
                calon = sorted((n for n in TIM if n not in dipakai), key=lambda n: (beban[n], TIM.index(n)))
                s["reviewer"] = calon[0]
                dipakai.add(calon[0])
            s["usulan"] = True
            beban[s["reviewer"]] += 1
        bz = t1.at[x.id, "buzzer_review"] if x.id in t1.index else ""
        kartu.append(dict(id=x.id, kelompok=x.kelompok, platform=x.platform, judul=x.judul, text=x.text,
                          url=x.sumber_url, slots=slots, cek_buzzer=cek_buzzer, buzzer_t1=bz,
                          label_t1=t1.at[x.id, "label_review"] if x.id in t1.index else ""))
    data = json.dumps(dict(tim=TIM, kartu=kartu), ensure_ascii=False)
    html = TEMPLATE.replace("/*DATA*/", data.replace("</", "<\\/"))
    (D / "lengkapi_3lapis.html").write_text(html, encoding="utf-8")
    n_slot = sum(1 for c in kartu for s in c["slots"] if not s["label"])
    print(f"{len(kartu)} kartu, {n_slot} suara kosong, beban usulan: {beban}")


TEMPLATE = r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lengkapi Review 3 Lapis</title>
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
.tab b{font-weight:600}
.spacer{flex:1}
.btn{border:0;background:var(--acc);color:#fff;border-radius:8px;padding:8px 14px;font:inherit;font-weight:600;cursor:pointer}
.btn.ghost{background:transparent;color:var(--mute);border:1px solid var(--line);font-weight:400}
label.chk{font-size:13px;color:var(--mute);display:flex;gap:6px;align-items:center;cursor:pointer}
main{padding:14px 16px 80px}
.help{color:var(--mute);font-size:14px;margin:0 0 14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px;margin-bottom:12px}
.card.done{opacity:.55}
.meta{font-size:12px;color:var(--mute);display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px}
.meta a{color:var(--acc)}
.badge{font-size:11px;font-weight:600;padding:2px 8px;border-radius:999px;background:var(--line);color:var(--ink)}
.badge.ok{background:var(--ok);color:#fff}.badge.warn{background:var(--warn);color:#fff}
details{font-size:13px;color:var(--mute);margin-bottom:6px}
.teks{font-size:16px;margin:4px 0 12px;white-space:pre-wrap;word-break:break-word}
.slot{display:grid;grid-template-columns:130px 1fr;gap:8px;align-items:center;padding:6px 0;border-top:1px dashed var(--line)}
.slot .who{font-size:13px;color:var(--mute)}
.slot select{font:inherit;font-size:13px;padding:3px 4px;border-radius:6px;border:1px solid var(--line);background:var(--card);color:var(--ink);max-width:120px}
.pick{display:flex;gap:6px;flex-wrap:wrap}
.pick button{font:inherit;font-size:13px;padding:5px 11px;border-radius:8px;border:1.5px solid var(--line);
background:transparent;color:var(--ink);cursor:pointer}
.pick button[data-v=negatif].on{background:var(--neg);border-color:var(--neg);color:#fff}
.pick button[data-v=netral].on{background:var(--net);border-color:var(--net);color:#fff}
.pick button[data-v=positif].on{background:var(--pos);border-color:var(--pos);color:#fff}
.pick button[data-v=tidak_relevan].on{background:var(--tr);border-color:var(--tr);color:#fff}
.pick button[data-v="1"].on{background:var(--neg);border-color:var(--neg);color:#fff}
.pick button[data-v="0"].on{background:var(--pos);border-color:var(--pos);color:#fff}
.fixed{font-size:13px;font-weight:600}
.fixed.negatif{color:var(--neg)}.fixed.netral{color:var(--net)}.fixed.positif{color:var(--pos)}.fixed.tidak_relevan{color:var(--tr)}
.diskusi{margin-top:10px;padding:10px;border-radius:8px;background:var(--bg)}
.diskusi .q{font-size:13px;font-weight:600;margin-bottom:6px}
.diskusi input{width:100%;margin-top:8px;font:inherit;font-size:13px;padding:6px 8px;border-radius:6px;border:1px solid var(--line);background:var(--card);color:var(--ink)}
.hasil{font-size:13px;margin-top:8px;color:var(--mute)}
.empty{text-align:center;color:var(--mute);padding:40px 0}
@media (max-width:560px){.slot{grid-template-columns:1fr}}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>Lengkapi Review 3 Lapis</h1>
  <div class="row" style="font-size:13px;color:var(--mute)"><span id="prog"></span></div>
  <div class="bar"><i id="barfill"></i></div>
  <div class="row">
    <button class="tab on" data-tab="suara">1. Isi suara <b id="n-suara"></b></button>
    <button class="tab" data-tab="diskusi">2. Diskusi seri <b id="n-diskusi"></b></button>
    <button class="tab" data-tab="buzzer">3. Cek buzzer <b id="n-buzzer"></b></button>
    <span class="spacer"></span>
    <label class="chk"><input type="checkbox" id="sembunyi"> sembunyikan yang selesai</label>
    <button class="btn" id="unduh">Unduh hasil</button>
  </div>
</div></header>
<main><div class="wrap">
  <p class="help" id="help"></p>
  <div id="list"></div>
</div></main>
<script>
const DATA = /*DATA*/;
const LB = {negatif:"Negatif", netral:"Netral", positif:"Positif", tidak_relevan:"Tidak relevan"};
const HELP = {
 suara:"Kartu yang suaranya belum 3. Untuk setiap baris kosong, pilih label yang diberikan orang tersebut (nama bisa diganti). Kalau setelah lengkap ketiganya beda, kartu otomatis pindah ke tab Diskusi.",
 diskusi:"Ketiga orang memilih label yang berbeda, jadi belum ada suara terbanyak. Diskusikan lalu pilih label akhir hasil diskusi. Catatan alasan boleh diisi singkat.",
 buzzer:"Kolom buzzer di berkas hasil tersalin sama di ketiga slot. Pilihan di bawah sudah diisi dari review tahap 1. Cukup cek; ganti kalau keputusan tim berbeda."
};
const KEY = "lengkapi3lapis.v1";
let S = {};                     // id -> {suara:{slot:{reviewer,label}}, diskusi:{label,catatan}, buzzer}
try { S = JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e) { S = {}; }
const simpan = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch(e) {} };
const st = id => (S[id] = S[id] || {suara:{}, diskusi:{}, buzzer:null});
let TAB = "suara";

function votes(c){
  return c.slots.map(s => {
    const u = (S[c.id] && S[c.id].suara[s.slot]) || {};
    return {slot:s.slot, reviewer:u.reviewer || s.reviewer, label:s.label || u.label || "", tetap:!!s.label};
  });
}
const perluIsi = c => c.slots.some(s => !s.label);
const isiLengkap = c => votes(c).every(v => v.label);
const seri = c => { const v = votes(c); return v.every(x => x.label) && new Set(v.map(x => x.label)).size === 3; };
const diskusiSelesai = c => !!(S[c.id] && S[c.id].diskusi.label);
const buzzerVal = c => (S[c.id] && S[c.id].buzzer != null) ? S[c.id].buzzer : c.buzzer_t1;
function mayoritas(c){
  if (seri(c)) return diskusiSelesai(c) ? S[c.id].diskusi.label + " (diskusi)" : "";
  const n = {}; votes(c).forEach(v => { if (v.label) n[v.label] = (n[v.label]||0) + 1; });
  const top = Object.entries(n).sort((a,b) => b[1]-a[1])[0];
  return top && top[1] >= 2 ? top[0] : "";
}
const listFor = t => DATA.kartu.filter(c => t === "suara" ? perluIsi(c) : t === "diskusi" ? seri(c) : c.cek_buzzer);
function selesai(c, t){
  if (t === "suara") return isiLengkap(c);
  if (t === "diskusi") return diskusiSelesai(c);
  return true;
}

function el(tag, attrs, ...kids){
  const e = document.createElement(tag);
  for (const k in attrs || {}) { if (k === "class") e.className = attrs[k]; else if (k.startsWith("on")) e[k] = attrs[k]; else e.setAttribute(k, attrs[k]); }
  kids.flat().forEach(k => k != null && e.append(k));
  return e;
}
function picker(opts, val, onPick){
  return el("div", {class:"pick"}, opts.map(([v, txt]) =>
    el("button", {"data-v":v, class: String(val) === String(v) ? "on" : "", type:"button", onclick:() => onPick(v)}, txt)));
}

function kartuEl(c){
  const t = TAB, done = selesai(c, t);
  const head = el("div", {class:"meta"},
    el("span", {class:"badge"}, c.platform), el("span", {class:"badge"}, c.kelompok === "jalur_b" ? "jalur B" : "utama"),
    el("span", {}, c.id), c.url ? el("a", {href:c.url, target:"_blank", rel:"noopener"}, "buka sumber") : null,
    done && t !== "buzzer" ? el("span", {class:"badge ok"}, "selesai") : null);
  const kids = [head];
  if (c.judul) kids.push(el("details", {}, el("summary", {}, "judul / konteks"), c.judul));
  kids.push(el("div", {class:"teks"}, c.text));

  if (t === "suara" || t === "diskusi") {
    votes(c).forEach(v => {
      let who, right;
      if (v.tetap) {
        who = el("span", {class:"who"}, (v.reviewer || "(tanpa nama)") + ` · orang ${v.slot}`);
        right = el("span", {class:"fixed " + v.label}, LB[v.label]);
      } else {
        const lain = votes(c).filter(x => x.slot !== v.slot).map(x => x.reviewer);
        const sel = el("select", {onchange:e => { const u = st(c.id); u.suara[v.slot] = {...(u.suara[v.slot]||{}), reviewer:e.target.value}; simpan(); render(); }},
          DATA.tim.map(n => { const o = el("option", {value:n}, n + (lain.includes(n) ? " (sudah menilai)" : "")); if (n === v.reviewer) o.selected = true; if (lain.includes(n)) o.disabled = true; return o; }));
        who = el("span", {class:"who"}, sel, ` · orang ${v.slot}`);
        right = t === "suara" ? picker(Object.entries(LB), v.label, val => {
          const u = st(c.id); u.suara[v.slot] = {reviewer:v.reviewer, label: v.label === val ? "" : val}; simpan(); render();
        }) : el("span", {class:"fixed " + v.label}, LB[v.label] || "-");
      }
      kids.push(el("div", {class:"slot"}, who, right));
    });
    if (seri(c)) {
      const d = st(c.id).diskusi;
      kids.push(el("div", {class:"diskusi"},
        el("div", {class:"q"}, "Ketiganya beda. Hasil diskusi:"),
        picker(Object.entries(LB), d.label || "", val => { const u = st(c.id); u.diskusi.label = u.diskusi.label === val ? "" : val; simpan(); render(); }),
        el("input", {placeholder:"catatan singkat (opsional)", value:d.catatan || "", onchange:e => { st(c.id).diskusi.catatan = e.target.value; simpan(); }})));
    }
    const m = mayoritas(c);
    kids.push(el("div", {class:"hasil"}, "Label akhir: ", m ? el("b", {}, LB[m.split(" ")[0]] + (m.includes("diskusi") ? " (hasil diskusi)" : "")) : "belum ada"));
  } else {
    const b = buzzerVal(c);
    kids.push(el("div", {class:"slot"}, el("span", {class:"who"}, "Akun ini buzzer?"),
      picker([["1","Ya, buzzer"],["0","Bukan buzzer"]], b, val => { st(c.id).buzzer = val; simpan(); render(); })));
    kids.push(el("div", {class:"hasil"}, "Label sentimen akhir: " + (LB[mayoritas(c).split(" ")[0]] || "-") +
      (c.buzzer_t1 !== "" ? ` · keputusan tahap 1: ${c.buzzer_t1 === "1" ? "buzzer" : "bukan buzzer"}` : "")));
  }
  return el("div", {class:"card" + (done && t !== "buzzer" ? " done" : "")}, kids);
}

function render(){
  const y = window.scrollY;
  const hide = document.getElementById("sembunyi").checked;
  const L = listFor(TAB).filter(c => !(hide && selesai(c, TAB)));
  const list = document.getElementById("list");
  list.replaceChildren(...(L.length ? L.map(kartuEl) : [el("div", {class:"empty"}, "Tidak ada kartu di sini.")]));
  document.getElementById("help").textContent = HELP[TAB];
  // progres
  const su = listFor("suara"), di = listFor("diskusi");
  const slotTot = su.reduce((a,c) => a + c.slots.filter(s => !s.label).length, 0);
  const slotIsi = su.reduce((a,c) => a + votes(c).filter(v => !v.tetap && v.label).length, 0);
  const diIsi = di.filter(diskusiSelesai).length;
  document.getElementById("n-suara").textContent = `${slotIsi}/${slotTot}`;
  document.getElementById("n-diskusi").textContent = `${diIsi}/${di.length}`;
  document.getElementById("n-buzzer").textContent = listFor("buzzer").length;
  const tot = slotTot + di.length, isi = slotIsi + diIsi;
  document.getElementById("prog").textContent = `${isi} dari ${tot} isian selesai` + (isi === tot ? " · siap diunduh" : "");
  document.getElementById("barfill").style.width = (tot ? isi / tot * 100 : 100) + "%";
  window.scrollTo(0, y);
}

document.querySelectorAll(".tab").forEach(b => b.onclick = () => {
  document.querySelectorAll(".tab").forEach(x => x.classList.toggle("on", x === b));
  TAB = b.dataset.tab; window.scrollTo(0, 0); render();
});
document.getElementById("sembunyi").onchange = render;
document.getElementById("unduh").onclick = () => {
  const q = s => '"' + String(s ?? "").replace(/"/g, '""') + '"';
  const rows = [["jenis","id","slot","reviewer","label","buzzer","catatan"]];
  DATA.kartu.forEach(c => {
    votes(c).forEach(v => { if (!v.tetap && v.label) rows.push(["suara", c.id, v.slot, v.reviewer, v.label, "", ""]); });
    if (seri(c) && diskusiSelesai(c)) rows.push(["diskusi", c.id, "", "", S[c.id].diskusi.label, "", S[c.id].diskusi.catatan || ""]);
    if (c.cek_buzzer) rows.push(["buzzer", c.id, "", "", "", buzzerVal(c), ""]);
  });
  const blob = new Blob(["﻿" + rows.map(r => r.map(q).join(",")).join("\r\n")], {type:"text/csv;charset=utf-8"});
  const a = el("a", {href:URL.createObjectURL(blob), download:"isian_lengkapi_3lapis.csv"});
  document.body.append(a); a.click(); a.remove();
};
render();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
