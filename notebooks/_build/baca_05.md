@@ rekap
Ada 56 konfigurasi dari 9 model. Urutan teratas diisi model fine-tune dengan input teks + judul. IndoBERT dengan augmentasi jalur B + terarah ada di urutan pertama (0,616), lalu IndoBERT jalur B (0,614) dan IndoBERTweet jalur B + terarah (0,609). Selisih tiga teratas ini sangat kecil, jadi praktis seri. Baseline TF-IDF terbaik muncul di urutan 7 (0,603), juga dengan jalur B + terarah. Jarak antara model terbaik dan TF-IDF hanya 0,013, lebih kecil dari yang saya kira. XLM-RoBERTa terbaiknya baru di urutan 19 (0,580).

Satu catatan soal angka. Kernel IndoBERTweet dijalankan ulang di Kaggle untuk menambah varian terarah, dan konfigurasi lama ikut dilatih ulang. Karena pelatihan di GPU tidak sepenuhnya deterministik, skor lamanya ikut bergeser, misalnya IndoBERTweet jalur B dari 0,614 menjadi 0,597. Pergeseran sebesar ini masih di dalam standar deviasi antar fold (sekitar 0,02 sampai 0,04), dan ini sekaligus menunjukkan bahwa selisih di bawah 0,02 antar konfigurasi tidak boleh dibaca sebagai kemenangan yang pasti.

@@ terbaik
Kalau diambil satu konfigurasi terbaik per model, urutannya: IndoBERT fine-tune (0,616), IndoBERTweet fine-tune (0,609), TF-IDF + LogReg (0,603), TF-IDF + LinearSVM (0,587), IndoBERT embedding + LogReg (0,586), XLM-RoBERTa fine-tune (0,580), lalu BiLSTM + attention (0,514). IndoBERT embedding + LogReg setara dengan TF-IDF, jadi representasi IndoBERT tanpa dilatih ulang belum memberi kelebihan. Kenaikan baru muncul saat bobot IndoBERT ikut dilatih (fine-tune). XLM-RoBERTa kalah dari kedua model Indonesia walaupun sama-sama di-fine-tune, karena model ini dilatih untuk 100 bahasa sehingga kosakata bahasa gaul Indonesia-nya lebih sedikit. BiLSTM paling rendah karena 3.329 teks terlalu sedikit untuk melatih LSTM dari awal. Di semua model, F1 positif paling rendah (0,26 sampai 0,35).

@@ dampak-aug
Tabel ini membandingkan setiap varian augmentasi dengan versi tanpa augmentasi di model dan input yang sama. Jalur B selalu menaikkan skor, walaupun kadang kecil, misalnya IndoBERTweet teks + judul naik 0,013 dan IndoBERT naik 0,008. Parafrase hampir selalu menurunkan skor atau tidak berpengaruh, misalnya IndoBERT teks + judul turun 0,003 dan BiLSTM teks saja turun 0,026 tanpa satu fold pun membaik. Pengecualiannya Linear SVM, yang naik 0,031 sampai 0,036 dengan augmentasi lengkap, karena tanpa augmentasi SVM hampir tidak pernah menebak positif. XLM-RoBERTa juga pengecualian: semua varian augmentasi menaikkan skornya, termasuk parafrase (+0,013), karena tanpa augmentasi model ini paling lemah di kelas positif (F1 positif 0,225).

Varian jalur B + terarah dibahas lebih rinci di bagian hasil pelabelan terarah di bawah.

@@ dampak-aug-rata
Dirata-rata di semua model, jalur B membaik di 9 dari 9 konfigurasi (+0,012 macro-F1, +0,028 F1 positif), sedangkan parafrase hanya membaik di 1 dari 9 (-0,007 macro-F1, -0,020 F1 positif), yaitu di XLM-RoBERTa. Gabungan jalur B + parafrase rata-ratanya mirip jalur B (+0,013), tapi hanya membaik di 9 dari 14 konfigurasi, dan rata-rata itu terangkat oleh Linear SVM dan XLM-RoBERTa yang memang lemah tanpa augmentasi. Jalur B + terarah membaik di 5 dari 8 konfigurasi (+0,009). Jadi yang paling konsisten membantu adalah komentar positif asli dari jalur B, bukan parafrase.

