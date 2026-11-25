"""Bangun laporan progress dalam format paper (Format UAS FP Paper (1).docx).

Pakai : python laporan/paper/hitung_prf.py && python laporan/paper/gambar_paper.py && python laporan/paper/buat_paper.py
Output: Laporan Progress UAS NLP - Kelompok J (Format Paper).docx
"""
import copy
import re
from pathlib import Path

import docx
import pandas as pd
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.oxml.ns import qn
from docx.shared import Pt, Cm

ROOT = Path(__file__).resolve().parents[2]
D, FIG, O = ROOT / "data", ROOT / "figures", ROOT / "data" / "09_perbandingan"
TEMPLATE = ROOT / "Format UAS FP Paper (1).docx"
OUT = ROOT / "Laporan Progress UAS NLP - Kelompok J (Format Paper).docx"

d = docx.Document(TEMPLATE)
body = d.element.body
P = d.paragraphs
PROTO = {"judul": P[0], "penulis": P[2], "h1": P[20], "isi": P[21], "h2": P[28], "abs_label": P[5],
         "abs": P[7], "kw": P[17], "caption": P[35]}
PROTO = {k: copy.deepcopy(v._p) for k, v in PROTO.items()}
TABEL_PROTO = copy.deepcopy(d.tables[0]._tbl)
for el in list(body.iterchildren()):
    if el.tag != qn("w:sectPr"):
        body.remove(el)
sect = body.find(qn("w:sectPr"))


def f3(x):
    return f"{x:.3f}".replace(".", ",")


def _baru(jenis, teks="", bold_awal=None, highlight=False, align=None):
    p_el = copy.deepcopy(PROTO[jenis])
    for r in p_el.findall(qn("w:r")):
        p_el.remove(r)
    sect.addprevious(p_el)
    p = docx.text.paragraph.Paragraph(p_el, d._body)
    rpr = PROTO[jenis].find(qn("w:r"))
    rpr = rpr.find(qn("w:rPr")) if rpr is not None else None
    if bold_awal:
        r = p.add_run(bold_awal)
        if rpr is not None:
            r._r.insert(0, copy.deepcopy(rpr))
        r.bold = True
    for i, bagian in enumerate(re.split(r"\*\*", teks)):
        if not bagian:
            continue
        r = p.add_run(bagian)
        if rpr is not None:
            r._r.insert(0, copy.deepcopy(rpr))
        if jenis == "abs":
            r.bold = False
        if i % 2:
            r.bold = True
        if highlight:
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    if align is not None:
        p.alignment = align
    return p


def judul_bab(t):
    p = _baru("h1", t)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6)
    return p


def subbab(t):
    p = _baru("h2", t)
    p.paragraph_format.keep_with_next = True
    return p


def subsub(t):
    p = _baru("isi", f"**{t}**")
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.keep_with_next = True
    return p


