"""Isi laporan revisi (bagian 3 dan seterusnya). Dipanggil oleh buat_laporan.py.

Angka di bagian model dibaca langsung dari berkas hasil, supaya laporan tetap cocok kalau pipeline dijalankan ulang
setelah review 3 lapis. Pembahasan di bagian model ditulis dari hasil run dengan label final review 3 lapis.
"""
import pandas as pd

TABEL_ALUR = [
    ("1. Scraping", "Ambil tweet dan komentar dari 4 platform", "scraping/", "data/01_raw/"),
    ("2. Satu format", "Satukan skema, samarkan nama akun", "scraping/to_csv.py", "data/02_csv/"),
    ("3. Filter", "Gerbang filter, setiap kandidat buang dicek manual", "notebooks/01_filter_data.ipynb",
     "data/03_filtered/, audit/keputusan_manual.csv"),
    ("4. Labeling AI", "3 AI melabeli terpisah, suara terbanyak", "labeling/", "data/04_labeled/label_llm.csv"),
    ("5. Review 3 lapis", "Teks yang tidak disepakati AI dinilai 3 orang", "labeling/review/3lapis/",
     "data/04_labeled/review_3lapis.csv"),
    ("6. Dataset final", "Label akhir dan pembagian 5 fold", "labeling/finalize.py", "data/05_final/dataset_model.csv"),
    ("7. Augmentasi", "Positif jalur B dan parafrase back-translation", "augmentasi/",
     "data/05_final/augmentasi_prepro.csv"),
    ("8. Preprocessing dan baseline", "Tiga tingkat preprocessing, TF-IDF", "notebooks/02_preprocessing_baseline.ipynb",
     "data/06_baseline/"),
    ("9. Transformer", "Fine-tuning IndoBERTweet, IndoBERT, XLM-R (Kaggle)", "notebooks/03_transformer_kaggle.ipynb",
     "data/07_transformer/"),
    ("10. Embedding dan BiLSTM", "IndoBERT embedding + LogReg, BiLSTM + attention", "notebooks/04_embedding_bilstm_kaggle.ipynb",
     "data/08_embedding_bilstm/"),
    ("11. Perbandingan", "Dampak tiap metode dan analisis kesalahan", "notebooks/05_perbandingan_analisis_kesalahan.ipynb",
     "figures/05_*.png"),
]
ISTILAH_BARU = [
    ("Judul", "Teks unggahan tempat komentar ditulis: judul video YouTube, caption Instagram, deskripsi TikTok, atau tweet yang dikutip/dibalas di X. Di versi sebelumnya disebut konteks"),
    ("Augmentasi", "Menambah data latih buatan. Di sini khusus kelas positif, dari akun Raffi dan dari parafrase"),
    ("Back-translation", "Teks diterjemahkan ke bahasa Inggris lalu kembali ke Indonesia, supaya didapat kalimat lain dengan makna sama"),
    ("Fleiss' kappa", "Ukuran kesepakatan lebih dari dua penilai. 0 berarti sama dengan kebetulan, 1 berarti sepakat sempurna"),
]


