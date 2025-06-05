# Laporan Proyek Machine Learning - Leo Prangs Tobing

## Project Overview

**Latar Belakang:**

Dalam era digital, jumlah buku yang tersedia secara daring terus meningkat dengan sangat pesat. Platform-platform seperti Amazon, Goodreads, atau sistem perpustakaan digital menyediakan katalog buku yang sangat luas, yang justru dapat menyulitkan pembaca dalam menemukan buku yang sesuai dengan preferensi atau minat mereka. Hal ini menciptakan kebutuhan akan sistem rekomendasi yang cerdas untuk membantu pengguna menavigasi pilihan yang sangat banyak.

Sistem rekomendasi telah menjadi komponen penting dalam meningkatkan **pengalaman pengguna** dan **personalisasi** dalam berbagai platform digital, termasuk dalam industri buku. Dalam konteks ini, sistem rekomendasi dapat memberikan saran buku yang relevan berdasarkan minat pembaca, riwayat interaksi, atau penilaian (rating) mereka terhadap buku sebelumnya. Selain membantu pengguna menemukan buku yang sesuai, sistem ini juga berperan penting dalam meningkatkan **keterlibatan pengguna**, **retensi pembaca**, dan bahkan **peningkatan penjualan** atau sirkulasi buku di platform penyedia layanan.

Dua pendekatan umum yang sering digunakan dalam pengembangan sistem rekomendasi adalah **Content-Based Filtering (CBF)** dan **Collaborative Filtering (CF)**. Content-Based Filtering bekerja dengan membandingkan fitur-fitur konten antar buku (seperti genre, penulis, atau kata kunci deskripsi), sedangkan Collaborative Filtering menggunakan pola interaksi pengguna lain yang memiliki preferensi serupa. Menurut Aggarwal (2016), kedua pendekatan ini merupakan dasar dari kebanyakan sistem rekomendasi modern. Di sisi lain, Jannach et al. (2010) menekankan pentingnya sistem rekomendasi dalam mendukung eksplorasi item dalam katalog besar, termasuk dalam konteks literatur atau buku.

**Referensi:**

- Aggarwal, C. C. (2016). *Recommender Systems: The Textbook*. Springer.
- Jannach, D., Adomavicius, G., Tuzhilin, A., & Kantor, P. (2010). *Recommender Systems – Challenges, Insights and Research Opportunities*. ACM Transactions on Intelligent Systems and Technology (TIST), 1(1), 1–38.

---

## Business Understanding

**Problem Statements:**

- Banyak pengguna kesulitan menemukan buku yang sesuai dengan minat mereka karena banyaknya pilihan.
- Rekomendasi buku yang ditampilkan sering kali tidak dipersonalisasi berdasarkan preferensi pengguna sebelumnya.
- Tidak adanya sistem pendukung keputusan yang membantu pengguna mengeksplorasi buku-buku baru yang relevan dengan preferensi mereka.

**Project Goals:**

- Mengembangkan sistem rekomendasi buku yang dapat memberikan saran bacaan personal berdasarkan data riwayat rating pengguna.
- Membandingkan dua pendekatan sistem rekomendasi, yaitu Content-Based Filtering dan Collaborative Filtering, untuk mengevaluasi mana yang lebih efektif dalam memberikan rekomendasi yang relevan.
- Mengukur performa model menggunakan metrik evaluasi seperti **Precision** dan **Recall** berdasarkan buku-buku yang paling disukai (rating tertinggi) oleh pengguna.

**Solution Approach:**

- **Content-Based Filtering (CBF):** Rekomendasi diberikan berdasarkan kesamaan konten antar buku, seperti kesamaan tag, genre, atau fitur tekstual lainnya.
- **Collaborative Filtering (CF):** Rekomendasi dibuat berdasarkan perilaku dan pola rating dari pengguna lain yang memiliki preferensi serupa.
- Untuk evaluasi, dilakukan split data berdasarkan buku-buku dengan rating tertinggi sebagai *ground truth*, dan sistem akan diuji apakah mampu merekomendasikan buku tersebut kembali dalam top-N hasil.
- Metrik yang digunakan untuk mengevaluasi performa adalah **Precision** dan **Recall**, untuk mengukur seberapa relevan dan lengkap rekomendasi yang dihasilkan oleh sistem.

