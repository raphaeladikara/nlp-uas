# Pelabelan terarah kelas positif

Tujuannya menambah contoh positif asli untuk data latih. Dasarnya ada di notebook 05 (bagian strategi kelas positif):

- learning curve kelas positif belum jenuh, jadi data positif asli masih menaikkan F1 positif;
- parafrase back-translation tidak membantu (0 dari 8 konfigurasi membaik);
- kalau teks diurutkan dengan skor positif dari model, 100 teks teratas berisi 26% positif, sedangkan sampel acak hanya 2,5%.

Scraping ulang tidak diperlukan. Sumbernya 2.623 teks cadangan yang sudah lolos filter tapi belum pernah dilabeli
(`data/03_filtered/cadangan_belum_dilabel.csv`).

## Aturan penting

- Hasilnya **hanya untuk data latih**, sama seperti jalur B. Tidak masuk fold uji, tidak masuk statistik sentimen di
  notebook 06, karena sampelnya sengaja dipilih yang condong positif.
- Teks dari akun yang sudah ada di dataset final dibuang supaya tidak bocor ke fold uji.
- Alurnya sama dengan data utama: 3 annotator AI dengan `labeling/codebook.md`, teks yang tidak disepakati bulat
  dinilai 3 orang, ketiganya beda diputus koordinator, lalu Fleiss' kappa dihitung.
- Annotator (AI maupun manusia) tidak diberi tahu skor atau cara pilih teks. Ada 50 teks acak yang dicampur dengan
  250 teks skor tertinggi, supaya annotator tidak hanya melihat teks yang condong positif, sekaligus sebagai pembanding
  porsi positif kalau tidak diurutkan.

## Status

Semua langkah sudah dijalankan (23 Nov 2026). Ringkasannya ada di `ringkasan_terarah.md`: 33 positif dari 250 teks
skor tertinggi (13%) dan 2 dari 50 teks acak (4%), kappa 0,260 di 73 kartu, 32 positif masuk augmentasi. Tujuh kartu
yang ketiganya beda diputus mengikuti mayoritas 3 AI (`review/koordinator.csv`). Kalau koordinator ingin mengubahnya,
edit berkas itu lalu jalankan lagi langkah 4 dan 5.

Dampaknya ke model (24 Nov 2026): IndoBERT fine-tune teks + judul jalur B + terarah menjadi konfigurasi tunggal
terbaik (macro-F1 0,616, F1 positif 0,352), TF-IDF + LogReg naik 0,015, model dengan representasi beku turun. Semua
perubahan masih di dalam variasi antar fold. Tabelnya di `data/09_perbandingan/dampak_terarah.csv`.

## Langkah

1. Pilih teks dan buat batch (sudah dijalankan, 22 Nov 2026):

   ```
   python labeling/terarah/pilih_terarah.py
   ```

   Hasil: `data/03_filtered/terarah_untuk_label.csv` (300 teks) dan `labeling/terarah/batches/batch_29.md`, `batch_30.md`.

2. Tiga annotator AI (Claude Opus, Sonnet, Haiku) melabeli batch 29 dan 30 secara terpisah dengan `labeling/codebook.md`,
   lalu menulis jawabannya ke `labeling/terarah/hasil/<opus|sonnet|haiku>/batch_XX.jsonl`.

3. Gabungkan suara AI dan buat kartu review:

   ```
   python labeling/terarah/gabung_terarah.py
   ```

   Hasil: `labeling/terarah/review/perlu_review_3_orang.csv` (pemisah `;`). Setiap kartu sudah punya 3 nama reviewer.
   Isi kolom `label_1`, `label_2`, `label_3` (negatif / netral / positif / tidak_relevan) dan `buzzer_1` (ya / kosong),
   lalu simpan sebagai `labeling/terarah/review/hasil review 3 orang.csv`.

   Cara yang lebih mudah: buka `labeling/terarah/review/review_terarah.html` (dibuat oleh
   `python labeling/terarah/buat_html_terarah.py`), pilih nama sendiri, beri label, lalu klik **Unduh isian saya**.
   Taruh kelima berkas `isian_terarah_<Nama>.csv` di folder `review/`; langkah 4 menggabungkannya otomatis.

   Uji cepat sebelum review (label masih dari AI): `python labeling/terarah/uji_cepat_terarah.py`.

4. Hitung label akhir dan Fleiss' kappa:

   ```
   python labeling/terarah/gabung_terarah.py --final
   ```

   Kalau ada kartu yang ketiganya beda, isi `labeling/terarah/review/koordinator.csv` (kolom `id,label`) lalu jalankan
   lagi. Hasil: `data/05_final/augmentasi_terarah.csv` dan `labeling/terarah/ringkasan_terarah.md`.

5. Jalankan ulang notebook 02, unggah dataset Kaggle versi baru, lalu jalankan ulang kernel 03 dan 04 (langkah 4 sampai 7
   di `JALANKAN_ULANG.md`). Begitu `augmentasi_terarah.csv` ada, notebook 02 sampai 04 otomatis menambah varian
   **jalur B + terarah**, jadi dampaknya bisa dibandingkan langsung dengan jalur B saja di notebook 05.
