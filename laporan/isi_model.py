"""Isi laporan bagian 11 sampai 15 (model, perbandingan, analisis kesalahan, temuan sentimen, kesimpulan).

Dipanggil dari isi_laporan.ISI. Tabel angka dibaca langsung dari berkas hasil pipeline.
"""
import pandas as pd

SENT = ["negatif", "netral", "positif"]


def f3(x):
    return f"{x:.3f}".replace(".", ",")


def f1(x):
    return f"{x:.1f}".replace(".", ",")


def ribu(x):
    return f"{int(x):,}".replace(",", ".")


def sel(kol, c):
    return f"{ribu(kol[c])} ({f1(kol[c] / kol.sum() * 100)}%)"


def ringkas_hasil(D):
    """Gabungkan hasil per fold semua model (notebook 02, 03, 04) menjadi satu tabel."""
    nama = {"indobertweet": "IndoBERTweet fine-tune", "indobert": "IndoBERT fine-tune", "xlmr": "XLM-RoBERTa fine-tune"}
    r = [pd.read_csv(D / "06_baseline" / "hasil_per_fold.csv")]
    for f in sorted((D / "07_transformer").glob("hasil_per_fold_*.csv")):
        t = pd.read_csv(f)
        r.append(t.assign(model=t.model.map(nama)))
    f = D / "08_embedding_bilstm" / "hasil_per_fold_embed_bilstm.csv"
    if f.exists():
        r.append(pd.read_csv(f))
    h = pd.concat(r, ignore_index=True)
    g = (h.groupby(["model", "input", "augmentasi"], sort=False)
         .agg(macro_f1=("macro_f1", "mean"), sd=("macro_f1", "std"), f1_negatif=("f1_negatif", "mean"),
              f1_netral=("f1_netral", "mean"), f1_positif=("f1_positif", "mean"), akurasi=("akurasi", "mean"))
         .reset_index().sort_values("macro_f1", ascending=False))
    return h, g


