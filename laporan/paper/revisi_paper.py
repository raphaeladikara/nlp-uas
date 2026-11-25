"""Menerapkan revisi 25 Nov ke paper hasil ekspor Google Docs.

Sumber: docx yang diunduh dari Google Docs (sudah berisi suntingan manual tim). Skrip ini tidak membangun
paper dari nol seperti buat_paper.py, tapi menyunting docx itu supaya format dari Google Docs tetap terjaga.

    python laporan/paper/revisi_paper.py <docx_sumber> <docx_hasil>
"""
import copy
import re
import sys

import docx
from docx.oxml.ns import qn

SUMBER, HASIL = sys.argv[1], sys.argv[2]
d = docx.Document(SUMBER)
P = d.paragraphs


def cari(awal):
    hasil = [p for p in d.paragraphs if p.text.startswith(awal)]
    assert len(hasil) == 1, (awal, len(hasil))
    return hasil[0]


def isi(p, bagian):
    """Ganti isi paragraf. bagian: str atau list (teks, tebal, miring). Format run pertama dipertahankan."""
    if isinstance(bagian, str):
        bagian = [(bagian, None, None)]
    runs = p._p.findall(qn("w:r"))
    contoh = copy.deepcopy(runs[0]) if runs else None
    for r in runs:
        p._p.remove(r)
    for teks, tebal, miring in bagian:
        r = copy.deepcopy(contoh)
        for t in r.findall(qn("w:t")):
            r.remove(t)
        rpr = r.find(qn("w:rPr"))
        if rpr is None:
            rpr = r.makeelement(qn("w:rPr"), {})
            r.insert(0, rpr)
        for tag in ("w:b", "w:bCs", "w:i", "w:iCs"):
            for e in rpr.findall(qn(tag)):
                rpr.remove(e)
        if tebal:
            for tag in ("w:b", "w:bCs"):
                rpr.insert(0, rpr.makeelement(qn(tag), {qn("w:val"): "1"}))
        if miring:
            for tag in ("w:i", "w:iCs"):
                rpr.insert(0, rpr.makeelement(qn(tag), {qn("w:val"): "1"}))
        t = r.makeelement(qn("w:t"), {})
        t.text = teks
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r.append(t)
        p._p.append(r)
    return p


# templat paragraf dan tabel diambil dari dokumen itu sendiri
T_ISI = copy.deepcopy(cari("Data diambil dari 22 Oktober")._p)
T_SUB = copy.deepcopy(cari("Pembagian data dan metrik")._p)
T_JUDUL_TABEL = copy.deepcopy(cari("Tabel 1. Jumlah data mentah")._p)
T_KOSONG = copy.deepcopy(cari("Tabel 1. Jumlah data mentah")._p.getnext().getnext())
T_TABEL = copy.deepcopy(d.tables[2]._tbl)
T_REF = copy.deepcopy(cari("Bayer, M.")._p)


class Penyisip:
    """Menyisipkan elemen berurutan setelah satu elemen jangkar."""

    def __init__(self, jangkar):
        self.akhir = jangkar._p if hasattr(jangkar, "_p") else jangkar

    def _taruh(self, el):
        self.akhir.addnext(el)
        self.akhir = el
        return el

    def paragraf(self, templat, bagian):
        el = copy.deepcopy(templat)
        self._taruh(el)
        isi(docx.text.paragraph.Paragraph(el, None), bagian)
        return el

    def isi(self, bagian, tanpa_indent=False):
        el = self.paragraf(T_ISI, bagian)
        if tanpa_indent:
            ind = el.find(qn("w:pPr")).find(qn("w:ind"))
            ind.set(qn("w:firstLine"), "0")
        return el

    def sub(self, teks):
        return self.paragraf(T_SUB, [(teks, True, None)])

    def tabel(self, judul, header, baris, lebar):
        self.paragraf(T_JUDUL_TABEL, judul)
        self._taruh(buat_tabel(header, baris, lebar))
        self._taruh(copy.deepcopy(T_KOSONG))


