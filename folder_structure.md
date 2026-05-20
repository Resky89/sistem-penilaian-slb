# Struktur Folder Proyek: Sistem Penilaian SLB

Proyek ini dirancang menggunakan pendekatan **Modular Monorepo**, di mana *Frontend*, *Backend*, dan *Data Mining* ditempatkan dalam satu repositori untuk mempermudah manajemen, namun tetap terisolasi secara fungsional *(Separation of Concerns)*. Hal ini sangat mendukung penulisan *clean code* dan prinsip *DRY (Don't Repeat Yourself)*.

---

## 📂 Root Directory
```text
Sistem-Penilaian-SLB/
├── backend/                  # (Flask REST API)
├── frontend/                 # (Laravel UI)
├── data-mining/              # (Eksperimen & Pelatihan Model ML)
├── database_erd.md           # Dokumentasi Database (Telah dibuat)
├── folder_structure.md       # Dokumentasi Struktur Proyek
└── .gitignore                # Mengabaikan file tidak penting untuk git
```

---

### 1. 🟢 `frontend/` (Laravel)
Bertugas murni sebagai *Backend-for-Frontend* (BFF). Modul ini hanya mengatur User Interface (UI), User Experience (UX), dan berkomunikasi dengan Flask API. **Tidak ada koneksi langsung ke database MySQL di sini.**

```text
frontend/
├── app/
│   ├── Http/
│   │   ├── Controllers/      # Logika antarmuka (mis: AssessmentController.php)
│   │   └── Middleware/       # Middleware untuk mengecek token session dari API
│   └── Services/             # 🌟 Kelas khusus (ApiService.php) untuk HTTP request ke Flask (DRY pattern)
├── config/                   # Konfigurasi aplikasi frontend
├── public/                   # Aset publik statis (CSS, JS, Images, build framework CSS)
├── resources/
│   ├── css/                  # File CSS
│   ├── js/                   # Skrip interaktif sisi klien
│   └── views/                # Templating Blade
│       ├── components/       # 🌟 Komponen UI Reusable (contoh: x-button, x-form-input)
│       ├── layouts/          # Template master (header, sidebar, footer)
│       ├── auth/             # Halaman login/logout
│       └── assessments/      # Halaman form input penilaian (Tab akademik & portofolio)
└── routes/
    └── web.php               # Routing URL untuk halaman UI ke browser
```

**Konsep Utama:**
- Semua interaksi API dibungkus di dalam folder `Services/` untuk menghindari pengulangan kode saat memanggil API.
- Folder `components/` mencegah kita menulis kode HTML yang berulang-ulang untuk form, tombol, atau alert.

---

### 2. 🔵 `backend/` (Flask)
Bertugas sebagai **REST API** yang mengelola *business logic*, operasi *Create-Read-Update-Delete* (CRUD) ke database, memvalidasi sesi/token, serta mengeksekusi model Machine Learning untuk melakukan prediksi secara *real-time*.

```text
backend/
├── app/
│   ├── __init__.py           # Inisialisasi Flask, CORS, ORM (SQLAlchemy)
│   ├── models.py             # Skema tabel database (Berdasarkan ERD)
│   ├── routes.py             # Registrasi endpoint REST API (menggunakan Blueprint)
│   ├── controllers/          # Logika endpoint spesifik (AuthController, AssessmentController)
│   ├── services/             # 🌟 Logika bisnis internal aplikasi
│   └── ml_integration.py     # 🌟 Skrip khusus untuk me-load .pkl dan mengeksekusi prediksi
├── models/
│   ├── random_forest.pkl     # File model ML final (dicopy dari output folder data-mining)
│   └── tfidf_vectorizer.pkl  # Objek TF-IDF untuk pemrosesan teks portofolio
├── config.py                 # Konfigurasi environment (Database URI, Secret Key API)
├── requirements.txt          # Daftar dependensi API (flask, sqlalchemy, scikit-learn, dll)
└── run.py                    # Entry point utama untuk menjalankan server Flask API
```

**Konsep Utama:**
- Kelas di `ml_integration.py` sangat krusial; tugasnya hanya menerima JSON dari Frontend, meneruskannya ke file `.pkl`, dan mengembalikan JSON hasil (rekomendasi dan klasifikasi) ke Frontend.

---

### 3. 🟣 `data-mining/`
Bertugas sebagai **Lab Eksperimen**. Di sinilah data mentah dibersihkan, diekstraksi, dan algoritma *Random Forest* dilatih (di-*training*). Setelah model menunjukkan tingkat akurasi yang memuaskan, barulah model tersebut (file `.pkl`) di-deploy ke folder `backend/`.

```text
data-mining/
├── datasets/
│   ├── raw/                  # Data mentah (mis: DATA MENTAH.xlsx)
│   └── processed/            # Data yang sudah dibersihkan dan siap ditraining
├── notebooks/                # 🌟 File Jupyter Notebook (.ipynb) untuk eksperimen bertahap
│   ├── 01_data_exploration.ipynb
│   ├── 02_preprocessing_and_tfidf.ipynb
│   └── 03_model_training_rf.ipynb
├── src/                      # Kumpulan skrip Python modular pembantu
│   ├── data_cleaning.py      # Fungsi untuk membuang baris kosong, normalisasi ejaan
│   └── model_evaluation.py   # Fungsi menghitung metrik (Accuracy, Precision, Recall)
├── outputs/                  # Direktori hasil eksekusi model
│   ├── random_forest.pkl     # Model hasil training
│   ├── tfidf_vectorizer.pkl  # Objek teks-ke-vektor
│   └── evaluation_report.txt # Laporan performa model
├── train_model.py            # Skrip utama otomatisasi *training end-to-end*
└── requirements.txt          # Dependensi ML (pandas, scikit-learn, matplotlib, jupyter)
```

**Konsep Utama:**
- Sangat terisolasi. Eksperimen Machine Learning tidak akan merusak kestabilan layanan *Backend API* maupun *Frontend UI*.
- Jika ada penambahan data siswa baru dan ingin di-*retrain*, kita cukup menjalankannya di folder ini.
