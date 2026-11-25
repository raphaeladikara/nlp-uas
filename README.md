# UAS NLP Kelompok 10 (J): Sentimen Publik terhadap Raffi Ahmad

Analisis sentimen komentar media sosial terhadap Raffi Ahmad setelah kasus pernyataan "mahasiswa bayaran" di Bundaran HI
(29 Oktober 2026). Pertanyaan utamanya: apakah publik masih membela Raffi, dan bagaimana sikap itu berubah dari fase
pra, puncak, sampai pasca kejadian.

## Isi repo

| Folder / file | Isi |
|---|---|
| `scraping/` | Skrip pengambilan data X, Instagram, YouTube, TikTok (Apify + YouTube API). Key dibaca dari `.env`, tidak ikut di repo. |
| `filtering/`, `notebooks/01_filter_data.ipynb` | Filter relevansi, duplikat, dan kandidat buzzer. Semua kandidat dibaca manual. |
| `labeling/` | Codebook, batch pelabelan 3 anotator AI, halaman review HTML, hasil review manusia 3 lapis, pelabelan terarah. |
| `augmentasi/` | Back-translation (MarianMT di Kaggle) untuk kelas positif. |
| `notebooks/` | 01 filter, 02 preprocessing + baseline TF-IDF, 03 transformer (Kaggle), 04 embedding + BiLSTM (Kaggle), 05 perbandingan + analisis kesalahan, 06 analisis sentimen. Notebook dibangun dari `notebooks/_build/*.py`; kernel Kaggle ada di `notebooks/_kaggle/`. |
| `data/` | Data per tahap (`00_pilot` sampai `09_perbandingan`). `data/05_final/` berisi dataset final. |
| `figures/` | Semua grafik notebook dan paper. |
| `laporan/` | Skrip pembangun laporan dan paper (`laporan/paper/buat_paper.py`). |
| `resources/` | Kamus slang, stopword, leksikon InSet. |
| `dokumentasi_data.md` | Dokumentasi lengkap pipeline data. |
| `JALANKAN_ULANG.md` | Urutan menjalankan ulang pipeline. |
| `catatan_bias_sampel.md` | Catatan bias sampel dan sampel kontrol YouTube/TikTok. |
| `_arsip_versi_lama/` | Versi lama (model biner IndoBERTweet, paper sebelum revisi 24 Nov). |

Data mentah `data/01_raw/*.json` (108 MB, berisi profil akun publik) sengaja tidak diunggah. File itu bisa dibuat ulang
dengan skrip di `scraping/`, dan semua tahap setelahnya (`02_csv` dst.) sudah ada di repo.

## Keputusan desain

- **Rentang dan sumber.** 22 Okt sampai 14 Nov 2026, dibagi fase pra, puncak (29 Okt sampai 2 Nov), dan pasca. Sumber:
  X (kuota per hari, mode Latest), postingan berita publik di Instagram (jalur A), akun Instagram Raffi sendiri
  (jalur B, awalnya hanya untuk analisis), YouTube, dan TikTok. Target sekitar 3.000 teks bersih, kualitas di atas kuantitas.
- **Label dua tingkat.** L1 negatif/netral/positif terhadap Raffi (target model utama), L2 subkategori.
- **Pelabelan.** Tiga anotator AI (Claude Opus, Sonnet, Haiku), voting mayoritas. Atas permintaan dosen (konsultasi
  17 Nov), setiap teks yang tidak bulat dinilai 3 orang anggota kelompok, lalu dihitung Fleiss' kappa.
- **Filter.** Setiap gerbang filter hanya menandai kandidat; semua kandidat dibaca manual
  (`data/03_filtered/audit/keputusan_manual.csv`, 61 teks diselamatkan). Akun buzzer dikeluarkan dari data latih dan
  statistik utama, tetapi dilaporkan terpisah.
- **Sampel kontrol** YouTube/TikTok hanya untuk mengecek bias, tidak pernah untuk melatih model.
- **Tanpa target biner.** Model akhir tetap 3 kelas. Kelas positif yang langka ditambah dengan komentar positif jalur B,
  parafrase back-translation, dan pelabelan terarah. Semua tambahan hanya masuk fold latih, dan setiap model dibandingkan
  dengan dan tanpa tambahan.
- **Input.** Kolom "konteks" diganti nama menjadi "judul" (judul postingan/video). Untuk BERT: tanpa lowercase, emoji
  diubah ke kata bahasa Indonesia.
- **Model.** TF-IDF + LogReg, fine-tune IndoBERTweet, IndoBERT, XLM-R, embedding IndoBERT + LogReg, BiLSTM + attention.
  Model GPU dijalankan di Kaggle (T4).

## Progres

| Tanggal | Yang terjadi |
|---|---|
| 14 Nov | Topik diganti dari pajak transaksi digital ke sentimen Raffi Ahmad. Scraping dan 27 batch pelabelan AI selesai. |
| 16 Nov | Review 5 orang selesai, dataset 3.272 teks. Baseline TF-IDF dan IndoBERTweet (versi biner) selesai. Laporan progress dan presentasi dibuat. |
| 17 Nov | Revisi setelah konsultasi dosen: audit filter manual, batch 28 (39 teks baru), review 3 lapis + Fleiss' kappa, target biner dihapus, augmentasi positif, tambah model IndoBERT, XLM-R, embedding, BiLSTM. |
| 22 Nov | Review 3 lapis selesai (kappa 0,286), dataset final 3.329 teks (84 positif). Notebook 05 dan laporan revisi dibuat. Learning curve belum jenuh, jadi disiapkan pelabelan terarah (300 teks). |
| 23 Nov | Pelabelan AI terarah selesai. XLM-R run pertama selesai. |
| 24 Nov | Review tim untuk data terarah digabung (kappa 0,260, 35 positif dari 300, 32 dipakai sebagai augmentasi latih). Paper format UAS disusun ulang. |

## Hasil utama (macro-F1, 3 kelas, rata-rata fold)

| Model | Macro-F1 |
|---|---|
| Ensemble IndoBERT + IndoBERTweet, jalur B + terarah | 0,628 |
| IndoBERT teks+judul, jalur B + terarah (model tunggal terbaik) | 0,616 |
| TF-IDF + LogReg, jalur B + terarah | 0,603 |
| XLM-R terbaik (run kedua, 24 Nov) | 0,584 |

Temuan lain: jalur B membantu di 8 dari 9 konfigurasi (kecuali XLM-R), parafrase back-translation hanya membantu 1 dari 9 (XLM-R), threshold
tuning tidak menambah skor, dan data terarah justru menurunkan model embedding beku. Selisih antar model terbaik masih
di dalam simpangan baku antar fold. Detail angka ada di `notebooks/05_perbandingan_analisis_kesalahan.ipynb` dan
`data/09_perbandingan/`.

## Menjalankan

Pakai venv bersama di folder induk (`../.venv`, dependensi di `../requirements.txt`), jalankan dari folder `UAS/`.
Urutan lengkap ada di `JALANKAN_ULANG.md`. Catatan: jsonl mentah LLM untuk batch 01 sampai 28 sudah tidak ada, jadi
`labeling/aggregate.py` jangan dijalankan ulang.