def buat_tabel(header, baris, lebar):
    tbl = copy.deepcopy(T_TABEL)
    rows = tbl.findall(qn("w:tr"))
    tr_head, tr_isi = rows[0], rows[1]
    for r in rows:
        tbl.remove(r)
    tblpr = tbl.find(qn("w:tblPr"))
    tblpr.find(qn("w:tblW")).set(qn("w:w"), str(sum(lebar)))
    grid = tbl.find(qn("w:tblGrid"))
    for g in list(grid):
        grid.remove(g)
    for w in lebar:
        grid.append(grid.makeelement(qn("w:gridCol"), {qn("w:w"): str(w)}))

    def baris_baru(templat, sel, tebal_semua=False):
        tr = copy.deepcopy(templat)
        tcs = tr.findall(qn("w:tc"))
        contoh = copy.deepcopy(tcs[1])
        for tc in tcs:
            tr.remove(tc)
        for i, teks in enumerate(sel):
            tc = copy.deepcopy(contoh)
            tcpr = tc.find(qn("w:tcPr"))
            for e in list(tcpr):
                tcpr.remove(e)
            tcpr.append(tcpr.makeelement(qn("w:tcW"), {qn("w:w"): str(lebar[i]), qn("w:type"): "dxa"}))
            p = docx.text.paragraph.Paragraph(tc.find(qn("w:p")), None)
            tebal = tebal_semua or (isinstance(teks, str) and teks.startswith("**"))
            isi(p, [(teks.strip("*"), tebal, None)])
            tr.append(tc)
        return tr

    kepala = baris_baru(tr_head, header, True)
    # header diulang di halaman berikut dan tidak boleh tertinggal sendirian di bawah halaman
    trpr = kepala.find(qn("w:trPr"))
    trpr.find(qn("w:tblHeader")).set(qn("w:val"), "1")
    for p in kepala.iter(qn("w:p")):
        ppr = p.find(qn("w:pPr"))
        ppr.insert(0, ppr.makeelement(qn("w:keepNext"), {qn("w:val"): "1"}))
    tbl.append(kepala)
    for b in baris:
        tr = baris_baru(tr_isi, b)
        tr.find(qn("w:trPr")).find(qn("w:cantSplit")).set(qn("w:val"), "1")
        tbl.append(tr)
    return tbl


def ganti_tabel(tabel, header, baris, lebar):
    baru = buat_tabel(header, baris, lebar)
    tabel._tbl.addnext(baru)
    tabel._tbl.getparent().remove(tabel._tbl)


def hapus(p):
    p._p.getparent().remove(p._p)


# Nomor tabel lama digeser dulu, karena ada dua tabel baru di subbab Material
GESER = {"2": "4", "3": "5", "4": "6", "5": "7", "6": "8"}
for p in d.paragraphs:
    if re.search(r"Tabel [2-6]\b", p.text):
        isi(p, re.sub(r"Tabel ([2-6])\b", lambda m: "Tabel " + GESER[m.group(1)], p.text))

# 1. Abstract dan keywords
ABSTRAK = {
    "Background:": "Public reaction to Raffi Ahmad after the 29 October 2026 \"paid students\" declaration is spread "
    "across thousands of comments on four social media platforms. Classifying stance toward him is difficult because "
    "supportive comments are rare (2.5%) and are often written in an angry tone directed at his critics.",
    "Objective:": "This study builds and compares models that classify netizens' stance toward Raffi Ahmad (negative, "
    "neutral, positive), and tests whether post titles and positive-class augmentation improve the classification.",
    "Methods:": "We collected 7,020 texts from X, Instagram, YouTube, and TikTok (22 October to 14 November 2026) and "
    "passed them through eight filtering gates whose flagged candidates were checked manually. Three LLM annotators "
    "labeled 3,525 sampled texts, and every non-unanimous text was relabeled by three human annotators (Fleiss' kappa "
    "0.286), resulting in 3,329 texts. Nine models were compared using grouped stratified 5-fold cross-validation with "
    "two inputs (comment only and comment with post title) and three train-only augmentation sources.",
    "Results:": "Fine-tuned IndoBERT with comment and title input plus augmentation from real positive comments achieved "
    "the best single-model macro-F1 of 0.616 (positive-class F1 0.352), while an IndoBERT and IndoBERTweet ensemble "
    "reached 0.628. Adding the post title gave the most consistent improvement. Real positive comments improved all "
    "nine configurations, whereas back-translation improved only one of nine. Only 2.5% of comments supported Raffi, "
    "and the negative share rose from 63.2% to 69.3% after his clarification.",
    "Conclusion:": "Post context and real positive examples matter more than the choice of model. Supportive comments "
    "written in an angry tone remain the main source of error.",
    "Keywords:": "stance classification; Indonesian sentiment analysis; IndoBERT; data augmentation; LLM-assisted "
    "annotation",
}
for label, teks in ABSTRAK.items():
    p = cari(label)
    isi(p, [(label + " ", True, None), (teks, None, None)])
    pf = p._p.get_or_add_pPr()
    if pf.find(qn("w:jc")) is None:
        pf.append(pf.makeelement(qn("w:jc"), {qn("w:val"): "both"}))

# 2 sampai 4. Gerbang filter, relevansi, buzzer
lama = cari("Data mentah lalu disaring")
s = Penyisip(lama)
s.isi("Data mentah lalu melewati delapan gerbang filter. Setiap gerbang dijalankan oleh skrip Python di notebook "
      "filter. Aturan otomatis di setiap gerbang hanya menandai teks sebagai kandidat untuk dibuang, tidak langsung "
      "membuangnya. Setiap kandidat kemudian dibaca satu per satu oleh anggota tim, lalu diputuskan dibuang atau "
      "dipertahankan. Keputusan dan alasannya dicatat per teks di berkas audit (119 keputusan tertulis untuk gerbang "
      "2, 4, dan 5), dan notebook sengaja berhenti dengan error kalau masih ada kandidat yang belum diputuskan.")