Saya melihat dua penyebab parafrase gagal. Pertama, sekitar 1 dari 6 parafrase maknanya rusak atau berbalik (hasil cek manual di notebook 02), jadi model belajar dari label yang salah. Kedua, parafrase memakai judul yang sama dengan teks aslinya, jadi model bisa menghafal judul unggahan yang banyak positifnya, bukan cara orang membela Raffi. Komentar jalur B ditulis orang lain di unggahan lain, jadi variasinya asli. Keputusannya: parafrase tidak dipakai.

@@ dampak-judul
Judul menaikkan macro-F1 di semua model, paling besar di IndoBERT embedding + LogReg (+0,064), XLM-RoBERTa (+0,060), dan TF-IDF + LogReg (+0,058), dan di ketiganya membaik di 5 dari 5 fold. IndoBERT fine-tune juga naik 0,048 di 5 dari 5 fold. Untuk IndoBERTweet kenaikannya kecil (+0,006, 3 dari 5 fold), dan F1 positif-nya malah turun. Dugaan saya, IndoBERTweet dilatih dari tweet pendek, sedangkan input teks + judul bisa sampai 256 token dengan judul berita yang panjang.

@@ per-fold
Model terbaik (IndoBERT, teks + judul, jalur B + terarah) dibandingkan dengan TF-IDF + LogReg terbaik (teks + judul, jalur B + terarah). Model terbaik unggul di 3 dari 5 fold, seri di fold 2, dan kalah di fold 4 (-0,028). Jadi kelebihan model transformer di data ini belum konsisten. F1 positif-nya naik turun jauh, dari 0,258 di fold 1 sampai 0,519 di fold 3, karena setiap fold hanya punya 16 atau 17 teks positif.

@@ strategi
Pertama, seberapa jelek F1 positif 0,3? Kalau semua teks ditebak positif, F1 positif hanya 0,049, dan average precision (AP) tebakan acak 0,025. Model terbaik mendapat AP 0,383, kira-kira 15 kali tebakan acak. Jadi modelnya memang belajar sesuatu, tapi masih jauh dari bagus. Standar deviasi F1 positif antar fold sekitar 0,1, karena satu teks positif yang benar atau salah sudah menggeser F1 sekitar 0,03 sampai 0,05.

Kedua, ensemble. Rata-rata probabilitas IndoBERT dan IndoBERTweet (keduanya teks + judul + jalur B + terarah) mendapat macro-F1 0,628, tertinggi dari semua konfigurasi, dengan AP positif 0,381. Versi jalur B saja mendapat 0,617 (AP 0,346). Kenaikan macro-F1 ensemble dibanding model tunggal terbaik hanya 0,012 dan masih di dalam standar deviasi, dan AP-nya tidak lebih tinggi dari IndoBERT terarah sendirian (0,383). Jadi ensemble di sini lebih banyak menstabilkan tebakan netral dan negatif daripada menambah kemampuan menemukan teks positif. Kalau XLM-RoBERTa ikut dirata-rata (versi jalur B), macro-F1 malah turun dari 0,617 ke 0,602, karena model ketiga ini jauh lebih lemah (AP 0,245). Jadi ensemble yang dipakai cukup IndoBERT dan IndoBERTweet.

Ketiga, menggeser ambang kelas positif. Bobot dipilih dari 4 fold lain lalu dipakai di fold uji. Hasilnya tidak konsisten. Untuk IndoBERTweet jalur B, F1 positif malah turun dari 0,295 ke 0,277, untuk IndoBERT terarah turun dari 0,352 ke 0,340, dan bobot yang terpilih berbeda-beda tiap fold (0,5 sampai 2). Hanya ensemble 3 model yang naik (0,602 ke 0,620), dan itu pun karena model ketiganya menarik probabilitas positif turun. Model dengan class weight sudah cukup berani menebak positif, dan ambang terbaik di satu fold tidak berlaku di fold lain. Jadi cara ini tidak dipakai.

@@ kurva
Dengan 17 teks positif di data latih, F1 positif hanya 0,064. Naik ke 0,082 dengan 33 teks, lalu melompat ke 0,210 dengan 50 teks dan 0,272 dengan 67 teks. Kurvanya belum mendatar di ujung kanan, jadi model belum jenuh. Kalau teks positif asli ditambah, F1 positif kemungkinan besar masih naik. Ini berbeda dengan parafrase, yang menambah jumlah tapi tidak menambah variasi.

