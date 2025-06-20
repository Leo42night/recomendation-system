# -*- coding: utf-8 -*-
"""[dicoding-submisi]-proyek_rekomendasi.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DDwVfSewNLXvr8X256975S-EpUwcdzYA

# Laporan Proyek Machine Learning - Leo Prangs Tobing
"""

# from google.colab import drive
# drive.mount('/content/drive')

"""## Data Understanding

### Load Data

Siapkan semua library yang diperlukan proyek & load dataset. Dataset yang digunakan adalah **Book-Crossing: User review ratings** dari [Kaggle](https://www.kaggle.com/datasets/ruchi798/bookcrossing-dataset), dengan file yang digunakan adalah `Preprocessed_data.csv` (kombinasi informasi user, buku dan rating)
"""

# # buka block kode ini, downgrage numpy==2.0.2 jadi versi yang kompatible dgn lingkunan scikit-suprise di GColab
# # restar ulang sesi, lalu comment kembali kode setelah selesai
# !pip install numpy==1.24.4 --force-reinstall

# !pip install -qq scikit-surprise==1.1.4
# !pip install -qq kagglehub

# load & EDA
import kagglehub
import pandas as pd

# Preprocesasing
import numpy as np # ajust dtype
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

# modelling
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader

# Untuk .py file (run in terminal)
from IPython.display import display

# Inferensi
import random

# Download latest version
path = kagglehub.dataset_download("ruchi798/bookcrossing-dataset")

print("Path to dataset files:", path)

df = pd.read_csv(f"{path}/Books Data with Category Language and Summary/Preprocessed_data.csv")
print("df.shape", df.shape)
display(df.head())

"""**Insight:**

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
Beberapa analisis yang punya insight penting (ditampilkan di markdown setelah output kode di bawah).
"""

# Melihat jumlah user dan jumlah buku
print(f"{df['user_id'].nunique()} user, {df['isbn'].nunique()} buku")
print('\n---------- Change DType ---------')
display(df.info())
display(df[df['age'] == 5].head(3))
display(df[df['year_of_publication'] == 1376])

print('\n--------- Null Values ---------')
print('df.isna().sum():\n',df.isna().sum())

print('\n--------- Outliers ---------')
display('df.describe().T: ',df.describe().T)


print('\n--------- Invalid Values ---------')
for col in ['age', 'Language', 'Category']: # kolom kategori atau ordinal yang perlu diperiksa
    print(f"{col}: {df[col].unique().tolist()}")
display(df[df['Summary'] == '9'].head(3))

"""**Insight:**
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

## Data Preparation

### Pembersihan
Hapus kolom tidak berguna, ubah tipe data age & year menjadi **int**, isi null menggunakan string kosong (""), & ubah data invalid "9" menjadi string kosong ("").
"""

df2 = df.copy(deep=True) # Berganti ke versi 2 (lebih bersih)

# --- CLEANING ---
# Hapus 7 kolom yang tidak diperlukan
df2 = df2.drop(columns=['Unnamed: 0', 'img_s', 'img_m', 'img_l', 'city', 'state', 'country', 'Summary'])

# ubah tipe data
df2['age'] = df2['age'].astype(int)
df2['year_of_publication'] = df2['year_of_publication'].astype(int)

# isi nilai null
df2['book_author'] = df2['book_author'].astype(str).fillna('')

# ubah data invalid
df2['Language'] = df2['Language'].replace('9', '', regex=False)
df2['Category'] = df2['Category'].replace('9', '', regex=False)

df2.shape

"""- `df2` digunakan untuk preprocessing 2 model selanjutnya yang berdasarkan unik book (`df_book`) untuk model CBF, data unik relasi user-book-rating (`train_df_cf`) untuk model CF, dan `test_ground_truth` untuk evaluasi.
- Walau dapat dipakai untuk model CBF, Kolom `Summary` dihapus karena dapat menimbulkan noise.

### Sampling
Ambil irisan dari masing-masing top 500 User dan Buku (untuk performa).
"""

# --- SAMPLING ---
# ambil 500 user_id yang paling sering muncul
top_500_users = df['user_id'].value_counts().nlargest(500).index.tolist()

# ambil 500 isbn yang paling sering muncul
top_500_isbns = df['isbn'].value_counts().nlargest(500).index.tolist()