def ISI_MODEL(para, judul, caption, tabel, kode, gambar, butir, ROOT):
    D = ROOT / "data"
    FIG = ROOT / "figures"
    hasil, g = ringkas_hasil(D)

    # 11. MODEL
    judul("11. Model yang Dibandingkan", 1)
    para("Semua model dievaluasi dengan grouped stratified 5-fold CV yang sama (bagian 8), jadi setiap teks menjadi data "
         "uji tepat sekali dan hasil antarmodel bisa dibandingkan per fold. Ukuran utamanya macro-F1, yaitu rata-rata F1 "
         "ketiga kelas. Kami memakai macro-F1, bukan akurasi, karena kelasnya sangat tidak seimbang. Model yang selalu "
         "menebak negatif sudah mendapat akurasi 0,663, padahal tidak pernah benar di kelas netral dan positif.")
    caption("Tabel 19. Model yang dibandingkan")
    tabel([
        ["Model", "Cara kerja", "Notebook"],
        ["Kelas terbanyak, leksikon InSet", "Baseline tanpa pembelajaran: selalu menebak negatif, atau menjumlah skor kata positif dan negatif", "02"],
        ["TF-IDF + LogReg / Linear SVM", "Menghitung bobot n-gram kata dan huruf, judul dibuat vektor terpisah dengan bobot 0,5, class weight balanced", "02"],
        ["IndoBERT embedding + LogReg", "IndoBERT tidak dilatih ulang. Rata-rata vektor semua token (768 dimensi) dipakai sebagai fitur LogReg", "04"],
        ["BiLSTM + attention", "Membaca teks kata demi kata dari dua arah, lalu attention memilih kata yang paling menentukan. Embedding kata dari IndoBERT dan dibekukan", "04"],
        ["IndoBERTweet fine-tune", "BERT yang dilatih dari tweet Indonesia, dilatih ulang untuk 3 kelas", "03"],
        ["IndoBERT fine-tune", "BERT dari teks Indonesia formal (Wikipedia, berita)", "03"],
        ["XLM-RoBERTa fine-tune", "Model multibahasa 100 bahasa, satu-satunya yang membedakan huruf besar dan kecil", "03"],
    ], lebar=[4.2, 10, 1.8], ukuran=8)
    para("Tiga model terakhir dan BiLSTM adalah model yang memahami konteks kalimat, sesuai saran dosen untuk menambah "
         "algoritma yang memahami konteks. IndoBERT embedding + LogReg ada di antara TF-IDF dan fine-tuning: representasinya "
         "sudah kontekstual, tapi bobot IndoBERT tidak ikut dilatih. Jadi dari perbandingan ketiganya bisa dilihat berapa "
         "kenaikan yang datang dari representasi kontekstual dan berapa dari proses fine-tuning.")
    para("Model transformer dilatih dengan learning rate 2e-5, batch 16, 5 epoch, dan warmup 10%. Pengaturan ini umum "
         "untuk fine-tuning BERT ukuran base, dan sama untuk ketiga model supaya perbedaan hasil datang dari modelnya, "
         "bukan dari tuning. Epoch terbaik dipilih dari data validasi (10% data latih, dipisah per grup), bukan dari fold "
         "uji. Input teks saja dipotong di 128 token, sedangkan teks + judul di 256 token dengan format "
         "[CLS] komentar [SEP] judul [SEP]. Semua model berbasis BERT dijalankan di Kaggle (GPU T4) lewat Kaggle CLI.")
    para("Setiap model diuji dengan dua input (teks saja dan teks + judul) dan empat varian augmentasi. Untuk model "
         "transformer kami tidak menjalankan semua 8 kombinasi, supaya kuota GPU Kaggle cukup untuk tiga model (satu "
         "kernel dengan 6 kombinasi butuh sekitar 1 jam). Yang dijalankan adalah keempat varian untuk teks + judul, ditambah tanpa augmentasi dan augmentasi lengkap untuk "
         "teks saja.")
    para("Setelah pelabelan terarah selesai (bagian 12.4), ada varian kelima, yaitu jalur B + terarah. Varian ini dijalankan "
         "untuk TF-IDF + LogReg, IndoBERT embedding + LogReg, dan BiLSTM di kedua input, serta untuk IndoBERT dan IndoBERTweet "
         "fine-tune di input teks + judul. XLM-RoBERTa sengaja tidak dilatih ulang, karena model ini paling lemah di antara "
         "model fine-tune dan satu kernel butuh sekitar 1 jam GPU.")

    # 12. HASIL
    judul("12. Hasil dan Perbandingan", 1)
    terbaik = g.loc[g.groupby("model").macro_f1.idxmax()].sort_values("macro_f1", ascending=False)
    caption("Tabel 20. Konfigurasi terbaik tiap model (rata-rata 5 fold)")
    tabel([["Model", "Input", "Augmentasi", "Macro-F1", "F1 neg", "F1 net", "F1 pos"]] +
          [[r.model, r.input, r.augmentasi, f"{f3(r.macro_f1)} ± {f3(r.sd)}", f3(r.f1_negatif), f3(r.f1_netral),
            f3(r.f1_positif)] for r in terbaik.itertuples()], lebar=[4, 2.2, 2.8, 2.6, 1.4, 1.4, 1.4], ukuran=8)
    gambar(FIG / "05_model_terbaik.png", 15)
    caption("Gambar 4. Macro-F1 konfigurasi terbaik tiap model")
    ISI_HASIL(para, judul, caption, tabel, gambar, butir, ROOT, hasil, g, terbaik)

    # 14. TEMUAN SENTIMEN
    s = pd.read_csv(D / "05_final" / "semua_label.csv")
    a = s[(s.kelompok == "utama") & ~s.buzzer & s.label.isin(SENT)]
    b = s[(s.kelompok == "jalur_b") & ~s.buzzer & s.label.isin(SENT)]
    judul("14. Temuan: Bagaimana Sikap Warganet terhadap Raffi", 1)
    para("Bagian ini kembali ke pertanyaan awal, yaitu apakah warganet masih membela Raffi. Angkanya diambil dari label "
         "akhir yang sudah dicek manusia (notebooks/06_analisis_sentimen.ipynb), bukan dari tebakan model, karena model "
         "terbaik pun masih sering salah di kelas positif.")
    ct = pd.DataFrame({"a": a.label.value_counts(), "b": b.label.value_counts()}).reindex(SENT)
    caption("Tabel 25. Sebaran sentimen jalur A dan jalur B")
    tabel([["Kelompok", "Negatif", "Netral", "Positif", "Total"],
           ["Jalur A (unggahan berita dan kreator)", *[sel(ct.a, c) for c in SENT], ribu(ct.a.sum())],
           ["Jalur B (akun Instagram Raffi)", *[sel(ct.b, c) for c in SENT], ribu(ct.b.sum())]], lebar=[5.5, 2.8, 2.8, 2.4, 1.6])
    para("Hanya 2,5% komentar jalur A yang positif, jadi dari setiap 40 komentar tentang kasus ini kira-kira hanya satu "
         "yang membela atau mendukung Raffi. Kalau ditimbang jumlah like (bobot 1 + like), porsinya turun menjadi 0,2%. "
         "Median like komentar positif hanya 2, sedangkan komentar negatif 7. Jadi pembelanya bukan hanya sedikit, tapi "
         "juga jarang disetujui warganet lain.")
    ctf = pd.crosstab(a.fase, a.label).reindex(["pra", "puncak", "pasca"])[SENT]
    caption("Tabel 26. Sentimen jalur A per fase")
    tabel([["Fase", "Teks", "Negatif", "Netral", "Positif"]] +
          [[i, str(int(r.sum())), *[f"{f1(r[c] / r.sum() * 100)}%" for c in SENT]] for i, r in ctf.iterrows()],
          lebar=[3, 2, 2.5, 2.5, 2.5])
    para("Fase pra hanya punya 30 teks, karena sebelum 29 Oktober Raffi belum dikaitkan dengan kasus apa pun. Dari fase "
         "puncak ke pasca, negatif naik dari 63,1% menjadi 69,3%, dan uji chi-square memberi p = 0,0002. Jadi setelah "
         "klarifikasi, sikap warganet tidak melunak. Positif tetap di 2 sampai 3%.")
    gambar(FIG / "06_tren_harian.png", 16)
    caption("Gambar 7. Proporsi sentimen per hari (hari dengan minimal 20 teks)")
    para("Grafik harian memperlihatkan tiga tahap. Di hari deklarasi (29 Oktober), 83,3% komentar netral karena yang "
         "diejek adalah peserta yang mengaku dibayar, belum Raffi. Mulai 30 dan 31 Oktober sasarannya pindah ke Raffi, dan "
         "negatif naik menjadi 58,9% lalu 68,2%. Tanggal 31 Oktober adalah hari klarifikasi sekaligus hari dengan teks "
         "terbanyak (554). Puncak kedua datang setelah temuan ICW tanggal 9 November: negatif 74,5% sampai 76,9% di 9 "
         "sampai 11 November, tertinggi di seluruh periode.")
    para("Topik yang dibahas juga bergeser. Di fase puncak, kontrak Rp14,7 miliar hanya 1,9% dari aspek yang dibahas, lalu "
         "naik menjadi 42,9% di fase pasca. Sebaliknya, mahasewa turun dari 29,1% menjadi 4,1%. Aspek yang paling negatif "
         "adalah jabatan utusan khusus (80,1% negatif), kontrak Rp14,7 miliar (77,5%), dan klarifikasi (76,6%). Aspek "
         "mahasewa justru paling rendah (40,3%), karena komentarnya lebih sering mengejek peserta daripada Raffi.")
    para("Antarplatform, TikTok paling negatif (76,0%) sekaligus paling positif (6,1%), jadi paling terbelah. Instagram dan "
         "X paling banyak netral (sekitar 36%), karena di sana banyak yang mengejek mahasiswa bayaran atau pemerintah tanpa "
         "menyebut Raffi.")
    para("Pembela yang ada kebanyakan membela dengan argumen (42 dari 84 teks positif), sisanya dukungan (22) dan simpati "
         "(16). Argumennya berulang: Raffi hanya diundang dan yang salah panitia, atau kontrak itu kerja sama biasa. "
         "Contohnya \"Dia memang di undang kan shari sblumnya...mnrt sy yg dipersalahkan yg buat acarany\".")
    para("Temuan yang paling di luar dugaan kami ada di jalur B. Kami mengira komentar di akun Raffi sendiri akan jauh "
         "lebih positif karena yang berkomentar biasanya pengikutnya. Ternyata 78,0% komentar di sana negatif, lebih tinggi "
         "dari Instagram jalur A (62,7%, p < 0,0001). Di fase pasca, 246 dari 298 komentar jalur B negatif. Contohnya "
         "\"Mayan kenyang ya 14.7M lohhhh dari APBN, mantap kaliiii\" dan \"Minimal nyusul ngundurin diri fii\". "
         "Kelihatannya warganet sengaja datang ke akun Raffi untuk menyampaikan kritik secara langsung.")
    para("Dari 14 teks yang diputuskan buzzer oleh tim saat review, 12 negatif dan 2 positif. Banyak yang memakai template "
         "yang sama, misalnya \"Peringatan darurat ... Gerakan #indonesiasadar\". Karena teks ini sudah dikeluarkan, "
         "proporsi negatif di atas tidak dinaikkan oleh buzzer.")

    ISI_PENUTUP(para, judul, caption, tabel, butir, ROOT, g, terbaik)


