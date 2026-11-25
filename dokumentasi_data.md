# Dokumentasi Data UAS NLP: Sentimen Publik terhadap Raffi Ahmad

**Nama:** Raphael Angelo Adikara Purnama
**NIM:** 164241055
**Mata kuliah:** Natural Language Processing (UAS)

Dokumen ini mencatat semua yang saya lakukan pada data, dari scraping sampai dataset siap dimodelkan, beserta
alasan tiap keputusan. Angka di sini diambil dari output script yang benar-benar dijalankan. Rincian
per tahap filter ada di `notebooks/01_filter_data.ipynb`, uji bias sampling di `catatan_bias_sampel.md`,
dan hasil pemeriksaan akhir di `data/05_final/laporan_kesiapan.md` (dibuat ulang otomatis setiap
`labeling/finalize.py` dijalankan).

## Alur singkat

| tahap | script | output |
|---|---|---|
| 1. Scraping | `scraping/scrape_x.py`, `scrape_ig.py`, `scrape_yt.py`, `scrape_tt.py`, `scrape_profiles.py` | `data/01_raw/` |
| 2. Satu skema CSV | `scraping/to_csv.py` | `data/02_csv/` |
| 3. Filter dan sampling | `notebooks/01_filter_data.ipynb` | `data/03_filtered/` |
| 4. Sampel kontrol bias | `scraping/scrape_yt_kontrol.py`, `scrape_tt_kontrol.py`, `filtering/filter_kontrol_*.py` | `data/03_filtered/kontrol_*` |
| 5. Labeling 3 annotator | `labeling/make_batches.py` (`--tambahan` untuk batch 28), `labeling/codebook.md`, `labeling/aggregate.py` | `data/04_labeled/label_llm.csv` |
| 6. Review manusia | `labeling/review/bagi_review.py` (1 orang), `labeling/review/buat_review_3lapis.py` dan `gabung_review_3lapis.py` (3 orang) | `labeling/review/hasil/*.csv`, `labeling/review/3lapis/`, `data/04_labeled/review_3lapis.csv` |
| 7. Dataset final dan split | `labeling/finalize.py` | `data/05_final/dataset_model.csv` |
| 8. Back-translation (GPU Kaggle) | `augmentasi/siapkan_bt.py`, `augmentasi/kaggle_bt/back_translation.py` | `data/05_final/augmentasi_bt_mentah.csv` |
| 9. Preprocessing, augmentasi, baseline | `notebooks/02_preprocessing_baseline.ipynb` | `data/05_final/dataset_prepro.csv`, `augmentasi_prepro.csv`, `data/06_baseline/` |
| 10. Fine-tuning transformer (GPU Kaggle) | `notebooks/03_transformer_kaggle.ipynb` (dibangun `notebooks/_build/build_03.py`, satu kernel per model) | `data/07_transformer/` |
| 11. IndoBERT embedding + LogReg, BiLSTM + attention (GPU Kaggle) | `notebooks/04_embedding_bilstm_kaggle.ipynb` | `data/08_embedding_bilstm/` |
| 12. Perbandingan dan analisis kesalahan | `notebooks/05_perbandingan_analisis_kesalahan.ipynb` | `figures/05_*.png` |

Dataset Kaggle versi 2 (privat): `raphaeladikara/uas-nlp-raffi-v2`. Cara menjalankan ulang semuanya setelah review
3 lapis selesai ada di `JALANKAN_ULANG.md`.

## 1. Scraping

Periode penelitian 22 Oktober sampai 14 November 2026, dibagi tiga fase: pra (22 sampai 28 Oktober),
puncak (29 Oktober sampai 2 November), dan pasca (3 sampai 14 November).

**X.** Tweet diambil per hari dengan mode Latest, memakai tiga query: "raffi ahmad" (maks. 120 per hari),
raffi plus istilah kasus (120 per hari), dan variasi salah ketik "rafi ahmad" (40 per hari). Saya memakai
kuota harian supaya kurva per hari tidak didominasi hari yang viral. Mode Latest dipilih karena mode Top
condong ke tweet populer. Ini penting untuk bagian bias di bawah, karena X jadi satu-satunya sumber
yang tidak diurutkan berdasarkan like.