@@ peringkat
Kalau teks diurutkan berdasarkan skor positif, 50 teks teratas berisi 17 positif (34%), 100 teratas berisi 26 (26%), dan 200 teratas berisi 38 (19%). Kalau diambil acak, 200 teks hanya berisi sekitar 5 positif. Dari sini saya menyarankan pelabelan terarah dari 2.623 teks cadangan, bukan scraping ulang: model mengurutkan teks cadangan, lalu teks teratas dilabeli dengan alur yang sama (3 AI, lalu 3 orang untuk teks yang tidak disepakati). Waktu itu saya memperkirakan 40 sampai 60 positif baru dari 300 teks.

Ada satu syarat. Teks dari pelabelan terarah sengaja dipilih yang condong positif, jadi tidak boleh masuk data uji atau statistik sentimen di notebook 06. Perlakuannya sama seperti jalur B, yaitu hanya menambah data latih. Hasil sebenarnya ada di bagian berikut.

@@ terarah
Hasilnya di bawah perkiraan. Dari 250 teks dengan skor positif tertinggi, hanya 33 yang positif (13%), dan dari 50 teks acak ada 2 (4%). Totalnya 35 positif dari 300 teks, bukan 40 sampai 60. Presisinya juga lebih rendah dari peringkat di data berlabel (19% di 200 teratas). Dugaan saya, teks cadangan memang sisa yang tidak terpilih di sampel utama, dan 18 di antaranya ternyata tidak relevan. Walaupun begitu, pengurutan tetap sekitar 3 kali lebih efisien daripada sampel acak. Setelah 2 teks dibuang karena akunnya sudah ada di dataset final dan 1 teks dinilai buzzer, ada 32 teks positif baru untuk augmentasi.

Labelnya berasal dari 227 teks yang disepakati bulat 3 AI, 66 teks yang diputuskan mayoritas 3 orang, dan 7 kartu yang ketiga penilainya memilih label berbeda. Untuk 7 kartu ini koordinator memakai label mayoritas 3 AI, dan keputusannya dicatat di `labeling/terarah/review/koordinator.csv` supaya bisa diubah kalau tim tidak setuju. Fleiss' kappa di 73 kartu review adalah 0,260, setara dengan review utama (0,286). Kappa positif paling tinggi (0,549), sedangkan netral paling rendah (0,116).

Dampaknya ke model terbagi dua. TF-IDF dan model fine-tune terbantu: TF-IDF + LogReg teks + judul naik 0,015 (4 dari 5 fold) dengan F1 positif naik 0,047, IndoBERTweet naik 0,012, dan IndoBERT praktis sama (+0,001), tapi F1 positif-nya naik 0,028 dan AP positif naik dari 0,333 ke 0,383. Sebaliknya, model yang bobot BERT-nya dibekukan malah turun: IndoBERT embedding + LogReg turun 0,016 di kedua input, dan BiLSTM turun 0,006 sampai 0,016. Dugaan saya, teks terarah dipilih dari skor TF-IDF, jadi isinya condong ke kata yang memang sudah dikenali TF-IDF, sedangkan untuk model dengan representasi beku, 32 teks ini lebih menggeser batas kelas daripada menambah pola baru. Semua kenaikan ini masih di dalam standar deviasi antar fold, jadi terarah membantu sedikit, bukan lompatan besar.

XLM-RoBERTa tidak dilatih ulang dengan varian terarah. Model ini paling lemah di antara model fine-tune dan satu kernel butuh sekitar 1 jam GPU, jadi kuota Kaggle dipakai untuk IndoBERT dan IndoBERTweet saja.

@@ lowercase
Kedua tokenizer mencetak `do_lower_case` True. IndoBERTweet memecah "BOIKOT RANS" menjadi `['boikot', 'ran', '##s']`, dan IndoBERT menjadi `['bo', '##ikot', 'rans']`, sama persis dengan versi huruf kecilnya. Jadi untuk IndoBERTweet dan IndoBERT, teks di-lowercase atau tidak di preprocessing hasilnya sama, karena tokenizer tetap mengubahnya menjadi huruf kecil. Percobaan dengan dan tanpa lowercase tidak perlu dijalankan untuk dua model ini. Satu-satunya model yang membaca huruf kapital adalah XLM-RoBERTa (cased).