def _aug(dampak, nama):
    t = dampak[dampak.augmentasi == nama]
    return t, int((t["Δ macro-F1"] > 0).sum()), len(t)


def ISI_HASIL(para, judul, caption, tabel, gambar, butir, ROOT, hasil, g, terbaik):
    D = ROOT / "data"
    FIG = ROOT / "figures"
    O = D / "09_perbandingan"
    top = g.iloc[0]
    tf = g[g.model.str.startswith("TF-IDF")].iloc[0]
    para(f"Model terbaik adalah **{top.model}** dengan input {top.input} dan augmentasi {top.augmentasi}, macro-F1 "
         f"{f3(top.macro_f1)} ± {f3(top.sd)}. Baseline TF-IDF terbaik ({tf.model}, {tf.input}, {tf.augmentasi}) mendapat "
         f"{f3(tf.macro_f1)}, jadi selisihnya {f3(top.macro_f1 - tf.macro_f1)}. Selisih ini lebih kecil dari yang kami "
         "harapkan, dan per fold model transformer tidak selalu menang (notebook 05, bagian perbandingan per fold). "
         "IndoBERT embedding + LogReg, yang bobot BERT-nya tidak ikut dilatih, setara dengan TF-IDF, sedangkan BiLSTM + "
         "attention paling rendah di antara model yang belajar, karena 3.329 teks terlalu sedikit untuk melatih LSTM dari awal.")

    judul("12.1 Dampak augmentasi", 2)
    dampak = pd.read_csv(O / "dampak_augmentasi.csv")
    rows = [["Varian", "Konfigurasi membaik", "Rata-rata Δ macro-F1", "Rata-rata Δ F1 positif"]]
    for v in ["jalur B", "parafrase", "jalur B + parafrase", "jalur B + terarah"]:
        t, n, m = _aug(dampak, v)
        rows.append([v, f"{n} dari {m}", f3(t["Δ macro-F1"].mean()), f3(t["Δ F1 positif"].mean())])
    caption("Tabel 21. Dampak augmentasi dibanding tanpa augmentasi, dirata-rata di semua model dan input")
    tabel(rows, lebar=[4, 3.5, 3.5, 3.5])
    _, nb_, mb = _aug(dampak, "jalur B")
    tp, np_, mp = _aug(dampak, "parafrase")
    para(f"Hasilnya cukup jelas. **Komentar positif jalur B membantu di {nb_} dari {mb} konfigurasi**, sedangkan "
         f"**parafrase back-translation membantu di {np_} dari {mp}**. Parafrase justru menurunkan F1 positif rata-rata "
         f"{f3(-tp['Δ F1 positif'].mean())}. Kami melihat dua penyebab. Pertama, sekitar 1 dari 6 parafrase maknanya "
         "rusak atau berbalik (bagian 10), jadi model belajar dari label yang salah. Kedua, parafrase hanya mengulang "
         "teks positif yang sudah ada dengan kata lain dan memakai judul yang sama dengan teks aslinya, jadi model cenderung "
         "menghafal judul unggahan, bukan cara orang membela Raffi. Komentar jalur B ditulis orang yang berbeda di unggahan "
         "yang berbeda, jadi variasinya asli.")
    para("Model yang terbantu parafrase hanya Linear SVM dan XLM-RoBERTa. Tanpa augmentasi, Linear SVM hampir tidak pernah "
         "menebak positif, dan XLM-RoBERTa punya F1 positif paling rendah di antara model fine-tune (0,225). Jadi parafrase "
         "hanya berguna untuk model yang sangat lemah di kelas minoritas, bukan untuk model Indonesia yang sudah lebih kuat. "
         "Kesimpulan kami: **parafrase tidak dipakai, dan dasar augmentasinya adalah jalur B.** Varian jalur B + terarah "
         "dibahas terpisah di bagian 12.4.")

    judul("12.2 Dampak judul", 2)
    para("Menambahkan judul unggahan menaikkan macro-F1 di hampir semua model, paling besar di TF-IDF + LogReg (+0,058) dan "
         "IndoBERT embedding + LogReg (+0,064), dan membaik di kelima fold. IndoBERT fine-tune juga naik 0,048 di kelima "
         "fold. Ini wajar karena separuh teks (50,8%) ditandai "
         "annotator butuh judul supaya sasarannya jelas. Untuk IndoBERTweet efeknya kecil (+0,006), kemungkinan karena "
         "IndoBERTweet dilatih dari tweet pendek, sedangkan input teks + judul bisa sampai 256 token.")

    judul("12.3 Strategi untuk kelas positif", 2)
    st = pd.read_csv(O / "strategi_positif.csv")
    lc = pd.read_csv(O / "learning_curve_positif.csv")
    pk = pd.read_csv(O / "peringkat_positif.csv")
    para("F1 positif semua model berada di kisaran 0,2 sampai 0,35. Angka ini memang rendah, tapi perlu dibaca dengan "
         "pembanding yang tepat. Kelas positif hanya 2,5%, jadi menebak positif untuk semua teks hanya memberi F1 positif "
         "0,049, dan average precision (AP) tebakan acak 0,025. Model tunggal terbaik mendapat AP 0,383, kira-kira 15 kali "
         "tebakan acak. Selain itu, setiap fold uji hanya punya 16 atau 17 teks positif, jadi satu tebakan benar atau salah "
         "sudah menggeser F1 positif sekitar 0,03 sampai 0,05. Itulah sebabnya standar deviasi F1 positif antar fold besar "
         "(sekitar 0,1).")
    para("Kami menguji dua cara untuk menaikkan F1 positif tanpa menambah data, lalu satu analisis untuk melihat apakah data "
         "tambahan masih berguna, lalu benar-benar menambah data lewat pelabelan terarah (bagian 12.4).")
    caption("Tabel 22. Ensemble dan penggeseran ambang kelas positif (rata-rata 5 fold)")
    tabel([["Konfigurasi", "AP positif", "Macro-F1", "F1 positif", "Macro-F1 + ambang", "F1 positif + ambang"]] +
          [[r["konfigurasi"], f3(r["AP positif"]), f3(r["macro-F1"]), r["F1 positif"].replace(".", ","),
            f3(r["macro-F1 + ambang"]), r["F1 positif + ambang"].replace(".", ",")] for _, r in st.iterrows()],
          lebar=[6, 1.8, 1.8, 2.5, 2, 2.5], ukuran=8)
    ens_all = st[st.konfigurasi.str.startswith("ensemble IndoBERT")]
    ens = ens_all[~ens_all.konfigurasi.str.endswith("terarah")].iloc[0]
    ens_t = ens_all[ens_all.konfigurasi.str.endswith("terarah")]
    ens3 = st[st.konfigurasi.str.startswith("ensemble 3")]
    tunggal = st[~st.konfigurasi.str.startswith("ensemble")]
    t_ap = tunggal.loc[tunggal["AP positif"].idxmax()]
    para(f"**Ensemble.** Probabilitas IndoBERT dan IndoBERTweet fine-tune (teks + judul) dirata-rata. Dengan augmentasi "
         f"jalur B hasilnya macro-F1 {f3(ens['macro-F1'])} dan AP positif {f3(ens['AP positif'])}"
         + (f", dan dengan jalur B + terarah macro-F1 {f3(ens_t.iloc[0]['macro-F1'])} dan AP positif "
            f"{f3(ens_t.iloc[0]['AP positif'])}, macro-F1 tertinggi dari semua konfigurasi" if len(ens_t) else "")
         + f". Kenaikannya masih di dalam variasi antar fold, dan AP ensemble tidak lebih tinggi dari model tunggal terbaik "
         f"({t_ap['konfigurasi'].split(' |')[0]}, AP {f3(t_ap['AP positif'])}). Jadi ensemble lebih banyak menstabilkan "
         "tebakan negatif dan netral daripada menambah kemampuan menemukan teks positif."
         + (f" Kalau XLM-RoBERTa ikut dirata-rata (versi jalur B), hasilnya malah turun (macro-F1 "
            f"{f3(ens3.iloc[0]['macro-F1'])}, AP {f3(ens3.iloc[0]['AP positif'])}), karena model ini jauh lebih lemah. Jadi "
            "ensemble yang kami pakai cukup dua model Indonesia." if len(ens3) else ""))
    para("**Menggeser ambang kelas positif.** Probabilitas positif dikalikan bobot (0,5 sampai 12) sebelum diambil kelas "
         "tertinggi. Bobot dipilih dari 4 fold lain lalu diterapkan ke fold uji, supaya fold uji tidak ikut menentukan. "
         "Hasilnya tidak membaik secara konsisten, dan bobot yang terpilih berbeda-beda tiap fold. Artinya model fine-tune dengan class weight "
         "sudah cukup berani menebak positif, dan dengan 16 teks positif per fold, ambang yang terbaik di satu fold tidak "
         "berlaku di fold lain. Jadi cara ini tidak kami pakai.")
    b = lc.iloc[-1]
    para(f"**Learning curve.** TF-IDF + LogReg dilatih ulang dengan hanya 25%, 50%, 75%, dan 100% teks positif di data latih. "
         f"F1 positif naik dari {f3(lc.iloc[0]['F1 positif'])} (sekitar {int(lc.iloc[0]['positif di data latih'])} teks positif) "
         f"menjadi {f3(b['F1 positif'])} ({int(b['positif di data latih'])} teks positif), dan kurvanya belum mendatar. "
         "Artinya model belum jenuh, dan menambah teks positif asli kemungkinan besar masih menaikkan F1 positif.")
    gambar(FIG / "05_learning_curve_positif.png", 12)
    caption("Gambar 5. Learning curve kelas positif")
    r100 = pk[pk["teks teratas"] == 100].iloc[0]
    r200 = pk[pk["teks teratas"] == 200].iloc[0]
    para("**Dari mana data positif tambahan?** Kami tidak perlu scraping ulang. Ada 2.623 teks cadangan yang sudah lolos "
         "filter tapi belum dilabeli. Kalau diambil acak, hanya sekitar 2,5% yang positif. Tapi kalau teks diurutkan dulu "
         f"berdasarkan skor positif dari model, 100 teks teratas berisi {int(r100.positif)} positif ({f1(r100.presisi * 100)}%) "
         f"dan 200 teratas berisi {int(r200.positif)} ({f1(r200.presisi * 100)}%), sekitar 8 sampai 10 kali lipat dibanding "
         "acak. Jadi cara paling hemat adalah pelabelan terarah: model mengurutkan teks cadangan, lalu 200 sampai 300 teratas "
         "dilabeli dengan alur yang sama (3 AI, lalu 3 orang untuk teks yang tidak disepakati). Teks hasil pelabelan terarah "
         "tidak boleh masuk data uji atau statistik sentimen, karena sampelnya sengaja dipilih yang condong positif. "
         "Perlakuannya sama seperti jalur B, yaitu hanya menambah data latih.")

    judul("12.4 Hasil pelabelan terarah", 2)
    dt = pd.read_csv(O / "dampak_terarah.csv")
    lt = pd.read_csv(D / "04_labeled" / "label_terarah.csv")
    para("Saran di atas kami jalankan (folder labeling/terarah/). Ada 300 teks cadangan yang dilabeli: 250 dengan skor "
         "positif TF-IDF tertinggi dan 50 acak sebagai pembanding. Annotator, baik AI maupun manusia, tidak diberi tahu skor "
         "atau cara pilih teksnya. Alurnya sama dengan data utama. Sebanyak 227 teks disepakati bulat oleh 3 AI, 73 teks "
         "dinilai 3 orang, 66 di antaranya diputuskan mayoritas, dan 7 kartu yang ketiga penilainya memilih label berbeda "
         "diputus koordinator dengan mengikuti mayoritas 3 AI. Keputusan koordinator ini dicatat di "
         "labeling/terarah/review/koordinator.csv. Fleiss' kappa di 73 kartu adalah 0,260, setara dengan review utama "
         "(0,286). Kappa positif paling tinggi (0,549) dan netral paling rendah (0,116).")
    para("Hasilnya di bawah perkiraan kami. Dari 250 teks skor tertinggi hanya 33 yang positif (13%), dan dari 50 teks "
         "acak ada 2 (4%), jadi totalnya 35 positif, bukan 40 sampai 60. Presisinya juga lebih rendah dari peringkat di data "
         "berlabel (19% di 200 teratas). Dugaan kami, teks cadangan memang sisa yang tidak terpilih di sampel utama, dan 18 "
         "di antaranya ternyata tidak relevan. Walaupun begitu, pengurutan tetap sekitar 3 kali lebih efisien daripada sampel "
         "acak. Setelah 2 teks dibuang karena akunnya sudah ada di dataset final dan 1 teks dinilai buzzer, ada 32 teks "
         "positif baru. Teks ini hanya ditambahkan ke fold latih sebagai varian jalur B + terarah, sama seperti jalur B.")
    caption("Tabel 23. Dampak pelabelan terarah dibanding jalur B saja (rata-rata 5 fold)")
    tabel([["Model", "Input", "Macro-F1 jalur B", "+ terarah", "Fold membaik", "F1 pos jalur B", "+ terarah"]] +
          [[r[0], r[1], f3(r[2]), f3(r[3]), r[5], f3(r[6]), f3(r[7])] for r in dt.itertuples(index=False)],
          lebar=[4, 2.2, 2, 1.6, 1.6, 2, 1.6], ukuran=8)
    para("Dampaknya terbagi dua. TF-IDF dan model fine-tune terbantu: TF-IDF + LogReg teks + judul naik 0,015 dengan F1 "
         "positif naik 0,047, IndoBERTweet naik 0,012, dan IndoBERT praktis sama (+0,001), tapi F1 positif-nya naik 0,028 "
         "dan AP positif naik dari 0,333 ke 0,383. Recall positif model terbaik naik dari 27,4% ke 35,7%. Sebaliknya, model "
         "yang bobot BERT-nya dibekukan malah turun: IndoBERT embedding + LogReg turun 0,016 di kedua input dan BiLSTM turun "
         "0,006 sampai 0,016. Dugaan kami, teks terarah dipilih dari skor TF-IDF, jadi isinya condong ke kata yang memang "
         "sudah dikenali TF-IDF, sedangkan untuk model dengan representasi beku, 32 teks ini lebih menggeser batas kelas "
         "daripada menambah pola baru. Semua perubahan ini masih di dalam standar deviasi antar fold, jadi pelabelan terarah "
         "membantu sedikit, bukan lompatan besar. XLM-RoBERTa tidak dilatih ulang dengan varian ini, karena paling lemah dan "
         "kuota GPU lebih berguna untuk dua model Indonesia.")
    para("Ringkasnya, strategi kelas positif yang kami pakai adalah model fine-tune dengan class weight, input teks + judul, "
         "augmentasi jalur B + terarah, dan ensemble IndoBERT + IndoBERTweet. Parafrase dan penggeseran ambang tidak dipakai "
         "karena tidak membantu secara konsisten. Learning curve masih belum jenuh, tapi teks cadangan yang tersisa ternyata "
         "tidak sekaya perkiraan awal, jadi tambahan teks positif berikutnya kemungkinan perlu sumber baru.")

    # 13. ANALISIS KESALAHAN
    judul("13. Analisis Kesalahan", 1)
    ct = pd.read_csv(O / "confusion_terbaik.csv", index_col=0)
    sp = pd.read_csv(O / "positif_per_sub.csv", index_col=0)
    para(f"Analisis ini memakai prediksi {top.model} ({top.input}, {top.augmentasi}) di kelima fold uji, jadi setiap teks "
         "diprediksi tepat sekali saat menjadi data uji.")
    gambar(FIG / "05_confusion_matrix.png", 15)
    caption("Gambar 6. Confusion matrix baseline TF-IDF dan model terbaik")
    para(f"Recall per kelas adalah negatif {f1(ct.loc['negatif', 'negatif'] * 100)}%, netral "
         f"{f1(ct.loc['netral', 'netral'] * 100)}%, dan positif {f1(ct.loc['positif', 'positif'] * 100)}%. Teks positif "
         f"yang salah hampir semuanya ditebak negatif ({f1(ct.loc['positif', 'negatif'] * 100)}% dari semua teks positif), "
         "bukan netral. Kesalahan terbanyak secara jumlah adalah negatif ditebak netral dan netral ditebak negatif, yaitu batas "
         "yang juga paling sering diperdebatkan penilai manusia (kappa netral 0,219).")
    caption("Tabel 24. Ketepatan model terbaik untuk teks positif per sub-kategori")
    tabel([["Sub-kategori", "Teks", "Benar"]] +
          [[i, str(int(r["size"])), f"{f1(r['mean'] * 100)}%"] for i, r in sp.iterrows() if r["size"] >= 5],
          lebar=[4, 2, 2])
    para("Pola terpenting ada di sub-kategori positif. Dukungan seperti \"Terus buat kebaikan selalu Sukses\" cukup sering "
         "benar, tapi **pembelaan** sebagian besar salah. Pembelaan biasanya ditulis dengan nada marah atau mengejek, tapi "
         "sasarannya pengkritik Raffi, misalnya \"kerja namany itu proooo dunia gak ada gratisss "
         "fahammmmm\". Model membaca nadanya yang negatif, padahal sikapnya ke Raffi positif. Ini kelemahan yang sama dengan "
         "leksikon InSet, hanya lebih ringan.")
    para("Per kelompok teks, model paling sering salah di teks yang butuh judul untuk dipahami, teks yang juga mengkritik pihak "
         "lain (pemerintah, polisi, Willie Salim), dan teks yang panjang. Di teks yang mengkritik pihak lain, model harus "
         "memutuskan apakah Raffi ikut dikritik, dan ini juga yang paling sering diperdebatkan penilai manusia. Kesalahan "
         "netral ditebak negatif kebanyakan berupa berita yang menyebut Raffi bersama kata yang terdengar negatif "
         "(\"Rans festival sepi setelah beberapa pihak memboikot raffi ahmad...\"), atau kemarahan ke pihak lain. "
         "Sebaliknya, sindiran yang butuh pengetahuan kasus seperti \"3M buat karhutla kata Desta Raffi : masih ada 11M "
         "brooo\" sering ditebak netral.")
    para("Model terbaik dan baseline TF-IDF salah di teks yang cukup berbeda. Sekitar 355 teks hanya benar di "
         "salah satu model, ke arah mana pun, jadi jumlah perbaikan dan kemundurannya hampir sama. Ini juga alasan ensemble masuk akal: model yang kesalahannya berbeda bisa saling menutupi.")