s.isi("Cara ini kami pakai setelah konsultasi dengan dosen. Di versi awal, aturan otomatis langsung membuang teks. "
      "Setelah teks yang terbuang di versi awal kami baca ulang, ternyata banyak yang sebenarnya opini tentang Raffi. "
      "Tabel 2 membandingkan jumlah teks yang dibuang di versi awal (aturan langsung membuang) dan versi akhir (aturan "
      "menandai, manusia memutuskan).")
s.tabel(
    "Tabel 2. Delapan gerbang filter, cara pemeriksaan, dan jumlah teks",
    ["No", "Gerbang", "Aturan otomatis yang menandai kandidat", "Pemeriksaan manual", "Dibuang versi awal",
     "Dibuang versi akhir", "Sisa teks"],
    [
        ["0", "Data mentah", "ID kembar dibuang", "-", "-", "-", "7.020"],
        ["1", "Rentang tanggal", "Tanggal di luar 22 Oktober sampai 14 November 2026",
         "Tidak ada kandidat, karena rentang sudah dipakai saat scraping", "0", "0", "7.020"],
        ["2", "Komentar pemilik unggahan",
         "Penulis komentar adalah pemilik unggahan atau video (penanda Apify di Instagram, ID channel di YouTube, "
         "username di TikTok)",
         "28 kandidat dibaca. Dibuang kalau hanya balasan teknis atau ucapan terima kasih, dipertahankan kalau berisi "
         "opini tentang Raffi", "28", "16 (12 dipertahankan)", "7.004"],
        ["3", "Tanpa isi", "Setelah normalisasi NFKC dan mention dihapus, tidak ada satu pun huruf atau angka",
         "Teks yang terbuang di versi awal dibaca ulang, lalu aturan dilonggarkan. Yang dibuang: 84 emoji saja, 64 "
         "kosong atau mention saja, 2 tanda baca saja", "177", "150 (27 diselamatkan, misalnya \"14 M\" dan "
         "\"B O I K O T\")", "6.854"],
        ["4a", "Bahasa asing (X)", "Kode bahasa dari X bukan Indonesia",
         "20 kandidat dibaca. Dibuang hanya kalau berbahasa asing dan tidak membahas Raffi", "17",
         "6 (14 dipertahankan)", "6.848"],
        ["4b", "Spam", "Daftar kata judi online dan promosi (slot, gacor, giveaway, cek bio)",
         "10 kandidat dibaca, semuanya opini yang memakai kata itu untuk menyindir", "10", "0 (10 dipertahankan)",
         "6.848"],
        ["5", "Relevansi (X)", "Teks dan tweet induknya tidak memuat kata kunci Raffi atau kasus",
         "Semua 61 kandidat dibaca", "61", "60 (1 dipertahankan)", "6.788"],
        ["6", "Duplikat",
         "Sama persis setelah huruf kecil dan tanda baca dibuang, atau cosine TF-IDF karakter 3 sampai 5 gram "
         ">= 0,85 untuk teks minimal 5 kata",
         "Satu wakil per klaster dipertahankan. Jumlah akun per klaster disimpan untuk gerbang buzzer", "79",
         "79 (37 akun sama mengulang, 42 salinan dari akun lain)", "6.709"],
        ["7", "Buzzer", "Aturan keras dan skor poin (Tabel 3)", "Zona batas diputuskan di tahap review", "36", "36",
         "6.673"],
        ["8", "Batas per sumber", "Maksimal 25 tweet per thread X (komentar per unggahan sudah dibatasi saat "
         "scraping)", "Tidak ada kandidat", "0", "0", "6.673"],
        ["", "**Total", "", "", "**408", "**347", "**6.673"],
    ],
    [420, 1150, 2000, 2350, 850, 1350, 850],
)
s.isi("Dengan cara baru ini, teks yang lolos naik dari 6.612 menjadi 6.673, jadi 61 teks diselamatkan dari "
      "pembuangan yang keliru. Kesalahan terbanyak ada di gerbang tanpa isi. Di versi awal, teks yang ditulis dengan "
      "huruf unicode bergaya seperti \"𝒃𝒐𝒊𝒌𝒐𝒕 𝒂𝒋𝒂\" atau huruf dipisah spasi seperti \"B O I K O T\" dianggap tidak "
      "punya huruf. Teks \"14 M\" juga ikut terbuang, padahal di kasus ini artinya jelas merujuk ke kontrak Rp14,7 "
      "miliar. Gerbang spam juga tidak menangkap satu pun spam. Kesepuluh kandidatnya ternyata opini, misalnya "
      "\"Raffi Mesin Pencuci Uang paling Gacor\". Teks emoji saja tetap kami buang karena sasarannya tidak bisa "
      "dipastikan. Emoji muntah di bawah berita kontrak bisa ditujukan ke Raffi, ke kementerian, atau ke beritanya.")