**Instagram.** Ada dua jalur. Jalur A adalah unggahan publik (akun berita dan diskusi) yang ditemukan
lewat kata kunci dan hashtag kasus. Jalur B adalah unggahan akun Raffi sendiri (@ukp_mudaseni_raffiahmad
dan @raffinagita1717). Jalur B tidak saya pakai untuk training, karena orang yang berkomentar di akun
Raffi sendiri kebanyakan fans atau haters yang memang datang khusus, jadi tidak mewakili percakapan umum.
Jalur B hanya dipakai sebagai pembanding di analisis.

**YouTube.** Lewat YouTube Data API v3 (gratis). Video dicari dengan 7 query kasus, judulnya harus
menyebut Raffi, RANS, atau mahasewa. Lalu dipilih 20 video dengan komentar terbanyak (maks. 3 per
channel supaya satu channel tidak mendominasi), dan diambil 100 komentar teratas per video.

**TikTok.** Video dicari dengan 6 query kasus, dipilih 14 video relevan dengan komentar terbanyak
(maks. 2 per kreator), lalu diambil 60 komentar per video.

Profil akun (umur akun, followers, jumlah posting) ikut diambil supaya bisa dipakai filter buzzer.
Nama akun tidak disimpan. Yang disimpan hanya hash-nya (`author_hash`), dan mention di teks diganti
`@user`, jadi data ini sudah anonim.

## 2. Filter (revisi setelah konsultasi dosen)

Di versi pertama setiap gerbang filter membuang teks hanya berdasarkan aturan otomatis. Dosen mengingatkan
bahwa aturan seperti "balasan pemilik unggahan pasti bukan opini" bisa overklaim, dan bahwa tweet relevan bisa
ikut tersaring di gerbang relevansi X. Setelah dicek ulang, kekhawatiran itu benar di hampir semua gerbang.
Karena itu aturan otomatis sekarang hanya menghasilkan **kandidat**, lalu setiap kandidat dibaca satu per satu.
Keputusan dan alasan per teks ada di `data/03_filtered/audit/keputusan_manual.csv`, dan notebook 01 berhenti
dengan error kalau ada kandidat yang belum diperiksa.

| gerbang | dasar penandaan di kode | versi 1 dibuang | versi 2 dibuang | temuan cek manual |
|---|---|---|---|---|
| 2. pemilik unggahan | IG: flag `is_created_by_media_owner` dari Apify atau username = pemilik unggahan; YouTube: `authorChannelId` = `channelId` video; TikTok: username = pembuat video; X: tidak dipakai | 28 | 16 | 12 balasan kreator (@julia_4j, @andovidalopez) berisi opini tentang Raffi |
| 3. tanpa isi | setelah normalisasi NFKC, tidak ada satu pun huruf atau angka (emoji saja, mention saja, tanda baca, kosong) | 177 | 150 | 27 teks seperti "14 M 😱", "𝒃𝒐𝒊𝒌𝒐𝒕 𝒂𝒋𝒂", "B O I K O T" dulu terbuang karena huruf unicode, huruf dipisah spasi, atau aturan terlalu ketat |
| 4a. bahasa asing (X) | kode `lang` dari X bukan Indonesia | 17 | 6 | 14 tweet ternyata berbahasa Indonesia, Jawa, atau campuran tentang Raffi |
| 4b. spam | daftar kata judol/promosi (`gacor`, `giveaway`, `slot`, ...) | 10 | 0 | ke-10 teks adalah opini yang memakai kata itu untuk menyindir |
| 5. relevansi X | teks dan judul tidak memuat kata kunci Raffi/kasus (dicocokkan setelah NFKC) | 61 | 60 | 1 tweet "gurita bisnis" relevan; 1 tweet berhuruf unicode tebal sekarang cocok kata kunci; 5 balasan yang tweet induknya tidak ter-scrape tetap dibuang karena sasarannya tidak bisa dipastikan |
| 6. duplikat | klaster kemiripan karakter (cosine >= 0,85) per akun; teks >= 5 kata dari akun berbeda | 79 | 79 | 37 akun sama mengulang, 42 salinan dari akun lain (satu wakil per klaster dipertahankan) |
| 7. buzzer | aturan keras + skor poin (rincian di bawah) | 36 | 36 | daftar sama persis dengan versi 1 |

