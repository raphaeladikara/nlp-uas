# Laporan kesiapan dataset model

**Status: SIAP**  
Review manusia: review 3 lapis, 881 kartu (utama 775) (`labeling/review/3lapis/`)

## Corong label

| tahap | jumlah |
|---|---|
| utama (jalur A) dilabeli | 3525 |
|   - label dari 3 LLM sepakat bulat | 2750 |
|   - label dari review 3 orang | 775 |
| - dikeluarkan: buzzer hasil review | 14 |
| - dibuang: tidak relevan | 182 |
| - dibuang: review belum punya label (seri, belum diputus) | 0 |
| dataset model | 3329 |
|   (label disamakan: teks identik di sumber yang sama) | 6 |
| (augmentasi) positif jalur B untuk fold latih | 42 |
| (augmentasi) positif jalur B dibuang karena akun/teks ada di data utama | 0 |

## Distribusi kelas

| label | n | % |
|---|---|---|
| negatif | 2206 | 66.3 |
| netral | 1039 | 31.2 |
| positif | 84 | 2.5 |

## Fold CV (grouped by akun + teks identik, stratified)

| fold   |   negatif |   netral |   positif |   All |
|:-------|----------:|---------:|----------:|------:|
| 0      |       441 |      208 |        17 |   666 |
| 1      |       441 |      208 |        17 |   666 |
| 2      |       442 |      208 |        16 |   666 |
| 3      |       441 |      207 |        17 |   665 |
| 4      |       441 |      208 |        17 |   666 |
| All    |      2206 |     1039 |        84 |  3329 |

## Kesepakatan reviewer manusia (review 3 lapis, Fleiss' kappa)


- kartu: 881 (utama 775, jalur B 106)
- dinilai lengkap 3 orang: 881, hanya 2 orang: 0, kosong: 0
- keputusan label: mayoritas 852, diskusi 29

**Fleiss' kappa = 0.286** (cukup (fair), skala Landis & Koch) di 881 kartu yang lengkap dinilai 3 orang, 4 kategori (negatif, netral, positif, tidak_relevan). Kesepakatan teramati P_o = 0.569, kesepakatan kebetulan P_e = 0.396.
Krippendorff's alpha (nominal) di 881 kartu yang dinilai minimal 2 orang = 0.286.

## Kappa per kelompok

| kelompok                                        |   kartu |   kappa | tafsir            |   p_o |   p_e | sepakat_bulat   | minimal_2_sama   |
|:------------------------------------------------|--------:|--------:|:------------------|------:|------:|:----------------|:-----------------|
| semua kartu, 4 kategori                         |     881 |   0.286 | cukup (fair)      | 0.569 | 0.396 | 37%             | 97%              |
| kelompok jalur_b                                |     106 |   0.484 | sedang (moderate) | 0.689 | 0.397 | 55%             | 97%              |
| kelompok utama                                  |     775 |   0.257 | cukup (fair)      | 0.553 | 0.398 | 35%             | 97%              |
| platform instagram                              |     334 |   0.332 | cukup (fair)      | 0.591 | 0.388 | 40%             | 97%              |
| platform tiktok                                 |     101 |   0.199 | sedikit           | 0.521 | 0.402 | 30%             | 97%              |
| platform x                                      |     262 |   0.32  | cukup (fair)      | 0.603 | 0.416 | 42%             | 97%              |
| platform youtube                                |     184 |   0.193 | sedikit           | 0.507 | 0.389 | 28%             | 96%              |
| 3 kelas sentimen (ketiga orang menilai relevan) |     725 |   0.291 | cukup (fair)      | 0.621 | 0.465 | 44%             | 99%              |

## Kappa per kategori (kartu lengkap)

| kategori      |   kappa |   dipilih (%) |
|:--------------|--------:|--------------:|
| negatif       |   0.3   |          39.5 |
| netral        |   0.219 |          48   |
| positif       |   0.581 |           3.4 |
| tidak_relevan |   0.331 |           9.1 |

Catatan: kartu ini adalah teks yang TIDAK disepakati bulat oleh 3 LLM, jadi memang teks paling ambigu. Kappa di sini lebih rendah daripada kalau seluruh dataset dinilai ulang.


## Sumber label

| sumber_label    |    n |
|:----------------|-----:|
| llm_bulat       | 2642 |
| manusia_3_orang |  687 |

## Pemeriksaan

| cek | hasil | detail |
|---|---|---|
| tidak ada teks jalur B / buzzer / kontrol di dataset | OK |  |
| id unik | OK |  |
| semua label di {negatif, netral, positif} | OK |  |
| teks tidak kosong | OK |  |
| semua teks punya fold | OK |  |
| tidak ada akun yang muncul di dua fold | OK |  |
| tidak ada teks identik di dua fold | OK |  |
| tiap fold punya ketiga kelas | OK |  |
| teks identik di sumber yang sama berlabel konsisten | OK |  |
| setiap teks review 3 lapis punya label akhir | OK |  |
| kartu review dinilai minimal 2 orang | OK | mayoritas 749, diskusi 26 |
| metadata LLM (sarkasme, butuh judul) tersedia | OK |  |

## Catatan untuk modeling

- Kelas positif hanya 2.5%. Pakai class weight / oversampling di train saja, dan laporkan macro-F1 serta F1 per kelas, bukan akurasi.
- 51% teks ditandai butuh konteks. Bandingkan model teks saja vs teks + konteks.
- 138 teks dari akun media X ikut training (label sesuai isi), tapi dikeluarkan dari statistik opini publik.
- Evaluasi memakai grouped 5-fold CV dengan kolom `fold`: latih di 4 fold, uji di 1 fold, ulangi 5 kali, laporkan rata-rata dan standar deviasi. Tuning hyperparameter dilakukan di dalam fold latih saja (nested), jangan memakai fold uji. Jangan membuat split acak baru, supaya tidak bocor.