s.isi("Dari 6.673 teks yang lolos, 525 adalah komentar jalur B, dan semuanya ikut dilabeli. Sisanya 6.148 teks "
      "jalur A, lalu kami ambil sampel acak bertingkat per platform (strata tanggal untuk X, strata unggahan atau "
      "video untuk platform lain), bukan berdasarkan like terbanyak. Hasilnya 3.525 teks jalur A dilabeli dan 2.623 "
      "teks menjadi cadangan.")
s.isi([("Pemeriksaan relevansi. ", True, None),
       ("Komentar Instagram, YouTube, dan TikTok sudah pasti berada di bawah unggahan tentang kasus ini, karena "
        "unggahannya dipilih saat scraping. Di YouTube misalnya, judul video harus menyebut Raffi, RANS, atau "
        "mahasewa. Tweet berbeda, karena pencarian X juga bisa cocok dengan username atau nama tampilan penulis, "
        "bukan isi tweet. Karena itu gerbang relevansi hanya dipakai untuk X. Sebuah tweet ditandai sebagai kandidat "
        "tidak relevan kalau teks dan tweet induknya tidak memuat satu pun kata kunci berikut: raffi atau rafi, RANS, "
        "Nagita, mahasewa, mahasiswa bayaran, settingan, sewaan, palsu, atau bodong, deklarasi, bundaran, utusan "
        "khusus, stafsus, 14 M atau 14 miliar, dan ICW. Pencocokan dilakukan setelah normalisasi NFKC, supaya tweet "
        "seperti \"𝗥𝗔𝗙𝗙𝗜 𝗔𝗛𝗠𝗔𝗗 … Shutdown this guy\" tetap cocok.", None, None)])
s.isi("Semua 61 kandidat dibaca, bukan hanya sampelnya, jadi tidak ada tweet yang terbuang tanpa dibaca. Satu tweet "
      "dipertahankan walaupun tidak memuat kata kunci, yaitu ajakan menumbangkan \"gurita bisnis\", karena di "
      "periode ini istilah itu merujuk ke bisnis Raffi. Sebanyak 55 tweet dibuang karena jelas membahas topik lain, "
      "misalnya fans JKT48, KRL Surabaya, iklan koin kuno, puisi, dan dua tweet berbahasa Telugu. Lima balasan "
      "pendek ikut dibuang karena tweet induknya tidak ikut ter-scrape, sehingga sasarannya tidak bisa dipastikan, "
      "misalnya \"Instansi itu...\". Kelima teks ini satu-satunya bagian yang mungkin relevan tapi tetap terbuang, "
      "dan kami catat sebagai keterbatasan.")
s.isi("Kebalikannya, yaitu teks yang memuat kata kunci tapi tidak membahas Raffi, ditangani di tahap pelabelan. "
      "Annotator memberi label tidak relevan, dan 182 teks dengan label akhir tidak relevan dikeluarkan dari "
      "dataset. Risiko yang tidak bisa kami periksa adalah tweet relevan yang sejak awal tidak dikembalikan oleh "
      "pencarian X, karena tweet itu tidak pernah masuk data.")
s.isi([("Penandaan buzzer. ", True, None),
       ("Kami memakai istilah \"terindikasi buzzer\" untuk teks yang polanya menyerupai pesan terkoordinasi atau "
        "akun yang dipakai khusus untuk satu isu. Ini bukan klaim bahwa akunnya pasti dibayar. Penandaan dibuat tiga "
        "lapis. Lapis pertama adalah aturan keras: kalau satu saja terpenuhi, teks langsung dikeluarkan. Lapis kedua "
        "adalah skor poin dari sinyal lemah. Satu sinyal belum cukup untuk menuduh, tapi kalau beberapa sinyal "
        "menumpuk, teksnya jadi mencurigakan. Lapis ketiga adalah penilaian isi teks oleh annotator dan manusia untuk "
        "teks di zona batas. Aturan dan bobotnya ada di Tabel 3.", None, None)])
