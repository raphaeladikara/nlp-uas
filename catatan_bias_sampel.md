# Catatan: bias sampel "komentar teratas di konten kritis"

## Masalahnya

Ada dua lapis seleksi yang membuat persentase negatif bisa terlihat lebih tinggi dari aslinya.

1. **Pemilihan sumber.** Video YouTube/TikTok dan unggahan IG dicari dengan kata kunci kasus
   ("mahasiswa bayaran", "boikot rans", "14 miliar"), lalu diurutkan berdasarkan jumlah komentar.
   Konten yang paling ramai biasanya memang yang judulnya menyerang Raffi.
2. **Pemilihan komentar.** YouTube diambil `order=relevance`, IG `sort_by=popular`, TikTok komentar
   teratas. Komentar yang paling banyak disukai cenderung yang paling keras.

X tidak kena lapis kedua karena diambil mode *Latest* dengan kuota per hari.

## Cek awal (2.503 teks yang sudah punya label mayoritas, 14 Nov)

| platform | negatif | netral | positif |
|---|---|---|---|
| X (Latest, tidak diurut like) | 61% | 37% | 2% |
| Instagram | 63% | 35% | 2% |
| TikTok | 77% | 16% | 6% |

Negatif menurut kuartil like di dalam tiap sumber:

| platform | 25% like teratas | 25% terbawah |
|---|---|---|
| TikTok | 90% | 67% |
| Instagram | 67% | 61% |
| X | 50% | 60% |

Kesimpulan sementara: dominasi negatif tetap muncul di X yang tidak diurut like, jadi bukan semata
artefak sampling. Bias like terlihat jelas di TikTok, kecil di IG.

## Yang sudah dikerjakan

- `scraping/scrape_yt_kontrol.py`: ambil 100 komentar **terbaru** (`order=time`) dari 20 video YouTube
  yang sama. Hasil 1.820 komentar, tidak ada yang tumpang tindih dengan sampel teratas.
- `filtering/filter_kontrol_yt.py`: aturan filter yang sama dengan notebook 01, lalu ambil 25 komentar
  acak per video, jadi 500 teks (`data/03_filtered/kontrol_yt_untuk_label.csv`).
- Dilabeli 3 annotator sebagai batch 22-24 dengan kelompok `kontrol_yt`. Batch 01-21 tidak berubah.
- Kelompok `kontrol_yt` **tidak dipakai untuk training**. Fungsinya hanya mengukur bias.

## Hasil uji kontrol (label lengkap, 14 Nov)

YouTube, 20 video yang sama, hanya teks relevan:

| sampel | n | negatif | netral | positif |
|---|---|---|---|---|
| teratas (`order=relevance`) | 694 | 69,7% | 28,1% | 2,2% |
| terbaru (`order=time`, kontrol) | 427 | 72,8% | 23,4% | 3,7% |

Rata-rata per video (bobot tiap video sama): teratas 70,9% vs terbaru 72,5%. Selisih berpasangan
-1,5 poin, bootstrap 95% CI [-7,5; +4,5]. **Tidak ada bukti bahwa mengambil komentar teratas
menaikkan persentase negatif di YouTube.** Sampel terbaru justru sedikit lebih negatif.

Angka seluruh platform (kelompok `utama`), per komentar vs bobot per sumber:

| platform | per komentar | bobot per sumber |
|---|---|---|
| X | 62,6% | 62,4% |
| Instagram | 63,5% | 65,8% |
| YouTube | 69,7% | 70,9% |
| TikTok | 77,3% | 77,2% |

Bobot per sumber hampir tidak mengubah angka, jadi tidak ada satu sumber viral yang mendominasi.

TikTok, 14 video yang sama, hanya teks relevan. Actor TikTok tidak bisa urut terbaru, jadi kontrolnya
adalah komentar **di luar 60 teratas** (`scraping/scrape_tt_kontrol.py`, 110 per video, biaya Apify
$1,93, lalu `filtering/filter_kontrol_tt.py` mengambil 30 acak per video):

| sampel | n | median like | negatif | netral | positif |
|---|---|---|---|---|---|
| 60 teratas | 485 | 18 | 77,3% | 16,3% | 6,4% |
| di luar teratas (kontrol) | 404 | 2 | 74,3% | 20,8% | 5,0% |

Rata-rata per video: 77,2% vs 74,4%. Selisih berpasangan +2,8 poin, bootstrap 95% CI [-3,1; +9,9].
Komentar teratas memang sedikit lebih negatif, tapi selisihnya kecil dan tidak signifikan. Gradien
kuartil like (90% vs 67%) yang terlihat sebelumnya hanya terjadi di dalam 60 teratas. Begitu
dibandingkan dengan komentar yang benar-benar di luar jajaran populer, efeknya tinggal ~3 poin.

**Kesimpulan:** di kedua platform yang diuji, mengambil komentar teratas paling banyak menggeser
persentase negatif beberapa poin. Dominasi negatif (60-77%) tetap ada di semua sampel, termasuk X
yang tidak diurut like. Yang tetap tidak bisa dikoreksi adalah lapis pertama (sumber dipilih lewat
kata kunci kasus), jadi klaim harus dibatasi ke percakapan publik seputar kasus.

## Yang dipakai di notebook analisis

1. **Teratas vs terbaru (YouTube).** Bandingkan % negatif sampel `utama` YouTube dengan `kontrol_yt`
   pada video yang sama. Selisihnya adalah ukuran langsung bias "komentar teratas". Uji dengan
   chi-square atau selisih proporsi plus interval kepercayaan bootstrap.
2. **Gradien like.** Tabel % negatif per kuartil like di dalam tiap sumber, per platform (seperti tabel
   di atas, diperbarui setelah label lengkap).
3. **Bobot per sumber.** Selain angka per komentar, laporkan rata-rata proporsi per sumber (tiap video
   atau unggahan bobotnya sama), supaya satu video viral tidak mendominasi.
4. **X sebagai patokan.** X paling dekat ke sampel tanpa seleksi like, jadi angka X dilaporkan
   terpisah dan dipakai sebagai pembanding utama.
5. **Sikap sumber.** Tandai tiap video/unggahan sebagai kritis, berita netral, atau pro dari judul
   atau caption, lalu laporkan sentimen per kelompok sumber.
6. **Bahasa klaim.** Tulis "sentimen dalam percakapan publik seputar kasus", bukan "sentimen
   masyarakat Indonesia", dan jelaskan dua lapis seleksi di bagian keterbatasan.

Kelompok `kontrol_yt` dan `kontrol_tt` hanya untuk uji bias, tidak masuk training maupun statistik utama.