| tahap | X | Instagram | YouTube | TikTok | total |
|---|---|---|---|---|---|
| 0. mentah (setelah buang ID kembar) | 2.197 | 1.989 | 2.000 | 834 | 7.020 |
| 2. pemilik unggahan | 2.197 | 1.975 | 1.998 | 834 | 7.004 |
| 3. tanpa isi | 2.197 | 1.832 | 1.992 | 833 | 6.854 |
| 4. bahasa asing dan spam | 2.191 | 1.832 | 1.992 | 833 | 6.848 |
| 5. relevansi X | 2.131 | 1.832 | 1.992 | 833 | 6.788 |
| 6. duplikat | 2.088 | 1.807 | 1.987 | 827 | 6.709 |
| 7. buzzer | 2.056 | 1.804 | 1.986 | 827 | 6.673 |
| 9. sampel untuk dilabeli | 1.314 | 1.434 | 801 | 501 | 4.050 |

Revisi ini menyelamatkan 61 teks (6.673 lolos, versi 1: 6.612). Supaya label yang sudah ada tidak perlu diulang,
sampel versi 1 (3.498 teks) dibekukan di `audit/sampel_v1.csv`. Teks baru diambil dengan peluang yang sama dengan
rasio sampling versi 1 di platformnya (Instagram 71,3%, X 63,5%, TikTok 60,5%, YouTube 40,3%), sehingga 27 teks
baru masuk jalur A dan 12 masuk jalur B. Ke-39 teks ini dilabeli tiga annotator yang sama sebagai batch 28.
Normalisasi NFKC juga mengubah tulisan 74 teks lama yang memakai huruf unicode bergaya (isinya sama).

**Alasan buzzer.** Filter buzzer dibuat tiga lapis:

| alasan | jenis | dasar |
|---|---|---|
| akun X dibuat < 30 hari sebelum posting | aturan keras | `author.createdAt` dibanding tanggal tweet (13 teks) |
| akun ditandai otomatis oleh X | aturan keras | field `isAutomated` (0 teks) |
| narasi sama ditulis >= 3 akun | aturan keras | teks >= 5 kata dengan kemiripan karakter >= 0,85 dari >= 3 akun (6 klaster) |
| satu akun memposting teks hampir sama >= 3 kali | aturan keras | flooding dari `author_hash` yang sama (7 teks) |
| skor >= 4 | skor poin | akun baru (< 3 bulan +2, < 6 bulan +1), following > 10x followers, username generik, akun kosong, > 100 tweet/hari, 3 sampai 5 teks (+1) atau >= 6 teks (+2) soal isu ini, teks mirip 1 akun lain (+2), >= 3 hashtag (10 teks) |
| skor 2 sampai 3 (zona batas) | lapis 3: isi teks | tidak dibuang otomatis; annotator menilai dari isi teks, lalu manusia memutuskan (14 teks akhirnya dinilai buzzer) |

Sinyal profil tidak dipakai untuk YouTube karena penonton YouTube memang punya channel kosong (di run pertama 78%
komentar YouTube masuk zona batas hanya karena itu). Aturan "narasi sama >= 3 akun" ikut menangkap meme
"Sultan andara ANGGARAN DARI NEGARA" (11 akun) yang kelihatannya lelucon viral, bukan narasi pesanan. Dampaknya
hanya satu teks wakil klaster, tapi ini dicatat sebagai kemungkinan salah tangkap. Rincian per teks ada di
notebook 01 bagian 7.

Sampling di tahap 9 dilakukan acak per strata (tanggal untuk X, unggahan atau video untuk platform lain),
bukan berdasarkan like terbanyak, supaya komentar biasa tetap terwakili.

## 3. Uji bias sampling