s.tabel(
    "Tabel 3. Aturan dan skor penandaan buzzer",
    ["Lapis", "Indikator", "Bobot atau aturan", "Jumlah teks"],
    [
        ["Aturan keras", "Akun X dibuat kurang dari 30 hari sebelum tweet diposting", "Langsung dikeluarkan", "13"],
        ["Aturan keras", "Satu akun memposting teks hampir sama 3 kali atau lebih", "Langsung dikeluarkan", "7"],
        ["Aturan keras", "Teks minimal 5 kata yang hampir sama (cosine >= 0,85) ditulis 3 akun berbeda atau lebih",
         "Langsung dikeluarkan", "6 klaster"],
        ["Aturan keras", "Akun ditandai otomatis (bot) oleh X", "Langsung dikeluarkan", "0"],
        ["Skor", "Akun berumur kurang dari 3 bulan / kurang dari 6 bulan", "+2 / +1", ""],
        ["Skor", "Memposting 6 teks atau lebih / 3 sampai 5 teks soal isu ini", "+2 / +1", ""],
        ["Skor", "Teks mirip dengan teks akun lain", "+2", ""],
        ["Skor", "Following lebih dari 10 kali followers, username generik, akun kosong, akun X tanpa bio dengan "
         "followers di bawah 50, lebih dari 100 tweet per hari, 3 hashtag atau lebih", "Masing-masing +1", ""],
        ["Keputusan", "Skor 0 sampai 1", "Lolos", "6.104"],
        ["Keputusan", "Skor 2 sampai 3 (zona batas)", "Tetap dilabeli, diputuskan lewat penilaian isi", "580"],
        ["Keputusan", "Skor 4 atau lebih", "Dikeluarkan", "10"],
    ],
    [1300, 4400, 2300, 1000],
)
s.isi("Sinyal profil tidak dipakai untuk YouTube. Pada percobaan pertama, 78% komentar YouTube masuk zona batas "
      "hanya karena channel penonton memang kosong. Hal yang sama membuat bobot sinyal akun kosong kami turunkan "
      "menjadi 1 di platform lain. Sinyal yang lebih sulit dipalsukan, yaitu umur akun dan perilaku posting, tetap "
      "berbobot 2.")
s.isi("Totalnya, 36 teks dikeluarkan di gerbang ini (26 aturan keras, 10 skor tinggi), dan 32 di antaranya dari X. "
      "Untuk 580 teks zona batas, ketiga LLM menilai isi teksnya dengan kriteria di codebook. Teks dianggap buzzer "
      "kalau bunyinya seperti pesan pesanan, misalnya template pembelaan atau promosi yang tidak menanggapi isi "
      "unggahan, atau ajakan seragam dengan hashtag kampanye. Komentar kasar atau pendek dari orang biasa tidak "
      "dianggap buzzer. Teks yang ditandai buzzer oleh minimal satu LLM masuk review manusia. Ada 25 teks seperti "
      "ini, dan setelah dinilai tiga orang, 14 diputuskan terindikasi buzzer dan 11 tidak.")
s.isi("Teks yang dikeluarkan tidak dihapus, tapi disimpan terpisah supaya bisa dilaporkan sendiri. Kami juga mencatat "
      "satu kemungkinan salah tangkap. Aturan narasi sama dari 3 akun atau lebih ikut menangkap meme \"Sultan andara "
      "ANGGARAN DARI NEGARA\" yang ditulis 11 akun. Meme ini kelihatannya lelucon viral, bukan narasi pesanan, tapi "
      "dampaknya hanya satu teks wakil klaster.")
hapus(lama)

# 5 sampai 7. Pelabelan, 871 dan 881, suara terbanyak, kappa, jalur A dan B
lama = cari("Setiap teks diberi label sikap terhadap Raffi")
s = Penyisip(lama)
s.isi("Sampel yang dilabeli berisi 4.050 teks: 3.525 teks jalur A dan 525 teks jalur B. Setiap teks diberi label "
      "sikap terhadap Raffi, yaitu negatif, netral, positif, atau tidak relevan. Tiga LLM (Claude Opus, Sonnet, dan "
      "Haiku) melabeli secara terpisah dan tidak bisa melihat jawaban satu sama lain. Ada 3.169 teks yang disepakati "
      "bulat oleh ketiganya (2.750 jalur A dan 419 jalur B), dan labelnya langsung dipakai. Sisanya 881 teks (775 "
      "jalur A dan 106 jalur B) masuk review manusia.")
s.isi("Satu kartu review berisi satu teks, jadi 881 kartu sama dengan 881 teks berbeda. Setiap kartu dinilai tepat "
      "tiga orang dari lima anggota kelompok, sehingga totalnya 2.643 penilaian. Label akhir adalah label yang "
      "dipilih minimal dua dari tiga orang, dan ini berlaku di 852 kartu. Kalau ketiga orang memilih tiga label "
      "berbeda (29 kartu), label diputuskan lewat diskusi tim. Di versi awal, antrean review berisi 871 kartu (767 "
      "jalur A dan 104 jalur B) yang masing-masing dinilai satu orang. Setelah revisi filter, 39 teks baru ikut "
      "dilabeli dan 10 di antaranya tidak disepakati bulat, jadi antreannya menjadi 881 kartu. Semua angka review di "
      "laporan ini memakai 881 kartu.")
s.isi("Fleiss' kappa dihitung dari 881 kartu itu dengan empat kategori. Untuk setiap kartu dihitung proporsi pasangan "
      "penilai yang sepakat, lalu dirata-rata menjadi kesepakatan teramati Po = 0,569. Kesepakatan kebetulan "
      "Pe = 0,396 dihitung dari proporsi setiap kategori di semua penilaian. Nilai kappa adalah (Po - Pe) / (1 - Pe) "
      "= 0,286, masuk kategori cukup (fair). Fleiss' kappa tidak mensyaratkan tiga orang yang sama di setiap kartu, "
      "cukup jumlah penilai per kartu sama, jadi kombinasi tiga dari lima orang boleh berbeda antar kartu. Angkanya "
      "rendah karena kartu yang direview memang teks yang membuat tiga LLM tidak sepakat. Kappa per kategori paling "
      "rendah di netral (0,219) dan paling tinggi di positif (0,581).")
