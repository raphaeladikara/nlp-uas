# Daftar perubahan paper (revisi 25 November)

Sebelum: docx dari Google Docs (Downloads). Sesudah: `Laporan UAS NLP - Kelompok J (Format Paper, Revisi 25 Nov).docx`. Dibuat otomatis dengan membandingkan kedua docx per paragraf dan per baris tabel.

## 1. Abstract: paragraf "Background: Reaksi warganet terhadap Raffi Ahmad setelah dek..." (diubah sebagian)

Sebelum:

> Background: <Berisi problem umum, khusus dan urgensi penelitian>

Sesudah:

> Background: Reaksi warganet terhadap Raffi Ahmad setelah deklarasi "mahasiswa bayaran" pada 29 Oktober 2026 tersebar di ribuan komentar di empat platform media sosial. Sikap terhadap Raffi sulit diklasifikasikan secara otomatis karena komentar yang membelanya sangat sedikit (2,5%) dan sering ditulis dengan nada marah kepada pengkritiknya.

## 2. Abstract: paragraf "Objective: Penelitian ini membangun dan membandingkan model ..." (diubah sebagian)

Sebelum:

> Objective: Solusi yang diusulkan untuk mengatasi problem

Sesudah:

> Objective: Penelitian ini membangun dan membandingkan model untuk mengklasifikasikan sikap warganet terhadap Raffi Ahmad (negatif, netral, positif), serta menguji apakah judul unggahan dan augmentasi kelas positif dapat memperbaiki hasil klasifikasi.

## 3. Abstract: paragraf "Methods: Sebanyak 7.020 teks dikumpulkan dari X, Instagram, ..." (diubah sebagian)

Sebelum:

> Methods: Tahapan metodologi dari penelitian yang dilakukan

Sesudah:

> Methods: Sebanyak 7.020 teks dikumpulkan dari X, Instagram, YouTube, dan TikTok (22 Oktober sampai 14 November 2026), lalu disaring melalui delapan gerbang filter yang kandidatnya diperiksa manual. Sampel 3.525 teks dilabeli tiga LLM, dan setiap teks yang tidak disepakati bulat dinilai ulang oleh tiga orang (Fleiss' kappa 0,286), sehingga diperoleh 3.329 teks. Sembilan model dibandingkan dengan grouped stratified 5-fold cross-validation, dua jenis input (komentar saja dan komentar dengan judul unggahan), serta tiga sumber augmentasi yang hanya ditambahkan ke data latih.

## 4. Abstract: paragraf "Results: Fine-tuning IndoBERT dengan input komentar dan judu..." (diubah sebagian)

Sebelum:

> Results: Hasil dari penelitian yang dilakukan

Sesudah:

> Results: Fine-tuning IndoBERT dengan input komentar dan judul serta augmentasi dari komentar positif asli mendapat macro-F1 tertinggi untuk model tunggal, yaitu 0,616 (F1 positif 0,352), sedangkan ensemble IndoBERT dan IndoBERTweet mencapai 0,628. Judul unggahan memberi kenaikan yang paling konsisten. Komentar positif asli menaikkan skor di delapan dari sembilan konfigurasi, sedangkan back-translation hanya membantu satu dari sembilan. Hanya 2,5% komentar yang membela Raffi, dan porsi komentar negatif naik dari 63,2% menjadi 69,3% setelah klarifikasinya.

## 5. Abstract: paragraf "Conclusion: Konteks unggahan dan contoh positif asli lebih b..." (diubah sebagian)

Sebelum:

> Conclusion: Kesimpulan dari penelitian

Sesudah:

> Conclusion: Konteks unggahan dan contoh positif asli lebih berpengaruh daripada pilihan model. Komentar pembelaan yang ditulis dengan nada marah masih menjadi sumber kesalahan utama.

## 6. Abstract: paragraf "Keywords: klasifikasi sikap; analisis sentimen bahasa Indone..." (diubah sebagian)

Sebelum:

> Keywords: <Maksimal 5>

Sesudah:

> Keywords: klasifikasi sikap; analisis sentimen bahasa Indonesia; IndoBERT; augmentasi data; pelabelan dengan LLM

## 7. Introduction: paragraf "Penelitian sentimen bahasa Indonesia sudah banyak memakai mo..." (diubah sebagian)

Sebelum:

> Penelitian sentimen bahasa Indonesia sudah banyak memakai model pralatih seperti IndoBERT (Wilie et al., 2020; Koto et al., 2020) dan IndoBERTweet (Koto et al., 2021), dan benchmark seperti NusaX (Winata et al., 2023) menunjukkan model ini kuat untuk bahasa Indonesia.

Sesudah:

> Penelitian sentimen bahasa Indonesia sudah banyak memakai model pralatih seperti IndoBERT (Wilie et al., 2020) dan IndoBERTweet (Koto et al., 2021), dan benchmark seperti NusaX (Winata et al., 2023) menunjukkan model ini kuat untuk bahasa Indonesia.

## 8. Related Works: paragraf "Survei analisis sentimen menunjukkan pergeseran dari leksiko..." (diubah sebagian)

Sebelum:

> Untuk bahasa Indonesia, IndoNLU (Wilie et al., 2020) merilis IndoBERT beserta benchmark tugas pemahaman, IndoLEM (Koto et al., 2020) merilis IndoBERT versi lain, dan IndoBERTweet (Koto et al., 2021) dilatih khusus dari tweet Indonesia.

Sesudah:

> Untuk bahasa Indonesia, IndoNLU (Wilie et al., 2020) merilis IndoBERT beserta benchmark tugas pemahaman, dan IndoBERTweet (Koto et al., 2021) dilatih khusus dari tweet Indonesia.

## 9. Related Works: paragraf "Untuk pelabelan, beberapa penelitian menunjukkan LLM bisa me..." (diubah sebagian)

Sebelum:

> Karena itu kami memakai tiga LLM sebagai annotator awal, lalu semua teks yang tidak disepakati bulat dinilai tiga orang dan diukur dengan Fleiss’ kappa (Fleiss, 1971; Landis & Koch, 1977).

Sesudah:

> Karena itu kami memakai tiga LLM sebagai annotator awal, lalu semua teks yang tidak disepakati bulat dinilai tiga orang dan diukur dengan Fleiss’ kappa (Fleiss, 1971).

## 10. Related Works: paragraf "Untuk kelas yang tidak seimbang, Henning et al. (2023) meran..." (diubah sebagian)

Sebelum:

> Survei augmentasi teks (Feng et al., 2021; Shorten et al., 2021; Bayer et al., 2022; Chen et al., 2023) menunjukkan back-translation (Sennrich et al., 2016) sebagai salah satu cara paling umum, tapi juga mencatat risiko makna berubah. Kami memakai OPUS-MT (Tiedemann & Thottingal, 2020) untuk back-translation dan membandingkannya dengan menambah teks positif asli. Untuk evaluasi kelas langka kami memakai average precision di samping F1, karena kurva precision-recall lebih informatif daripada ROC saat data tidak seimbang (Saito & Rehmsmeier, 2015).

Sesudah:

> Survei augmentasi teks (Feng et al., 2021; Shorten et al., 2021; Bayer et al., 2022; Chen et al., 2023) menunjukkan back-translation sebagai salah satu cara paling umum, tapi juga mencatat risiko makna berubah. Kami memakai OPUS-MT (Tiedemann et al., 2024) untuk back-translation dan membandingkannya dengan menambah teks positif asli. Untuk evaluasi kelas langka kami memakai average precision di samping F1, karena AP hanya menilai seberapa baik model menaruh teks positif di urutan atas, sehingga tidak ikut terangkat oleh banyaknya teks negatif yang mudah ditebak.

Sebelum:

> Terakhir, penyaringan akun buzzer kami dasarkan pada temuan bahwa akun terkoordinasi sering memakai pola teks dan aktivitas yang seragam (Cresci, 2020).

Sesudah:

> Terakhir, penyaringan buzzer kami dasarkan pada pola pasukan siber di Indonesia yang memakai banyak akun dengan narasi seragam (Sastramidjaja & Wijayanto, 2022). Hays et al. (2023) menunjukkan aturan sederhana dari beberapa fitur akun sudah bisa menyamai model rumit di dataset deteksi bot, tetapi juga mengingatkan bahwa label bot di dataset seperti itu sering terlalu disederhanakan. Karena itu kami memakai aturan yang transparan dan tetap memeriksa zona batas secara manual.

## 11. Material: paragraf baru

> Data mentah lalu melewati delapan gerbang filter. Setiap gerbang dijalankan oleh skrip Python di notebook filter. Aturan otomatis di setiap gerbang hanya menandai teks sebagai kandidat untuk dibuang, tidak langsung membuangnya. Setiap kandidat kemudian dibaca satu per satu oleh anggota tim, lalu diputuskan dibuang atau dipertahankan. Keputusan dan alasannya dicatat per teks di berkas audit (119 keputusan tertulis untuk gerbang 2, 4, dan 5), dan notebook sengaja berhenti dengan error kalau masih ada kandidat yang belum diputuskan.

## 12. Material: paragraf baru

> Cara ini kami pakai setelah konsultasi dengan dosen. Di versi awal, aturan otomatis langsung membuang teks. Setelah teks yang terbuang di versi awal kami baca ulang, ternyata banyak yang sebenarnya opini tentang Raffi. Tabel 2 membandingkan jumlah teks yang dibuang di versi awal (aturan langsung membuang) dan versi akhir (aturan menandai, manusia memutuskan).

## 13. Material: paragraf baru

> Tabel 2. Delapan gerbang filter, cara pemeriksaan, dan jumlah teks

## 14. Material: tabel baru

| No | Gerbang | Aturan otomatis yang menandai kandidat | Pemeriksaan manual | Dibuang versi awal | Dibuang versi akhir | Sisa teks |
|---|---|---|---|---|---|---|
| 0 | Data mentah | ID kembar dibuang | - | - | - | 7.020 |
| 1 | Rentang tanggal | Tanggal di luar 22 Oktober sampai 14 November 2026 | Tidak ada kandidat, karena rentang sudah dipakai saat scraping | 0 | 0 | 7.020 |
| 2 | Komentar pemilik unggahan | Penulis komentar adalah pemilik unggahan atau video (penanda Apify di Instagram, ID channel di YouTube, username di TikTok) | 28 kandidat dibaca. Dibuang kalau hanya balasan teknis atau ucapan terima kasih, dipertahankan kalau berisi opini tentang Raffi | 28 | 16 (12 dipertahankan) | 7.004 |
| 3 | Tanpa isi | Setelah normalisasi NFKC dan mention dihapus, tidak ada satu pun huruf atau angka | Teks yang terbuang di versi awal dibaca ulang, lalu aturan dilonggarkan. Yang dibuang: 84 emoji saja, 64 kosong atau mention saja, 2 tanda baca saja | 177 | 150 (27 diselamatkan, misalnya "14 M" dan "B O I K O T") | 6.854 |
| 4a | Bahasa asing (X) | Kode bahasa dari X bukan Indonesia | 20 kandidat dibaca. Dibuang hanya kalau berbahasa asing dan tidak membahas Raffi | 17 | 6 (14 dipertahankan) | 6.848 |
| 4b | Spam | Daftar kata judi online dan promosi (slot, gacor, giveaway, cek bio) | 10 kandidat dibaca, semuanya opini yang memakai kata itu untuk menyindir | 10 | 0 (10 dipertahankan) | 6.848 |
| 5 | Relevansi (X) | Teks dan tweet induknya tidak memuat kata kunci Raffi atau kasus | Semua 61 kandidat dibaca | 61 | 60 (1 dipertahankan) | 6.788 |
| 6 | Duplikat | Sama persis setelah huruf kecil dan tanda baca dibuang, atau cosine TF-IDF karakter 3 sampai 5 gram >= 0,85 untuk teks minimal 5 kata | Satu wakil per klaster dipertahankan. Jumlah akun per klaster disimpan untuk gerbang buzzer | 79 | 79 (37 akun sama mengulang, 42 salinan dari akun lain) | 6.709 |
| 7 | Buzzer | Aturan keras dan skor poin (Tabel 3) | Zona batas diputuskan di tahap review | 36 | 36 | 6.673 |
| 8 | Batas per sumber | Maksimal 25 tweet per thread X (komentar per unggahan sudah dibatasi saat scraping) | Tidak ada kandidat | 0 | 0 | 6.673 |
|  | Total |  |  | 408 | 347 | 6.673 |

## 15. Material: paragraf baru

> Dengan cara baru ini, teks yang lolos naik dari 6.612 menjadi 6.673, jadi 61 teks diselamatkan dari pembuangan yang keliru. Kesalahan terbanyak ada di gerbang tanpa isi. Di versi awal, teks yang ditulis dengan huruf unicode bergaya seperti "𝒃𝒐𝒊𝒌𝒐𝒕 𝒂𝒋𝒂" atau huruf dipisah spasi seperti "B O I K O T" dianggap tidak punya huruf. Teks "14 M" juga ikut terbuang, padahal di kasus ini artinya jelas merujuk ke kontrak Rp14,7 miliar. Gerbang spam juga tidak menangkap satu pun spam. Kesepuluh kandidatnya ternyata opini, misalnya "Raffi Mesin Pencuci Uang paling Gacor". Teks emoji saja tetap kami buang karena sasarannya tidak bisa dipastikan. Emoji muntah di bawah berita kontrak bisa ditujukan ke Raffi, ke kementerian, atau ke beritanya.

## 16. Material: paragraf baru

> Dari 6.673 teks yang lolos, 525 adalah komentar jalur B, dan semuanya ikut dilabeli. Sisanya 6.148 teks jalur A, lalu kami ambil sampel acak bertingkat per platform (strata tanggal untuk X, strata unggahan atau video untuk platform lain), bukan berdasarkan like terbanyak. Hasilnya 3.525 teks jalur A dilabeli dan 2.623 teks menjadi cadangan.

## 17. Material: paragraf baru

> Pemeriksaan relevansi. Komentar Instagram, YouTube, dan TikTok sudah pasti berada di bawah unggahan tentang kasus ini, karena unggahannya dipilih saat scraping. Di YouTube misalnya, judul video harus menyebut Raffi, RANS, atau mahasewa. Tweet berbeda, karena pencarian X juga bisa cocok dengan username atau nama tampilan penulis, bukan isi tweet. Karena itu gerbang relevansi hanya dipakai untuk X. Sebuah tweet ditandai sebagai kandidat tidak relevan kalau teks dan tweet induknya tidak memuat satu pun kata kunci berikut: raffi atau rafi, RANS, Nagita, mahasewa, mahasiswa bayaran, settingan, sewaan, palsu, atau bodong, deklarasi, bundaran, utusan khusus, stafsus, 14 M atau 14 miliar, dan ICW. Pencocokan dilakukan setelah normalisasi NFKC, supaya tweet seperti "𝗥𝗔𝗙𝗙𝗜 𝗔𝗛𝗠𝗔𝗗 … Shutdown this guy" tetap cocok.

## 18. Material: paragraf baru

> Semua 61 kandidat dibaca, bukan hanya sampelnya, jadi tidak ada tweet yang terbuang tanpa dibaca. Satu tweet dipertahankan walaupun tidak memuat kata kunci, yaitu ajakan menumbangkan "gurita bisnis", karena di periode ini istilah itu merujuk ke bisnis Raffi. Sebanyak 55 tweet dibuang karena jelas membahas topik lain, misalnya fans JKT48, KRL Surabaya, iklan koin kuno, puisi, dan dua tweet berbahasa Telugu. Lima balasan pendek ikut dibuang karena tweet induknya tidak ikut ter-scrape, sehingga sasarannya tidak bisa dipastikan, misalnya "Instansi itu...". Kelima teks ini satu-satunya bagian yang mungkin relevan tapi tetap terbuang, dan kami catat sebagai keterbatasan.

## 19. Material: paragraf baru

> Kebalikannya, yaitu teks yang memuat kata kunci tapi tidak membahas Raffi, ditangani di tahap pelabelan. Annotator memberi label tidak relevan, dan 182 teks dengan label akhir tidak relevan dikeluarkan dari dataset. Risiko yang tidak bisa kami periksa adalah tweet relevan yang sejak awal tidak dikembalikan oleh pencarian X, karena tweet itu tidak pernah masuk data.

## 20. Material: paragraf baru

> Penandaan buzzer. Kami memakai istilah "terindikasi buzzer" untuk teks yang polanya menyerupai pesan terkoordinasi atau akun yang dipakai khusus untuk satu isu. Ini bukan klaim bahwa akunnya pasti dibayar. Penandaan dibuat tiga lapis. Lapis pertama adalah aturan keras: kalau satu saja terpenuhi, teks langsung dikeluarkan. Lapis kedua adalah skor poin dari sinyal lemah. Satu sinyal belum cukup untuk menuduh, tapi kalau beberapa sinyal menumpuk, teksnya jadi mencurigakan. Lapis ketiga adalah penilaian isi teks oleh annotator dan manusia untuk teks di zona batas. Aturan dan bobotnya ada di Tabel 3.

## 21. Material: paragraf baru

> Tabel 3. Aturan dan skor penandaan buzzer

## 22. Material: tabel baru

| Lapis | Indikator | Bobot atau aturan | Jumlah teks |
|---|---|---|---|
| Aturan keras | Akun X dibuat kurang dari 30 hari sebelum tweet diposting | Langsung dikeluarkan | 13 |
| Aturan keras | Satu akun memposting teks hampir sama 3 kali atau lebih | Langsung dikeluarkan | 7 |
| Aturan keras | Teks minimal 5 kata yang hampir sama (cosine >= 0,85) ditulis 3 akun berbeda atau lebih | Langsung dikeluarkan | 6 klaster |
| Aturan keras | Akun ditandai otomatis (bot) oleh X | Langsung dikeluarkan | 0 |
| Skor | Akun berumur kurang dari 3 bulan / kurang dari 6 bulan | +2 / +1 |  |
| Skor | Memposting 6 teks atau lebih / 3 sampai 5 teks soal isu ini | +2 / +1 |  |
| Skor | Teks mirip dengan teks akun lain | +2 |  |
| Skor | Following lebih dari 10 kali followers, username generik, akun kosong, akun X tanpa bio dengan followers di bawah 50, lebih dari 100 tweet per hari, 3 hashtag atau lebih | Masing-masing +1 |  |
| Keputusan | Kena minimal satu aturan keras (berapa pun skornya) | Dikeluarkan | 26 |
| Keputusan | Skor 4 atau lebih | Dikeluarkan | 10 |
| Keputusan | Skor 2 sampai 3 (zona batas), tidak kena aturan keras | Tetap dilabeli, diputuskan lewat penilaian isi | 580 |
| Keputusan | Skor 0 sampai 1, tidak kena aturan keras | Lolos | 6.093 |
|  | Total yang masuk gerbang 7 |  | 6.709 |

## 23. Material: paragraf baru

> Empat kelompok keputusan di Tabel 3 tidak saling tumpang tindih dan jumlahnya 6.709, sama dengan teks yang masuk gerbang buzzer. Teks yang kena aturan keras langsung dikeluarkan berapa pun skornya, jadi tidak dihitung lagi di baris skor. Dari 26 teks itu, 11 sebenarnya punya skor 0 sampai 1 dan 15 punya skor 2 sampai 3. Yang lolos ke tahap berikutnya adalah 6.093 teks lolos ditambah 580 teks zona batas, yaitu 6.673 teks seperti di Tabel 2.

## 24. Material: paragraf baru

> Sinyal profil tidak dipakai untuk YouTube. Pada percobaan pertama, 78% komentar YouTube masuk zona batas hanya karena channel penonton memang kosong. Hal yang sama membuat bobot sinyal akun kosong kami turunkan menjadi 1 di platform lain. Sinyal yang lebih sulit dipalsukan, yaitu umur akun dan perilaku posting, tetap berbobot 2.

## 25. Material: paragraf baru

> Totalnya, 36 teks dikeluarkan di gerbang ini (26 aturan keras, 10 skor tinggi), dan 32 di antaranya dari X. Untuk 580 teks zona batas, ketiga LLM menilai isi teksnya dengan kriteria di codebook. Teks dianggap buzzer kalau bunyinya seperti pesan pesanan, misalnya template pembelaan atau promosi yang tidak menanggapi isi unggahan, atau ajakan seragam dengan hashtag kampanye. Komentar kasar atau pendek dari orang biasa tidak dianggap buzzer. Teks yang ditandai buzzer oleh minimal satu LLM masuk review manusia. Ada 25 teks seperti ini, dan setelah dinilai tiga orang, 14 diputuskan terindikasi buzzer dan 11 tidak.

## 26. Material: paragraf baru

> Teks yang dikeluarkan tidak dihapus, tapi disimpan terpisah supaya bisa dilaporkan sendiri. Kami juga mencatat satu kemungkinan salah tangkap. Aturan narasi sama dari 3 akun atau lebih ikut menangkap meme "Sultan andara ANGGARAN DARI NEGARA" yang ditulis 11 akun. Meme ini kelihatannya lelucon viral, bukan narasi pesanan, tapi dampaknya hanya satu teks wakil klaster.

## 27. Material: paragraf baru

> Pelabelan oleh tiga LLM. Sampel yang dilabeli berisi 4.050 teks, yaitu 3.525 teks jalur A dan 525 teks jalur B. Setiap teks diberi label sikap terhadap Raffi: negatif, netral, positif, atau tidak relevan. Aturannya kami tulis di codebook. Aturan terpentingnya adalah cek sasaran: label negatif atau positif hanya diberikan kalau yang disikapi memang Raffi, yaitu dirinya, jabatannya, RANS, atau klarifikasinya. Komentar yang hanya mengejek mahasiswa bayaran atau pihak lain dilabeli netral. Tiga LLM (Claude Opus, Sonnet, dan Haiku) melabeli batch yang sama secara terpisah dan tidak bisa melihat jawaban satu sama lain. Judul unggahan ditulis di atas setiap kelompok komentar, karena banyak komentar seperti "14M" atau "pantes aja" baru jelas maknanya kalau unggahannya diketahui. Ada 3.169 teks yang disepakati bulat oleh ketiga LLM (2.750 jalur A dan 419 jalur B), dan labelnya langsung dipakai. Sisanya 881 teks (775 jalur A dan 106 jalur B) tidak disepakati bulat atau ditandai buzzer oleh minimal satu LLM, sehingga masuk review manusia.

## 28. Material: paragraf baru

> Review manusia versi awal. Di versi awal tanggal 16 November, antrean review berisi 871 kartu (767 jalur A dan 104 jalur B), dan setiap kartu hanya dinilai satu orang. Kartu dibagi bergiliran ke lima anggota kelompok, sekitar 168 kartu per orang. Ada juga 30 kartu kalibrasi yang dinilai kelima orang untuk mengukur kesepakatan, dan dari kartu itu didapat Fleiss' kappa 0,393. Setiap orang menerima satu halaman HTML yang bisa dibuka offline di browser. Halaman itu menampilkan teks, judul unggahan, tautan ke sumbernya, suara ketiga LLM beserta catatannya, dan panduan singkat dari codebook. Setelah selesai, hasilnya diekspor ke CSV lalu digabung. Masalahnya, label sebagian besar kartu bergantung pada satu orang yang kebetulan mendapat kartu itu, dan kappa hanya dihitung dari 30 kartu.

## 29. Material: paragraf baru

> Review tiga orang. Setelah konsultasi tanggal 17 November, dosen meminta setiap teks yang belum disepakati dinilai tiga orang. Revisi filter juga menambah 39 teks baru yang dilabeli sebagai batch 28, dan 10 di antaranya tidak disepakati bulat, jadi antreannya menjadi 881 kartu. Satu kartu berisi satu teks, jadi 881 kartu sama dengan 881 teks berbeda. Setiap kartu punya tiga slot penilai. Slot pertama diisi hasil review versi awal supaya pekerjaan lama tidak terbuang. Untuk 30 kartu kalibrasi yang dulu dinilai lima orang, kami mengambil tiga penilai secara acak (seed 42), supaya semua kartu punya jumlah penilai yang sama. Dari 2.643 slot, 909 sudah terisi dari review lama. Sisanya 1.734 slot dibagi rata ke lima orang dalam berkas tugas masing-masing, dengan aturan satu orang tidak pernah mendapat kartu yang sama dua kali.

## 30. Material: paragraf baru

> Setelah putaran pertama, masih ada 72 kartu yang kurang penilai. Kekurangannya, yaitu 84 penilaian, diisi lewat halaman HTML tambahan oleh anggota yang belum pernah menilai kartu itu. Di halaman yang sama, 25 kartu yang ditandai buzzer juga dicek ulang. Label akhir adalah label yang dipilih minimal dua dari tiga orang, dan ini berlaku di 852 kartu. Kalau ketiga orang memilih tiga label berbeda (29 kartu), label diputuskan lewat diskusi tim. Dari hasil diskusi itu, dua kartu yang dilabeli positif kami koreksi menjadi negatif, karena isinya ternyata memuji orang yang meneriaki Raffi dan musisi yang ikut boikot. Semua angka review di laporan ini memakai 881 kartu dari review tiga orang, bukan 871 kartu versi awal.

## 31. Material: paragraf baru

> Kesepakatan penilai. Fleiss' kappa dihitung dari 881 kartu dengan empat kategori. Untuk setiap kartu dihitung proporsi pasangan penilai yang sepakat, lalu dirata-rata menjadi kesepakatan teramati Po = 0,569. Kesepakatan kebetulan Pe = 0,396 dihitung dari proporsi setiap kategori di semua penilaian. Nilai kappa adalah (Po - Pe) / (1 - Pe) = 0,286, masuk kategori cukup (fair). Fleiss' kappa tidak mensyaratkan tiga orang yang sama di setiap kartu, cukup jumlah penilai per kartu sama, jadi kombinasi tiga dari lima orang boleh berbeda antar kartu. Angkanya rendah karena kartu yang direview memang teks yang membuat tiga LLM tidak sepakat. Kappa paling rendah di kategori netral (0,219) dan paling tinggi di positif (0,581). Kartu jalur B lebih mudah disepakati (0,484) daripada jalur A (0,257), karena komentar di akun Raffi biasanya langsung ditujukan ke Raffi.

## 32. Material: paragraf baru

> Dataset final. Dataset final hanya berisi jalur A. Dari 3.525 teks jalur A, 14 teks dikeluarkan karena terindikasi buzzer saat review dan 182 teks dibuang karena tidak relevan, sehingga tersisa 3.329 teks: 2.206 negatif (66,3%), 1.039 netral (31,2%), dan 84 positif (2,5%). Jalur B dilabeli dengan alur yang sama tetapi disimpan terpisah dari dataset utama. Cara jalur B dipakai dijelaskan di subbab Augmentasi kelas positif.

## 33. Material: paragraf dihapus

> Data mentah lalu disaring dari teks kosong, spam, duplikat, teks yang tidak membahas Raffi, dan buzzer. Setiap aturan otomatis hanya menandai kandidat, lalu kandidat itu dibaca manual, dan 61 teks diselamatkan dari pembuangan yang keliru. Buzzer ditandai dengan aturan keras dan skor poin, dan teks di zona batas diputuskan manusia. Dari teks yang lolos, 3.525 teks jalur A dan 525 teks jalur B diambil sebagai sampel untuk dilabeli, dan 2.623 teks disimpan sebagai cadangan.

## 34. Material: paragraf dihapus

> Setiap teks diberi label sikap terhadap Raffi: negatif, netral, positif, atau tidak relevan. Tiga LLM (Claude Opus, Sonnet, dan Haiku) melabeli secara terpisah. Sebanyak 2.750 teks jalur A disepakati bulat. Sisanya, bersama teks jalur B yang tidak disepakati, dinilai tiga anggota kelompok dari lima orang yang ada, total 881 kartu. Fleiss’ kappa di 881 kartu ini 0,286, masuk kategori cukup (fair). Angkanya rendah karena kartu yang direview memang teks yang sulit, yaitu teks yang membuat tiga LLM tidak sepakat. Setelah 14 teks buzzer dan 182 teks tidak relevan dikeluarkan, dataset final berisi 3.329 teks: 2.206 negatif (66,3%), 1.039 netral (31,2%), dan 84 positif (2,5%).

## 35. Preprocessing dan input: paragraf baru

> Untuk model TF-IDF, teks di-lowercase, URL dan mention diganti token, dan huruf yang diulang dipendekkan. Untuk model BERT, preprocessing-nya lebih ringan: URL dibuang, mention diganti @user, tanda # dibuang, huruf berulang dipendekkan, dan emoji diubah menjadi kata bahasa Indonesia, misalnya emoji tertawa menjadi "wajah gembira berurai air mata". Huruf besar dan kecil tidak kami ubah sebelum teks masuk tokenizer, dan keputusan itu diserahkan ke tokenizer masing-masing model. IndoBERTweet (indolem/indobertweet-base-uncased) dan IndoBERT (indobenchmark/indobert-base-p1) adalah model uncased. Tokenizernya memakai pengaturan do_lower_case = True, jadi di dalam tokenizer "BOIKOT" dan "boikot" tetap menjadi token yang sama. Artinya, tanpa lowercase di sini berarti kami tidak membuang informasi kapital di tahap preprocessing, bukan berarti kedua model itu membaca kapital. Hanya XLM-RoBERTa (cased) yang benar-benar membedakan huruf kapital.

## 36. Preprocessing dan input: paragraf baru

> Setiap model diuji dengan dua input: teks saja, dan teks + judul dengan format [CLS] komentar [SEP] judul [SEP]. Judul ditambahkan karena separuh teks (50,8%) ditandai annotator butuh judul supaya sasarannya jelas. Contohnya komentar TikTok "Kan mereka bekerja, ya pasti harus dibayar". Kalau dibaca sendiri, tidak jelas siapa "mereka" dan bagaimana sikapnya ke Raffi. Komentar ini ada di bawah video berjudul "ICW Temukan Rp 14,7 Miliar Uang Negara Yang Mengalir ke Perusahaan Raffi Ahmad", jadi maksudnya membela perusahaan Raffi yang dibayar negara, dan labelnya positif. Input modelnya menjadi:

## 37. Preprocessing dan input: paragraf baru

> [CLS] Kan mereka bekerja, ya pasti harus dibayar [SEP] ICW Temukan Rp 14,7 Miliar Uang Negara Yang Mengalir ke Perusahaan Raffi Ahmad [SEP]

## 38. Preprocessing dan input: paragraf baru

> Panjang maksimal input adalah 128 token untuk teks saja dan 256 token untuk teks + judul. Kalau melebihi batas, bagian yang lebih panjang dipotong lebih dulu. Untuk TF-IDF, judul dijadikan vektor terpisah dengan bobot 0,5.

## 39. Preprocessing dan input: paragraf dihapus

> Untuk model TF-IDF, teks di-lowercase, URL dan mention diganti token, dan huruf yang diulang dipendekkan. Untuk model BERT, teks dikirim apa adanya tanpa lowercase dan emoji diubah menjadi kata bahasa Indonesia. Setiap model diuji dengan dua input: teks saja, dan teks + judul dengan format [CLS] komentar [SEP] judul [SEP]. Judul ditambahkan karena separuh teks (50,8%) ditandai annotator butuh judul supaya sasarannya jelas.

## 40. Augmentasi kelas positif: paragraf baru

> Dataset final hanya punya 84 teks positif, jadi setiap fold latih hanya berisi sekitar 67 teks positif. Di versi awal kami hanya memakai class weight, dan F1 positif berhenti di 0,338. Karena itu, di versi akhir kami menambah contoh positif dari tiga sumber yang dicoba bertahap: jalur B, parafrase, lalu pelabelan terarah. Semua tambahan berlabel positif dan hanya masuk fold latih. Fold uji selalu berisi data asli jalur A tanpa tambahan, jadi angka evaluasi tetap mengukur kemampuan model di percakapan publik yang sebenarnya.

## 41. Augmentasi kelas positif: paragraf baru

> Jalur B. Sumber pertama adalah komentar di 8 unggahan dua akun Instagram Raffi sendiri (@raffinagita1717 dan @ukp_mudaseni_raffiahmad). Komentar ini sudah kami scraping sejak awal, tetapi di versi awal sengaja tidak dipakai untuk melatih model, hanya sebagai pembanding. Alasannya, yang berkomentar di akun Raffi kebanyakan pengikutnya atau orang yang sengaja datang untuk menyerangnya, jadi isinya tidak mewakili percakapan publik. Setelah konsultasi dengan dosen, kami memakai komentar positif dari jalur B untuk menambah data latih, karena di sana pembelaan terhadap Raffi lebih mudah ditemukan. Dari 571 komentar mentah, 525 lolos filter dan dilabeli dengan alur yang sama dengan jalur A (tiga LLM, lalu tiga orang untuk teks yang tidak disepakati). Setelah teks tidak relevan dan buzzer dibuang, tersisa 514 teks dengan 78,0% negatif dan 8,2% positif (42 teks). Porsi positif ini lebih dari tiga kali jalur A, walaupun jumlahnya tetap kecil. Yang kami ambil hanya 42 teks positif itu, karena kelas negatif dan netral sudah cukup banyak di data utama. Kalau seluruh jalur B dimasukkan, proporsi kelas di data latih justru bergeser ke negatif. Kami juga memeriksa bahwa tidak ada akun atau teks jalur B yang sama dengan data utama, dan hasilnya tidak ada yang perlu dibuang. Jalur B tidak pernah masuk fold uji maupun statistik sikap warganet.

## 42. Augmentasi kelas positif: paragraf baru

> Parafrase. Sumber kedua adalah parafrase dari teks positif yang sudah ada. Teks diterjemahkan dari bahasa Indonesia ke bahasa Inggris lalu kembali ke bahasa Indonesia memakai OPUS-MT di GPU Kaggle (back-translation). Hasilnya 253 parafrase dari 103 teks positif (67 dari jalur A dan 36 dari jalur B). Parafrase dari teks yang sedang berada di fold uji ikut dikeluarkan dari data latih fold itu, supaya model tidak pernah melihat versi lain dari teks yang sedang diuji.

## 43. Augmentasi kelas positif: paragraf baru

> Pelabelan terarah. Sumber ketiga kami tambahkan pada 22 November, setelah learning curve kelas positif menunjukkan model masih kekurangan contoh positif asli. Melabeli semua 2.623 teks cadangan terlalu mahal, jadi kami memakai model TF-IDF untuk mengurutkan teks cadangan berdasarkan skor positif. Lalu 250 teks teratas dan 50 teks acak sebagai pembanding dilabeli dengan alur yang sama. Annotator tidak diberi tahu skor atau cara teks itu dipilih. Sebanyak 73 kartu yang tidak disepakati bulat tiga LLM dinilai tiga orang (Fleiss' kappa 0,260). Hasilnya 35 teks positif, dan setelah teks buzzer dan teks dari akun yang sudah ada di dataset utama dibuang, tersisa 32 teks positif baru.

## 44. Augmentasi kelas positif: paragraf baru

> Ada 7 kartu terarah yang seri, artinya ketiga orang memilih tiga label berbeda. Berbeda dengan data utama, ketujuh kartu ini tidak kami diskusikan, tetapi diputus dengan mayoritas tiga LLM. Ada tiga alasan. Pertama, data terarah hanya dipakai sebagai tambahan data latih, tidak pernah masuk data uji atau statistik sikap warganet, jadi labelnya tidak memengaruhi angka evaluasi secara langsung. Kedua, setiap kartu sudah punya mayoritas dua dari tiga LLM yang dibuat terpisah dari penilaian manusia, jadi ada pendapat ketiga yang independen. Ketiga, dari tujuh kartu itu hanya satu yang akhirnya berlabel positif, sehingga paling banyak satu dari 32 teks augmentasi bergantung pada aturan ini.

## 45. Augmentasi kelas positif: paragraf baru

> Secara total ada 327 baris augmentasi: 42 komentar jalur B, 253 parafrase, dan 32 teks terarah. Setiap sumber diuji terpisah dan digabung, lalu dibandingkan dengan kondisi tanpa augmentasi pada model, input, dan fold yang sama (Tabel 6).

## 46. Augmentasi kelas positif: paragraf dihapus

> Augmentasi hanya ditambahkan ke fold latih, tidak pernah ke fold uji. Ada tiga sumber. Jalur B berisi 42 komentar positif dari akun Raffi sendiri. Parafrase dibuat dengan back-translation Indonesia ke Inggris lalu kembali ke Indonesia memakai OPUS-MT. Pelabelan terarah dibuat dari teks cadangan: model TF-IDF mengurutkan 2.623 teks cadangan berdasarkan skor positif, lalu 250 teks teratas dan 50 teks acak dilabeli dengan alur yang sama (3 LLM, lalu 3 orang). Annotator tidak diberi tahu skor atau cara pilih teksnya. Hasilnya 32 teks positif baru.

## 47. Model: paragraf "Kami membandingkan sembilan model. Dua baseline tanpa pembel..." (diubah sebagian)

Sebelum:

> BiLSTM + attention (Zhou et al., 2016) memakai embedding kata IndoBERT yang dibekukan.

Sesudah:

> BiLSTM + attention (Minaee et al., 2021) memakai embedding kata IndoBERT yang dibekukan.

## 48. Perkembangan Metode: paragraf "Metode di atas bukan rancangan pertama kami. Versi awal sele..." (diubah sebagian)

Sebelum:

> Tabel 2 merangkum apa yang berubah dan alasannya.

Sesudah:

> Tabel 4 merangkum apa yang berubah dan alasannya.

## 49. Perkembangan Metode: paragraf "Tabel 4. Metode versi awal (16 November) dan versi akhir (24..." (diubah sebagian)

Sebelum:

> Tabel 2.

Sesudah:

> Tabel 4.

## 50. Perkembangan Metode: tabel dengan header "Bagian | Versi awal | Versi akhir | Alasan perubahan" (diubah)

Baris sebelum:

| Bagian | Versi awal | Versi akhir | Alasan perubahan |
|---|---|---|---|
| Review manusia | Teks yang tidak disepakati 3 AI dibagi ke 5 orang, 1 orang per teks. Kappa 0,393 dari 30 teks bersama | Setiap teks yang tidak disepakati dinilai 3 orang. Kappa 0,286 dari 881 kartu | Saran dosen. Label tidak lagi bergantung pada satu orang, dan kappa dihitung dari semua kartu |

Baris sesudah:

| Bagian | Versi awal | Versi akhir | Alasan perubahan |
|---|---|---|---|
| Review manusia | 871 kartu yang tidak disepakati 3 AI dibagi ke 5 orang, 1 orang per kartu. Kappa 0,393 dari 30 kartu kalibrasi yang dinilai kelima orang | Setiap teks yang tidak disepakati dinilai 3 orang. Kappa 0,286 dari 881 kartu | Saran dosen. Label tidak lagi bergantung pada satu orang, dan kappa dihitung dari semua kartu |

## 51. Perkembangan Metode: paragraf "Perubahan terbesar ada di label. Di versi awal, teks yang ti..." (diubah sebagian)

Sebelum:

> Karena labelnya berubah, angka versi awal dan versi akhir di Tabel 2 tidak bisa dibandingkan langsung.

Sesudah:

> Karena labelnya berubah, angka versi awal dan versi akhir di Tabel 4 tidak bisa dibandingkan langsung.

## 52. Result: paragraf "Setiap model dijalankan dengan dua input dan beberapa varian..." (diubah sebagian)

Sebelum:

> Setiap model dijalankan dengan dua input dan beberapa varian augmentasi, jadi totalnya ada 56 konfigurasi dari sembilan model.

Sesudah:

> Setiap model dijalankan dengan dua input dan beberapa varian augmentasi, jadi totalnya ada 57 konfigurasi dari sembilan model.

Sebelum:

> Tabel 3 mengambil satu konfigurasi terbaik untuk setiap model.

Sesudah:

> Tabel 5 mengambil satu konfigurasi terbaik untuk setiap model.

## 53. Result: paragraf "Tabel 5. Comparison Method..." (diubah sebagian)

Sebelum:

> Tabel 3.

Sesudah:

> Tabel 5.

## 54. Result: tabel dengan header "No | Method | Input dan augmentasi | P | R | F1-Score | F1 positif" (diubah)

Baris sebelum:

| No | Method | Input dan augmentasi | P | R | F1-Score | F1 positif |
|---|---|---|---|---|---|---|
| 4 | XLM-RoBERTa fine-tune | teks + judul, jalur B + parafrase | 0,579 | 0,592 | 0,580 ± 0,039 | 0,279 |

Baris sesudah:

| No | Method | Input dan augmentasi | P | R | F1-Score | F1 positif |
|---|---|---|---|---|---|---|
| 4 | XLM-RoBERTa fine-tune | teks + judul, jalur B + parafrase | 0,582 | 0,592 | 0,584 ± 0,017 | 0,295 |

## 55. Dampak judul dan augmentasi: paragraf "Judul menaikkan macro-F1 di semua model, paling besar di XLM..." (diubah sebagian)

Sebelum:

> Judul menaikkan macro-F1 di semua model, paling besar di IndoBERT embedding + LogReg (+0,064), XLM-RoBERTa (+0,060), dan TF-IDF + LogReg (+0,058).

Sesudah:

> Judul menaikkan macro-F1 di semua model, paling besar di XLM-RoBERTa (+0,071), IndoBERT embedding + LogReg (+0,064), dan TF-IDF + LogReg (+0,058).

## 56. Dampak judul dan augmentasi: paragraf baru

> Tabel 6. Macro-F1 tanpa dan dengan augmentasi (input teks + judul, fold sama)

## 57. Dampak judul dan augmentasi: tabel baru

| Model | Tanpa augmentasi | + jalur B | + parafrase | + jalur B + parafrase | + jalur B + terarah |
|---|---|---|---|---|---|
| TF-IDF + LogReg | 0,584 | 0,589 | 0,576 | 0,584 | 0,603 |
| TF-IDF + LinearSVM | 0,551 | - | - | 0,587 | - |
| IndoBERT fine-tune | 0,607 | 0,614 | 0,603 | 0,606 | 0,616 |
| IndoBERTweet fine-tune | 0,584 | 0,597 | 0,583 | 0,595 | 0,609 |
| XLM-RoBERTa fine-tune | 0,550 | 0,534 | 0,568 | 0,584 | 0,551 |
| IndoBERT embedding + LogReg | 0,585 | 0,586 | 0,569 | 0,570 | 0,570 |
| BiLSTM + attention | 0,507 | 0,512 | 0,499 | 0,498 | 0,505 |

## 58. Dampak judul dan augmentasi: paragraf baru

> Tabel 6 membandingkan setiap varian augmentasi langsung dengan kondisi tanpa augmentasi. Model, input, dan pembagian fold-nya sama, jadi yang berbeda hanya data positif tambahan di fold latih. Tanda "-" berarti kombinasi itu tidak dijalankan karena keterbatasan kuota GPU. Kalau semua konfigurasi dihitung, termasuk input teks saja, jalur B menaikkan macro-F1 di 8 dari 9 konfigurasi (rata-rata +0,008) dan F1 positif rata-rata +0,016. Satu-satunya yang turun adalah XLM-RoBERTa (0,550 ke 0,534), dan model ini juga paling tidak stabil antar fold, misalnya standar deviasi F1 positif jalur B mencapai 0,122. Jalur B + terarah membantu di 6 dari 9 konfigurasi. Parafrase hanya membantu XLM-RoBERTa (1 dari 9) dan justru menurunkan F1 positif rata-rata 0,018. Dari cek manual, sekitar 1 dari 6 parafrase maknanya rusak atau berbalik, dan parafrase memakai judul yang sama dengan teks aslinya, jadi model bisa menghafal judul. Untuk model utama, IndoBERT fine-tune, macro-F1 naik dari 0,607 tanpa augmentasi menjadi 0,616 dengan jalur B + terarah, dan F1 positif naik dari 0,293 menjadi 0,352.

## 59. Dampak judul dan augmentasi: paragraf "Tabel 7. Tambahan pelabelan terarah di atas jalur B..." (diubah sebagian)

Sebelum:

> Tabel 5. Dampak pelabelan terarah dibanding jalur B saja

Sesudah:

> Tabel 7. Tambahan pelabelan terarah di atas jalur B

## 60. Dampak judul dan augmentasi: tabel dengan header "Model | Input | Macro-F1 jalur B | + terarah | Fold membaik | F1 posit" (diubah)

Baris sebelum:

(tidak ada, baris baru)

Baris sesudah:

| Model | Input | Macro-F1 jalur B | + terarah | Fold membaik | F1 positif jalur B | + terarah |
|---|---|---|---|---|---|---|
| XLM-RoBERTa fine-tune | teks + judul | 0,534 | 0,551 | 3/5 | 0,198 | 0,279 |

## 61. Dampak judul dan augmentasi: paragraf "Berbeda dengan Tabel 6, Tabel 7 tidak membandingkan dengan k..." (diubah sebagian)

Sebelum:

> (tidak ada, kalimat baru)

Sesudah:

> Berbeda dengan Tabel 6, Tabel 7 tidak membandingkan dengan kondisi tanpa augmentasi, tetapi melihat tambahan yang diberikan teks terarah kalau jalur B sudah dipakai.

Sebelum:

> Tabel 5 menunjukkan dampaknya terbagi dua.

Sesudah:

> Tabel 7 menunjukkan dampaknya terbagi dua.

## 62. Dampak judul dan augmentasi: paragraf dihapus

> Tabel 4. Dampak augmentasi dibanding tanpa augmentasi

## 63. Dampak judul dan augmentasi: tabel dihapus

| Varian | Konfigurasi membaik | Rata-rata Δ macro-F1 | Rata-rata Δ F1 positif |
|---|---|---|---|
| jalur B | 9 dari 9 | 0,012 | 0,028 |
| parafrase | 1 dari 9 | -0,007 | -0,020 |
| jalur B + parafrase | 9 dari 14 | 0,013 | 0,026 |
| jalur B + terarah | 5 dari 8 | 0,009 | 0,023 |

## 64. Dampak judul dan augmentasi: paragraf dihapus

> Komentar positif jalur B menaikkan skor di 9 dari 9 konfigurasi. Parafrase hanya membantu XLM-RoBERTa dan justru menurunkan F1 positif rata-rata 0,020. Dari cek manual, sekitar 1 dari 6 parafrase maknanya rusak atau berbalik, dan parafrase memakai judul yang sama dengan teks aslinya, jadi model bisa menghafal judul. Pelabelan terarah membantu di 5 dari 8 konfigurasi.

## 65. Strategi lain untuk kelas positif: paragraf "Kalau semua teks ditebak positif, F1 positif hanya 0,049, da..." (diubah sebagian)

Sebelum:

> Menambahkan XLM-RoBERTa ke ensemble justru menurunkan macro-F1 dari 0,617 ke 0,602.

Sesudah:

> Menambahkan XLM-RoBERTa ke ensemble justru menurunkan macro-F1 dari 0,617 ke 0,612.

## 66. Discussion: paragraf "Temuan pertama, model fine-tune hanya sedikit lebih baik dar..." (diubah sebagian)

Sebelum:

> (tidak ada, kalimat baru)

Sesudah:

> Hal yang sama terjadi di XLM-RoBERTa. Kernelnya ikut selesai dijalankan ulang pada 24 November dan hasilnya menggantikan run pertama, sehingga konfigurasi teks + judul jalur B bergeser dari 0,563 ke 0,534. Semua angka XLM-RoBERTa di laporan ini memakai run kedua.

## 67. Discussion: paragraf "Tabel 8 melengkapi Tabel 4. Kalau Tabel 4 berisi apa yang be..." (diubah sebagian)

Sebelum:

> Tabel 6 melengkapi Tabel 2. Kalau Tabel 2 berisi apa yang berubah dari versi awal, Tabel 6 berisi hasil dari setiap saran dosen setelah kami kerjakan.

Sesudah:

> Tabel 8 melengkapi Tabel 4. Kalau Tabel 4 berisi apa yang berubah dari versi awal, Tabel 8 berisi hasil dari setiap saran dosen setelah kami kerjakan.

## 68. Discussion: paragraf "Tabel 8. Saran dosen dan tindak lanjutnya..." (diubah sebagian)

Sebelum:

> Tabel 6.

Sesudah:

> Tabel 8.

## 69. Discussion: tabel dengan header "Saran dosen | Yang kami kerjakan | Hasil" (diubah)

Baris sebelum:

| Saran dosen | Yang kami kerjakan | Hasil |
|---|---|---|
| Relevansi dan buzzer harus jelas siapa yang memutuskan | Kata kunci dan skor menandai, manusia memutuskan, tidak_relevan dinilai 3 AI dan 3 orang | 14 buzzer dan 182 teks tidak relevan dikeluarkan |

Baris sesudah:

| Saran dosen | Yang kami kerjakan | Hasil |
|---|---|---|
| Relevansi dan buzzer harus jelas siapa yang memutuskan | Kata kunci dan skor menandai, manusia memutuskan, tidak_relevan dinilai 3 AI dan 3 orang | 36 teks dikeluarkan di gerbang buzzer, 14 lagi setelah review, dan 182 teks tidak relevan dikeluarkan. Kriterianya di Tabel 2 dan Tabel 3 |

Baris sebelum:

| Saran dosen | Yang kami kerjakan | Hasil |
|---|---|---|
| Sampel positif dari akun Raffi dan augmentasi | Jalur B, parafrase back-translation, dan pelabelan terarah, hanya di fold latih | Jalur B membantu 9/9, parafrase 1/9, terarah 5/8 |

Baris sesudah:

| Saran dosen | Yang kami kerjakan | Hasil |
|---|---|---|
| Sampel positif dari akun Raffi dan augmentasi | Jalur B, parafrase back-translation, dan pelabelan terarah, hanya di fold latih | Jalur B membantu 8/9, parafrase 1/9, terarah 6/9 |

## 70. Discussion: paragraf "Keterbatasan penelitian ini ada di jumlah teks positif yang ..." (diubah sebagian)

Sebelum:

> Tujuh kartu terarah yang seri juga diputus dengan mayoritas 3 LLM, bukan lewat diskusi tim. XLM-RoBERTa tidak dilatih ulang dengan varian terarah karena paling lemah dan satu kernel butuh sekitar satu jam GPU.

Sesudah:

> Tujuh kartu terarah yang seri juga diputus dengan mayoritas 3 LLM, bukan lewat diskusi tim, walaupun dampaknya paling banyak satu teks augmentasi. Lima balasan X yang tweet induknya tidak ter-scrape ikut terbuang di gerbang relevansi, dan penandaan buzzer hanya menunjukkan indikasi, bukan bukti bahwa akunnya dibayar. Penilai manusia juga bisa melihat suara ketiga LLM saat menilai, jadi label manusia mungkin ikut terpengaruh label LLM.

## 71. References: paragraf dihapus

> Cresci, S. (2020). A decade of social bot detection. Communications of the ACM, 63(10), 72–83.

## 72. References: paragraf baru

> Hays, C., Schutzman, Z., Raghavan, M., Walk, E., & Zimmer, P. (2023). Simplistic collection and labeling practices limit the utility of benchmark datasets for Twitter bot detection. In Proceedings of the ACM Web Conference 2023. Association for Computing Machinery.

## 73. References: paragraf baru

> Minaee, S., Kalchbrenner, N., Cambria, E., Nikzad, N., Chenaghlu, M., & Gao, J. (2021). Deep learning-based text classification: A comprehensive review. ACM Computing Surveys, 54(3), 1–40.

## 74. References: paragraf dihapus

> Koto, F., Rahimi, A., Lau, J. H., & Baldwin, T. (2020). IndoLEM and IndoBERT: A benchmark dataset and pre-trained language model for Indonesian NLP. In Proceedings of the 28th International Conference on Computational Linguistics. International Committee on Computational Linguistics.

## 75. References: paragraf dihapus

> Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159–174.

## 76. References: paragraf baru

> Sastramidjaja, Y., & Wijayanto. (2022). Cyber troops, online manipulation of public opinion and co-optation of Indonesia's cybersphere (Trends in Southeast Asia, No. 7). ISEAS–Yusof Ishak Institute.

## 77. References: paragraf dihapus

> Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLoS ONE, 10(3), e0118432.

## 78. References: paragraf dihapus

> Sennrich, R., Haddow, B., & Birch, A. (2016). Improving neural machine translation models with monolingual data. In Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics. Association for Computational Linguistics.

## 79. References: paragraf "Tiedemann, J., Aulamo, M., Bakshandaeva, D., Boggia, M., Grö..." (diubah sebagian)

Sebelum:

> Tiedemann, J., & Thottingal, S. (2020). OPUS-MT: Building open translation services for the world. In Proceedings of the 22nd Annual Conference of the European Association for Machine Translation. European Association for Machine Translation.

Sesudah:

> Tiedemann, J., Aulamo, M., Bakshandaeva, D., Boggia, M., Grönroos, S.-A., Nieminen, T., Raganato, A., Scherrer, Y., Vázquez, R., & Virpioja, S. (2024). Democratizing neural machine translation with OPUS-MT. Language Resources and Evaluation, 58, 713–755.

## 80. References: paragraf dihapus

> Zhou, P., Shi, W., Tian, J., Qi, Z., Li, B., Hao, H., & Xu, B. (2016). Attention-based bidirectional long short-term memory networks for relation classification. In Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). Association for Computational Linguistics.