Ada kekhawatiran bahwa persentase negatif terlihat lebih tinggi dari aslinya. Penyebabnya ada dua:
sumber dipilih lewat kata kunci kasus, dan di YouTube, Instagram, serta TikTok yang diambil adalah
komentar teratas. Lapis kedua bisa diuji, jadi saya mengambil sampel kontrol dari video yang sama:

- **YouTube:** 100 komentar terbaru (`order=time`) per video, difilter dengan aturan yang sama, lalu
  diambil 25 acak per video. Hasilnya 500 teks.
- **TikTok:** scraper TikTok tidak punya opsi urutan terbaru, jadi saya mengambil 110 komentar per
  video, membuang 60 teratas yang sudah ada, lalu mengambil 30 acak dari sisanya. Hasilnya 420 teks
  dengan median like 2, sedangkan sampel teratas median like-nya 18. Biaya Apify-nya $1,93.

Kedua sampel kontrol dilabeli tiga annotator yang sama, dengan codebook yang sama:

| platform | sampel teratas | sampel kontrol | selisih per video (95% CI bootstrap) |
|---|---|---|---|
| YouTube | 69,7% negatif | 72,8% negatif | -1,5 poin [-7,5; +4,5] |
| TikTok | 77,3% negatif | 74,3% negatif | +2,8 poin [-3,1; +9,9] |

Mengambil komentar teratas hanya menggeser persentase negatif beberapa poin, dan selisihnya tidak
signifikan di kedua platform. X, yang tidak diurutkan berdasarkan like, juga tetap 62,6% negatif. Jadi
dominasi negatif memang ada di data, bukan efek dari cara sampling. Yang tidak bisa diuji adalah lapis
pertama (sumber dipilih lewat kata kunci kasus). Karena itu klaim di analisis saya batasi ke "percakapan
publik seputar kasus", bukan "sentimen masyarakat Indonesia". Rincian lengkap ada di
`catatan_bias_sampel.md`.

Kelompok `kontrol_yt` dan `kontrol_tt` hanya dipakai untuk uji ini, tidak masuk training dan tidak
masuk statistik utama. Batch labeling 01 sampai 21 tidak berubah saat kontrol ditambahkan (dicek dengan
hash berkas), karena kontrol ditulis sebagai batch baru 22 sampai 27.

## 4. Labeling

Setiap teks dilabeli tiga annotator Claude (Opus, Sonnet, Haiku) yang bekerja terpisah dan tidak bisa
melihat jawaban satu sama lain. Mereka membaca batch yang sama persis, dengan konteks unggahan (caption IG,
judul video, atau tweet yang dikutip) ditulis di atas tiap kelompok komentar. Konteks ini perlu karena
banyak komentar baru jelas maknanya kalau tahu unggahannya, misalnya "14M" atau "pantes aja".

Aturannya ada di `labeling/codebook.md`. Yang paling penting adalah cek sasaran: label negatif atau
positif hanya diberikan kalau yang disikapi memang Raffi (dirinya, jabatannya, RANS, atau
klarifikasinya). Komentar yang hanya mengejek mahasiswa bayaran atau polisi tanpa menyinggung Raffi
dilabeli netral, dengan `target_lain` diisi pihak yang diejek. Tanpa aturan ini, persentase negatif
terhadap Raffi akan membengkak oleh kemarahan ke pihak lain.

Label akhir diambil dari suara terbanyak. Dari 4.967 teks yang dilabeli (termasuk jalur B, buzzer, dan
kontrol), 78,5% disepakati bulat oleh ketiga annotator. Di data utama, kesepakatan per pasangan annotator
adalah Opus dan Sonnet 0,875, Opus dan Haiku 0,845, serta Sonnet dan Haiku 0,844. Haiku paling sering
berbeda, jadi saya memakai tiga annotator dengan suara terbanyak, bukan mengandalkan satu model.

Dua annotator kehilangan masing-masing satu jawaban (Sonnet di batch 18, Haiku di batch 14). Teks itu
tetap punya dua suara dan otomatis masuk antrean review karena tidak disepakati bulat.

## 5. Review manusia