s.isi("Dataset final hanya berisi jalur A. Dari 3.525 teks jalur A, 14 teks dikeluarkan karena terindikasi buzzer saat "
      "review dan 182 teks dibuang karena tidak relevan, sehingga tersisa 3.329 teks: 2.206 negatif (66,3%), 1.039 "
      "netral (31,2%), dan 84 positif (2,5%). Jalur B dilabeli dengan alur yang sama tetapi terpisah dari dataset "
      "utama. Jalur B tidak masuk data uji maupun statistik sikap warganet, dan hanya 42 komentar positifnya yang "
      "dipakai sebagai augmentasi di data latih.")
hapus(lama)

# 9 dan 10. Preprocessing BERT dan contoh judul
lama = cari("Untuk model TF-IDF, teks di-lowercase")
s = Penyisip(lama)
s.isi("Untuk model TF-IDF, teks di-lowercase, URL dan mention diganti token, dan huruf yang diulang dipendekkan. Untuk "
      "model BERT, preprocessing-nya lebih ringan: URL dibuang, mention diganti @user, tanda # dibuang, huruf "
      "berulang dipendekkan, dan emoji diubah menjadi kata bahasa Indonesia, misalnya emoji tertawa menjadi \"wajah "
      "gembira berurai air mata\". Huruf besar dan kecil tidak kami ubah sebelum teks masuk tokenizer, dan keputusan "
      "itu diserahkan ke tokenizer masing-masing model. IndoBERTweet (indolem/indobertweet-base-uncased) dan IndoBERT "
      "(indobenchmark/indobert-base-p1) adalah model uncased. Tokenizernya memakai pengaturan do_lower_case = True, "
      "jadi di dalam tokenizer \"BOIKOT\" dan \"boikot\" tetap menjadi token yang sama. Artinya, tanpa lowercase di "
      "sini berarti kami tidak membuang informasi kapital di tahap preprocessing, bukan berarti kedua model itu "
      "membaca kapital. Hanya XLM-RoBERTa (cased) yang benar-benar membedakan huruf kapital.")
s.isi("Setiap model diuji dengan dua input: teks saja, dan teks + judul dengan format [CLS] komentar [SEP] judul [SEP]. "
      "Judul ditambahkan karena separuh teks (50,8%) ditandai annotator butuh judul supaya sasarannya jelas. "
      "Contohnya komentar TikTok \"Kan mereka bekerja, ya pasti harus dibayar\". Kalau dibaca sendiri, tidak jelas "
      "siapa \"mereka\" dan bagaimana sikapnya ke Raffi. Komentar ini ada di bawah video berjudul \"ICW Temukan Rp "
      "14,7 Miliar Uang Negara Yang Mengalir ke Perusahaan Raffi Ahmad\", jadi maksudnya membela perusahaan Raffi yang "
      "dibayar negara, dan labelnya positif. Input modelnya menjadi:")
s.isi([("[CLS] Kan mereka bekerja, ya pasti harus dibayar [SEP] ICW Temukan Rp 14,7 Miliar Uang Negara Yang Mengalir "
        "ke Perusahaan Raffi Ahmad [SEP]", None, True)], tanpa_indent=True)
s.isi("Panjang maksimal input adalah 128 token untuk teks saja dan 256 token untuk teks + judul. Kalau melebihi batas, "
      "bagian yang lebih panjang dipotong lebih dulu. Untuk TF-IDF, judul dijadikan vektor terpisah dengan bobot 0,5.",
      tanpa_indent=True)
hapus(lama)

# 6 dan 8. Augmentasi hanya positif di fold latih, seri di pelabelan terarah
s = Penyisip(cari("Augmentasi hanya ditambahkan ke fold latih"))
s.isi("Semua data augmentasi berlabel positif. Jumlahnya 327 baris: 42 komentar jalur B, 253 parafrase, dan 32 teks "
      "dari pelabelan terarah. Data ini hanya ditambahkan ke fold latih. Parafrase dari teks yang sedang berada di "
      "fold uji juga dikeluarkan dari data latih fold itu, supaya model tidak pernah melihat versi lain dari teks yang "
      "sedang diuji. Fold uji selalu berisi data asli tanpa tambahan.")