print("Top 500 User IDs:")
print(top_500_users[:10]) # print beberapa contoh
print("\nTop 500 ISBNs:")
print(top_500_isbns[:10]) # print beberapa contoh

# Filter the DataFrame to include only interactions from the top 500 users
df_filtered_users = df2[df2['user_id'].isin(top_500_users)]

# Further filter the result to include only interactions with the top 500 ISBNs
df2 = df_filtered_users[df_filtered_users['isbn'].isin(top_500_isbns)].reset_index(drop=True)

df2.shape

"""Dataset hasil filter: **~29.000** baris.

### Pembuatan Data untuk Model

#### CBF: `df_book`, `tfidf_matrix`, `isbn_to_index` & `index_to_isbn`
Versi unik buku + combined_features (gabungan title, author, publisher, language, category) untuk CBF. Setiap fitur penting digabung karena TF-IDF Butuh Representasi Teks Tunggal. `df_book` dipakai juga saat menampilkan Top-N rekomendasi
"""

df_book = df2.copy(deep=True)

# ambil nilai book unik berdasarka isbn
df_book = df_book.drop_duplicates('isbn')

# Gabungkan kolom-kolom teks (nilai pengelompokkan dan kepemilikan)
df_book['combined_features'] = df_book[['book_title', 'book_author', 'publisher', 'Language', 'Category']].agg(' '.join, axis=1)

pd.set_option('display.max_colwidth', None) # Jangan potong isi kolom
pd.set_option('display.width', None) # Biarkan lebar menyesuaikan layar
pd.set_option('display.max_columns', None) # Tampilkan semua kolom jika banyak

# sederhanakan tabel
df_book = df_book[['isbn', 'book_title', 'combined_features']].reset_index(drop=True)

print(df_book.shape)
df_book.sample(10)

"""**Proses setelah fitur digabung jadi 1 kalimat:**
- Membandingkan kemiripan antar buku berdasarkan konten atau metadata-nya. Caranya? Fitur-fitur dalam string (`combined_features`)  ditransformasikan ke dalam bentuk vektor menggunakan **TF-IDF (Term Frequency - Inverse Document Frequency)**. TF-IDF mengubah kumpulan teks menjadi representasi vektor numerik yang menekankan kata-kata penting dan khas, lalu digunakan untuk mengukur kemiripan antar dokumen.
"""

# TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words='english')

# Transformasikan ke bentuk numerik
tfidf_matrix = tfidf.fit_transform(df_book['combined_features'])

# Ukuran matriks (baris: isbn, kolom: kata unik dari combined_features)
print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")

# Contoh kata-kata (fitur) yang dihasilkan
feature_names = tfidf.get_feature_names_out()
print(f"Contoh fitur: {feature_names[:20]}")

"""**Hasilnya:** Didapatkan matriks TF-IDF dengan ukuran 500 ✖ 1377

Membuat index `isbn_to_index` dan `index_to_isbn`: digunakan untuk menjembatani antara format ISBN (string) dan posisi data dalam matriks TF-IDF (indeks numerik) sehingga memungkinkan pencarian dan interpretasi kemiripan antar buku.
"""

isbn_to_index = {isbn: idx for idx, isbn in enumerate(df_book['isbn'])}
index_to_isbn = {v: k for k, v in isbn_to_index.items()}
print(isbn_to_index)
print(index_to_isbn)

"""**Kenapa Diperlukan:**
- Matriks `tfidf_matrix` adalah array numerik (baris ke-0, ke-1, dst.).
- Untuk mencari cosine similarity antar buku, perlu tahu indeks baris dari sebuah ISBN.

#### `train_data` & `test_ground_truth`
- Buat ground truth: Ambil hanya buku dengan rating >= 5.
- Pisahkan test dan train: Gunakan 1 buku terakhir dari user sebagai test, sisanya sebagai train.
- Model Content-Based Filtering (CBF) yang menggunakan kemiripan antar fitur dievaluasi menggunakan data train dan test ini.
"""

# --- Filter rating >= 5 (threshold minimum rating yang dianggap relevan (Disukai)) ---
liked = df2[df2["rating"] >= 5]