@@ cm
Recall negatif 82,2%, netral 67,4%, dan positif 35,7%. Recall positif ini lebih tinggi dari model jalur B sebelumnya (27,4%), dan ini efek langsung dari teks positif terarah. Teks positif yang salah hampir semuanya ditebak negatif (57,1% dari semua teks positif), hanya 7,1% yang ditebak netral.

@@ kelompok
Model paling sering salah di teks yang juga mengkritik pihak lain (macro-F1 0,490 dibanding 0,620) dan teks yang ditandai butuh judul (0,530 dibanding 0,675). Teks lebih dari 40 kata juga lebih sulit (akurasi 66,7%, teks 1 sampai 5 kata 81,3%). Per platform, X paling rendah (macro-F1 0,536), kemungkinan karena separuh tweet tidak punya judul. Teks sarkasme akurasinya tinggi (84,1%) karena hampir semuanya negatif, tapi macro-F1-nya rendah (0,510). Fase pasca lebih sulit dari fase puncak (0,569 dibanding 0,647), karena di fase pasca topiknya melebar ke kontrak Rp14,7 miliar dan bisnis Raffi.

@@ jenis-salah
Dari 786 teks yang salah (23,6%), dua kesalahan terbesar adalah negatif ditebak netral (341) dan netral ditebak negatif (331). Ini batas yang sama dengan yang paling sering diperdebatkan penilai manusia (kappa netral 0,219). Untuk teks positif, dukungan cukup sering benar (77,3%), tapi pembelaan hanya benar 16,7% (7 dari 42). Angka pembelaan ini naik dari 4 dari 42 di model jalur B, tapi tetap jenis teks positif yang paling sulit.

@@ contoh
Contoh positif yang ditebak negatif memperlihatkan polanya. Hampir semuanya pembelaan yang ditulis dengan nada kesal ke pengkritik Raffi, misalnya "Herannya klen ngamuk sama raffi ahmad tapi gk ada yg ngamuk sama si zaskia mecca...", "kerja namany itu proooo dunia gak ada gratisss fahammmmm", dan "netizen harusnya paham bedanya tamu undangan instansi sama peserta aksi massa". Model membaca nadanya, bukan sasarannya.

Contoh netral yang ditebak negatif ada dua jenis: berita yang menyebut Raffi bersama kata yang terdengar negatif ("Rans festival sepi setelah beberapa pihak memboikot raffi ahmad..."), dan kemarahan ke pihak lain, misalnya ke pemerintah ("tahun lalu uya kuya dan syahroni yang ditumbalin...") atau ke buzzer. Contoh negatif yang ditebak netral kebanyakan sindiran yang butuh pengetahuan kasus, seperti "3M buat karhutla kata Desta Raffi : masih ada 11M brooo 🤣🤣🤣" dan "Didunia ini gak ada yg abadi. Sepandai2 raffi ahmad akhirnya jatuh juga 😜". Ada juga kritik yang cukup jelas tapi tetap lolos, misalnya "Udah jelas KKN ini. Segera cekal rafi ahmad dan tangkap."

@@ diperbaiki
Ada 428 teks yang salah di kedua model. Sebanyak 354 teks salah di baseline tapi benar di model terbaik, dan 358 sebaliknya. Jadi kedua model salah di teks yang cukup berbeda, dan jumlah perbaikannya hampir sama dengan jumlah kemundurannya, sejalan dengan selisih macro-F1 yang kecil. Contoh yang diperbaiki model terbaik hampir semuanya teks netral yang ditebak negatif oleh TF-IDF karena memuat kata seperti "bully", "miris", atau "nyalahkan", misalnya "Gara2 video ini aktor raffi ahmad di bully netizen sebelah 😂" dan "Astaghfirullaah. Mirisnya negeriku 😢". TF-IDF hanya menghitung kata, sedangkan IndoBERT bisa membaca bahwa kata negatif itu bukan sikap penulis terhadap Raffi.

