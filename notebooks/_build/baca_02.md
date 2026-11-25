@@ data
Dataset berisi 3.329 teks: 2.206 negatif (66,3%), 1.039 netral (31,2%), dan 84 positif (2,5%). Label ini sudah final. Teks yang tidak disepakati bulat ketiga AI dinilai lengkap oleh 3 orang (review 3 lapis, 881 kartu), lalu diambil suara terbanyak, dan 29 kartu yang ketiganya berbeda diputus lewat diskusi tim. Kolom `fold` dibuat oleh `labeling/finalize.py`. Tiap fold berisi 665 sampai 666 teks dengan 16 atau 17 teks positif.

@@ judul
Contoh di atas memperlihatkan kenapa judul dibutuhkan. "wajib di Audit." tidak menyebut siapa pun, tapi judulnya "ICW Bongkar Raffi Ahmad Terima Kontrak Jasa Influencer Rp14 Miliar dari APBN", jadi yang diminta diaudit adalah kontrak Raffi. "Wkwk jadi tau kan siapa yang mahasewa?" juga baru jelas sasarannya setelah membaca caption "MUAK BANGET sama Willie Salim & Raffi Ahmad". Contoh X memperlihatkan keterbatasan judul di X: judulnya hanya tweet induk yang dibalas atau dikutip, dan kalau tweet induknya tidak ikut ter-scrape, judulnya hanya keterangan bahwa tweet ini membalas akun lain.

@@ punya-judul
Semua komentar Instagram, TikTok, dan YouTube punya judul, sedangkan di X hanya 52,1% (tweet yang mengutip atau membalas). Secara keseluruhan 81,8% teks punya judul.

@@ statistik
Teksnya pendek. Setengah teks hanya 12 kata atau kurang, dan 95% di bawah 63 kata. Sebanyak 27,7% teks memuat emoji, jadi cara emoji diubah memang berpengaruh. Ada 19,0% teks yang memuat kata kapital minimal 4 huruf, misalnya "BOIKOT" atau "MAMPUS". Inilah alasan lowercase tidak dipakai untuk model BERT. Separuh teks (50,8%) ditandai annotator butuh judul supaya maknanya jelas.

@@ prepro
Contoh di atas memperlihatkan perbedaan ketiga versi. Di `teks_bert`, "KAMI ADALAH PUTERA DAN PUTERI BAYARAN" tetap kapital dan 😂 menjadi "wajah gembira berurai air mata". Di `teks_lengkap` untuk TF-IDF, semua menjadi huruf kecil, emoji menjadi satu token `emo_wajah_gembira_berurai_air_mata`, stopword seperti "adalah" dan "dan" dibuang, dan slang dinormalisasi, misalnya "gk" menjadi "enggak" dan "yah" menjadi "ya".

@@ contoh-input
Komentar ini tidak menyebut Raffi sama sekali ("yang datang adalah yang mau update liputan kalau acaranya sepi"). Labelnya negatif karena judulnya "RAFFI AHMAD MAKIN TERPOJOK! ... TIBA-TIBA DIDEMO PAS BAWA ACARA!", jadi yang diejek sepi adalah acara yang dibawakan Raffi. Model teks saja tidak punya cara untuk mengetahuinya. Untuk BERT, judul ditaruh setelah `[SEP]` dan huruf kapitalnya tetap.

@@ kosakata
Normalisasi emoji, tawa, dan slang memangkas kosakata dari 15.251 menjadi 10.141 kata unik. Membuang stopword hanya mengurangi kosakata sedikit (9.734), tapi rata-rata panjang teks turun dari 21,9 menjadi 14,8 token. Stemming memangkas kosakata paling banyak (7.469). Dampaknya ke model diuji di bagian ablation.

@@ bt-saring
Back-translation menghasilkan 484 parafrase dari 177 teks. Lima parafrase terakhir berasal dari 2 teks yang dulu belum pernah dinilai positif, sehingga dijalankan tersendiri di Kaggle (`augmentasi/siapkan_bt_tambahan.py`). Kedua teks itu akhirnya dikoreksi menjadi negatif, jadi parafrasenya tidak terpakai. Saringan otomatis membuang 140 parafrase yang jelas rusak: 61 karena mention `@user` berubah (MarianMT kadang menerjemahkan nama pengganti sementara menjadi kata lain seperti "Burdi"), 51 karena terpotong lebih dari separuh, 19 karena muncul simbol aneh seperti ♪ dan ▪, 7 karena pengulangan karakter, dan 2 karena terlalu pendek. Tersisa 344 parafrase.

Saringan otomatis tidak bisa mengecek makna, jadi saya membaca 40 parafrase acak yang lolos. Hasilnya 33 dari 40 (82,5%) masih mempertahankan sikap positif ke Raffi, misalnya "sabar raffi ahmad masi banyak orang yg percaya sm km" menjadi "bersabar, Raffi ahmad masih banyak orang yang percaya padamu". Sisanya 7 rusak, dan yang paling berbahaya adalah makna yang berbalik, seperti "Ujian orang baik ,, sehat sehat a Raffi" menjadi "Raffi sangat berbahaya". Jadi sekitar 1 dari 6 parafrase kemungkinan membawa label yang salah. Ini kelemahan back-translation untuk teks gaul, dan dampaknya akan terlihat dari perbandingan dengan dan tanpa parafrase di bawah. Daftar lengkap hasil cek ada di `augmentasi/cek_manual_bt.csv`.