# --- Mapping user -> daftar (isbn, rating) ---
user_liked_books = defaultdict(list)

for _, row in liked.iterrows():
    user_liked_books[row["user_id"]].append((row["isbn"], row["rating"]))

# --- Split ke train dan test (test: buku dengan rating tertinggi) ---
train_data = []
test_ground_truth = {}

for user, books in user_liked_books.items():
    if len(books) < 2:
        print("ada user dengan data terlalu sedikit di-skip")
        continue  # user dengan data terlalu sedikit di-skip

    # Urutkan buku berdasarkan rating (tinggi ke rendah)
    books_sorted = sorted(books, key=lambda x: x[1], reverse=True)
    highest_rating = books_sorted[0][1]

    # Ambil semua buku dengan rating tertinggi sebagai test
    test_books = [isbn for isbn, rating in books_sorted if rating == highest_rating]

    # Sisanya masuk ke data latih
    train_books = [isbn for isbn, rating in books_sorted if rating < highest_rating]

    if len(test_books) > 0 and len(train_books) > 0:
        test_ground_truth[user] = test_books
        train_data.extend([(user, isbn) for isbn in train_books])

print(user_liked_books)

"""`test_ground_truth` menunjukkan data kebenaran (buku yang seharusnya disukai/dibaca oleh pengguna di data uji. Jika kita lihat hasilnya"""

print(train_data[:5])
print(test_ground_truth)

"""Hasil memperlihatkan target `test_ground_truth` memiliki jumlah bervariasi karena diambil dari list kelompok buku dengan rating tertinggi

#### `trainset_surp_cf` (CF)
- Dibuat menggunakan `train_data`, yang kemudian dipakai untuk melatih model Collaborative Filtering.
- Model CF yang menggunakan pola user book dari user lain yang serupa (dari train data) dan merekomendasikannya, hasilnya akan dievaluasi dengan data testing.
"""

# Buat DataFrame dari train_data
train_df_cf = pd.DataFrame(train_data, columns=["user_id", "isbn"])
train_df_cf["rating"] = 5  # Karena semua data ini adalah rating >= 5 (menyederhanakan model)

"""**Dengan memberikan rating 5:**
- Dianggap bahwa setiap interaksi adalah positif (user menyukai buku tersebut).
- Ini umum dalam skenario implicit feedback, untuk mensimulasikan preferensi tinggi.

**Proses:** Data diubah ke format surprise dengan skala rating 1–5 agar bisa digunakan untuk pelatihan model rekomendasi.
"""

# Buat dataset surprise
reader = Reader(rating_scale=(1, 5)) # memberi tahu bahwa semua rating berada pada skala 1 hingga 5
train_data_surp = Dataset.load_from_df(train_df_cf[["user_id", "isbn", "rating"]], reader) # menjadi objek dataset yang bisa digunakan oleh library surprise
trainset_surp_cf = train_data_surp.build_full_trainset() # trainset adalah objek yang berisi semua data pelatihan yang siap digunakan oleh algoritma surprise

"""**Hasil:** Dihasilkan trainset siap pakai untuk model CF (seperti SVD).

## Modelling

### Content-Based Filtering (CBF)
Membuat sistem CBF untuk merekomendasikan buku berdasarkan kemiripan konten (TF-IDF) dari buku-buku yang pernah disukai oleh pengguna. Caranya:
- Menggunakan Cosine Similarity untuk mengukur kemiripan arah antara dua vektor dalam ruang vektor, dengan nilai berkisar dari -1 hingga 1
- Ambil semua buku yang disukai,
- Untuk setiap buku, ambil 5 buku paling mirip,
- Gabungkan semua rekomendasi dari buku-buku yang disukai pengguna,
- Gunakan dict.fromkeys untuk menghapus duplikat sambil mempertahankan urutan,
- Ambil hanya 10 buku teratas sebagai hasil akhir.
- Terakhir, lihat sample Top-10 Recomendation
"""

def get_similar_books(isbn, top_n=10):
    if isbn not in isbn_to_index:
        return []
    idx = isbn_to_index[isbn]
    cosine_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_sim.argsort()[::-1][1:top_n+1]
    return [index_to_isbn[i] for i in similar_indices]