s.isi("Pelabelan terarah memakai aturan suara terbanyak yang sama. Sebanyak 73 kartu yang tidak disepakati bulat tiga "
      "LLM dinilai tiga orang (Fleiss' kappa 0,260). Ada 7 kartu yang seri, artinya ketiga orang memilih tiga label "
      "berbeda. Berbeda dengan data utama, ketujuh kartu ini tidak kami diskusikan, tetapi diputus dengan mayoritas "
      "tiga LLM. Ada tiga alasan. Pertama, data terarah hanya dipakai sebagai tambahan data latih, tidak pernah masuk "
      "data uji atau statistik sikap warganet, jadi labelnya tidak memengaruhi angka evaluasi secara langsung. Kedua, "
      "setiap kartu sudah punya mayoritas dua dari tiga LLM yang dibuat terpisah dari penilaian manusia, jadi ada "
      "pendapat ketiga yang independen. Ketiga, dari tujuh kartu itu hanya satu yang akhirnya berlabel positif, "
      "sehingga paling banyak satu dari 32 teks augmentasi bergantung pada aturan ini.")

# Tabel 4 (versi awal dan akhir): baris review manusia
for t in d.tables:
    for r in t.rows:
        if r.cells[0].text.strip() == "Review manusia":
            isi(r.cells[1].paragraphs[0], "871 kartu yang tidak disepakati 3 AI dibagi ke 5 orang, 1 orang per kartu. "
                "Kappa 0,393 dari 30 kartu kalibrasi yang dinilai kelima orang")
        if r.cells[0].text.startswith("Relevansi dan buzzer"):
            isi(r.cells[2].paragraphs[0], "36 teks dikeluarkan di gerbang buzzer, 14 lagi setelah review, dan 182 teks "
                "tidak relevan dikeluarkan. Kriterianya di Tabel 2 dan Tabel 3")

# 8. Tabel 6: tanpa vs dengan augmentasi
judul6 = cari("Tabel 6. Dampak augmentasi")
isi(judul6, "Tabel 6. Macro-F1 tanpa dan dengan augmentasi (input teks + judul, fold sama)")
tabel6 = [t for t in d.tables if t.rows[0].cells[0].text.strip() == "Varian"][0]
ganti_tabel(tabel6,
            ["Model", "Tanpa augmentasi", "+ jalur B", "+ parafrase", "+ jalur B + parafrase", "+ jalur B + terarah"],
            [
                ["TF-IDF + LogReg", "0,584", "0,589", "0,576", "0,584", "0,603"],
                ["TF-IDF + LinearSVM", "0,551", "-", "-", "0,587", "-"],
                ["IndoBERT fine-tune", "0,607", "0,614", "0,603", "0,606", "0,616"],
                ["IndoBERTweet fine-tune", "0,584", "0,597", "0,583", "0,595", "0,609"],
                ["XLM-RoBERTa fine-tune", "0,539", "0,563", "0,552", "0,580", "-"],
                ["IndoBERT embedding + LogReg", "0,585", "0,586", "0,569", "0,570", "0,570"],
                ["BiLSTM + attention", "0,507", "0,512", "0,499", "0,498", "0,505"],
            ],
            [2400, 1300, 1100, 1100, 1500, 1500])
isi(cari("Komentar positif jalur B menaikkan skor"),
    "Tabel 6 membandingkan setiap varian augmentasi langsung dengan kondisi tanpa augmentasi. Model, input, dan "
    "pembagian fold-nya sama, jadi yang berbeda hanya data positif tambahan di fold latih. Tanda \"-\" berarti "
    "kombinasi itu tidak dijalankan karena keterbatasan kuota GPU. Kalau semua konfigurasi dihitung, termasuk input "
    "teks saja, jalur B menaikkan macro-F1 di 9 dari 9 konfigurasi (rata-rata +0,012) dan F1 positif rata-rata "
    "+0,028. Jalur B + terarah membantu di 5 dari 8 konfigurasi. Parafrase hanya membantu XLM-RoBERTa (1 dari 9) dan "
    "justru menurunkan F1 positif rata-rata 0,020. Dari cek manual, sekitar 1 dari 6 parafrase maknanya rusak atau "
    "berbalik, dan parafrase memakai judul yang sama dengan teks aslinya, jadi model bisa menghafal judul. Untuk "
    "model utama, IndoBERT fine-tune, macro-F1 naik dari 0,607 tanpa augmentasi menjadi 0,616 dengan jalur B + "
    "terarah, dan F1 positif naik dari 0,293 menjadi 0,352.")
isi(cari("Tabel 7. Dampak pelabelan terarah"), "Tabel 7. Tambahan pelabelan terarah di atas jalur B")
p = cari("Dari 250 teks cadangan dengan skor tertinggi")
isi(p, "Berbeda dengan Tabel 6, Tabel 7 tidak membandingkan dengan kondisi tanpa augmentasi, tetapi melihat tambahan "
    "yang diberikan teks terarah kalau jalur B sudah dipakai. " + p.text.replace("Tabel 7 menunjukkan", "Tabel 7 "
    "menunjukkan"))