Yang direview manusia adalah teks yang tidak disepakati bulat oleh ketiga annotator, dan teks zona batas
buzzer yang dinilai buzzer oleh minimal satu annotator. Antreannya 871 kartu: 767 dari data utama dan 104
dari jalur B. Kartu kelompok kontrol tidak dimasukkan, karena label kontrol hanya dipakai untuk
membandingkan proporsi dan cukup memakai suara terbanyak.

Review dikerjakan 5 orang. `labeling/review/bagi_review.py` membagi kartu dengan dua aturan:

- **30 kartu kalibrasi** dikerjakan semua reviewer. Kartunya dipilih acak dari kartu review label data
  utama, dengan 6 di antaranya kartu yang minimal satu annotator menilai positif. Kartu ini tercampur
  dengan kartu biasa dan tidak ditandai, supaya dikerjakan dengan cara yang sama. Gunanya untuk mengukur
  kesepakatan antar-manusia dengan Fleiss' kappa, dan label akhirnya diambil dari suara terbanyak reviewer.
- **Sisa 841 kartu** diurutkan per kelompok, jenis review, platform, dan label LLM, lalu dibagikan
  bergiliran. Jadi tiap orang mendapat campuran yang seimbang, sekitar 168 kartu ditambah 30 kartu
  kalibrasi, totalnya sekitar 198 per orang.

Setiap reviewer menerima satu berkas HTML yang berdiri sendiri (`untuk_reviewer/review_<Nama>.html`),
karena datanya ditanam langsung di dalam berkas. Berkas ini bisa dibuka offline di browser tanpa server
dan tanpa akun. Saya memilih cara ini dibanding membuat web di Vercel, karena Vercel butuh database dan
login supaya jawaban lima orang bisa terkumpul. Itu terlalu banyak infrastruktur untuk 871 kartu. Progres
tersimpan otomatis di browser masing-masing. Setelah selesai, reviewer mengekspor
`hasil_review_<Nama>.csv` dan mengirimnya ke saya. Halaman review juga memuat panduan singkat yang
diringkas dari codebook, supaya kelima orang memakai aturan yang sama.

Semua CSV reviewer saya taruh di `labeling/review/hasil/`. Kalau ada kartu kalibrasi yang seri (misalnya
2-2-1), atau teks identik di sumber yang sama mendapat label berbeda dari reviewer yang berbeda, saya
memutuskannya sendiri lewat `labeling/review/hasil/koordinator.csv` (kolom `id,label_review,buzzer_review,reviewer`
dengan `reviewer` diisi `koordinator`). Jawaban koordinator selalu menang. Gabungan semua review
tersimpan di `data/04_labeled/review_manusia.csv`.

### Review 3 lapis (revisi setelah konsultasi dosen)

Dosen meminta setiap teks yang belum disepakati dilabeli **3 orang**, lalu diambil suara terbanyak dan dihitung
Fleiss' kappa. Di review pertama, kartu biasa hanya dikerjakan 1 orang. Karena itu
`labeling/review/buat_review_3lapis.py` memisahkan data menjadi dua berkas di `labeling/review/3lapis/`:

- `sepakat_bulat_gt.csv`: 3.169 teks (2.750 utama, 419 jalur B) yang disepakati bulat Opus, Sonnet, dan Haiku.
  Labelnya langsung dipakai sebagai ground truth.