@@ saran-dosen
| saran dosen | yang dikerjakan | hasil | bukti |
|---|---|---|---|
| Gerbang filter jangan overklaim | Aturan otomatis hanya menandai kandidat, setiap kandidat dibaca manual | 61 teks diselamatkan | `data/03_filtered/audit/keputusan_manual.csv`, notebook 01 |
| Relevansi dan buzzer: siapa yang memutuskan | Relevansi: kata kunci menandai, manusia memutuskan, lalu `tidak_relevan` dinilai 3 AI dan 3 orang. Buzzer: aturan keras dan skor poin, zona batas diputuskan manusia | 14 buzzer dan 182 tidak relevan dikeluarkan | `dokumentasi_data.md` bagian 2, `data/05_final/laporan_kesiapan.md` |
| Label dinilai 3 orang, hitung Fleiss' kappa | Semua teks yang tidak disepakati 3 AI dinilai 3 orang, termasuk teks pelabelan terarah | 881 kartu, kappa 0,286; terarah 73 kartu, kappa 0,260 | `labeling/review/3lapis/ringkasan_kappa.md`, `labeling/terarah/ringkasan_terarah.md` |
| Hapus target biner | Semua model 3 kelas | tidak ada target biner | notebook 02 sampai 05 |
| Sampel positif dari akun Raffi, augmentasi | Jalur B, parafrase, dan pelabelan terarah, hanya di fold latih, diuji per varian | jalur B membantu 9/9, parafrase 1/9, terarah 5/8 | bagian dampak augmentasi dan hasil pelabelan terarah |
| BERT tanpa lowercase | Teks dikirim apa adanya, emoji jadi kata Indonesia | IndoBERTweet dan IndoBERT uncased, jadi tidak berpengaruh | bagian lowercase di atas, log Kaggle |
| IndoBERT embedding + LogReg, model kontekstual | Embedding + LogReg, BiLSTM, fine-tune 3 model | fine-tune terbaik (0,616) | notebook 03 dan 04 |
| F1 positif rendah | Ensemble, ambang, learning curve, peringkat cadangan, pelabelan terarah | terarah dan ensemble membantu sedikit, ambang tidak | bagian strategi dan hasil pelabelan terarah |
| Analisis kesalahan | Confusion matrix, per kelompok, contoh | pembelaan bernada marah paling sering salah (hanya 16,7% benar) | bagian analisis kesalahan |

@@ kesimpulan
## Kesimpulan

- Model tunggal terbaik adalah fine-tune IndoBERT dengan input teks + judul dan augmentasi jalur B + terarah (macro-F1 0,616), praktis seri dengan IndoBERT jalur B (0,614) dan IndoBERTweet jalur B + terarah (0,609). Ensemble IndoBERT + IndoBERTweet dengan augmentasi yang sama paling tinggi (0,628, AP positif 0,381). XLM-RoBERTa lebih lemah (0,580) dan tidak menambah apa-apa kalau ikut di-ensemble.
- Jarak dengan TF-IDF + LogReg terbaik (0,603) kecil dan model terbaik hanya unggul di 3 dari 5 fold.
- Judul adalah tambahan input yang paling konsisten membantu.
- Augmentasi jalur B membantu di semua konfigurasi, sedangkan parafrase back-translation hanya membantu XLM-RoBERTa, model yang paling lemah.
- Pelabelan terarah menghasilkan 35 positif dari 300 teks (13% di teks skor tertinggi, 4% di teks acak) dan 32 dipakai sebagai augmentasi. Hasilnya menaikkan F1 positif dan AP model fine-tune dan TF-IDF, tapi menurunkan model dengan representasi beku, dan semua perubahannya masih di dalam variasi antar fold. Jadi terarah membantu sedikit, bukan lompatan besar.
- Menggeser ambang kelas positif tidak membantu secara konsisten.
- F1 positif sekitar 0,35 masih rendah, tapi sekitar 15 kali tebakan acak kalau dilihat dari AP. Learning curve belum jenuh, jadi menambah teks positif asli tetap langkah paling menjanjikan, hanya saja teks cadangan yang tersisa ternyata tidak sekaya perkiraan awal.
- Kesalahan utama model ada di pembelaan yang ditulis dengan nada marah ke pengkritik Raffi, dan di batas negatif dan netral yang juga diperdebatkan penilai manusia.