# Keterbatasan
p = cari("Keterbatasan penelitian ini ada di")
isi(p, p.text.replace(
    "Tujuh kartu terarah yang seri juga diputus dengan mayoritas 3 LLM, bukan lewat diskusi tim.",
    "Tujuh kartu terarah yang seri juga diputus dengan mayoritas 3 LLM, bukan lewat diskusi tim, walaupun dampaknya "
    "paling banyak satu teks augmentasi. Lima balasan X yang tweet induknya tidak ter-scrape ikut terbuang di gerbang "
    "relevansi, dan penandaan buzzer hanya menunjukkan indikasi, bukan bukti bahwa akunnya dibayar."))

# 11. Referensi: maksimal 5 referensi lama, 4 pengganti terbaru
SITASI = [
    ("(Wilie et al., 2020; Koto et al., 2020)", "(Wilie et al., 2020)"),
    ("IndoBERT beserta benchmark tugas pemahaman, IndoLEM (Koto et al., 2020) merilis IndoBERT versi lain, dan "
     "IndoBERTweet", "IndoBERT beserta benchmark tugas pemahaman, dan IndoBERTweet"),
    ("(Fleiss, 1971; Landis & Koch, 1977)", "(Fleiss, 1971)"),
    ("back-translation (Sennrich et al., 2016)", "back-translation"),
    ("OPUS-MT (Tiedemann & Thottingal, 2020)", "OPUS-MT (Tiedemann et al., 2024)"),
    ("karena kurva precision-recall lebih informatif daripada ROC saat data tidak seimbang (Saito & Rehmsmeier, "
     "2015)", "karena AP hanya menilai seberapa baik model menaruh teks positif di urutan atas, sehingga tidak ikut "
     "terangkat oleh banyaknya teks negatif yang mudah ditebak"),
    ("(Zhou et al., 2016)", "(Minaee et al., 2021)"),
    ("Terakhir, penyaringan akun buzzer kami dasarkan pada temuan bahwa akun terkoordinasi sering memakai pola teks "
     "dan aktivitas yang seragam (Cresci, 2020).",
     "Terakhir, penyaringan buzzer kami dasarkan pada pola pasukan siber di Indonesia yang memakai banyak akun dengan "
     "narasi seragam (Sastramidjaja & Wijayanto, 2022). Hays et al. (2023) menunjukkan aturan sederhana dari beberapa "
     "fitur akun sudah bisa menyamai model rumit di dataset deteksi bot, tetapi juga mengingatkan bahwa label bot di "
     "dataset seperti itu sering terlalu disederhanakan. Karena itu kami memakai aturan yang transparan dan tetap "
     "memeriksa zona batas secara manual."),
]
for lama_, baru in SITASI:
    kena = [p for p in d.paragraphs if lama_ in p.text]
    assert len(kena) == 1, lama_
    isi(kena[0], kena[0].text.replace(lama_, baru))

for awal in ["Koto, F., Rahimi, A.", "Landis, J. R.", "Zhou, P.", "Saito, T.", "Cresci, S.", "Sennrich, R."]:
    hapus(cari(awal))
isi(cari("Tiedemann, J., & Thottingal"),
    "Tiedemann, J., Aulamo, M., Bakshandaeva, D., Boggia, M., Grönroos, S.-A., Nieminen, T., Raganato, A., "
    "Scherrer, Y., Vázquez, R., & Virpioja, S. (2024). Democratizing neural machine translation with OPUS-MT. "
    "Language Resources and Evaluation, 58, 713–755.")
REF_BARU = [
    ("Henning, S.", "Hays, C., Schutzman, Z., Raghavan, M., Walk, E., & Zimmer, P. (2023). Simplistic collection and "
     "labeling practices limit the utility of benchmark datasets for Twitter bot detection. In Proceedings of the ACM "
     "Web Conference 2023. Association for Computing Machinery."),
    ("Mosbach, M.", "Minaee, S., Kalchbrenner, N., Cambria, E., Nikzad, N., Chenaghlu, M., & Gao, J. (2021). Deep "
     "learning-based text classification: A comprehensive review. ACM Computing Surveys, 54(3), 1–40."),
    ("Shorten, C.", "Sastramidjaja, Y., & Wijayanto. (2022). Cyber troops, online manipulation of public opinion and "
     "co-optation of Indonesia's cybersphere (Trends in Southeast Asia, No. 7). ISEAS–Yusof Ishak Institute."),
]
for sebelum, teks in REF_BARU:
    el = copy.deepcopy(T_REF)
    cari(sebelum)._p.addprevious(el)
    isi(docx.text.paragraph.Paragraph(el, None), teks)

d.save(HASIL)
ref = [p.text for p in d.paragraphs]
i = ref.index("References")
daftar = [t for t in ref[i + 1:] if t.strip()]
tahun = [int(m.group(1)) for t in daftar for m in [re.search(r"\((\d{4})\)", t)] if m]
print("referensi:", len(daftar), "| sebelum 2021:", sum(y < 2021 for y in tahun))
