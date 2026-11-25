# Menjalankan ulang pipeline setelah review 3 lapis selesai

Semua hasil model sekarang **sementara**, karena label manusia masih dari review 1 orang. Setelah kelima anggota
mengisi `labeling/review/3lapis/tugas_<Nama>.csv`, jalankan langkah berikut dari folder `UAS/` (venv di `../.venv`).

1. Selesaikan sisa review: buka `labeling/review/3lapis/lengkapi_3lapis.html` di browser (dibuat ulang dengan
   `python labeling/review/buat_html_lengkapi.py`), isi tab suara, diskusi, dan buzzer, klik **Unduh hasil**, lalu
   pindahkan `isian_lengkapi_3lapis.csv` ke `labeling/review/3lapis/`. Setelah itu gabungkan dan hitung Fleiss' kappa:

   ```
   python labeling/review/gabung_review_3lapis.py
   ```

2. Bangun ulang dataset final. Status di `data/05_final/laporan_kesiapan.md` harus **SIAP**
   (cek "setiap kartu review dinilai 3 orang" harus OK):

   ```
   python labeling/finalize.py
   ```

3. Kalau ada teks yang sekarang positif tapi belum punya parafrase (tidak ada di `augmentasi/kaggle_data/bt_sumber.csv`),
   jalankan `python augmentasi/siapkan_bt.py`, unggah ulang dataset Kaggle, jalankan kernel
   `uas-nlp-raffi-back-translation`, lalu salin `augmentasi_bt.csv` ke `data/05_final/augmentasi_bt_mentah.csv`.

4. Jalankan notebook 02 (preprocessing, augmentasi, TF-IDF). Notebook ini juga menyalin `dataset_prepro.csv` dan
   `augmentasi_prepro.csv` ke `augmentasi/kaggle_data/`.

5. Unggah versi dataset Kaggle baru lalu jalankan keempat kernel (maksimal 2 GPU bersamaan):

   ```
   cd augmentasi/kaggle_data && kaggle datasets version -p . -m "label 3 lapis"
   cd notebooks/_kaggle/indobertweet && kaggle kernels push -p .   # lalu embed_bilstm, indobert, xlmr
   ```

6. Unduh hasilnya:

   ```
   kaggle kernels output raphaeladikara/uas-nlp-raffi-indobertweet -p data/07_transformer
   kaggle kernels output raphaeladikara/uas-nlp-raffi-indobert -p data/07_transformer
   kaggle kernels output raphaeladikara/uas-nlp-raffi-xlmr -p data/07_transformer
   kaggle kernels output raphaeladikara/uas-nlp-raffi-embedding-bilstm -p data/08_embedding_bilstm
   ```

   Lalu isi output notebook 03 dan 04 lokal dari log Kaggle (Kaggle CLI tidak mengunduh notebook yang sudah dijalankan):

   ```
   python notebooks/_build/isi_output_kaggle.py
   ```

7. Bangun dan jalankan notebook 05 (perbandingan, strategi kelas positif, analisis kesalahan). Notebook ini menyimpan
   tabelnya ke `data/09_perbandingan/`, yang dibaca langsung oleh laporan. Kalau angkanya berubah, perbarui teks
   pembacaan di `notebooks/_build/baca_05.md`, lalu:

   ```
   python notebooks/_build/build_05.py
   cd notebooks && jupyter nbconvert --to notebook --execute --inplace 05_perbandingan_analisis_kesalahan.ipynb && cd ..
   python notebooks/_build/isi_baca.py notebooks/05_perbandingan_analisis_kesalahan.ipynb notebooks/_build/baca_05.md
   python laporan/buat_laporan.py
   ```

## Pelabelan terarah kelas positif

Sudah dijalankan (23 sampai 24 Nov 2026), dan hasilnya sudah masuk notebook 02 sampai 05 serta laporan. Kalau label
terarah diubah (misalnya keputusan di `labeling/terarah/review/koordinator.csv`), jalankan `python labeling/terarah/gabung_terarah.py --final`,
unggah ulang dataset Kaggle, lalu ulangi langkah 4 sampai 7. XLM-R tidak perlu dijalankan ulang.

Untuk menambah teks positif asli dari teks cadangan, ikuti `labeling/terarah/README.md`. Setelah
`data/05_final/augmentasi_terarah.csv` terbentuk, ulangi langkah 4 sampai 7 di atas. Notebook 02 sampai 04 otomatis
menambah varian augmentasi "jalur B + terarah".

## Laporan progress format paper

Dibangun dari `Format UAS FP Paper (1).docx`:

```
python laporan/paper/hitung_prf.py
python laporan/paper/gambar_paper.py
python laporan/paper/buat_paper.py
```

Hasilnya `Laporan Progress UAS NLP - Kelompok J (Format Paper).docx`.