def para(t):
    p = _baru("isi", t, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.first_line_indent = Cm(0.75)
    return p


def kosong():
    return _baru("isi", "")


def caption(t, ikut=True):
    p = _baru("caption", t)
    p.paragraph_format.keep_with_next = ikut
    return p


def gambar(path, lebar_cm, teks):
    p = _baru("isi", "", align=WD_ALIGN_PARAGRAPH.CENTER)
    p.add_run().add_picture(str(path), width=Cm(lebar_cm))
    p.paragraph_format.keep_with_next = True
    caption(teks, ikut=False)


def tabel(baris, lebar=None, ukuran=9):
    t = d.add_table(rows=len(baris), cols=len(baris[0]))
    t.style = d.styles["Table Grid"]
    sect.addprevious(t._tbl)
    for i, row in enumerate(baris):
        for j, isi in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            r = c.paragraphs[0].add_run(str(isi))
            r.font.size = Pt(ukuran)
            r.bold = i == 0
            if lebar:
                c.width = Cm(lebar[j])
    kosong()
    return t


# JUDUL DAN PENULIS
_baru("judul", "Klasifikasi Sikap Warganet terhadap Raffi Ahmad setelah Kasus “Mahasiswa Bayaran” "
               "dengan Model Transformer Bahasa Indonesia dan Augmentasi Kelas Positif")
kosong()
# Daftar penulis dan tanpa abstrak, mengikuti suntingan manual di docx versi 24 Nov
_baru("penulis", "Mikael Ardiyanta Widyadana Purniawan, Raphael Angelo Adikara Purnama, Aditya Naufal Jay Putra, "
                  "Najwa Yasyfa Dhiya Sugina, Exsalia Eka Nevita, Anindhito Gading Rasunajati")
_baru("penulis", "Kelompok 10 · Program Studi S1 Teknologi Sains Data, Fakultas Teknologi Maju dan Multidisiplin, "
                  "Universitas Airlangga")

# INTRODUCTION
judul_bab("Introduction")
para("Pada 29 Oktober 2026 sekelompok orang yang mengaku mahasiswa membacakan deklarasi di Bundaran HI. Tidak lama "
     "kemudian beredar pengakuan bahwa sebagian peserta dibayar, dan nama Raffi Ahmad ikut terseret karena posisinya sebagai "
     "utusan khusus presiden dan karena hadir di acara tersebut. Kasus ini lalu melebar ke klarifikasi Raffi, ajakan boikot "
     "RANS, dan temuan ICW soal kontrak Rp14,7 miliar. Pertanyaan yang ingin kami jawab sederhana: bagaimana sikap warganet "
     "terhadap Raffi, dan apakah masih ada yang membelanya.")
para("Pertanyaan ini sulit dijawab dengan membaca komentar satu per satu, karena jumlahnya ribuan dan tersebar di empat "
     "platform. Klasifikasi sentimen otomatis bisa membantu, tapi ada dua masalah khusus di data ini. Pertama, kelas positif "
     "sangat sedikit, hanya 84 dari 3.329 teks (2,5%), jadi model cenderung mengabaikannya (Henning et al., 2023). Kedua, "
     "pembelaan sering ditulis dengan nada marah ke pengkritik Raffi, misalnya “kerja namany itu proooo dunia gak ada "
     "gratisss”. Nadanya negatif, padahal sikapnya ke Raffi positif. Ini membuat masalahnya lebih dekat ke klasifikasi "
     "sikap terhadap target daripada sentimen biasa.")
para("Penelitian sentimen bahasa Indonesia sudah banyak memakai model pralatih seperti IndoBERT (Wilie et al., 2020; Koto "
     "et al., 2020) dan IndoBERTweet (Koto et al., 2021), dan benchmark seperti NusaX (Winata et al., 2023) menunjukkan model "
     "ini kuat untuk bahasa Indonesia. Namun sebagian besar benchmark memakai data yang kelasnya cukup seimbang dan topiknya "
     "umum. Bahasa media sosial Indonesia juga penuh singkatan, campur bahasa daerah, dan sarkasme (Aji et al., 2022). "
     "Penelitian kami mengambil kasus yang lebih sempit, yaitu satu tokoh dan satu peristiwa, dengan kelas positif yang "
     "sangat langka dan label yang dibuat dengan bantuan LLM lalu divalidasi manusia.")
para("Isi laporan progress ini adalah dataset 3.329 teks berlabel sikap terhadap Raffi dari empat platform, lengkap dengan "
     "catatan filter, pelabelan, dan review-nya. Di atas dataset itu kami membandingkan sembilan model pada pembagian fold "
     "yang sama, termasuk dampak judul unggahan dan tiga jenis augmentasi kelas positif, lalu membaca kesalahan model satu "
     "per satu. Kami juga menjelaskan bagaimana metode ini berubah dari versi awal tanggal 16 November sampai versi "
     "sekarang, dan kenapa kami akhirnya memilih IndoBERT sebagai model utama.")

# RELATED WORKS
judul_bab("Related Works")
para("Survei analisis sentimen menunjukkan pergeseran dari leksikon dan fitur kata ke model pralatih berbasis transformer "
     "(Wankhade et al., 2022; Tan et al., 2023). BERT (Devlin et al., 2019) dan turunannya menjadi dasar sebagian besar "
     "pendekatan terbaru. Untuk bahasa Indonesia, IndoNLU (Wilie et al., 2020) merilis IndoBERT beserta benchmark tugas "
     "pemahaman, IndoLEM (Koto et al., 2020) merilis IndoBERT versi lain, dan IndoBERTweet (Koto et al., 2021) dilatih khusus "
     "dari tweet Indonesia. Model multibahasa XLM-RoBERTa (Conneau et al., 2020) juga sering dipakai sebagai pembanding. "
     "Inisiatif NusaCrowd (Cahyawijaya et al., 2023) dan NusaX (Winata et al., 2023) memperluas sumber data bahasa Indonesia "
     "dan bahasa daerah. Leksikon InSet (Koto & Rahmaningtyas, 2017) kami pakai sebagai baseline tanpa pembelajaran.")
para("Untuk pelabelan, beberapa penelitian menunjukkan LLM bisa menjadi annotator yang murah dan cukup akurat untuk tugas "
     "teks media sosial (Gilardi et al., 2023; Törnberg, 2023; Wang et al., 2021; Ding et al., 2023). Tapi hasilnya "
     "tidak selalu stabil antar tugas (Zhu et al., 2023; Kocoń et al., 2023), jadi Pangakis et al. (2023) dan Ziems et "
     "al. (2024) menyarankan agar label LLM selalu divalidasi dengan label manusia. Zhang et al. (2024) juga menemukan LLM "
     "masih tertinggal dari model kecil yang di-fine-tune untuk sentimen yang butuh pemahaman target. Karena itu kami memakai "
     "tiga LLM sebagai annotator awal, lalu semua teks yang tidak disepakati bulat dinilai tiga orang dan diukur dengan "
     "Fleiss’ kappa (Fleiss, 1971; Landis & Koch, 1977).")
para("Untuk kelas yang tidak seimbang, Henning et al. (2023) merangkum pilihan yang umum di NLP, yaitu pembobotan kelas, "
     "pengambilan ulang sampel, dan augmentasi data. Survei augmentasi teks (Feng et al., 2021; Shorten et al., 2021; Bayer et "
     "al., 2022; Chen et al., 2023) menunjukkan back-translation (Sennrich et al., 2016) sebagai salah satu cara paling umum, "
     "tapi juga mencatat risiko makna berubah. Kami memakai OPUS-MT (Tiedemann & Thottingal, 2020) untuk back-translation dan "
     "membandingkannya dengan menambah teks positif asli. Untuk evaluasi kelas langka kami memakai average precision di "
     "samping F1, karena kurva precision-recall lebih informatif daripada ROC saat data tidak seimbang (Saito & Rehmsmeier, "
     "2015). Mosbach et al. (2021) juga menunjukkan fine-tuning BERT di data kecil bisa tidak stabil, dan ini kami temukan "
     "sendiri saat menjalankan ulang model yang sama. Terakhir, penyaringan akun buzzer kami dasarkan pada temuan bahwa akun "
     "terkoordinasi sering memakai pola teks dan aktivitas yang seragam (Cresci, 2020).")

# METHODS
judul_bab("Methods")
para("Bagian ini dibagi dua. Subbab Material menjelaskan data yang kami kumpulkan dan bagaimana data itu dibersihkan dan "
     "dilabeli. Subbab Methodology menjelaskan alur penelitian, pembagian data, model, dan cara evaluasinya.")
subbab("Material")
para("Data diambil dari 22 Oktober sampai 14 November 2026 dan dibagi ke tiga fase: pra (22 sampai 28 Oktober), puncak "
     "(29 Oktober sampai 2 November), dan pasca (3 sampai 14 November). Di X yang diambil langsung tweet-nya. Di Instagram, "
     "YouTube, dan TikTok kami mencari unggahan atau video tentang kasus ini, lalu mengambil komentar di bawahnya. Komentar "
     "di unggahan berita dan diskusi publik kami sebut jalur A dan menjadi data utama. Komentar di akun Instagram Raffi "
     "sendiri kami sebut jalur B dan hanya dipakai sebagai pembanding dan bahan augmentasi, karena yang berkomentar di sana "
     "kemungkinan besar pengikutnya.")
caption("Tabel 1. Jumlah data mentah per platform")
tabel([["Platform", "Sumber", "Jumlah teks"],
       ["X", "tweet unik dari 24 hari pencarian", "2.197"],
       ["Instagram", "22 unggahan jalur A (1.418) dan 8 unggahan jalur B (571)", "1.989"],
       ["YouTube", "20 video, 100 komentar per video", "2.000"],
       ["TikTok", "14 video, sekitar 60 komentar per video", "834"],
       ["Total", "", "7.020"]], lebar=[2.5, 9.5, 2.5])
para("Data mentah lalu disaring dari teks kosong, spam, duplikat, teks yang tidak membahas Raffi, dan buzzer. Setiap aturan "
     "otomatis hanya menandai kandidat, lalu kandidat itu dibaca manual, dan 61 teks diselamatkan dari pembuangan yang keliru. "
     "Buzzer ditandai dengan aturan keras dan skor poin, dan teks di zona batas diputuskan manusia. Dari teks yang lolos, "
     "3.525 teks jalur A dan 525 teks jalur B diambil sebagai sampel untuk dilabeli, dan 2.623 teks disimpan sebagai cadangan.")
para("Setiap teks diberi label sikap terhadap Raffi: negatif, netral, positif, atau tidak relevan. Tiga LLM (Claude Opus, "
     "Sonnet, dan Haiku) melabeli secara terpisah. Sebanyak 2.750 teks jalur A disepakati bulat. Sisanya, bersama teks jalur "
     "B yang tidak disepakati, dinilai tiga anggota kelompok dari lima orang yang ada, total 881 kartu. Fleiss’ kappa di "
     "881 kartu ini 0,286, masuk kategori cukup (fair). Angkanya rendah karena kartu yang direview memang teks yang sulit, "
     "yaitu teks yang membuat tiga LLM tidak sepakat. Setelah 14 teks buzzer dan 182 teks tidak relevan dikeluarkan, dataset "
     "final berisi 3.329 teks: 2.206 negatif (66,3%), 1.039 netral (31,2%), dan 84 positif (2,5%).")
gambar(FIG / "p02_sebaran_label.png", 15.5, "Gambar 1. Sebaran label per platform dan per fase")
para("Gambar 1 menunjukkan kelas negatif paling banyak di semua platform. X menyumbang teks terbanyak (1.266), sedangkan "
     "TikTok paling sedikit (488) tapi porsi positifnya paling besar (30 teks, 6,1%). Per fase, porsi negatif naik dari "
     "63,2% di fase puncak ke 69,3% di fase pasca. Fase pra hanya berisi 30 teks, jadi angkanya tidak kami tafsirkan. "
     "Setiap teks juga punya judul unggahan, yaitu caption Instagram, judul video YouTube, deskripsi TikTok, atau "
     "tweet yang dibalas di X. Semua teks Instagram, YouTube, dan TikTok punya judul, sedangkan di X hanya 52,4%.")

subbab("Methodology")
para("Alur penelitian kami ada di Gambar 2. Setiap tahap punya skrip atau notebook sendiri, dan hasil antara disimpan "
     "sebagai berkas supaya bisa dicek ulang.")
gambar(FIG / "p01_alur_penelitian.png", 10, "Gambar 2. Alur penelitian")
subsub("Pembagian data dan metrik")
para("Data dibagi dengan grouped stratified 5-fold cross-validation. Teks dari akun yang sama dan teks identik selalu "
     "berada di fold yang sama, supaya model tidak menghafal gaya satu akun lalu diuji di akun itu juga. Setiap fold uji "
     "berisi sekitar 441 negatif, 208 netral, dan 16 sampai 17 positif. Semua model memakai pembagian fold yang sama, jadi "
     "hasilnya bisa dibandingkan per fold. Metrik utamanya macro-F1, karena model yang selalu menebak negatif sudah mendapat "
     "akurasi 0,663 tanpa pernah benar di kelas lain. Untuk kelas positif kami juga melaporkan F1 positif dan average "
     "precision (AP).")
subsub("Preprocessing dan input")
para("Untuk model TF-IDF, teks di-lowercase, URL dan mention diganti token, dan huruf yang diulang dipendekkan. Untuk model "
     "BERT, teks dikirim apa adanya tanpa lowercase dan emoji diubah menjadi kata bahasa Indonesia. Setiap model diuji dengan "
     "dua input: teks saja, dan teks + judul dengan format [CLS] komentar [SEP] judul [SEP]. Judul ditambahkan karena separuh "
     "teks (50,8%) ditandai annotator butuh judul supaya sasarannya jelas.")
subsub("Augmentasi kelas positif")
para("Augmentasi hanya ditambahkan ke fold latih, tidak pernah ke fold uji. Ada tiga sumber. Jalur B berisi 42 komentar "
     "positif dari akun Raffi sendiri. Parafrase dibuat dengan back-translation Indonesia ke Inggris lalu kembali ke "
     "Indonesia memakai OPUS-MT. Pelabelan terarah dibuat dari teks cadangan: model TF-IDF mengurutkan 2.623 teks cadangan "
     "berdasarkan skor positif, lalu 250 teks teratas dan 50 teks acak dilabeli dengan alur yang sama (3 LLM, lalu 3 orang). "
     "Annotator tidak diberi tahu skor atau cara pilih teksnya. Hasilnya 32 teks positif baru.")
subsub("Model")
para("Kami membandingkan sembilan model. Dua baseline tanpa pembelajaran, yaitu kelas terbanyak dan leksikon InSet. Dua "
     "model TF-IDF (Logistic Regression dan Linear SVM) dengan n-gram kata dan huruf, judul sebagai vektor terpisah berbobot "
     "0,5, dan class weight balanced. IndoBERT embedding + LogReg memakai rata-rata vektor token IndoBERT yang dibekukan. "
     "BiLSTM + attention (Zhou et al., 2016) memakai embedding kata IndoBERT yang dibekukan. Tiga model di-fine-tune, yaitu "
     "IndoBERT (indobenchmark/indobert-base-p1), IndoBERTweet (indolem/indobertweet-base-uncased), dan XLM-RoBERTa base. Model "
     "fine-tune memakai learning rate 2e-5, batch 16, 5 epoch, warmup 10%, class weight, dan epoch terbaik dipilih dari 10% "
     "data latih yang dipisah per grup. Semua model berbasis BERT dijalankan di GPU T4 Kaggle.")
para("Selain model tunggal, kami menguji ensemble dengan merata-ratakan probabilitas IndoBERT dan IndoBERTweet, dan "
     "penggeseran ambang kelas positif yang bobotnya dipilih dari 4 fold lain lalu diterapkan ke fold uji.")

subbab("Perkembangan Metode")
para("Metode di atas bukan rancangan pertama kami. Versi awal selesai pada 16 November 2026 dan sudah punya hasil model. "
     "Setelah konsultasi dengan dosen pada 17 November, sebagian besar tahapnya kami ubah. Lalu pada 22 sampai 24 November "
     "kami menambah pelabelan terarah, karena F1 positif masih rendah dan learning curve menunjukkan data positif belum "
     "cukup. Tabel 2 merangkum apa yang berubah dan alasannya.")
caption("Tabel 2. Metode versi awal (16 November) dan versi akhir (24 November)")
tabel([
    ["Bagian", "Versi awal", "Versi akhir", "Alasan perubahan"],
    ["Filter data", "Aturan otomatis langsung membuang teks",
     "Aturan hanya menandai kandidat, setiap kandidat dibaca manual",
     "Saran dosen supaya filter tidak overklaim. Ternyata 61 teks salah buang"],
    ["Review manusia", "Teks yang tidak disepakati 3 AI dibagi ke 5 orang, 1 orang per teks. Kappa 0,393 dari 30 teks "
     "bersama", "Setiap teks yang tidak disepakati dinilai 3 orang. Kappa 0,286 dari 881 kartu",
     "Saran dosen. Label tidak lagi bergantung pada satu orang, dan kappa dihitung dari semua kartu"],
    ["Dataset final", "3.272 teks: 2.200 negatif, 982 netral, 90 positif",
     "3.329 teks: 2.206 negatif, 1.039 netral, 84 positif", "Hasil filter dan review yang baru"],
    ["Target", "3 kelas dan biner (negatif atau bukan)", "3 kelas saja",
     "Saran dosen. Versi biner mencampur netral dan positif, padahal yang ingin kami tahu justru siapa yang membela Raffi"],
    ["Input BERT", "Huruf kecil semua, emoji jadi kata Inggris, komentar + konteks",
     "Teks apa adanya, emoji jadi kata Indonesia, teks + judul dengan [SEP]",
     "Saran dosen. Emoji disamakan dengan bahasa teksnya"],
    ["Model", "Baseline, TF-IDF, IndoBERTweet",
     "Ditambah IndoBERT dan XLM-R fine-tune, IndoBERT embedding + LogReg, BiLSTM + attention",
     "Saran dosen. Supaya kelihatan apakah kenaikan datang dari fine-tuning atau sudah dari representasi IndoBERT"],
    ["Kelas positif", "Hanya class weight. Jalur B tidak dipakai untuk latih",
     "Class weight + augmentasi jalur B, parafrase, dan pelabelan terarah, hanya di fold latih",
     "F1 positif versi awal hanya 0,338, dan learning curve belum mendatar"],
    ["Model utama", "IndoBERTweet teks saja, macro-F1 0,604, F1 positif 0,338",
     "IndoBERT teks + judul + jalur B + terarah, macro-F1 0,616, F1 positif 0,352",
     "Dijelaskan di paragraf berikut"],
], lebar=[2.4, 4.2, 4.4, 4.6], ukuran=8)
para("Perubahan terbesar ada di label. Di versi awal, teks yang tidak disepakati tiga AI hanya dinilai satu orang, jadi "
     "labelnya bergantung pada siapa yang kebetulan mendapat teks itu. Kappa 0,393 waktu itu juga hanya dihitung dari 30 "
     "teks yang dikerjakan semua orang. Di versi akhir kappanya turun ke 0,286, tapi angka ini lebih bisa dipercaya karena "
     "dihitung dari semua 881 kartu sulit, bukan dari sampel kecil. Karena labelnya berubah, angka versi awal dan versi "
     "akhir di Tabel 2 tidak bisa dibandingkan langsung. Perbandingan yang adil hanya bisa dibuat di dalam versi akhir, "
     "dengan fold yang sama.")
para("Model utama juga berganti dari IndoBERTweet ke IndoBERT. Di versi awal IndoBERTweet hanya kami bandingkan dengan "
     "TF-IDF, dan konteks malah menurunkan skornya (0,604 tanpa konteks, 0,583 dengan konteks). Setelah IndoBERT ikut diuji, "
     "polanya berbeda. Judul menaikkan macro-F1 IndoBERT sebesar 0,048 di kelima fold, sedangkan IndoBERTweet hanya naik "
     "0,006. Separuh teks butuh judul supaya sasarannya jelas, jadi kami memilih model yang bisa memanfaatkan judul itu. "
     "IndoBERT juga punya F1 positif (0,352) dan AP positif (0,383) tertinggi di antara model tunggal.")
para("Ensemble IndoBERT + IndoBERTweet sebenarnya mendapat macro-F1 lebih tinggi (0,628). Kami tetap menjadikan IndoBERT "
     "model utama karena selisihnya hanya 0,012 dan masih di dalam standar deviasi antar fold, AP positif ensemble tidak "
     "lebih tinggi (0,381), dan ensemble butuh dua kali waktu latih dan prediksi. Ensemble tetap kami laporkan sebagai "
     "pembanding.")

# RESULT
judul_bab("Result")
para("Setiap model dijalankan dengan dua input dan beberapa varian augmentasi, jadi totalnya ada 56 konfigurasi dari "
     "sembilan model. Untuk model fine-tune, tidak semua kombinasi dijalankan supaya kuota GPU Kaggle cukup. Tabel 3 "
     "mengambil satu konfigurasi terbaik untuk setiap model. Precision (P), recall (R), dan F1 adalah nilai macro yang "
     "dirata-rata dari 5 fold uji.")
prf = pd.read_csv(O / "perbandingan_prf.csv").sort_values("F1")
caption("Tabel 3. Comparison Method")
tabel([["No", "Method", "Input dan augmentasi", "P", "R", "F1-Score", "F1 positif"]] +
      [[str(i + 1), r.model, f"{r.input}, {r.augmentasi}", f3(r.P), f3(r.R), f"{f3(r.F1)} ± {f3(r.F1_sd)}",
        f3(r.F1_positif)] for i, r in enumerate(prf.itertuples())],
      lebar=[0.9, 4.2, 4.4, 1.3, 1.3, 2.4, 1.6], ukuran=8)
para("Fine-tune IndoBERT dengan teks + judul dan augmentasi jalur B + terarah mendapat macro-F1 tertinggi untuk model "
     "tunggal (0,616), diikuti IndoBERTweet (0,609) dan TF-IDF + LogReg (0,603). Ensemble IndoBERT + IndoBERTweet sedikit lebih "
     "tinggi (0,628). Jarak antara model transformer terbaik dan TF-IDF hanya 0,013, lebih kecil dari yang kami harapkan, dan "
     "per fold model terbaik hanya unggul di 3 dari 5 fold. IndoBERT embedding + LogReg setara TF-IDF, jadi kenaikan baru "
     "muncul saat bobot IndoBERT ikut dilatih. XLM-RoBERTa lebih lemah dari dua model Indonesia, dan BiLSTM paling rendah di "
     "antara model yang belajar karena 3.329 teks terlalu sedikit untuk melatih LSTM. Leksikon InSet hanya 0,315 karena "
     "kata negatif di pembelaan membuatnya salah arah.")
subsub("Dampak judul dan augmentasi")
para("Judul menaikkan macro-F1 di semua model, paling besar di IndoBERT embedding + LogReg (+0,064), XLM-RoBERTa (+0,060), "
     "dan TF-IDF + LogReg (+0,058). IndoBERT fine-tune naik 0,048 di 5 dari 5 fold, sedangkan IndoBERTweet hanya +0,006. "
     "Dugaan kami, IndoBERTweet dilatih dari tweet pendek, jadi kurang cocok dengan input panjang berisi judul berita.")
gambar(FIG / "p04_progres_indobert.png", 11, "Gambar 3. Macro-F1 dan F1 positif IndoBERT fine-tune per tahap perbaikan")
para("Gambar 3 memperlihatkan efek setiap perbaikan pada IndoBERT fine-tune dengan fold yang sama. Macro-F1 naik dari 0,559 "
     "(teks saja) ke 0,607 setelah judul ditambahkan, lalu ke 0,614 dengan jalur B dan 0,616 dengan pelabelan terarah. "
     "Kenaikan terbesar datang dari judul. Augmentasi hanya sedikit menggeser macro-F1, tapi F1 positif naik dari 0,293 "
     "ke 0,352, dan kelas inilah yang paling ingin kami perbaiki.")
dampak = pd.read_csv(O / "dampak_augmentasi.csv")
rows = [["Varian", "Konfigurasi membaik", "Rata-rata Δ macro-F1", "Rata-rata Δ F1 positif"]]
for v in ["jalur B", "parafrase", "jalur B + parafrase", "jalur B + terarah"]:
    t = dampak[dampak.augmentasi == v]
    dm, dp = t["Δ macro-F1"], t["Δ F1 positif"]
    rows.append([v, f"{int((dm > 0).sum())} dari {len(t)}", f3(dm.mean()), f3(dp.mean())])
caption("Tabel 4. Dampak augmentasi dibanding tanpa augmentasi")
tabel(rows, lebar=[4, 3.5, 3.5, 3.5])
para("Komentar positif jalur B menaikkan skor di 9 dari 9 konfigurasi. Parafrase hanya membantu XLM-RoBERTa dan justru "
     "menurunkan F1 positif rata-rata 0,020. Dari cek manual, sekitar 1 dari 6 parafrase maknanya rusak atau berbalik, dan "
     "parafrase memakai judul yang sama dengan teks aslinya, jadi model bisa menghafal judul. Pelabelan terarah membantu "
     "di 5 dari 8 konfigurasi.")
dt = pd.read_csv(O / "dampak_terarah.csv")
caption("Tabel 5. Dampak pelabelan terarah dibanding jalur B saja")
tabel([["Model", "Input", "Macro-F1 jalur B", "+ terarah", "Fold membaik", "F1 positif jalur B", "+ terarah"]] +
      [[r[0], r[1], f3(r[2]), f3(r[3]), r[5], f3(r[6]), f3(r[7])] for r in dt.itertuples(index=False)],
      lebar=[4, 2.2, 2, 1.6, 1.6, 2, 1.6], ukuran=8)
para("Dari 250 teks cadangan dengan skor tertinggi hanya 33 yang positif (13%), dan dari 50 teks acak ada 2 (4%). "
     "Fleiss’ kappa di 73 kartu review terarah 0,260, setara review utama. Tabel 5 menunjukkan dampaknya terbagi dua. "
     "TF-IDF dan model fine-tune terbantu: F1 positif IndoBERT naik dari 0,325 ke 0,352 dan AP positif dari 0,333 ke 0,383. "
     "Model dengan representasi beku justru turun. Semua perubahan ini masih di dalam standar deviasi antar fold.")
subsub("Strategi lain untuk kelas positif")
para("Kalau semua teks ditebak positif, F1 positif hanya 0,049, dan AP tebakan acak 0,025. AP model terbaik 0,383, sekitar "
     "15 kali tebakan acak. Ensemble IndoBERT + IndoBERTweet menaikkan macro-F1 tapi AP-nya (0,381) tidak lebih tinggi dari "
     "IndoBERT sendirian. Menambahkan XLM-RoBERTa ke ensemble justru menurunkan macro-F1 dari 0,617 ke 0,602. Penggeseran "
     "ambang kelas positif tidak membantu secara konsisten, dan bobot terbaiknya berbeda-beda tiap fold.")
gambar(FIG / "p03_learning_curve_positif.png", 11, "Gambar 4. Learning curve kelas positif (TF-IDF + LogReg)")
para("Gambar 4 menunjukkan F1 positif TF-IDF naik dari 0,064 dengan 17 teks positif di data latih menjadi 0,272 dengan 67 "
     "teks, dan kurvanya belum mendatar. Artinya menambah teks positif asli masih berguna.")
subsub("Analisis kesalahan")
gambar(FIG / "05_confusion_matrix.png", 15, "Gambar 5. Confusion matrix TF-IDF dan model terbaik")
para("Recall model terbaik adalah 82,2% untuk negatif, 67,4% untuk netral, dan 35,7% untuk positif. Teks positif yang salah "
     "hampir semuanya ditebak negatif (57,1% dari semua teks positif). Kesalahan terbanyak secara jumlah ada di batas negatif "
     "dan netral (341 dan 331 teks), batas yang juga paling sering diperdebatkan penilai manusia. Untuk teks positif, "
     "dukungan benar 77,3%, tapi pembelaan hanya benar 16,7% (7 dari 42). Model juga paling sering salah di teks yang "
     "mengkritik pihak lain (macro-F1 0,490) dan teks yang butuh judul (0,530).")
subsub("Temuan sikap warganet")
para("Dari label akhir yang sudah dicek manusia, hanya 2,5% komentar jalur A yang positif. Kalau ditimbang jumlah like, "
     "porsinya turun menjadi 0,2%. Dari fase puncak ke pasca, porsi negatif naik dari 63,2% menjadi 69,3% (uji chi-square "
     "p = 0,0002), jadi setelah klarifikasi sikap warganet tidak melunak. Di akun Instagram Raffi sendiri, 78,0% komentar "
     "negatif, lebih tinggi dari Instagram jalur A (62,7%).")

# DISCUSSION
judul_bab("Discussion")
para("Temuan pertama, model fine-tune hanya sedikit lebih baik dari TF-IDF. Kami melihat dua alasan. Data latih hanya "
     "sekitar 2.660 teks per fold dengan 67 positif, jadi kelebihan model besar belum terlihat penuh. Selain itu, label di "
     "batas negatif dan netral memang tidak konsisten (kappa netral 0,219), jadi skor tertinggi yang bisa dicapai ikut "
     "dibatasi oleh kualitas label itu sendiri. Model yang di-fine-tune juga tidak deterministik. Saat kernel IndoBERTweet "
     "dijalankan ulang, skor konfigurasi yang sama bergeser dari 0,614 ke 0,597, sejalan dengan temuan Mosbach et al. (2021). "
     "Jadi selisih di bawah 0,02 antar konfigurasi tidak bisa dibaca sebagai kemenangan yang pasti.")
para("Temuan kedua, data asli lebih berguna daripada data sintetis. Jalur B dan pelabelan terarah menambah variasi cara orang "
     "membela Raffi, sedangkan parafrase hanya mengulang teks yang sudah ada dan sebagian maknanya rusak. Ini sejalan dengan "
     "catatan Chen et al. (2023) bahwa augmentasi berbasis parafrase tidak selalu membantu model pralatih yang sudah kuat. "
     "Pelabelan terarah sendiri hasilnya di bawah perkiraan. Kami memperkirakan 40 sampai 60 positif dari 300 teks, ternyata "
     "35. Teks cadangan kelihatannya memang sisa yang tidak terpilih di sampel utama, dan 18 di antaranya tidak relevan.")
para("Temuan ketiga, kelemahan utama model adalah pembelaan yang ditulis dengan nada marah, misalnya “netizen harusnya "
     "paham bedanya tamu undangan instansi sama peserta aksi massa”. Model membaca nadanya, bukan sasarannya. Masalah ini "
     "lebih dekat ke deteksi sikap terhadap target. Untuk tahap berikutnya ada dua arah yang menurut kami paling masuk akal: "
     "memberi model informasi target secara eksplisit di input, atau memakai LLM sebagai pembanding karena LLM lebih mampu "
     "membaca konteks pembelaan walaupun masih perlu divalidasi (Zhang et al., 2024; Ziems et al., 2024).")
para("Tabel 6 melengkapi Tabel 2. Kalau Tabel 2 berisi apa yang berubah dari versi awal, Tabel 6 berisi hasil dari setiap "
     "saran dosen setelah kami kerjakan.")
caption("Tabel 6. Saran dosen dan tindak lanjutnya")
tabel([
    ["Saran dosen", "Yang kami kerjakan", "Hasil"],
    ["Gerbang filter jangan overklaim", "Aturan otomatis hanya menandai kandidat, setiap kandidat dibaca manual",
     "61 teks diselamatkan"],
    ["Relevansi dan buzzer harus jelas siapa yang memutuskan", "Kata kunci dan skor menandai, manusia memutuskan, "
     "tidak_relevan dinilai 3 AI dan 3 orang", "14 buzzer dan 182 teks tidak relevan dikeluarkan"],
    ["Label dinilai 3 orang dan dihitung Fleiss’ kappa", "Semua teks yang tidak disepakati 3 AI dinilai 3 orang, "
     "termasuk pelabelan terarah", "881 kartu, kappa 0,286; terarah 73 kartu, kappa 0,260"],
    ["Hapus target biner", "Semua model memakai 3 kelas", "Target biner tidak dipakai lagi"],
    ["Sampel positif dari akun Raffi dan augmentasi", "Jalur B, parafrase back-translation, dan pelabelan terarah, "
     "hanya di fold latih", "Jalur B membantu 9/9, parafrase 1/9, terarah 5/8"],
    ["BERT tanpa lowercase", "Teks dikirim apa adanya, emoji jadi kata Indonesia",
     "IndoBERT dan IndoBERTweet uncased, jadi tidak berpengaruh; hanya XLM-R yang membaca kapital"],
    ["Coba IndoBERT embedding + LogReg dan model kontekstual", "Embedding + LogReg, BiLSTM, fine-tune 3 model",
     "Fine-tune terbaik (0,616), embedding setara TF-IDF"],
    ["F1 positif masih rendah", "Ensemble, ambang, learning curve, peringkat cadangan, pelabelan terarah",
     "F1 positif naik dari 0,325 ke 0,352, ambang tidak membantu"],
    ["Analisis kesalahan", "Confusion matrix, akurasi per kelompok, pembacaan contoh",
     "Pembelaan bernada marah paling sering salah (16,7% benar)"],
], lebar=[4.2, 6.2, 5], ukuran=8)
para("Keterbatasan penelitian ini ada di jumlah teks positif yang kecil, kappa yang hanya cukup, data X yang terbatas pada "
     "tweet berisi kata kunci, dan tidak adanya umur akun di Instagram dan TikTok untuk filter buzzer. Tujuh kartu terarah "
     "yang seri juga diputus dengan mayoritas 3 LLM, bukan lewat diskusi tim. XLM-RoBERTa tidak dilatih ulang dengan varian "
     "terarah karena paling lemah dan satu kernel butuh sekitar satu jam GPU.")

# CONCLUSION
judul_bab("Conclusion")
para("Model terbaik untuk mengklasifikasi sikap warganet terhadap Raffi Ahmad adalah fine-tune IndoBERT dengan input teks "
     "+ judul dan augmentasi jalur B + terarah (macro-F1 0,616), dan ensemble IndoBERT + IndoBERTweet sedikit lebih tinggi "
     "(0,628). Judul unggahan adalah tambahan input yang paling konsisten membantu, augmentasi dengan teks positif asli lebih "
     "berguna daripada parafrase, dan kelas positif tetap paling sulit (F1 0,352). Dari sisi isi, hanya 2,5% komentar yang "
     "membela Raffi, dan sikap negatif justru naik setelah klarifikasi.")
para("Dibanding versi awal tanggal 16 November, metode kami berubah di hampir semua tahap. Label sekarang dinilai tiga "
     "orang, target biner dihapus, model yang diuji bertambah dari lima menjadi sembilan, dan kelas positif dibantu "
     "augmentasi dari teks asli. Model utama berganti dari IndoBERTweet ke IndoBERT karena IndoBERT bisa memanfaatkan judul "
     "unggahan, dan judul inilah tambahan input yang paling konsisten membantu.")
para("Sampai laporan progress ini, seluruh pipeline dari scraping sampai analisis kesalahan sudah selesai dan bisa "
     "dijalankan ulang. Pekerjaan berikutnya adalah menambah teks positif asli dari sumber baru karena teks cadangan sudah "
     "tidak sekaya perkiraan, mencoba input yang menyebut target secara eksplisit untuk membantu kasus pembelaan bernada "
     "marah, membandingkan dengan klasifikasi zero-shot oleh LLM, dan menjalankan setiap model dengan beberapa seed supaya "
     "selisih kecil antar konfigurasi bisa diuji lebih tegas.")

# REFERENCES
judul_bab("References")
REF = [
    "Aji, A. F., Winata, G. I., Koto, F., Cahyawijaya, S., Romadhony, A., Mahendra, R., Kurniawan, K., Moeljadi, D., Prasojo, R. E., Baldwin, T., Lau, J. H., & Ruder, S. (2022). One country, 700+ languages: NLP challenges for underrepresented languages and dialects in Indonesia. In Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). Association for Computational Linguistics.",
    "Bayer, M., Kaufhold, M.-A., & Reuter, C. (2022). A survey on data augmentation for text classification. ACM Computing Surveys, 55(7), 1–39.",
    "Cahyawijaya, S., Lovenia, H., Aji, A. F., Winata, G. I., Wilie, B., et al. (2023). NusaCrowd: Open source initiative for Indonesian NLP resources. In Findings of the Association for Computational Linguistics: ACL 2023. Association for Computational Linguistics.",
    "Chen, J., Tam, D., Raffel, C., Bansal, M., & Yang, D. (2023). An empirical survey of data augmentation for limited data learning in NLP. Transactions of the Association for Computational Linguistics, 11, 191–211.",
    "Conneau, A., Khandelwal, K., Goyal, N., Chaudhary, V., Wenzek, G., Guzmán, F., Grave, E., Ott, M., Zettlemoyer, L., & Stoyanov, V. (2020). Unsupervised cross-lingual representation learning at scale. In Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics. Association for Computational Linguistics.",
    "Cresci, S. (2020). A decade of social bot detection. Communications of the ACM, 63(10), 72–83.",
    "Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. In Proceedings of NAACL-HLT 2019. Association for Computational Linguistics.",
    "Ding, B., Qin, C., Liu, L., Chia, Y. K., Li, B., Joty, S., & Bing, L. (2023). Is GPT-3 a good data annotator? In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). Association for Computational Linguistics.",
    "Feng, S. Y., Gangal, V., Wei, J., Chandar, S., Vosoughi, S., Mitamura, T., & Hovy, E. (2021). A survey of data augmentation approaches for NLP. In Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021. Association for Computational Linguistics.",
    "Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. Psychological Bulletin, 76(5), 378–382.",
    "Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120.",
    "Henning, S., Beluch, W., Fraser, A., & Friedrich, A. (2023). A survey of methods for addressing class imbalance in deep-learning based natural language processing. In Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics. Association for Computational Linguistics.",
    "Kocoń, J., Cichecki, I., Kaszyca, O., Kochanek, M., Szydło, D., Baran, J., et al. (2023). ChatGPT: Jack of all trades, master of none. Information Fusion, 99, 101861.",
    "Koto, F., Lau, J. H., & Baldwin, T. (2021). IndoBERTweet: A pretrained language model for Indonesian Twitter with effective domain-specific vocabulary initialization. In Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing. Association for Computational Linguistics.",
    "Koto, F., Rahimi, A., Lau, J. H., & Baldwin, T. (2020). IndoLEM and IndoBERT: A benchmark dataset and pre-trained language model for Indonesian NLP. In Proceedings of the 28th International Conference on Computational Linguistics. International Committee on Computational Linguistics.",
    "Koto, F., & Rahmaningtyas, G. Y. (2017). InSet lexicon: Evaluation of a word list for Indonesian sentiment analysis in microblogs. In 2017 International Conference on Asian Language Processing (IALP). IEEE.",
    "Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159–174.",
    "Mosbach, M., Andriushchenko, M., & Klakow, D. (2021). On the stability of fine-tuning BERT: Misconceptions, explanations, and strong baselines. In International Conference on Learning Representations (ICLR 2021).",
    "Pangakis, N., Wolken, S., & Fasching, N. (2023). Automated annotation with generative AI requires validation. arXiv preprint arXiv:2306.00176.",
    "Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLoS ONE, 10(3), e0118432.",
    "Sennrich, R., Haddow, B., & Birch, A. (2016). Improving neural machine translation models with monolingual data. In Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics. Association for Computational Linguistics.",
    "Shorten, C., Khoshgoftaar, T. M., & Furht, B. (2021). Text data augmentation for deep learning. Journal of Big Data, 8, 101.",
    "Tan, K. L., Lee, C. P., & Lim, K. M. (2023). A survey of sentiment analysis: Approaches, datasets, and future research. Applied Sciences, 13(7), 4550.",
    "Tiedemann, J., & Thottingal, S. (2020). OPUS-MT: Building open translation services for the world. In Proceedings of the 22nd Annual Conference of the European Association for Machine Translation. European Association for Machine Translation.",
    "Törnberg, P. (2023). ChatGPT-4 outperforms experts and crowd workers in annotating political Twitter messages with zero-shot learning. arXiv preprint arXiv:2304.06588.",
    "Wang, S., Liu, Y., Xu, Y., Zhu, C., & Zeng, M. (2021). Want to reduce labeling cost? GPT-3 can help. In Findings of the Association for Computational Linguistics: EMNLP 2021. Association for Computational Linguistics.",
    "Wankhade, M., Rao, A. C. S., & Kulkarni, C. (2022). A survey on sentiment analysis methods, applications, and challenges. Artificial Intelligence Review, 55(7), 5731–5780.",
    "Wilie, B., Vincentio, K., Winata, G. I., Cahyawijaya, S., Li, X., Lim, Z. Y., Soleman, S., Mahendra, R., Fung, P., Bahar, S., & Purwarianti, A. (2020). IndoNLU: Benchmark and resources for evaluating Indonesian natural language understanding. In Proceedings of the 1st Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics and the 10th International Joint Conference on Natural Language Processing. Association for Computational Linguistics.",
    "Winata, G. I., Aji, A. F., Cahyawijaya, S., Mahendra, R., Koto, F., Romadhony, A., et al. (2023). NusaX: Multilingual parallel sentiment dataset for 10 Indonesian local languages. In Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics. Association for Computational Linguistics.",
    "Zhang, W., Deng, Y., Liu, B., Pan, S. J., & Bing, L. (2024). Sentiment analysis in the era of large language models: A reality check. In Findings of the Association for Computational Linguistics: NAACL 2024. Association for Computational Linguistics.",
    "Zhou, P., Shi, W., Tian, J., Qi, Z., Li, B., Hao, H., & Xu, B. (2016). Attention-based bidirectional long short-term memory networks for relation classification. In Proceedings of the 54th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers). Association for Computational Linguistics.",
    "Zhu, Y., Zhang, P., Haq, E.-U., Hui, P., & Tyson, G. (2023). Can ChatGPT reproduce human-generated labels? A study of social computing tasks. arXiv preprint arXiv:2304.10145.",
    "Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z., & Yang, D. (2024). Can large language models transform computational social science? Computational Linguistics, 50(1), 237–291.",
]
for ref in sorted(REF, key=lambda s: s.lower()):
    p = _baru("isi", ref, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    p.paragraph_format.left_indent = Cm(0.75)
    p.paragraph_format.first_line_indent = Cm(-0.75)
    p.paragraph_format.space_after = Pt(4)

d.save(OUT)
print("tersimpan:", OUT.name, "| referensi:", len(REF))