# Ambil semua buku yang disukai user dari train
user_liked_books = defaultdict(list)
for user, isbn in train_data: # Data Uji
    user_liked_books[user].append(isbn)

# Buat prediksi rekomendasi berdasarkan kesamaan buku yang disukai
predictions_cbf = {}
for user, liked_books in user_liked_books.items():
    recs = []
    for b in liked_books:
        recs.extend(get_similar_books(b, top_n=5))  # bisa ubah top_n
    # Filter duplikat
    predictions_cbf[user] = list(dict.fromkeys(recs))[:10]

print("predictions_cbf (CBF):", predictions_cbf)
print("Target Ground Truth:", test_ground_truth)

# Top-10 Recomendation
sample_user = 261105
user_gt_isbns = test_ground_truth[sample_user]

# Ambil judul buku berdasarkan ISBN
gt_titles = df_book[df_book['isbn'].isin(user_gt_isbns)][['isbn', 'book_title']]

# Tampilkan hasil
print(f"\nUser: {sample_user}")
print(f"Ground Truth (buku paling disukai):")
display(gt_titles.reset_index(drop=True))

# Ambil daftar ISBN rekomendasi
cbf_isbns = predictions_cbf.get(sample_user, [])

# Buat DataFrame hasil rekomendasi untuk CBF
cbf_df = df_book[df_book['isbn'].isin(cbf_isbns)][['isbn', 'book_title']]
cbf_df = cbf_df.set_index('isbn').loc[cbf_isbns].reset_index()
print("\nTop-10 Rekomendasi (Content-Based Filtering):")
display(cbf_df)

"""**Hasil:**
- `predictions_cbf` Ini adalah top-10 daftar ISBN buku yang direkomendasikan untuk tiap pengguna, berdasarkan konten buku yang mirip dengan yang pernah disukai.
- Hasil Prediction model CBF dan Target Ground Truth akan dibandingkan untuk mendapatkan skor evaluasi
- Dari hasil skema, diambil sampel contoh Top-10 rekomendasi user **261105** dengan buku favorit "Interview with the Vampire"

### Collaborative Filtering (CF) – SVD
- Berdasarkan pola rating yang diberikan oleh pengguna lain.
- Menggunakan **SVD (Singular Value Decomposition)** dari library `surprise` untuk memfaktorkan matriks user-item menjadi representasi laten. Cara Kerjanya:
 - SVD adalah teknik dari aljabar linier untuk memfaktorkan matriks menjadi:
 $$
  R \approx U \cdot \Sigma \cdot V^T
  $$
  - `R`: matriks user-item (rating), `U`: representasi pengguna dalam ruang laten, `V`: representasi item (buku) dalam ruang laten, `Σ`: bobot (singular values).
  - Tidak peduli isi/konten buku → murni berdasarkan pola interaksi. Contoh: "User A menyukai buku X dan Y, maka kemungkinan besar juga akan suka Z."

**Catatan⚠️:** Setiap sesi build modelling dijalankan, hasil evaluasi CF (prediction & recall) dapat bervariasi. Alasannya: Model SVD() dari Surprise menggunakan Stochastic Gradient Descent (SGD) untuk pelatihan. SGD bersifat acak karena:
- Inisialisasi bobot dilakukan secara acak.
- Urutan data pelatihan dapat memengaruhi jalannya pembelajaran.
"""

model_cf = SVD()
model_cf.fit(trainset_surp_cf)

"""**Hasil:** Proses ini menghasilkan model Collaborative Filtering berbasis SVD yang telah siap digunakan untuk memberikan prediksi rating dan rekomendasi buku, meskipun data awal hanya berupa interaksi (tanpa rating eksplisit).

**Penjelasan Kode dibawah:**
- **Bangun Rekomendasi untuk tiap user**
- Tujuan Fungsi `get_top_n_cf(...)` Membuat sistem rekomendasi berbasis Collaborative Filtering (CF) menggunakan model SVD untuk memprediksi top-N buku yang mungkin disukai oleh setiap user.
- Menampilkan sampel Top-10 rekomendasi
"""