def ISI(para, judul, caption, tabel, kode, gambar, butir, ROOT):
    D = ROOT / "data"
    FIG = ROOT / "figures"

    # 3. FILTER
    judul("3. Filter", 1)
    para("Sebelum dilabeli, data disaring lewat beberapa gerbang. Di laporan progress, setiap gerbang membuang teks "
         "hanya berdasarkan aturan otomatis. Saat konsultasi, dosen mengingatkan dua hal: aturan seperti \"balasan "
         "pemilik unggahan pasti bukan opini\" bisa overklaim, dan gerbang relevansi X bisa ikut membuang informasi "
         "yang relevan. Setelah kami cek ulang, kekhawatiran ini benar, dan bukan hanya di dua gerbang itu.")
    para("Karena itu aturan otomatis sekarang hanya menghasilkan **kandidat**. Setiap kandidat dibaca satu per satu, lalu "
         "keputusan (buang atau pertahankan) dan alasannya dicatat per teks di data/03_filtered/audit/keputusan_manual.csv. "
         "Notebook filter berhenti dengan error kalau ada kandidat yang belum diperiksa, jadi tidak ada teks yang "
         "terbuang tanpa dibaca. Fungsi yang dipakai:")
    caption("Kode 1. Fungsi pemeriksaan manual di notebooks/01_filter_data.ipynb")
    kode('''def periksa_manual(kandidat, gerbang, tahap):
    """Kandidat dari aturan otomatis dicocokkan dengan keputusan manual per teks."""
    k = df[kandidat.reindex(df.index, fill_value=False)]
    k = k[["id", "platform", "jalur", "konteks", "text"]].merge(
        manual[manual.gerbang.eq(gerbang)][["id", "keputusan", "alasan"]], on="id", how="left")
    belum = k[k.keputusan.isna()]
    assert belum.empty, f"{len(belum)} kandidat gerbang {gerbang} belum diperiksa"
    alasan = df.id.map(k.set_index("id").alasan)
    buang(df.id.isin(k[k.keputusan.eq("buang")].id), tahap, "cek manual: " + alasan)''')
    caption("Tabel 6. Dasar setiap gerbang dan hasil cek manual")
    tabel([
        ["Gerbang", "Dasar penandaan di kode", "Dibuang (progress)", "Dibuang (revisi)", "Temuan cek manual"],
        ["2. Pemilik unggahan", "IG: flag is_created_by_media_owner dari Apify atau username = pemilik unggahan. YouTube: authorChannelId = channelId video. TikTok: username = pembuat video", "28", "16", "12 balasan kreator berisi opini tentang Raffi"],
        ["3. Tanpa isi", "Setelah normalisasi NFKC tidak ada satu pun huruf atau angka", "177", "150", "27 teks bermakna dulu terbuang (huruf unicode, huruf dipisah spasi, \"14 M\")"],
        ["4a. Bahasa asing (X)", "Kode lang dari X bukan Indonesia", "17", "6", "14 tweet ternyata bahasa Indonesia, Jawa, atau campuran"],
        ["4b. Spam", "Daftar kata judol dan promosi", "10", "0", "Ke-10 teks adalah opini yang memakai kata gacor/giveaway/slot"],
        ["5. Relevansi X", "Teks dan judul tidak memuat kata kunci Raffi atau kasus", "61", "60", "1 tweet relevan diselamatkan, 1 lagi lolos karena NFKC"],
        ["6. Duplikat", "Klaster kemiripan karakter per akun dan antar akun", "79", "79", "37 akun sama mengulang, 42 salinan akun lain"],
        ["7. Buzzer", "Aturan keras dan skor poin (bagian 4)", "36", "36", "Daftar sama persis"],
    ], lebar=[2.6, 5.4, 1.8, 1.8, 4.4], ukuran=8)
    caption("Tabel 7. Sisa teks setelah tiap gerbang (revisi)")
    tabel([
        ["Gerbang", "X", "IG", "YT", "TT", "Total"],
        ["0. Data mentah", "2.197", "1.989", "2.000", "834", "7.020"],
        ["2. Pemilik unggahan", "2.197", "1.975", "1.998", "834", "7.004"],
        ["3. Tanpa isi", "2.197", "1.832", "1.992", "833", "6.854"],
        ["4. Bahasa asing dan spam", "2.191", "1.832", "1.992", "833", "6.848"],
        ["5. Relevansi X", "2.131", "1.832", "1.992", "833", "6.788"],
        ["6. Duplikat", "2.088", "1.807", "1.987", "827", "6.709"],
        ["7. Buzzer", "2.056", "1.804", "1.986", "827", "6.673"],
    ])
    para("Revisi gerbang menyelamatkan 61 teks: yang lolos sekarang 6.673, sedangkan di laporan progress 6.612. Gerbang 1 "
         "(rentang tanggal) dan 8 (batas 25 tweet per thread X) tetap tidak membuang apa pun.")
    gambar(FIG / "f02_corong_filter.png", 14)
    caption("Gambar 2. Jumlah teks setelah tiap gerbang")

    judul("3.1 Pemilik unggahan", 2)
    para("Penanda is_pemilik_sumber dibuat di scraping/to_csv.py dan hanya menjawab apakah penulisnya pemilik unggahan, "
         "bukan apakah isinya opini. Di laporan progress kami menganggap semuanya balasan admin akun berita. Ternyata "
         "pemilik unggahan di data ini juga kreator, misalnya @julia_4j dan @andovidalopez, yang membalas pembaca dengan "
         "pendapat mereka sendiri. Dari 28 teks, 12 dipertahankan dan 16 dibuang.")
    caption("Tabel 8. Contoh keputusan manual gerbang pemilik unggahan")
    tabel([
        ["Teks", "Keputusan", "Alasan"],
        ["Kita2 aja ngga bisa dia bohongin, apalagi Tuhan😁", "pertahankan", "menuduh Raffi berbohong, opini tentang Raffi"],
        ["Hasil pembodohan struktural ka", "pertahankan", "menilai bisnis Raffi"],
        ["Update: di statement klarifikasinya, salah satu alasannya adalah \"tidak mengetahui\". sadly I CALLED IT", "pertahankan", "menilai isi klarifikasi Raffi"],
        ["@user terima kasih tapi saya Andovi da Lopez 🙏", "buang", "membetulkan nama, tidak menyikapi topik"],
        ["@user EXACTLY", "buang", "isi yang disetujui ada di komentar induk yang tidak ter-scrape"],
        ["Buat yang storage HP ... Cek link di bio gue 🙌", "buang", "promosi"],
    ], lebar=[8, 2.2, 5.8])
    para("Teks pemilik unggahan yang dipertahankan tetap membawa penanda is_pemilik_sumber, jadi di analisis bisa "
         "dipisahkan dari komentar warganet biasa.")

    judul("3.2 Teks tanpa isi", 2)
    para("Ada dua masalah di aturan lama. Pertama, sebagian warganet menulis dengan huruf unicode bergaya, misalnya "
         "\"𝒃𝒐𝒊𝒌𝒐𝒕 𝒂𝒋𝒂\" atau \"𝗥𝗔𝗙𝗙𝗜 𝗔𝗛𝗠𝗔𝗗\". Bagi komputer ini bukan huruf A sampai Z, jadi dianggap tanpa isi. "
         "Kedua, aturan lama mensyaratkan kata minimal dua huruf atau tiga karakter, sehingga \"14 M 😱\" ikut terbuang "
         "padahal merujuk ke kontrak Rp14,7 miliar. Sekarang teks dinormalisasi dengan Unicode NFKC dulu, huruf yang "
         "dipisah spasi (\"B O I K O T\") disambung, lalu teks hanya dibuang kalau tidak ada satu pun huruf atau angka.")
    caption("Kode 2. Normalisasi dan aturan tanpa isi")
    kode('''def normalisasi(t):
    t = unicodedata.normalize("NFKC", str(t))
    t = re.sub(r"https?://\\S+|www\\.\\S+", " ", t)
    t = re.sub(r"@[\\w.]+", "@user", t)
    t = re.sub(r"\\b(?:[A-Za-z] ){2,}[A-Za-z]\\b", lambda m: m.group(0).replace(" ", ""), t)
    return re.sub(r"\\s+", " ", t).strip()

inti = df.text.str.replace("@user", " ", regex=False).str.strip()
ada_isi = inti.str.contains(r"[^\\W_]")   # minimal satu huruf atau angka, alfabet apa pun''')
    para("Yang dibuang sekarang 150 teks: 84 emoji saja, 64 kosong atau mention saja, dan 2 tanda baca saja. Teks emoji "
         "saja tetap dibuang dengan alasan yang berbeda, yaitu sasarannya tidak bisa dipastikan. 🤮 di bawah berita "
         "kontrak Rp14,7 miliar bisa ditujukan ke Raffi, ke kementerian, atau ke beritanya, sedangkan codebook kami "
         "mengharuskan sasaran Raffi untuk label negatif atau positif. Ada 27 teks yang dulu terbuang dan sekarang lolos, "
         "misalnya \"14 M\", \"RAFFI ANJINK\", \"boikot aja.sudah menodai citra\", dan \"Dia aja blm pernah jadi mahasiswa\".")

    judul("3.3 Bahasa asing dan spam", 2)
    para("Kode bahasa dari X ternyata sering salah untuk tweet pendek dan campuran. \"pantes di demo, afiliate sama rafi "
         "ahmad bjir\" diberi kode Inggris, dan \"rafi ahmad gek opo?\" (bahasa Jawa) juga bukan berkode Indonesia. Dari 20 "
         "kandidat, hanya 6 yang benar-benar asing dan tidak membahas Raffi (Urdu, Hindi, Rafi Ahmad Kidwai politikus India, "
         "CRPF India). Sebanyak 14 tweet dipertahankan.")
    para("Daftar kata spam lebih parah: dari 10 kandidat, tidak ada satu pun yang spam. Semuanya opini yang memakai kata "
         "itu untuk menyindir, misalnya \"Raffi Mesin Pencuci Uang paling Gacor\" dan \"dia lagi sibuk bagi2 giveaway "
         "sepeda motor nih si Rafi\". Spam yang sebenarnya (iklan koin kuno, ajakan follow back) justru tertangkap di "
         "gerbang relevansi X karena tidak menyebut Raffi.")

    judul("3.4 Relevansi tweet X", 2)
    para("Tweet ditandai tidak relevan kalau teks dan judulnya tidak memuat kata kunci Raffi atau kasus (raffi/rafi, RANS, "
         "Nagita, mahasewa, mahasiswa bayaran dan variasinya, deklarasi, bundaran, utusan khusus, stafsus, 14 M, ICW). "
         "Sesuai saran dosen, semua 61 kandidat kami baca, bukan sampelnya saja.")
    caption("Kode 3. Kata kunci relevansi X (dicocokkan setelah NFKC)")
    kode('''KUNCI = re.compile(r"raff?i|rafi|\\brans\\b|nagita|mahasewa|mahasiswa (?:bayaran|settingan|sewaan|palsu|bodong)|"
                   r"deklarasi|bundaran|utusan khusus|stafsus|14[ ,.]?[0-9]?\\s?m(?:iliar|ilyar)?\\b|icw", re.I)
cocok = df.text.str.contains(KUNCI) | df.konteks.fillna("").str.contains(KUNCI)
cek5 = periksa_manual((df.platform == "x") & ~cocok, "5", "5. tidak relevan (X)")''')
    para("Satu tweet dipertahankan: \"Tumbanglan gurita bisnis penuh konflik kepentingan milik buzzer 2 rezim ini\". "
         "Tweet ini tidak menyebut nama, tapi \"gurita bisnis\" di periode ini merujuk ke bisnis Raffi. Tweet "
         "\"𝗥𝗔𝗙𝗙𝗜 𝗔𝗛𝗠𝗔𝗗 ... Shutdown this guy\" yang dulu terbuang sekarang sudah cocok dengan kata kunci setelah NFKC. "
         "Sisanya 60 tweet memang topik lain: fans JKT48, KRL Surabaya, iklan koin kuno, puisi pribadi, kampanye "
         "pemerintah, dan bahasa Telugu.")
    para("Ada 5 balasan pendek yang mungkin relevan tapi tetap kami buang, misalnya \"Instansi itu...\" dan \"bandingkan "
         "dengan budget yang yang di mark-up oleh kementrian\". Tweet induknya tidak ikut ter-scrape, jadi sasarannya tidak "
         "bisa dipastikan, dan annotator juga hanya akan melihat teks yang sama. Ini kami catat sebagai keterbatasan.")

    judul("3.5 Duplikat", 2)
    para("Teks dikelompokkan dengan kemiripan n-gram karakter (cosine minimal 0,85). Dari setiap klaster hanya satu teks "
         "dipertahankan. Dari 79 teks yang dibuang, 37 adalah akun yang sama mengulang teksnya sendiri (misalnya satu akun "
         "yang membalas belasan tweet dengan \"Usut rans dan Raffi Ahmad\"), dan 42 adalah salinan dari akun lain "
         "(misalnya rekap \"harga per detik reels\"). Jumlah akun yang menyalin tetap disimpan di kolom n_akun_teks_mirip "
         "untuk tahap buzzer.")

    # 4. BUZZER
    judul("4. Menentukan Buzzer", 1)
    para("Tidak ada satu tanda pasti bahwa sebuah akun itu buzzer. Akun sepi bisa saja orang biasa. Karena itu kami "
         "memakai tiga lapis pengecekan. Tabel di bawah merangkum semua alasan yang bisa membuat sebuah teks dianggap "
         "buzzer, beserta dasarnya di kode dan jumlah teks yang tertangkap.")
    caption("Tabel 9. Alasan teks dianggap buzzer")
    tabel([
        ["Alasan", "Lapis", "Dasar", "Jumlah"],
        ["Akun X dibuat < 30 hari sebelum posting", "1 (aturan keras)", "author.createdAt dibandingkan tanggal tweet. Akun yang dibuat menjelang kasus lalu langsung membahas kasus adalah pola akun kampanye", "13 teks"],
        ["Satu akun memposting teks hampir sama >= 3 kali", "1 (aturan keras)", "klaster teks yang sama dari author_hash yang sama (flooding)", "7 teks"],
        ["Narasi sama ditulis >= 3 akun", "1 (aturan keras)", "teks >= 5 kata dengan kemiripan karakter >= 0,85 dari >= 3 akun berbeda (copy-paste narasi)", "6 klaster"],
        ["Akun ditandai otomatis oleh X", "1 (aturan keras)", "field isAutomated dari X", "0 teks"],
        ["Skor poin >= 4", "2 (skor)", "jumlah tanda lemah: akun < 3 bulan (+2) atau < 6 bulan (+1), following > 10x followers (+1), username generik (+1), akun kosong (+1), > 100 tweet per hari (+1), 3 sampai 5 teks (+1) atau >= 6 teks (+2) soal isu ini, teks mirip satu akun lain (+2), >= 3 hashtag (+1)", "10 teks"],
        ["Isi teks seperti pesan pesanan", "3 (isi teks)", "teks zona batas (skor 2 sampai 3) yang dicurigai minimal 1 AI, atau teks lolos yang dicurigai minimal 2 AI, lalu diputuskan manusia: template promosi atau pembelaan generik yang tidak menanggapi unggahan, ajakan seragam dengan hashtag kampanye", "14 teks"],
    ], lebar=[3.6, 2.2, 8, 2.2], ukuran=8)
    para("Untuk YouTube, tanda profil tidak dipakai. Hampir semua penonton YouTube punya channel kosong, jadi kalau tanda "
         "\"akun kosong\" dipakai, 78% komentar YouTube akan masuk zona batas. Untuk Instagram dan TikTok, bobotnya diturunkan "
         "menjadi 1 karena banyak akun pribadi yang hanya dipakai untuk melihat konten. Tanda yang lebih sulit dipalsukan, "
         "yaitu umur akun dan perilaku (teks mirip, posting berulang), tetap berbobot 2.")
    gambar(FIG / "f01_skor_buzzer.png", 15)
    caption("Gambar 3. Sebaran skor buzzer dan tanda yang paling sering muncul")
    caption("Tabel 10. Hasil lapis 1 dan 2 per platform")
    tabel([
        ["Platform", "Lolos", "Batas", "Aturan keras", "Skor >= 4", "Total"],
        ["Instagram", "1.760", "44", "3", "0", "1.807"],
        ["TikTok", "808", "19", "0", "0", "827"],
        ["X", "1.623", "433", "22", "10", "2.088"],
        ["YouTube", "1.902", "84", "1", "0", "1.987"],
        ["Total", "6.093", "580", "26", "10", "6.709"],
    ])
    para("Daftar 36 teks buzzer dari lapis 1 dan 2 sama persis dengan laporan progress, jadi revisi gerbang tidak mengubah "
         "siapa yang dianggap buzzer. X paling banyak tertangkap (32 dari 36) karena hanya X yang memberi umur akun dan "
         "jumlah tweet. Rincian alasan per teks ada di notebook 01 bagian 7.")
    para("Ada satu kemungkinan salah tangkap yang perlu dicatat. Aturan \"narasi sama >= 3 akun\" ikut menangkap meme "
         "\"Sultan andara ANGGARAN DARI NEGARA\" yang ditulis 11 akun di Instagram. Menurut kami ini lelucon viral, bukan "
         "narasi pesanan. Dampaknya hanya satu teks wakil klaster, karena salinannya sudah dibuang di gerbang duplikat.")
    caption("Tabel 11. Sikap teks buzzer terhadap Raffi")
    tabel([
        ["Kelompok", "Negatif", "Netral", "Positif", "Lainnya"],
        ["Cek akun (lapis 1 dan 2), 36 teks", "23", "10", "2", "1"],
        ["Cek isi (lapis 3), 14 teks", "11", "0", "3", "0"],
        ["Total 50 teks", "34", "10", "5", "1"],
    ])
    para("Buzzer yang tertangkap kebanyakan justru menyerang Raffi (34 dari 50), bukan membelanya.")

    # 5. SAMPLING
    judul("5. Sampling", 1)
    para("Kami mengambil sekitar 3.500 teks jalur A untuk dilabeli: X 1.300, Instagram 900, YouTube 800, dan TikTok 500. "
         "Pengambilannya acak per strata (tanggal untuk X, unggahan atau video untuk platform lain), bukan berdasarkan like.")
    para("Revisi gerbang menambah teks yang lolos, padahal 3.498 teks sampel lama sudah dilabeli dan direview. Kalau sampling "
         "diulang, random_state yang sama akan memberi sampel yang berbeda karena datanya berubah. Karena itu sampel lama "
         "dibekukan (audit/sampel_v1.csv), dan teks baru diambil dengan peluang yang sama dengan rasio sampling lama di "
         "platformnya: Instagram 71,3%, X 63,5%, TikTok 60,5%, dan YouTube 40,3%. Hasilnya 27 teks baru masuk jalur A "
         "dan 12 masuk jalur B. Sampel sekarang berisi 3.525 teks jalur A dan 525 teks jalur B, dan 2.623 teks disimpan "
         "sebagai cadangan.")
    para("Uji bias sampling di laporan progress tidak berubah: mengambil komentar teratas hanya menggeser persentase "
         "negatif beberapa poin dan selisihnya tidak signifikan (rincian di catatan_bias_sampel.md).")

    # 6. LABELING AI
    judul("6. Labeling oleh AI", 1)
    para("Setiap teks dilabeli tiga model AI (Claude Opus, Sonnet, dan Haiku) secara terpisah dengan codebook yang sama "
         "(labeling/codebook.md). Setiap AI membaca teks bersama judul unggahannya. Aturan terpentingnya: label negatif atau "
         "positif hanya diberikan kalau sasarannya Raffi. Komentar yang marah ke polisi atau mengejek mahasiswa bayaran "
         "tanpa menyinggung Raffi dilabeli netral.")
    para("Ke-39 teks baru dari revisi gerbang dilabeli sebagai batch 28 dengan cara yang sama. Batch 1 sampai 27 tidak "
         "berubah (dicek dengan hash berkas). Secara keseluruhan ketiga AI sepakat bulat di 78,2% teks (3.169 dari 4.050).")

    # 7. REVIEW 3 LAPIS
    judul("7. Review oleh Manusia (3 Lapis)", 1)
    para("Di laporan progress, 871 teks yang tidak disepakati AI dicek manusia, tapi kartu biasa hanya dikerjakan satu "
         "orang. Hanya 30 kartu kalibrasi yang dikerjakan kelima anggota. Dosen meminta setiap teks dilabeli tiga orang, "
         "lalu diambil suara terbanyak dan dihitung Fleiss' kappa. Karena itu datanya kami pisah menjadi dua berkas di "
         "labeling/review/3lapis/:")
    butir("• sepakat_bulat_gt.csv: 3.169 teks (2.750 data utama dan 419 jalur B) yang disepakati bulat ketiga AI. "
          "Labelnya langsung dipakai sebagai ground truth.")
    butir("• perlu_review_3_orang.csv: 881 teks (775 data utama dan 106 jalur B) yang belum disepakati, lengkap dengan "
          "kolom label_opus, label_sonnet, label_haiku, dan tiga slot penilai manusia.")
    para("Slot pertama diisi review lama. Untuk 30 kartu kalibrasi yang dulu dikerjakan 5 orang, diambil 3 penilai secara "
         "acak (seed 42), karena Fleiss' kappa membutuhkan jumlah penilai yang sama di setiap kartu. Dari 2.643 slot, 909 "
         "sudah terisi. Sisanya 1.734 slot dibagi rata, sekitar 342 kartu per orang (tugas_<Nama>.csv), dan tidak ada orang "
         "yang menilai kartu yang sama dua kali.")
    caption("Kode 4. Suara terbanyak 3 penilai (labeling/review/gabung_review_3lapis.py)")
    kode('''def mayoritas(vals):
    vals = [v for v in vals if v != ""]
    if len(vals) < 3:
        return "", "belum lengkap"
    v, n = Counter(vals).most_common(1)[0]
    return (v, "mayoritas") if n >= 2 else ("", "seri")   # seri -> diputus koordinator''')
    para("Label akhir adalah label yang dipilih minimal 2 dari 3 orang. Setelah putaran pertama, masih ada 72 kartu yang "
         "baru dinilai 2 orang atau belum dinilai sama sekali. Kekurangannya (84 suara) kami lengkapi lewat halaman "
         "labeling/review/3lapis/lengkapi_3lapis.html, dengan syarat orang yang mengisi belum pernah menilai kartu itu. "
         "Kartu yang ketiga penilainya memilih label berbeda tidak diputus pakai suara salah satu orang, tapi lewat "
         "diskusi tim, lalu hasilnya dicatat di berkas isian yang sama.")
    caption("Tabel 12. Hasil akhir review 3 lapis")
    tabel([
        ["Keadaan kartu", "Jumlah", "Cara menentukan label"],
        ["Ketiga orang sepakat", "326 (37%)", "label yang dipilih ketiganya"],
        ["2 lawan 1", "526 (60%)", "suara terbanyak"],
        ["Ketiganya berbeda", "29 (3%)", "diskusi tim"],
        ["Total", "881", "semua dinilai lengkap 3 orang"],
    ], lebar=[4.5, 3, 8.5])
    para("Saat mengecek hasil diskusi, kami menemukan dua keputusan positif yang bertentangan dengan isi teksnya. "
         "\"Menyala abangkuh, pahlawan sejati berani berteriak di kandang binatang buas...\" di video \"Raffi lagi "
         "Nge'MC diteriaki oleh pria tampan ini\" memuji orang yang meneriaki Raffi, dan tidak ada satu pun dari ketiga "
         "penilai yang memilih positif. Kartu serupa (\"Tetap Semangat mas Ayu menyuarakan suara rakyat\") juga diputus "
         "negatif. Yang kedua, \"betul mereka masih pumya etitude\" di video tentang musisi yang mundur dari RANS Carnival "
         "memuji musisi yang ikut boikot. Keduanya kami koreksi menjadi negatif, dan alasannya dicatat di kolom catatan "
         "isian. Koreksi ini penting karena kelas positif hanya 84 teks.")
    judul("7.1 Fleiss' kappa", 2)
    para("Fleiss' kappa mengukur seberapa jauh kesepakatan para penilai di atas kesepakatan yang bisa terjadi karena "
         "kebetulan. Rumusnya κ = (P_o − P_e) / (1 − P_e). P_o adalah rata-rata proporsi pasangan penilai yang memilih "
         "label sama di setiap kartu, dan P_e adalah peluang dua penilai kebetulan sama kalau mereka memilih acak "
         "mengikuti sebaran label keseluruhan. Jadi kappa bukan persentase kesepakatan. Kappa 0 berarti sama dengan "
         "menebak, dan 1 berarti sepakat sempurna.")
    caption("Tabel 13. Fleiss' kappa review 3 lapis (labeling/review/3lapis/ringkasan_kappa.md)")
    rk = pd.read_csv(ROOT / "labeling" / "review" / "3lapis" / "ringkasan_kappa.csv")
    tabel([["Kelompok", "Kartu", "Kappa", "Tafsir", "P_o", "P_e", "Sepakat bulat"]] +
          [[r.kelompok, str(r.kartu), f"{r.kappa:.3f}".replace(".", ","), r.tafsir,
            f"{r.p_o:.3f}".replace(".", ","), f"{r.p_e:.3f}".replace(".", ","), r.sepakat_bulat]
           for r in rk.itertuples()], lebar=[5.2, 1.4, 1.4, 2.8, 1.4, 1.4, 2.4], ukuran=8)
    para("Kappa keseluruhan 0,286, masuk kategori cukup (fair) di skala Landis dan Koch. P_o 0,569 artinya rata-rata "
         "sedikit di atas separuh pasangan penilai memilih label yang sama, sedangkan kebetulan saja sudah memberi 0,396. "
         "Krippendorff's alpha, yang dihitung sebagai pembanding, juga 0,286.")
    para("Angka ini rendah, tapi kami anggap wajar untuk kartu-kartu ini. Kartu review sengaja diambil dari teks yang "
         "ketiga AI saja tidak sepakat, jadi isinya memang teks yang paling ambigu. Kalau seluruh 3.525 teks dinilai "
         "manusia, kappa-nya hampir pasti lebih tinggi, karena 78% teks lainnya cukup jelas sampai ketiga AI memberi label "
         "sama. Beda pendapatnya juga tidak acak. Per kategori, kappa paling rendah ada di netral (0,219) dan paling "
         "tinggi di positif (0,581). Dari 526 kartu 2 lawan 1, 71,5% adalah negatif lawan netral, yaitu komentar yang "
         "marah ke acara, polisi, atau pemerintah, dan penilai berbeda pendapat apakah Raffi ikut menjadi sasaran. "
         "Komentar di akun Raffi (jalur B) lebih mudah dinilai (kappa 0,484), karena sasarannya sudah pasti Raffi.")
    para("Majority vote tetap aman dipakai karena 97% kartu punya minimal 2 penilai yang sepakat, dan 3% sisanya "
         "diputus lewat diskusi. Kappa yang rendah kami laporkan apa adanya sebagai keterbatasan label, terutama di batas "
         "negatif dan netral. Ini juga menjadi batas atas yang wajar untuk model: kalau manusia saja sering berbeda "
         "pendapat di batas itu, model juga akan kesulitan di sana.")

    # 8. DATASET FINAL
    judul("8. Dataset Final", 1)
    df = pd.read_csv(D / "05_final" / "dataset_model.csv")
    n = df.label.value_counts()
    para(f"finalize.py menggabungkan label AI dan label manusia. Label manusia dipakai kalau ada, kalau tidak ada dipakai "
         f"label AI. Buzzer hasil review dan teks tidak relevan dibuang. Hasilnya {len(df):,} teks: "
         f"{n['negatif']:,} negatif, {n['netral']:,} netral, dan {n['positif']} positif.".replace(",", "."))
    ct = pd.crosstab(df.platform, df.label, margins=True, margins_name="Total")
    caption("Tabel 12. Label per platform")
    nama = {"instagram": "Instagram", "tiktok": "TikTok", "x": "X", "youtube": "YouTube", "Total": "Total"}
    tabel([["Platform", "Negatif", "Netral", "Positif", "Total"]] +
          [[nama[i], *[f"{v:,}".replace(",", ".") for v in r]] for i, r in ct.iterrows()])
    para("Data dibagi menjadi 5 fold untuk pengujian (grouped stratified 5-fold). Semua teks dari satu akun dan semua teks "
         "identik selalu masuk fold yang sama, supaya model tidak bisa terlihat bagus hanya karena hafal gaya satu akun. "
         "Setiap fold berisi 16 atau 17 teks positif. Kolom konteks di dataset_model.csv sekarang bernama judul.")

    # 9. PREPROCESSING
    judul("9. Preprocessing", 1)
    judul("9.1 Apa yang dimaksud judul", 2)
    para("Dosen bertanya apa yang dimaksud \"konteks\" di laporan progress. Yang kami maksud adalah teks unggahan tempat "
         "komentar ditulis, jadi istilahnya kami ganti menjadi **judul**. Isinya berbeda per platform:")
    caption("Tabel 13. Isi kolom judul per platform")
    tabel([
        ["Platform", "Isi judul", "Teks yang punya judul"],
        ["YouTube", "judul video, diawali nama channel", "100%"],
        ["Instagram", "caption unggahan, diawali nama akun pemilik", "100%"],
        ["TikTok", "deskripsi video, diawali nama kreator", "100%"],
        ["X", "tweet yang dikutip atau dibalas; kalau tweet induk tidak ter-scrape, hanya keterangan bahwa tweet ini membalas akun lain", "52,4%"],
    ], lebar=[2.4, 10, 3.6])
    caption("Tabel 14. Contoh data komentar + judul")
    tabel([
        ["Judul", "Komentar", "Label"],
        ["Judul video Bimo Hakito: RAFFI AHMAD MAKIN TERPOJOK! GA BAKAL NYANGKA JADI BEGINI, TIBA-TIBA DIDEMO PAS BAWA ACARA!",
         "keberanian si mas tadi harusnya menular ke para-para mas dan para-para mbak, viralkan bung Bimo hakito", "negatif"],
        ["Deskripsi video @wartakotalive.com: Netizen Ramai Boikot Bisnisnya, Raffi Ahmad Klarifikasi dan Minta Maaf",
         "Allah ngak tidur ya", "negatif"],
        ["Caption unggahan @hanifmuh_: rame di Threads, musisi sama UMKM satu per satu mundur dari RANS Carnival",
         "Jogjakarta keren ❤️", "netral"],
    ], lebar=[7, 7, 2])
    para("Contoh pertama tidak menyebut Raffi sama sekali, tapi labelnya negatif karena komentar ini mendukung orang yang "
         "meneriaki Raffi di videonya. Contoh kedua tanpa judul bisa dibaca sebagai doa biasa. Separuh teks (50,5%) "
         "ditandai annotator butuh judul supaya maknanya jelas. Model menerima judul dengan dua cara: TF-IDF membuat vektor "
         "terpisah untuk judul (bobot 0,5), sedangkan model BERT menerima pasangan kalimat [CLS] komentar [SEP] judul [SEP].")
    judul("9.2 Tiga tingkat preprocessing", 2)
    butir("• Ringan, untuk semua model: mention jadi @user, URL dibuang, tanda # dibuang, huruf yang diulang dipendekkan "
          "(\"bangettt\" jadi \"banget\"). Huruf besar dan emoji tidak diubah.")
    butir("• Lengkap, khusus TF-IDF: ringan + huruf kecil, emoji jadi token, \"wkwk\" dan \"haha\" disamakan, slang "
          "dinormalisasi dengan kamus 711 kata, stopword dibuang dengan kata negasi tetap disimpan.")
    butir("• BERT, untuk semua model berbasis IndoBERT, IndoBERTweet, XLM-R, dan BiLSTM: ringan + emoji diubah menjadi kata "
          "bahasa Indonesia. **Tidak ada lowercase.**")
    para("Dua perubahan terakhir mengikuti saran dosen. Di laporan progress, teks untuk IndoBERTweet dibuat huruf kecil dan "
         "emoji diubah ke bahasa Inggris. Huruf kapital bisa membawa informasi, karena 19,1% teks memuat kata kapital minimal "
         "4 huruf seperti \"BOIKOT\" atau \"MAMPUS\". Jadi teks sekarang dikirim apa adanya dan keputusan huruf kecil "
         "diserahkan ke tokenizer. Ada satu hal yang kami temukan saat mengecek tokenizer: IndoBERTweet dan IndoBERT adalah "
         "model uncased, jadi tokenizer-nya tetap mengubah teks menjadi huruf kecil. Hanya XLM-RoBERTa (cased) yang benar-benar "
         "bisa membedakan \"BOIKOT\" dan \"boikot\". Buktinya ada di log Kaggle notebook 03 (data/07_transformer/*.log): "
         "kedua tokenizer mencetak do_lower_case True, dan \"BOIKOT RANS\" dipecah IndoBERTweet menjadi [boikot, ran, ##s], "
         "sama persis dengan versi huruf kecilnya. Jadi untuk dua model ini, pilihan lowercase di preprocessing tidak "
         "mengubah apa pun yang dibaca model, dan kami tidak perlu menjalankan percobaan dengan dan tanpa lowercase. Emoji diubah ke bahasa Indonesia (😂 menjadi \"wajah gembira berurai air "
         "mata\") memakai emoji.demojize(language=\"id\"), karena modelnya dilatih dari teks Indonesia.")
    caption("Tabel 15. Contoh teks sebelum dan sesudah preprocessing")
    tabel([
        ["Teks asli", "BERT", "Lengkap (TF-IDF)"],
        ["KAMI ADALAH PUTERA DAN PUTERI BAYARAN....!!!!😂😂", "KAMI ADALAH PUTERA DAN PUTERI BAYARAN....!!!! wajah gembira berurai air mata wajah gembira ...",
         "putera puteri bayaran emo_wajah_gembira_berurai_air_mata ..."],
        ["Pemerintah anjingg apbn dipake buat endorse raffi ahmad", "Pemerintah anjingg apbn dipake buat endorse raffi ahmad",
         "pemerintah anjingg apbn dipakai endorse raffi ahmad"],
    ], lebar=[5, 6, 5], ukuran=8)

    # 10. AUGMENTASI
    judul("10. Augmentasi Kelas Positif", 1)
    para("Kelas positif hanya 84 teks, jadi setiap fold uji hanya punya 16 atau 17 teks positif. Di laporan progress kami membuat "
         "target biner (negatif lawan bukan negatif) untuk mengakalinya. Dosen menyarankan tetap 3 kelas dan menambah data "
         "positif lewat augmentasi, jadi target biner kami hapus. Ada dua sumber:")
    butir("• Komentar positif dari akun Raffi (jalur B). Sesuai saran Bu Mar, komentar dari akun Raffi boleh dipakai untuk "
          "menambah contoh positif selama rentang waktunya sesuai (22 Oktober sampai 14 November). Yang diambil hanya yang "
          "label akhirnya positif, bukan buzzer, dan akun maupun teksnya tidak ada di data utama, supaya model tidak bisa "
          "menghafal gaya akun yang juga ada di data uji. Hasilnya 42 teks.")
    butir("• Parafrase back-translation. Teks positif diterjemahkan ke bahasa Inggris dengan Helsinki-NLP/opus-mt-id-en "
          "(dengan sampling supaya bervariasi), lalu kembali ke Indonesia dengan opus-mt-en-id. Prosesnya dijalankan di Kaggle "
          "(augmentasi/kaggle_bt/back_translation.py), sampai 3 parafrase per teks. Dua teks yang baru dinilai positif setelah review 3 lapis dijalankan tersendiri (augmentasi/siapkan_bt_tambahan.py), tapi keduanya akhirnya dikoreksi menjadi negatif, jadi parafrasenya tidak terpakai.")
    para("Back-translation menghasilkan 484 parafrase dari 177 teks. Saringan otomatis membuang 140 yang jelas rusak: mention "
         "@user berubah (61), terpotong lebih dari separuh (51), muncul simbol aneh seperti ♪ (19), pengulangan karakter (7), "
         "dan terlalu pendek (2), jadi tersisa 344. Dari jumlah itu yang dipakai hanya parafrase dari teks yang label akhirnya positif: 172 dari data utama dan 81 dari jalur B. Saringan tidak bisa mengecek makna, jadi kami membaca 40 parafrase acak yang lolos.")
    caption("Tabel 16. Contoh hasil cek manual parafrase")
    tabel([
        ["Teks asli", "Parafrase", "Makna tetap?"],
        ["sabar raffi ahmad masi banyak orang yg percaya sm km. sy dukung km100 persen", "bersabar, Raffi ahmad masih banyak orang yang percaya padamu aku mendukungmu 100 persen", "ya"],
        ["kalau memang kita berniat baik dan tulus pasti Allah bantu 😇", "Jika kita memiliki niat yang baik dan tulus, Allah akan membantu kita.", "ya"],
        ["Ujian orang baik ,, sehat sehat a Raffi 😇", "Tes orang baik, sehat. Raffi sangat berbahaya.", "tidak, makna berbalik"],
        ["MAMPUS LU DIKULITI NETIZEN 😂", "MAMPUS LU FOLLOWED NETIZEN rush", "tidak, makna hilang"],
    ], lebar=[6.5, 6.5, 3], ukuran=8)
    para("Hasilnya 33 dari 40 (82,5%) masih mempertahankan sikap positif ke Raffi. Jadi sekitar 1 dari 6 parafrase "
         "kemungkinan membawa label yang salah. Daftar lengkapnya ada di augmentasi/cek_manual_bt.csv.")
    para("Kedua sumber **hanya masuk ke fold latih**. Parafrase dari teks yang sedang menjadi data uji atau validasi tidak "
         "dipakai, karena isinya hampir sama dengan teks ujinya. Data uji di semua varian tetap teks jalur A asli, jadi "
         "perbandingan sebelum dan sesudah augmentasi diukur di data yang sama persis. Setiap model diuji dengan empat "
         "varian: tanpa augmentasi, + jalur B, + parafrase, dan + keduanya (rata-rata 42, 137, dan 260 teks tambahan per fold).")

    from isi_model import ISI_MODEL
    ISI_MODEL(para, judul, caption, tabel, kode, gambar, butir, ROOT)
