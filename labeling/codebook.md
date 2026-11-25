# Codebook Pelabelan: Sentimen Publik terhadap Raffi Ahmad

Dipakai oleh tiga annotator (Claude Opus, Sonnet, Haiku) yang bekerja terpisah. Setiap teks dinilai
bersama konteksnya (caption unggahan IG, judul video YouTube/TikTok, atau tweet yang dikutip).

## Latar peristiwa (supaya annotator paham rujukan singkat)

- **28 Okt 2026**: demo mahasiswa di Bundaran HI (Hari Sumpah Pemuda).
- **29 Okt 2026**: Polda Metro Jaya menggelar "Deklarasi Sumpah Pemuda Mahasiswa Indonesia 2026" di Bundaran HI.
  Raffi Ahmad (Utusan Khusus Presiden bidang Pembinaan Generasi Muda dan Pekerja Seni) hadir bersama Willie Salim.
  Ada peserta yang mengaku bukan mahasiswa dan dibayar, sehingga muncul istilah "mahasewa", "mahasiswa bayaran",
  "mahasiswa settingan", "jaket almamater sewaan", "universitas PSI".
- **30 Okt**: Raffi diteriaki peserta Indonesia Youth Summit di TIM.
- **31 Okt**: Raffi klarifikasi, mengaku hanya diundang dan tidak tahu susunan acara. Boikot RANS Carnival
  Yogyakarta mulai ramai, beberapa pengisi acara dan UMKM mundur.
- **2 Nov**: GSI Youth Fest (Solo) batal mengundang Raffi.
- **9-10 Nov**: ICW membongkar 8 paket kontrak jasa influencer senilai Rp14,7 miliar dari Kemendikbudristek dan KKP
  ke perusahaan terafiliasi Raffi (PT Rans Animasi Indonesia). KPK membuka peluang mendalami, RANS membantah ada
  konflik kepentingan. Rujukan singkat: "14M", "14,7 M", "APBN", "Sultan Andara (Anggaran dari Negara)".

## Field yang diisi

| Field | Nilai | Keterangan |
|---|---|---|
| `relevan` | `1` / `0` | 0 kalau teks tidak membahas Raffi, kasus di atas, atau pihak yang terkait langsung dengannya, atau isinya tidak bisa dipahami sama sekali (hanya tag teman, hanya emoji, bahasa asing, spam) |
| `sentimen` | `negatif` / `netral` / `positif` | sikap penulis **terhadap Raffi Ahmad** (lihat aturan di bawah). Kosongkan kalau `relevan=0` |
| `sub` | lihat tabel sub-kategori | satu nilai, harus cocok dengan `sentimen` |
| `aspek` | daftar, boleh lebih dari satu | `mahasewa`, `klarifikasi`, `jabatan_utusan`, `kontrak_14m`, `boikot_rans`, `kehidupan_pribadi`, `umum` |
| `target_lain` | daftar | pihak lain yang ikut dikritik/dibela: `polisi`, `pemerintah`, `willie_salim`, `mahasiswa_bayaran`, `mahasiswa_demo`, `media`, `tidak_ada` |
| `sarkasme` | `1` / `0` | pujian yang maksudnya menyindir, misalnya "Menyala APBN ku" atau "mantap sultan" |
| `butuh_konteks` | `1` / `0` | 1 kalau maknanya baru jelas setelah membaca konteks (contoh: "14M", "pantes aja") |
| `buzzer` | `1` / `0` | 1 kalau bunyinya seperti pesan pesanan: template promosi/pembelaan generik yang tidak menanggapi isi unggahan, ajakan seragam dengan hashtag kampanye, atau narasi pembelaan yang sangat rapi dan generik. Komentar kasar atau pendek dari orang biasa BUKAN buzzer |
| `catatan` | teks pendek | wajib diisi kalau `buzzer=1` atau kalau label sulit diputuskan (maks. 15 kata) |

