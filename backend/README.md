# Backend Sistem Penilaian SLB (SIPACA-SLB) - Panduan Lokal

Backend API untuk aplikasi Sistem Penilaian Siswa Sekolah Luar Biasa (SLB) menggunakan **Flask (flask-openapi3)** dengan dukungan klasifikasi model Machine Learning (**Random Forest**) dan penjelasan interpretabilitas model (**xAI SHAP**).

Aplikasi ini menggunakan **flask-openapi3** yang menyajikan validasi parameter otomatis menggunakan model Pydantic v2 dan dokumentasi Swagger UI interaktif yang kompatibel dengan standar WSGI untuk deployment shared hosting (cPanel).

---

## Persyaratan Sistem

Sebelum menjalankan backend secara lokal, pastikan perangkat Anda telah terinstal:
- **Python 3.10+** (Direkomendasikan menggunakan virtual environment)
- **MySQL Server** (XAMPP, Laragon, Docker, atau MySQL Standalone)

---

## Struktur Folder Backend Utama

- `app/`: Folder modul utama aplikasi backend Flask.
  - `config/`: Konfigurasi aplikasi (misal: [settings.py](file:///d:/projects/Sistem-Penilaian-SLB/backend/app/config/settings.py)).
  - `database/`: Inisialisasi koneksi database ([connection.py](file:///d:/projects/Sistem-Penilaian-SLB/backend/app/database/connection.py)).
  - `models/`: Representasi ORM SQLAlchemy untuk database ([db_models.py](file:///d:/projects/Sistem-Penilaian-SLB/backend/app/models/db_models.py)).
  - `repositories/`: Lapisan akses data langsung ke database MySQL.
  - `controllers/`: Logika alur proses bisnis aplikasi.
  - `schemas/`: Skema validasi data request/response menggunakan Pydantic.
  - `services/`: Service khusus (seperti logika Machine Learning & SHAP di [ml_service.py](file:///d:/projects/Sistem-Penilaian-SLB/backend/app/services/ml_service.py)).
  - `middleware/`: Middleware autentikasi JWT (`require_auth`) dan logic context request.
  - `utils/`: Custom exception handler dan helper response.
- `alembic/`: Modul migrasi schema database MySQL secara otomatis.
- `models_ml/`: Folder biner model Random Forest, TF-IDF Vectorizer, dan Label Encoders.
- `run.py`: Script untuk menjalankan Flask development server secara lokal.
- `passenger_asgi.py`: WSGI entrypoint utama untuk deployment cPanel Phusion Passenger.
- `test_backend.py`: Unit testing fungsionalitas backend menggunakan database SQLite memori sementara.

---

## Langkah Instalasi & Konfigurasi Lokal

### 1. Membuat dan Mengaktifkan Virtual Environment
Buka terminal pada direktori root proyek `Sistem-Penilaian-SLB/` (sejajar dengan folder `backend/`) dan jalankan:
```bash
# Membuat virtual environment
python -m venv venv

# Mengaktifkan di Windows (PowerShell)
venv\Scripts\Activate.ps1

# Mengaktifkan di Windows (CMD)
venv\Scripts\activate.bat

# Mengaktifkan di Linux/macOS
source venv/bin/activate
```

### 2. Install Dependencies
Masuk ke direktori `backend/` dan pasang modul Python yang dibutuhkan:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Konfigurasi Environment File (`.env`)
Salin file [.env.example](file:///d:/projects/Sistem-Penilaian-SLB/backend/.env.example) ke file `.env` di dalam folder `backend/`:
```bash
cp .env.example .env
```
Buka file `.env` yang baru dibuat dan sesuaikan konfigurasi kredensial MySQL lokal Anda:
- `DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/db_penilaian_slb`
- `JWT_SECRET=<kunci_rahasia_jwt_acak_dan_panjang>`

### 4. Jalankan Migrasi Database
Untuk memigrasikan tabel database ke MySQL lokal Anda:
```bash
alembic upgrade head
```
*(Catatan: Pastikan layanan database MySQL Anda sudah aktif).*

---

## Menjalankan Aplikasi

Jalankan server pengembangan Flask secara lokal:
```bash
python run.py
```
Server akan aktif secara default di alamat: `http://127.0.0.1:8001/`

### Akses Dokumentasi API Interaktif (Swagger UI)
Anda dapat mencoba setiap endpoint secara langsung melalui Swagger UI di:
👉 **[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)**

---

## Menjalankan Unit Test

Untuk memverifikasi fungsionalitas kode dan memastikan tidak ada error regresi pada database transaksi:
```bash
python test_backend.py
```
*(Proses pengujian menggunakan SQLite file sementara, sehingga tidak akan memengaruhi data pada database MySQL lokal Anda).*