def ISI_PENUTUP(para, judul, caption, tabel, butir, ROOT, g, terbaik):
    top = g.iloc[0]
    judul("15. Kesimpulan", 1)
    para(f"Model terbaik untuk mengklasifikasi sikap warganet terhadap Raffi adalah {top.model} dengan input {top.input} dan "
         f"augmentasi {top.augmentasi} (macro-F1 {f3(top.macro_f1)}), praktis seri dengan IndoBERT jalur B dan "
         "IndoBERTweet, dan ensemble IndoBERT + IndoBERTweet sedikit lebih tinggi (0,628). "
         "Tambahan judul unggahan memberi kenaikan paling konsisten, augmentasi jalur B membantu di semua konfigurasi, dan "
         "parafrase back-translation tidak membantu. Pelabelan terarah dari teks cadangan menghasilkan 32 teks positif baru "
         "dan menaikkan F1 positif model fine-tune dan TF-IDF, tapi kenaikannya kecil dan masih di dalam variasi antar fold. "
         "Kelas positif tetap paling sulit (F1 sekitar 0,35) karena contohnya sedikit dan pembelaan sering ditulis dengan "
         "nada marah.")
    para("Dari sisi isi, warganet sangat sedikit yang membela Raffi. Hanya 2,5% komentar yang positif, negatif naik setelah "
         "klarifikasi, dan bahkan di akun Instagram Raffi sendiri 78% komentarnya negatif.")

    judul("15.1 Jejak saran dosen", 2)
    para("Tabel berikut merangkum setiap saran dari konsultasi dosen, apa yang kami kerjakan, dan di mana hasilnya bisa dicek.")
    caption("Tabel 27. Saran dosen dan tindak lanjutnya")
    tabel([
        ["Saran", "Yang kami kerjakan", "Hasil", "Bukti"],
        ["Gerbang filter jangan overklaim", "Aturan otomatis hanya menandai kandidat, setiap kandidat dibaca manual oleh tim",
         "61 teks diselamatkan", "data/03_filtered/audit/keputusan_manual.csv, bagian 3"],
        ["Relevansi dan buzzer harus jelas siapa yang memutuskan",
         "Relevansi: kata kunci menandai, manusia memutuskan, lalu label tidak_relevan dinilai 3 AI dan 3 orang. Buzzer: "
         "aturan keras dan skor poin, zona batas diputuskan manusia", "14 teks buzzer, 182 tidak relevan",
         "bagian 3.4, 4, dan 7"],
        ["Label dinilai 3 orang dan dihitung Fleiss' kappa", "Semua teks yang tidak disepakati 3 AI dinilai 3 orang",
         "881 kartu lengkap, kappa 0,286 (cukup); pelabelan terarah 73 kartu, kappa 0,260",
         "labeling/review/3lapis/ringkasan_kappa.md, labeling/terarah/ringkasan_terarah.md, bagian 7.1 dan 12.4"],
        ["Hapus target biner, tetap 3 kelas", "Target biner dihapus dari semua notebook", "Semua model 3 kelas", "bagian 10"],
        ["Sampel positif dari akun Raffi dan augmentasi", "Jalur B, parafrase back-translation, dan pelabelan terarah, "
         "hanya di fold latih, diuji per varian", "Jalur B membantu, parafrase tidak, terarah membantu sedikit",
         "bagian 10, 12.1, dan 12.4"],
        ["BERT tanpa lowercase", "Teks dikirim apa adanya, emoji jadi kata Indonesia",
         "IndoBERTweet dan IndoBERT uncased (do_lower_case True), jadi lowercase tidak mengubah input. Hanya XLM-R yang "
         "membaca kapital", "log Kaggle di data/07_transformer/, bagian 9.2"],
        ["Coba IndoBERT embedding + LogReg dan model yang memahami konteks", "IndoBERT embedding + LogReg, BiLSTM + "
         "attention, fine-tune IndoBERTweet, IndoBERT, XLM-R", "Fine-tune terbaik", "bagian 11 dan 12"],
        ["F1 positif masih rendah", "Uji ensemble, penggeseran ambang, learning curve, peringkat teks cadangan, lalu "
         "pelabelan terarah 300 teks", "Terarah dan ensemble membantu sedikit (F1 positif 0,325 ke 0,352), ambang tidak",
         "notebooks/05, bagian 12.3 dan 12.4"],
        ["Analisis kesalahan", "Confusion matrix, akurasi per kelompok, pembacaan contoh",
         "Pembelaan bernada marah paling sering salah", "notebooks/05, bagian 13"],
    ], lebar=[3.6, 5, 3.6, 4], ukuran=8)

    judul("15.2 Keterbatasan", 2)
    butir("• Kelas positif hanya 84 teks, sehingga F1 positif sangat bergantung pada beberapa teks di setiap fold.")
    butir("• Kappa review 0,286 menunjukkan batas negatif dan netral memang subjektif, jadi label di batas itu tidak sempurna.")
    butir("• Data X hanya mencakup tweet yang mengandung kata kunci, dan Instagram serta TikTok tidak memberi umur akun "
          "untuk filter buzzer.")
    butir("• Pelabelan terarah sudah dijalankan, tapi hanya menghasilkan 32 teks positif baru, dan kenaikannya masih di "
          "dalam variasi antar fold. Tujuh kartu terarah yang seri diputus dengan mayoritas 3 AI, bukan oleh diskusi tim.")
    butir("• XLM-RoBERTa tidak dilatih ulang dengan varian terarah, dan pelatihan ulang di GPU tidak sepenuhnya "
          "deterministik (skor IndoBERTweet jalur B bergeser dari 0,614 ke 0,597 saat kernelnya dijalankan ulang), jadi "
          "selisih di bawah 0,02 antar konfigurasi tidak bisa dibaca sebagai kemenangan yang pasti.")