## Aturan sentimen terhadap Raffi

- **negatif**: mengkritik, menyindir, mengejek, menuduh, mengajak boikot/unfollow, kecewa, atau menyamakan Raffi
  dengan pihak yang dikritik. Sarkasme yang memuji tapi maksudnya mengejek tetap negatif.
- **positif**: membela, memaklumi, percaya klarifikasinya, simpati, mendukung, memuji karya/kepribadiannya, atau
  menyerang balik para pengkritik demi Raffi.
- **netral**: berita/informasi tanpa sikap, pertanyaan, ajakan menunggu fakta, atau marah kepada pihak lain
  (misalnya polisi) tanpa menyinggung Raffi sama sekali.
- Kalau teks mengkritik polisi DAN Raffi, labelnya negatif (target Raffi ikut dikritik).
- Kalau sikap ke Raffi campur (kasihan tapi kecewa), pilih yang paling dominan; kalau tetap seimbang, netral.
- Komentar di akun Raffi sendiri yang hanya berisi doa/pujian umum ("semangat aa") termasuk positif.

### Cek wajib sebelum memberi label negatif atau positif

Tanyakan: **apakah Raffi Ahmad (dirinya, jabatannya, RANS/bisnisnya, klarifikasinya, atau keluarganya) yang menjadi sasaran?**

- Sasaran disebut langsung (Raffi, rafi, aa, RANS, sultan andara, utusan khusus, stafsus, "artis yang hadir") atau
  komentar berada di unggahan yang caption-nya tentang Raffi dan jelas ditujukan kepadanya ("14M", "balikin duit rakyat",
  "klarifikasinya ga masuk akal") → nilai sikapnya ke Raffi.
- Komentar hanya mengejek mahasiswa bayaran ("mahasewa", "jamet bayaran", "semester 18", "kampus PSI"), polisi,
  pemerintah, atau acaranya secara umum, TANPA menyebut atau jelas menyindir Raffi → **netral** (sub `lainnya`),
  lalu isi `target_lain` dengan pihak yang diejek. Nada negatif ke pihak lain bukan sentimen negatif ke Raffi.
- Contoh: "Ngumpulin jamet2 darimana ini 😂" → netral, target_lain mahasiswa_bayaran.
  "Yang kemarin mahasiswa dihadang, yang ini mahasewa difasilitasi" → netral, target_lain polisi + mahasiswa_bayaran.
  "Raffi ngapain ikut acara settingan gini" → negatif.

## Sub-kategori

| sentimen | sub | Contoh |
|---|---|---|
| negatif | `kritik` | kritik dengan alasan: "stafsus kok diundang tidak tahu acaranya, tidak masuk akal" |
| negatif | `sindiran` | sarkasme/ejekan: "Menyala APBN ku", "mahasiswa semester 18" (kalau ditujukan ke acara Raffi) |
| negatif | `boikot` | ajakan boikot, unfollow, cancel acara |
| negatif | `hinaan` | makian atau serangan personal kasar |
| netral | `informasi` | berita, kronologi, fakta tanpa sikap |
| netral | `pertanyaan` | bertanya, menunggu penjelasan |
| netral | `lainnya` | relevan tapi tidak bersikap ke Raffi |
| positif | `membela` | membela dengan argumen: "dia cuma diundang, yang salah panitia" |
| positif | `simpati` | kasihan, empati: "kasihan aa jadi korban" |
| positif | `dukungan` | dukungan/pujian/doa tanpa argumen, khas penggemar: "semangat aa, kami selalu dukung" |

## Format jawaban

Satu baris JSON per teks, tanpa teks lain, urutan sama dengan input:

```json
{"id":"X_000123","relevan":1,"sentimen":"negatif","sub":"sindiran","aspek":["kontrak_14m"],"target_lain":["pemerintah"],"sarkasme":1,"butuh_konteks":1,"buzzer":0,"catatan":""}
```