def get_top_n_cf(model, trainset, all_isbns, users, n=10):
    top_n = defaultdict(list)

    for user in users:
        try:
            inner_uid = trainset.to_inner_uid(user)
        except ValueError:
            continue  # user tidak dikenal di trainset

        seen_books = set([isbn for (u, isbn) in train_data if u == user])
        unseen_books = [isbn for isbn in all_isbns if isbn not in seen_books]

        predictions = [model.predict(user, isbn) for isbn in unseen_books]
        predictions.sort(key=lambda x: x.est, reverse=True)

        top_n[user] = [pred.iid for pred in predictions[:n]]

    return top_n

# ISBN unik
all_isbns = df2["isbn"].unique()
users_to_eval = list(test_ground_truth.keys())

# Buat prediksi rekomendasi
predictions_cf = get_top_n_cf(model_cf, trainset_surp_cf, all_isbns, users_to_eval, n=10)
print("Predictions (CF): ", predictions_cf)
print("Target Ground Truth:", test_ground_truth)

# Pengujia sample user yang sama dengan Contoh di model CBF
# Tampilkan hasil
print(f"\nUser: {sample_user}")
print(f"Ground Truth (buku paling disukai):")
display(gt_titles.reset_index(drop=True))

# Ambil daftar ISBN rekomendasi
cf_isbns = predictions_cf.get(sample_user, [])

# Buat DataFrame hasil rekomendasi untuk CF
cf_df = df_book[df_book['isbn'].isin(cf_isbns)][['isbn', 'book_title']]
cf_df = cf_df.set_index('isbn').loc[cf_isbns].reset_index()
print("\nTop-10 Rekomendasi (Collaborative Filtering):")
display(cf_df)

"""**Hasil:** `predictions_cf`: berisi top-10 rekomendasi buku untuk tiap pengguna berdasarkan model CF. Rekomendasi akan dibandingkan dengan `test_ground_truth` untuk dapat skor evaluasi. Sampel menunjukkan perbedaan dengan hasil rekomendasi CBF

## Evaluation

### Metrik Precision & Recall
"""

# Evaluasi
def evaluate_precision_recall(predictions, ground_truth):
    precisions, recalls = [], []

    for user in ground_truth:
        if user not in predictions:
            continue
        true_items = set(ground_truth[user])
        pred_items = set(predictions[user])
        tp = len(true_items & pred_items)

        precision = tp / len(pred_items) if pred_items else 0
        recall = tp / len(true_items) if true_items else 0

        precisions.append(precision)
        recalls.append(recall)

    avg_precision = sum(precisions) / len(precisions) if precisions else 0
    avg_recall = sum(recalls) / len(recalls) if recalls else 0
    return avg_precision, avg_recall

"""### Content-Based Filtering (CBF)
Evaluasi dengan precision & recall
"""

precision_cbf, recall_cbf = evaluate_precision_recall(predictions_cbf, test_ground_truth) # bandingkan hasil prediksi dan target
print("Predictions:", predictions_cbf)
print("Ground Truth:", test_ground_truth)
print(f"Precision (CBF): {precision_cbf:.4f}, Recall (CBF): {recall_cbf:.4f}")

"""**Interpretasi:**
- `Precision = 0.0221 (≈ 2.21%)` Dari seluruh buku yang direkomendasikan, hanya 2.21% yang benar-benar disukai oleh user.
- `Recall = 0.0632 (≈ 6.32%)` Dari semua buku yang seharusnya direkomendasikan (user_liked_books), hanya 6.32% yang berhasil diprediksi.
- Precision tinggi → model merekomendasikan buku yang benar-benar disukai pengguna.
- Recall tinggi → model berhasil menangkap sebagian besar buku yang disukai pengguna.
- Jika kedua nilai rendah, kemungkinan:
 - Deskripsi buku tidak cukup informatif.
 - Kesamaan konten (TF-IDF) tidak mencerminkan preferensi pengguna.
 - Perlu pendekatan lain: collaborative filtering, matrix factorization, dll.

### Collaborative Filtering (CF)
Evaluasi precision dan recall
"""

precision_cf, recall_cf = evaluate_precision_recall(predictions_cf, test_ground_truth) # bandingkan hasil prediksi dan target
print("Predictions:", predictions_cf)
print("Ground Truth:", test_ground_truth)
print(f"Precision (CF): {precision_cf:.4f}, Recall (CF): {recall_cf:.4f}")