## Data Understanding

### Load Data
Siapkan semua library yang diperlukan proyek & load dataset. Dataset yang digunakan adalah **Book-Crossing: User review ratings** dari [Kaggle](https://www.kaggle.com/datasets/ruchi798/bookcrossing-dataset), dengan file yang digunakan adalah `Preprocessed_data.csv` (kombinasi informasi user, buku dan rating)

Terdapat **1.031.175 baris** data, dengan 19 kolom:

| No. | Kolom              | Deskripsi                                                                 |
|-----|--------------------|---------------------------------------------------------------------------|
| 1   | `Unnamed: 0`       | Indeks baris yang dihasilkan secara otomatis saat menyimpan file (bisa diabaikan). |
| 2   | `user_id`          | ID unik dari pengguna. Digunakan untuk mengidentifikasi user secara individual. |
| 3   | `location`         | Lokasi tempat tinggal pengguna dalam format "kota, provinsi, negara". |
| 4   | `age`              | Usia pengguna (dalam tahun). Tipe numerik. |
| 5   | `isbn`             | Nomor ISBN sebagai pengenal unik buku. |
| 6   | `rating`           | Nilai rating yang diberikan pengguna terhadap buku. Biasanya dalam skala 0–10. |
| 7   | `book_title`       | Judul lengkap dari buku. |
| 8   | `book_author`      | Nama penulis buku. |
| 9   | `year_of_publication` | Tahun buku tersebut diterbitkan. |
| 10  | `publisher`        | Nama penerbit buku. |
| 11  | `img_s`            | URL ke gambar sampul buku berukuran kecil (small). |
| 12  | `img_m`            | URL ke gambar sampul buku berukuran sedang (medium). |
| 13  | `img_l`            | URL ke gambar sampul buku berukuran besar (large). |
| 14  | `Summary`          | Ringkasan atau deskripsi isi buku. Dapat digunakan sebagai fitur teks dalam sistem rekomendasi. |
| 15  | `Language`         | Bahasa yang digunakan dalam buku (contoh: `en` untuk English). |
| 16  | `Category`         | Kategori atau genre buku, biasanya dalam bentuk list string (misalnya: `['Social Science']`). |
| 17  | `city`             | Kota asal pengguna (dipecah dari kolom `location`). |
| 18  | `state`            | Negara bagian atau provinsi asal pengguna (dipecah dari kolom `location`). |
| 19  | `country`          | Negara asal pengguna (dipecah dari kolom `location`). |


### EDA
Beberapa analisis yang punya insight penting:

- 92.107 user, 270.170 buku
- **change Dtype:** `age` & `year_of_publication` dapat diubah ke **int**
- **null value:** `book_author` = 1, `city` = 14k, `state` = 22k, `country` = 35k
- **number distribution:**
  - **outliers**: `age` diusia 5 untuk rata-rata pembaca usia 36 tahun, dan `year_of_publication` yang punya tahun 1376 untuk rata rata tahun 1995.
  - 50% data `rating` bernilai 0, mungkin karena: Rating default (belum memberikan penilaian) atau pengguna tidak suka bukunya.
- **Invalid Value**:
  - nilai `34.74389988072476` pade `age` perlu dibulatkan
  - nilai `9` pada `Summary`, `Language`, dan `Category` bisa berarti placeholder untuk metadata buku yang tidak perlu ditampilkan kembali setelah kemunculan pertama

Catatan: Hasil insight hanya untuk pemahaman umum, berguna atau tidak tergantung apakah kolom dipakai untuk modelling.

---

## Data Preparation

### Pembersihan Data
- **Data Cleaning:** Menghapus kolom tidak relevan [`Unnamed: 0`, `img_s`, `img_m`, `img_l`, `city`, `state`, `country`, `Summary`].
- **Change Dtype:** Mengubah `age` dan `year_of_publication` ke int.
- **Null Value:** menangani data `book_author` yang null, isi dengan string kosong ("").
- **Invalid Value:** Menangani nilai placeholder pada `Language` & `Category`, isi dengan string kosong ("").

Catatan:
- Walau dapat dipakai untuk model CBF, Kolom `Summary` dihapus karena dapat menimbulkan noise.

### Sampling
- Dipilih 500 pengguna dan 500 ISBN teratas berdasarkan frekuensi interaksi.
- Dataset hasil filter: ~29.000 baris.

### Pembuatan Data untuk Model
- `df_book`: Untuk model CBF, diperlukan fitur teks gabungan dari beberapa atribut buku:[`book_title`, `book_author`, `publisher`, `Language`, dan `Category`]
- `tfidf_matrix`: TF-IDF mengubah kumpulan teks menjadi representasi vektor numerik yang menekankan kata-kata penting dan khas, lalu digunakan untuk mengukur kemiripan antar dokumen. Didapatkan matriks TF-IDF dengan ukuran 500 ✖ 1377
- `isbn_to_index` & `index_to_isbn`: Digunakan untuk menjembatani antara format ISBN (string) dan posisi data dalam matriks TF-IDF (indeks numerik) sehingga memungkinkan pencarian dan interpretasi kemiripan antar buku. Karena untuk mencari cosine similarity antar buku, perlu tahu indeks baris dari sebuah ISBN.
- `train_data` & `test_ground_truth`: berdasarkan buku dengan rating ≥ 5, test = semua buku dengan rating tertinggi user. Nilai train digunakan untuk rekomendasi model CBF dan CF, kemudian diuji menggunakan data `testing`. 
- `trainset_surp_cf`: Dari `train_data` jadi `train_df_cf` kemudian jadi `trainset_surp_cf`, atur semua rating = 5 (karena semua data ini adalah rating >= 5, untuk menyederhanakan model). Data diubah ke format surprise dengan skala rating 1–5 agar bisa digunakan untuk pelatihan model rekomendasi CF.

---

## Modelling
Dalam tahap ini, dua model sistem rekomendasi dibangun dan dilatih:
1. **Content-Based Filtering (CBF)** menggunakan teknik **TF-IDF + Cosine Similarity**
2. **Collaborative Filtering (CF)** menggunakan algoritma **Singular Value Decomposition (SVD)** dari library `surprise`

### Content-Based Filtering (CBF)

#### Pendekatan:
- Membandingkan kemiripan antar buku berdasarkan konten atau metadata-nya.
- Fitur-fitur dalam string (`combined_features`)  ditransformasikan ke dalam bentuk vektor menggunakan **TF-IDF (Term Frequency - Inverse Document Frequency)** `tfidf_matrix`.
- Kemiripan antar buku dari `train_data` dihitung menggunakan **cosine similarity** antar vektor.
- `isbn_to_index` & `index_to_isbn` digunakan untuk menghubungkan ISBN (identitas buku) dengan indeks baris dalam tfidf_matrix

#### Langkah Implementasi:

1. **Fungsi Rekomendasi berdasarkan Kemiripan Buku**

   ```python
   def get_similar_books(isbn, top_n=10):
       idx = isbn_to_index[isbn]
       cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
       similar_indices = cosine_sim.argsort()[::-1][1:top_n+1]
       return [index_to_isbn[i] for i in similar_indices]
   ```

2. **Prediksi Buku untuk Tiap User**

   * Ambil buku-buku yang disukai user (`train_data`)
   * Untuk setiap buku, cari buku-buku mirip
   * Gabungkan, lalu ambil top-10 unik

   ```python
   predictions_cbf = {}
   for user, liked_books in user_liked_books.items():
       recs = []
       for b in liked_books:
           recs.extend(get_similar_books(b, top_n=5))
       predictions_cbf[user] = list(dict.fromkeys(recs))[:10]
   ```
  
3. **Contoh sampel**
- 👤 **User:** `261105`
- 🎯 **Ground Truth (Buku yang Paling Disukai):**

| ISBN       | Judul Buku                   |
| ---------- | ---------------------------- |
| 0345337662 | *Interview with the Vampire* |

- 📘 **Top-10 Rekomendasi – Content-Based Filtering (CBF):**

| ISBN       | Judul Buku                           |
| ---------- | ------------------------------------ |
| 0515127833 | *River's End*                        |
| 0743227441 | *The Other Boleyn Girl*              |
| 0380731851 | *Mystic River*                       |
| 0316899984 | *River, Cross My Heart*              |
| 0743203631 | *Gap Creek: The Story Of A Marriage* |
| 044022165X | *The Rainmaker*                      |
| 0440234743 | *The Testament*                      |
| 0440241537 | *The King of Torts*                  |
| 0440211727 | *A Time to Kill*                     |
| 0440220602 | *The Chamber*                        |

### Collaborative Filtering (CF) – SVD

#### Pendekatan:

- Berdasarkan pola rating yang diberikan oleh pengguna lain.
- Menggunakan **SVD (Singular Value Decomposition)** dari library `surprise` untuk memfaktorkan matriks user-item menjadi representasi laten.
- Model belajar dari `train_df_cf` (interaksi user-book dengan rating 5), yang diubah ke format surprise (`trainset_surp_cf`) dengan skala rating 1–5 agar bisa digunakan untuk pelatihan model.

**Catatan⚠️:** Setiap sesi build modelling dijalankan, hasil evaluasi CF (prediction & recall) dapat bervariasi. Alasannya: Model SVD() dari Surprise menggunakan Stochastic Gradient Descent (SGD) untuk pelatihan. SGD bersifat acak karena:
- Inisialisasi bobot dilakukan secara acak.
- Urutan data pelatihan dapat memengaruhi jalannya pembelajaran.

#### Langkah Implementasi:

1. **Latih Model SVD**

   ```python
   from surprise import SVD
   model_cf = SVD()
   model_cf.fit(trainset_surp_cf)
   ```

2. **Fungsi Rekomendasi untuk Tiap User**

   * Cari semua ISBN yang belum pernah dibaca user.
   * Prediksi rating untuk semua ISBN tersebut.
   * Ambil top-N berdasarkan nilai prediksi tertinggi.

   ```python
   def get_top_n(model, trainset, all_isbns, users, n=10):
       top_n = defaultdict(list)
       for user in users:
           seen_books = set([isbn for (u, isbn) in train_data if u == user])
           unseen_books = [isbn for isbn in all_isbns if isbn not in seen_books]
           predictions = [model.predict(user, isbn) for isbn in unseen_books]
           predictions.sort(key=lambda x: x.est, reverse=True)
           top_n[user] = [pred.iid for pred in predictions[:n]]
       return top_n
   ```

3. **Prediksi untuk Semua User**

   ```python
   all_isbns = df2["isbn"].unique()
   users_to_eval = list(test_ground_truth.keys())
   predictions_cf = get_top_n(model_cf, trainset, all_isbns, users_to_eval, n=10)
   ```

4. **Contoh sampel**
- 👤 **User:** `261105`
- 🎯 **Ground Truth (Buku yang Paling Disukai):**

| ISBN       | Judul Buku                   |
| ---------- | ---------------------------- |
| 0345337662 | *Interview with the Vampire* |

- 👥 **Top-10 Rekomendasi – Collaborative Filtering (CF):**

| ISBN       | Judul Buku                                                  |
| ---------- | ----------------------------------------------------------- |
| 0440234743 | *The Testament*                                             |
| 0452264464 | *Beloved (Plume Contemporary Fiction)*                      |
| 0345402871 | *Airframe*                                                  |
| 0446310786 | *To Kill a Mockingbird*                                     |
| 0671888587 | *I'll Be Seeing You*                                        |
| 0553582747 | *From the Corner of His Eye*                                |
| 0440225701 | *The Street Lawyer*                                         |
| 0140067477 | *The Tao of Pooh*                                           |
| 0345465083 | *Seabiscuit*                                                |
| 0679429220 | *Midnight in the Garden of Good and Evil: A Savannah Story* |

### Output Model

* `predictions_cbf`: dictionary `user_id → list of recommended isbn (top-10)` dari model CBF
* `predictions_cf`: dictionary `user_id → list of recommended isbn (top-10)` dari model CF (SVD)

Kedua output ini selanjutnya digunakan untuk evaluasi terhadap `test_ground_truth`.

---

## Evaluation

Tahapan ini bertujuan untuk **mengukur performa model rekomendasi** menggunakan metrik yang relevan terhadap **tugas personalisasi**, yaitu:

- **Precision**: seberapa relevan rekomendasi yang diberikan
- **Recall**: seberapa banyak item yang seharusnya direkomendasikan berhasil terjaring oleh sistem

**Tujuan Evaluasi:**

- Mengetahui seberapa baik model Content-Based Filtering (CBF) dan Collaborative Filtering (CF) dalam **memprediksi buku yang paling disukai** oleh pengguna.
- Membandingkan kinerja dua pendekatan untuk memahami keunggulan dan kelemahannya.

**Metodologi Evaluasi:**
- **Ground Truth:**
  -  Dibentuk dari buku-buku yang diberi **rating tertinggi (rating ≥ 5)** oleh pengguna.
  - Untuk setiap user, **semua buku dengan rating tertinggi** digunakan sebagai **test set** (`test_ground_truth`).
  - Sisanya digunakan sebagai data pelatihan model (`train_data`).

**Prediksi Model:**
- Setiap model menghasilkan top-10 rekomendasi untuk setiap user.
- Rekomendasi berupa daftar `isbn` (ID buku).

### Metrik Precision & Recall

Untuk setiap user:
- **Precision** = jumlah buku relevan yang berhasil direkomendasikan / total jumlah rekomendasi
- **Recall** = jumlah buku relevan yang berhasil direkomendasikan / total jumlah ground truth

```python
def evaluate_precision_recall(predictions, ground_truth):
    precisions, recalls = [], []
    for user in ground_truth:
        true_items = set(ground_truth[user])
        pred_items = set(predictions.get(user, []))
        if not pred_items:
            continue
        tp = len(true_items & pred_items)
        precision = tp / len(pred_items)
        recall = tp / len(true_items)
        precisions.append(precision)
        recalls.append(recall)
    return sum(precisions) / len(precisions), sum(recalls) / len(recalls)
```

### Evaluasi Content-Based Filtering (CBF)

```python
precision_cbf, recall_cbf = evaluate_precision_recall(predictions_cbf, test_ground_truth)
```

**Hasil:**

- **Precision (CBF): 0.0221 (≈ 2.21%)**
- **Recall (CBF): 0.0632 (≈ 6.32%)**
- **Interpretasi:**
  - CBF mampu menangkap preferensi pengguna lebih baik dibanding CF.
  - Meskipun performa masih rendah, model berhasil merekomendasikan beberapa buku relevan.

### Evaluasi Collaborative Filtering (CF)

```python
precision_cf, recall_cf = evaluate_precision_recall(predictions_cf, test_ground_truth)
```

**Hasil:**
- **Peringatan⚠️:** Setiap sesi build modelling dijalankan, hasil evaluasi CF (prediction & recall) dapat bervariasi. Karena pada tahap mdelling menggunakan SGD,Inisialisasi bobot dilakukan secara acak.
- **Skor** yang pernah didapat (hasil masih dapat barubah dari ini):
  - Precision (CF): 0.0128, Recall (CF): 0.0321
  - Precision (CF): 0.0102, Recall (CF): 0.0298
  - Precision (CF): 0.0114, Recall (CF): 0.0336
  - Precision (CF): 0.0126, Recall (CF): 0.0342
  - Precision (CF): 0.0128, Recall (CF): 0.0323
- `Precision (CF)` Dari seluruh rekomendasi yang diberikan oleh model ke pengguna, hanya `1.02%-1.28%`(~1.15%) yang benar-benar sesuai dengan selera mereka (buku dengan rating tertinggi).
- `Recall (CF)` Dari semua buku favorit (yang pengguna beri rating tertinggi), hanya  `2.98%-3.42%`(~3.20%) yang berhasil direkomendasikan oleh model.

### Perbandingan Hasil Matriks

| Model                   | Precision | Recall |
| ----------------------- | --------- | ------ |
| Content-Based Filtering | 0.0221    | 0.0632 |
| Collaborative Filtering | ~0.0115   | ~0.0320|

- **CBF unggul** dalam kedua metrik dibanding CF.
- Namun, kedua model masih menghasilkan nilai metrik yang **relatif rendah secara absolut**, menunjukkan bahwa sistem rekomendasi masih dapat ditingkatkan.
- Perlu dilakukan optimasi, seperti:
  - Hybrid model (menggabungkan CBF + CF)
  - Penerapan embedding model (Word2Vec, BERT, atau LightFM)
  - Tambahan data interaksi atau fitur (misal: review teks, genre eksplisit, dll.)

### Contoh Output Evaluasi (per user)
Berikut hasil yang sudah diubah ke dalam format **Markdown**:

- 👤 **User:** `261105`
- 🎯 **Ground Truth (Buku yang Paling Disukai):**

| ISBN       | Judul Buku                   |
| ---------- | ---------------------------- |
| 0345337662 | *Interview with the Vampire* |

- 📘 **Top-10 Rekomendasi – Content-Based Filtering (CBF):**

| ISBN       | Judul Buku                           |
| ---------- | ------------------------------------ |
| 0515127833 | *River's End*                        |
| 0743227441 | *The Other Boleyn Girl*              |
| 0380731851 | *Mystic River*                       |
| 0316899984 | *River, Cross My Heart*              |
| 0743203631 | *Gap Creek: The Story Of A Marriage* |
| 044022165X | *The Rainmaker*                      |
| 0440234743 | *The Testament*                      |
| 0440241537 | *The King of Torts*                  |
| 0440211727 | *A Time to Kill*                     |
| 0440220602 | *The Chamber*                        |

- 👥 **Top-10 Rekomendasi – Collaborative Filtering (CF):**

| ISBN       | Judul Buku                                                  |
| ---------- | ----------------------------------------------------------- |
| 0440234743 | *The Testament*                                             |
| 0452264464 | *Beloved (Plume Contemporary Fiction)*                      |
| 0345402871 | *Airframe*                                                  |
| 0446310786 | *To Kill a Mockingbird*                                     |
| 0671888587 | *I'll Be Seeing You*                                        |
| 0553582747 | *From the Corner of His Eye*                                |
| 0440225701 | *The Street Lawyer*                                         |
| 0140067477 | *The Tao of Pooh*                                           |
| 0345465083 | *Seabiscuit*                                                |
| 0679429220 | *Midnight in the Garden of Good and Evil: A Savannah Story* |

**Hasilnya:**
- CBF cenderung merekomendasikan buku dengan kemiripan deskriptif terhadap buku favorit user.
- CF memberikan buku yang disukai oleh pengguna lain dengan preferensi yang mirip, sehingga hasil lebih beragam secara konten.
- Beberapa buku seperti The Testament muncul di kedua sistem, menandakan bahwa buku itu relevan secara konten dan populer di kalangan pengguna serupa.