- `perlu_review_3_orang.csv`: 881 teks (775 utama, 106 jalur B) yang belum disepakati, lengkap dengan kolom
  `label_opus`, `label_sonnet`, `label_haiku`, dan tiga slot penilai. Slot pertama diisi review lama. Untuk 30 kartu
  kalibrasi yang dulu dikerjakan 5 orang, diambil 3 penilai acak (seed 42) supaya semua kartu punya jumlah penilai
  yang sama (syarat Fleiss' kappa). Dari 2.643 slot, 909 sudah terisi. Sisanya 1.734 slot dibagi rata, sekitar
  342 kartu per orang, dan tidak ada orang yang mendapat kartu yang sama dua kali (`tugas_<Nama>.csv`).

`gabung_review_3lapis.py` mengambil label yang dipilih minimal 2 dari 3 orang. Setelah putaran pertama masih ada
72 kartu yang kurang penilai. Kekurangannya (84 suara) diisi lewat `lengkapi_3lapis.html` oleh orang yang belum
pernah menilai kartu itu, sekaligus 25 kartu buzzer dicek ulang. Kartu yang ketiganya berbeda (29) diputus lewat
diskusi tim. Isiannya ada di `isian_lengkapi_3lapis.csv`. Dua keputusan diskusi berlabel positif dikoreksi menjadi
negatif oleh koordinator karena isinya memuji orang yang meneriaki Raffi dan musisi yang ikut boikot (alasannya ada
di kolom `catatan`).

Hasil akhirnya: 881 kartu dinilai lengkap 3 orang, 326 sepakat bulat, 526 dua lawan satu, dan 29 diputus diskusi.
Fleiss' kappa 0,286 (cukup), P_o 0,569, P_e 0,396, dan Krippendorff's alpha juga 0,286. Rinciannya per platform dan
per kategori ada di `ringkasan_kappa.md`. Kappa rendah karena kartu ini memang teks paling ambigu (ketiga AI pun
tidak sepakat), dan 71,5% kartu dua lawan satu adalah negatif lawan netral.

Metadata (sub, aspek, target_lain, sarkasme, butuh_konteks) untuk 39 teks batch 28 tidak tersimpan karena output
mentah LLM-nya sudah tidak ada. Metadata ini diisi ulang satu annotator dengan codebook yang sama
(`data/04_labeled/metadata_batch28_isi_ulang.csv`). Label sentimennya tetap dari review 3 orang.

## 6. Dataset final dan split

`labeling/finalize.py` membangun dataset model dengan aturan berikut:

1. Hanya kelompok `utama` (jalur A yang lolos filter). Jalur B, buzzer, dan kontrol tidak masuk.
2. Label akhir adalah label review manusia kalau ada. Kalau tidak ada, dipakai suara terbanyak tiga annotator.
3. Teks yang di-review sebagai buzzer dikeluarkan.
4. Teks `tidak_relevan` dan teks tanpa suara terbanyak (ketiga annotator beda) yang belum direview dibuang.
5. Evaluasi memakai **grouped stratified 5-fold cross-validation**, disimpan di kolom `fold` (0 sampai 4).
   Satu grup berisi semua teks dari akun yang sama dan semua teks yang identik, dan satu grup selalu
   berada di fold yang sama. Jadi akun yang sama atau teks kembar seperti "boikot rans" tidak bisa muncul
   di data latih dan data uji sekaligus. Kalau pembagian dilakukan acak biasa, model bisa terlihat bagus
   hanya karena hafal gaya satu akun (ada akun yang menulis 29 teks) atau teks yang sama persis.

Awalnya saya memakai satu split train/val/test 70/15/15. Masalahnya, test hanya berisi 12 teks positif,
jadi satu tebakan positif sudah menggeser recall sekitar 8 poin, dan perbedaan antar-model di kelas
positif tidak bisa dipercaya. Saya sempat mempertimbangkan scraping komentar pro-Raffi untuk menambah
positif, tapi tidak saya pakai untuk evaluasi. Sumbernya pasti konten pendukung, yang populasinya berbeda
(alasan yang sama dengan jalur B dikeluarkan), dan proporsi positif di data uji jadi buatan. Melabeli
2.601 teks cadangan juga saya tunda karena perkiraan biayanya sekitar 5 juta token, hanya untuk sekitar
60 positif tambahan. Penyaringan kata kunci positif juga sudah saya coba, tapi hanya menangkap 33 dari
85 positif yang ada, dengan presisi 6%. Dengan CV, setiap teks menjadi data uji tepat satu kali, jadi
ke-85 teks positif semuanya ikut dievaluasi. Hasilnya dilaporkan sebagai rata-rata dan standar deviasi
dari 5 fold. Pembagian fold ini tetap (seed 42), jadi semua model dibandingkan di fold yang sama.

**Pembaruan 22 Nov (pelabelan terarah).** Notebook 05 memperlihatkan dua hal yang mengubah pertimbangan di atas.
Learning curve kelas positif belum jenuh, dan model bisa mengurutkan teks: 100 teks dengan skor positif tertinggi
berisi 26% positif, bukan 2,5%. Jadi teks cadangan tidak perlu dilabeli semua. Cukup 250 teks dengan skor tertinggi
ditambah 50 teks acak sebagai pembanding (300 teks, sekitar 9 kali lebih hemat dari 2.601 teks), dengan perkiraan
40 sampai 60 positif tambahan. Hasilnya hanya masuk data latih, seperti jalur B, jadi data uji dan proporsi sentimen
tidak berubah. Alur dan skripnya ada di `labeling/terarah/README.md`.

Hasilnya (23 Nov): dari 250 teks skor tertinggi ada 33 positif (13%), dari 50 teks acak hanya 2 (4%). Perkiraan 40 sampai 60 positif ternyata terlalu optimis, karena skor model dilatih di teks yang condong ke topik yang sama, sedangkan teks cadangan lebih beragam. 73 teks yang tidak disepakati bulat 3 AI dinilai 3 orang (Fleiss' kappa 0,260), 7 kartu yang ketiganya beda diputus mengikuti mayoritas 3 AI (`labeling/terarah/review/koordinator.csv`). Setelah teks buzzer dan teks dari akun yang sudah ada di dataset final dibuang, tersisa 32 positif di `data/05_final/augmentasi_terarah.csv`. Varian jalur B + terarah menaikkan TF-IDF + LogReg teks + judul dari 0,589 ke 0,603 dan IndoBERTweet dari 0,597 ke 0,609, IndoBERT hampir sama (0,614 ke 0,616, F1 positif 0,325 ke 0,352), tetapi menurunkan IndoBERT embedding + LogReg dan BiLSTM. XLM-R ternyata ikut selesai dijalankan ulang pada 24 Nov (termasuk varian terarah) dan hasilnya menggantikan run 23 Nov; run lama tidak bisa diunduh lagi dari Kaggle. Dengan run kedua, XLM-R jalur B turun dari 0,563 ke 0,534, jadi jalur B membantu di 8 dari 9 konfigurasi, dan terarah menaikkan XLM-R dari 0,534 ke 0,551. Rinciannya di notebook 05 bagian hasil pelabelan terarah.

Hasil akhir (setelah review manusia):

| fold | negatif | netral | positif | total |
|---|---|---|---|---|
| 0 | 440 | 197 | 18 | 655 |
| 1 | 440 | 196 | 18 | 654 |
| 2 | 440 | 197 | 18 | 655 |
| 3 | 440 | 196 | 18 | 654 |
| 4 | 440 | 196 | 18 | 654 |
| total | 2.200 | 982 | 90 | 3.272 |

Dari 3.498 teks utama yang dilabeli, 14 dikeluarkan karena dinilai buzzer saat review dan 212 dibuang
karena tidak relevan. Label 2.632 teks berasal dari tiga annotator yang sepakat bulat, sedangkan 640
teks memakai label review manusia.

Script ini juga menjalankan pemeriksaan otomatis: tidak ada teks jalur B, buzzer, atau kontrol yang
masuk, id unik, label valid, tidak ada akun atau teks identik yang muncul di dua fold, tiap fold punya
ketiga kelas, teks identik di sumber yang sama berlabel konsisten, tidak ada kartu kalibrasi yang seri,
dan review sudah selesai. Status dataset baru menjadi SIAP kalau semua pemeriksaan lolos. Alur ini sudah
saya uji dengan jawaban reviewer buatan (lalu dihapus lagi), dan statusnya berubah menjadi SIAP setelah
semua kartu terisi dan konflik diputus lewat `koordinator.csv`.

## 7. Status kesiapan

Status sekarang **SIAP**. Kelima reviewer (Adit, Exsa, Mikael, Raphael, Yasyfa) sudah mengirim CSV,
dan semua 871 kartu sudah terisi. Di 30 kartu kalibrasi, Fleiss' kappa antar-reviewer 0,393, dan label
suara terbanyak reviewer sama dengan suara terbanyak LLM di 83% kartu. Kappa ini tergolong sedang ke
rendah. Wajar, karena kartu kalibrasi diambil dari teks yang memang tidak disepakati bulat oleh ketiga
annotator, jadi isinya teks yang paling ambigu.

Setelah CSV reviewer masuk, `finalize.py` masih menemukan dua masalah, lalu saya putuskan lewat
`labeling/review/hasil/koordinator.csv`:

- Satu kartu kalibrasi seri 2-2-1 (`X_2121128027350536255`, "emang sombong si songong ini ..klo rafi
  baek dia ngak kaya bininye"). Saya memakai aturan seri ikut suara terbanyak LLM, yaitu netral, karena
  sasaran ejekannya istri Raffi dan sikap ke Raffi sendiri tidak jelas.
- Tiga pasang teks identik di video TikTok yang sama berbeda label karena dikerjakan reviewer yang
  berbeda: "jogja keren", "maling teriak maling", dan "tipe-x juga mundur 😁". Ketiganya saya samakan
  menjadi negatif. Videonya tentang boikot RANS Carnival atau kasus mahasewa, jadi memuji Jogja atau
  menertawakan musisi yang mundur sama dengan mendukung boikot, yang di codebook masuk negatif.

`aggregate.py` sempat ikut dijalankan ulang. Ini aman, karena hasilnya sama persis (871 kartu review),
sebab input jawaban annotator tidak berubah.

## 8. Hal yang harus diperhatikan saat modeling

- **Kelas positif sangat sedikit** (90 teks, 2,8%; 18 per fold). Karena itu metrik utamanya
  macro-F1 dan F1 per kelas, bukan akurasi. Model yang selalu menebak negatif saja sudah dapat akurasi
  sekitar 66%. Class weight atau oversampling hanya boleh dilakukan di fold latih. Tuning hyperparameter
  juga dilakukan di dalam fold latih saja (nested CV), supaya fold uji tidak ikut dipakai memilih model.
  F1 positif tetap dilaporkan bersama standar deviasi antar-fold.
- **Positif tambahan untuk augmentasi.** Komentar positif dari jalur B, atau hasil scraping konten
  pendukung kalau nanti dilakukan, hanya boleh masuk ke fold latih sebagai eksperimen tambahan (dengan vs
  tanpa augmentasi), dan tidak boleh masuk fold uji maupun statistik sentimen.
- **51% teks butuh konteks.** Saya akan membandingkan model yang hanya membaca teks dengan model yang
  membaca teks plus konteks unggahan, karena konteks ini juga yang dipakai annotator saat memberi label.
- **138 teks dari akun media X** (88 netral, 50 negatif) tetap ikut training karena labelnya sesuai isi
  teks. Tapi teks ini saya keluarkan dari statistik opini publik, karena berita bukan opini warga.
- **Preprocessing model** (slang, stopword, stemming) tidak dilakukan di `dataset_model.csv`, karena itu
  bagian dari eksperimen. Kolom `text` hanya dinormalisasi ringan (URL dibuang, mention jadi `@user`).
  Preprocessing dan ablation-nya dikerjakan di `notebooks/02_preprocessing_baseline.ipynb`, dan hasilnya
  disimpan di `data/05_final/dataset_prepro.csv` (kolom `teks_ringan` untuk IndoBERT, `teks_lengkap`
  untuk TF-IDF).
- **Label adalah label LLM plus review manusia**, bukan anotasi manusia penuh. Hal ini saya tulis di
  keterbatasan, bersama tingkat kesepakatan antar-annotator di atas.

## Keterbatasan data

1. Sumber dipilih lewat kata kunci kasus, jadi hasil hanya berlaku untuk percakapan seputar kasus.
2. Fase pra hanya punya 30 teks berlabel (semuanya dari X), jadi perbandingan sebelum dan sesudah kasus lemah.
3. Instagram dan TikTok tidak memberi tanggal pembuatan akun, sehingga filter buzzer di dua platform itu
   lebih lemah dibanding X dan YouTube.
4. Kelas positif terlalu sedikit untuk dianalisis rinci per sub-kategori.