"""**Inferensi:**
- **Peringatan⚠️:** Setiap sesi build modelling dijalankan, hasil evaluasi CF (prediction & recall) dapat bervariasi. Karena pada tahap mdelling menggunakan SGD,Inisialisasi bobot dilakukan secara acak.
- Skor yang pernah didapat (hasil masih dapat barubah dari ini):
  - Precision (CF): 0.0128, Recall (CF): 0.0321
  - Precision (CF): 0.0102, Recall (CF): 0.0298
  - Precision (CF): 0.0114, Recall (CF): 0.0336
  - Precision (CF): 0.0126, Recall (CF): 0.0342
  - Precision (CF): 0.0128, Recall (CF): 0.0323
- `Precision (CF)` Dari seluruh rekomendasi yang diberikan oleh model ke pengguna, hanya `1.02%-1.28%`(~1.15%) yang benar-benar sesuai dengan selera mereka (buku dengan rating tertinggi).
- `Recall (CF)` Dari semua buku favorit (yang pengguna beri rating tertinggi), hanya  `2.98%-3.42%`(~3.20%) yang berhasil direkomendasikan oleh model.

### Perbandingan Hasil Metrik

| Model                   | Precision | Recall |
| ----------------------- | --------- | ------ |
| Content-Based Filtering | 0.0221    | 0.0632 |
| Collaborative Filtering | ~0.0115   | ~0.0320|

- CBF unggul dalam precision dan recall dibandingkan CF.
- CBF lebih baik dalam merekomendasikan buku yang benar-benar disukai (rating tinggi).
- Namun, kedua model masih memiliki akurasi rendah secara keseluruhan, yang menunjukkan perlunya peningkatan atau pendekatan hybrid.

### Too-10 Rekomendasi
Mengambil data user random dan kedua model akan mengembalikan 10 Rekomendasi terbaik bukunya masing masing. Penjelasan Kode:
- `df_book[df_book['isbn'].isin(cbf_isbns)]` mengambil baris yang ISBN-nya ada dalam daftar rekomendasi. Hal yang sama unutk CF
- `.loc[cbf_isbns]` menjaga urutan sesuai urutan rekomendasi. Hal yang sama unutk CF
- Ditampilkan dalam format tabel dengan kolom isbn dan book_title.
"""

# Pilih satu user secara acak dari test_ground_truth
# sample_user = random.choice(list(test_ground_truth.keys())) # Versi random
sample_user = 261105
user_gt_isbns = test_ground_truth[sample_user]

# Ambil judul buku berdasarkan ISBN
gt_titles = df_book[df_book['isbn'].isin(user_gt_isbns)][['isbn', 'book_title']]

# Tampilkan hasil
print(f"\nUser: {sample_user}")
print(f"Ground Truth (buku paling disukai):")
display(gt_titles.reset_index(drop=True))

# Ambil daftar ISBN rekomendasi
cbf_isbns = predictions_cbf.get(sample_user, [])
cf_isbns = predictions_cf.get(sample_user, [])

# Buat DataFrame hasil rekomendasi untuk CBF
cbf_df = df_book[df_book['isbn'].isin(cbf_isbns)][['isbn', 'book_title']]
cbf_df = cbf_df.set_index('isbn').loc[cbf_isbns].reset_index()
print("\nTop-10 Rekomendasi (Content-Based Filtering):")
display(cbf_df)

# Buat DataFrame hasil rekomendasi untuk CF
cf_df = df_book[df_book['isbn'].isin(cf_isbns)][['isbn', 'book_title']]
cf_df = cf_df.set_index('isbn').loc[cf_isbns].reset_index()
print("\nTop-10 Rekomendasi (Collaborative Filtering):")
display(cf_df)

"""Hasilnya:
- User: 261105
- Buku yang disukai (Ground Truth): '0345337662' → *Interview with the Vampire*
- CBF cenderung merekomendasikan buku dengan kemiripan deskriptif terhadap buku favorit user.
- CF memberikan buku yang disukai oleh pengguna lain dengan preferensi yang mirip, sehingga hasil lebih beragam secara konten.
- Beberapa buku seperti The Testament muncul di kedua sistem, menandakan bahwa buku itu relevan secara konten dan populer di kalangan pengguna serupa.


"""