@@ aug
Data augmentasi berisi 295 teks positif: 42 komentar jalur B, 172 parafrase dari teks positif data utama, dan 81 parafrase dari komentar jalur B. Hanya parafrase dari teks yang label akhirnya positif yang dipakai. Judul parafrase disamakan dengan judul teks aslinya. Kolom `fold_asal` menyimpan fold teks asli, jadi parafrase dari teks di fold uji bisa dibuang saat training. Komentar jalur B dan parafrasenya diberi `fold_asal` -1, karena tidak ada di data uji mana pun.

@@ baseline-awal
Tebak kelas terbanyak mendapat macro-F1 0,266 dengan F1 positif dan netral 0, walaupun akurasinya 0,663. Leksikon InSet hanya sedikit lebih baik (0,315). Tabel skor InSet menjelaskan kenapa: median skor ketiga kelas sama-sama negatif (-3 untuk negatif dan netral, -2 untuk positif). InSet mengukur nada kata, bukan sikap ke Raffi. Pembelaan yang marah ke pengkritik Raffi tetap mendapat skor negatif.

@@ tfidf
TF-IDF jauh di atas kedua baseline. Tanpa augmentasi, LogReg dengan teks saja mendapat 0,526 dan naik ke **0,584 ± 0,019** setelah judul ditambahkan. Linear SVM di bawahnya (0,506 dan 0,551). Hasil augmentasi dibahas di tabel berikutnya.

@@ rekap
Konfigurasi terbaik adalah **TF-IDF + LogReg, teks + judul, dengan augmentasi jalur B (0,589 ± 0,009)**. Selisihnya sangat tipis dengan Linear SVM teks + judul + augmentasi lengkap (0,587 ± 0,021) dan LogReg teks + judul tanpa augmentasi (0,584 ± 0,019). Jadi ketiganya praktis setara, tapi konfigurasi terbaik punya standar deviasi paling kecil.

Tabel dampak memperlihatkan bahwa efek augmentasi bergantung pada modelnya:

- **Linear SVM paling terbantu.** Augmentasi lengkap menaikkan macro-F1 sebesar 0,031 (teks saja) dan 0,036 (teks + judul), membaik di 4 dari 5 fold, dan F1 positif naik 0,093 sampai 0,108. SVM tanpa augmentasi jarang menebak positif (F1 positif 0,123 dan 0,165), dan 260 contoh positif tambahan per fold menggeser batas keputusannya.
- **Jalur B adalah augmentasi yang paling aman.** Untuk LogReg teks saja, jalur B memberi +0,025 dan membaik di kelima fold, dengan F1 positif +0,063.
- **Parafrase saja tidak membantu LogReg.** Selisihnya -0,009 di kedua input, dan hanya membaik di 2 dari 5 fold.
- **LogReg teks + judul hampir tidak berubah.** Selisihnya antara -0,009 dan +0,004, dan F1 positif justru turun sekitar 0,03. Dugaan saya, LogReg dengan class weight sudah memberi bobot besar ke kelas positif, jadi contoh tambahan tidak banyak mengubah. Parafrase juga membawa sekitar 17% label yang salah, dan parafrase memakai judul yang sama dengan teks aslinya, jadi model bisa menghafal judul unggahan yang banyak positifnya.

@@ grafik
Grafik ini merangkum tabel di atas. Batang abu-abu adalah dua baseline tanpa pembelajaran, biru tanpa augmentasi, dan oranye dengan augmentasi. Konfigurasi teks + judul selalu berada di atas teks saja, dan selisih antar varian augmentasi lebih kecil daripada selisih karena judul.

@@ ablasi
Keempat versi preprocessing hampir sama (0,526 sampai 0,552), dan perbedaannya lebih kecil dari standar deviasi antar fold (0,027 sampai 0,037). Versi "+ emoji, tawa, slang" sedikit paling tinggi (0,552), sedangkan membuang stopword justru menurunkan skor sedikit (0,526). Jadi untuk TF-IDF dengan n-gram huruf, langkah normalisasi tambahan tidak memberi dampak yang bisa dipastikan. Yang dampaknya jelas adalah **class weight**: tanpa class weight macro-F1 turun menjadi 0,483 dan F1 positif tinggal 0,062, karena model hampir tidak pernah menebak positif.

@@ kesimpulan
## Kesimpulan

Baseline terbaik adalah TF-IDF + LogReg dengan teks + judul dan augmentasi jalur B (macro-F1 0,589 ± 0,009), praktis setara dengan Linear SVM teks + judul + augmentasi lengkap (0,587 ± 0,021) dan LogReg teks + judul tanpa augmentasi (0,584 ± 0,019). Ketiganya jauh di atas tebak kelas terbanyak (0,266) dan leksikon InSet (0,315).

Dampak setiap metode yang diuji:

- **Judul** adalah tambahan yang paling berpengaruh: +0,058 untuk LogReg dan +0,045 untuk SVM tanpa augmentasi.
- **Augmentasi** membantu model yang lemah di kelas positif (SVM: +0,031 sampai +0,036, F1 positif +0,09 sampai +0,11) dan LogReg teks saja dengan jalur B (+0,025, membaik di 5 dari 5 fold), tapi hampir tidak mengubah LogReg teks + judul. Jalur B lebih aman daripada parafrase, karena parafrase back-translation membawa sekitar 17% makna yang rusak atau berbalik.
- **Class weight** penting: tanpanya macro-F1 turun 0,043 dan F1 positif turun dari 0,206 ke 0,062.
- **Langkah preprocessing** (slang, stopword, stemming) tidak memberi perbedaan yang melebihi variasi antar fold.

Kelas positif tetap yang paling lemah (F1 sekitar 0,27 sampai 0,30). TF-IDF hanya menghitung kata, jadi pembelaan yang ditulis dengan nada marah ke pengkritik Raffi tetap terbaca negatif. Notebook 03 dan 04 menguji model yang membaca kalimat secara utuh.
