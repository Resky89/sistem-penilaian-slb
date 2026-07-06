# Deploy Backend Sistem Penilaian SLB ke cPanel (CloudLinux Python App)

Panduan ini dibuat berdasarkan proses deploy aplikasi backend **Sistem Penilaian SLB (Flask + SQLAlchemy + Random Forest + SHAP)** ke hosting cPanel menggunakan **Python App (CloudLinux)** di ArenHost.

---

# 1. Persiapan

## Struktur Project

Pastikan struktur project di folder server Anda seperti berikut:

```text
slb.reskyprabowo.biz.id/
│
├── app/
├── models_ml/
├── alembic/
├── .env
├── requirements.txt
├── run.py
├── passenger_asgi.py
├── alembic.ini
└── README.md
```

---

# 2. Membuat Subdomain

1. Masuk ke **cPanel** Anda.
2. Cari menu **Domains** atau **Subdomains**.
3. Buat subdomain baru:
   ```text
   slb.reskyprabowo.biz.id
   ```
4. Setelah dibuat, direktori root subdomain di server Anda biasanya akan otomatis mengarah ke:
   ```text
   /home/reskypra/slb.reskyprabowo.biz.id/
   ```

---

# 3. Membuat Database

1. Masuk ke menu **MySQL® Database Wizard** di cPanel.
2. Ikuti wizard untuk membuat database dan user:
   * **Database:** `reskypra_db_penilaian_slb`
   * **User:** `reskypra_db_user`
   * **Password:** `********` (Gunakan password yang kuat)
3. Berikan hak akses penuh dengan mencentang **ALL PRIVILEGES**.

---

# 4. Import & Migrasi Database (Menggunakan Alembic)

Berbeda dengan cara manual meng-import file SQL, proyek ini menggunakan **Alembic** untuk membuat dan memigrasikan tabel database secara otomatis. 

Jalankan perintah berikut di Terminal cPanel (setelah virtual environment aktif):
```bash
alembic upgrade head
```
*(Tabel-tabel database beserta kolom SHAP akan terbentuk secara otomatis dan rapi di MySQL server hosting Anda).*

---

# 5. Upload Source Code

Upload seluruh isi folder `backend/` Anda (kecuali folder `venv/` lokal dan file SQLite `test_temp.db` lokal) ke direktori root aplikasi di cPanel:
```text
/home/reskypra/slb.reskyprabowo.biz.id/
```

---

# 6. Konfigurasi Python App

1. Buka menu **Setup Python App** di cPanel.
2. Klik **Create Application** dan isi kolom-kolomnya seperti berikut:
   * **Python Version:** Pilih **3.10** atau **3.11**
   * **Application Root:** `slb.reskyprabowo.biz.id`
   * **Application URL:** `slb.reskyprabowo.biz.id`
   * **Application Startup File:** `passenger_asgi.py`
   * **Application Entry Point:** `application` (tanpa tanda kutip, huruf kecil semua. Menunjuk pada `application` yang di-import di `passenger_asgi.py`)
3. Klik **Create**.

---

# 7. Install Dependency

1. Buka **Terminal** di cPanel Anda.
2. Aktifkan Virtual Environment sesuai dengan versi Python yang Anda pilih (cPanel menyediakannya di bagian atas halaman Python App Anda). Contoh:
   ```bash
   source /home/reskypra/virtualenv/slb.reskyprabowo.biz.id/3.11/bin/activate
   cd /home/reskypra/slb.reskyprabowo.biz.id
   ```
3. Bersihkan library usang/lama bawaan cPanel atau sisa-sisa library FastAPI terdahulu:
   ```bash
   pip uninstall fastapi uvicorn a2wsgi python-multipart matplotlib -y
   ```
4. Pasang semua dependencies baru yang tertulis di requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

---

# 8. Konfigurasi Environment (`.env`)

Buat file `.env` di dalam folder `/home/reskypra/slb.reskyprabowo.biz.id/` Anda menggunakan File Manager cPanel, lalu isikan kredensial database cPanel yang telah Anda buat di Langkah 3:

```env
DATABASE_URL=mysql+pymysql://reskypra_db_user:password_db@localhost:3306/reskypra_db_penilaian_slb
JWT_SECRET=supersecretkeyyangsangatpanjangdanaman123456!
ACCESS_TOKEN_EXPIRE_MINUTES=120
```

---

# 9. Config Settings di Project

Proyek ini telah dikonfigurasi menggunakan Pydantic Settings di file `app/config/settings.py` yang akan membaca file `.env` Anda secara otomatis:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

---

# 10. Mengatasi Masalah Tampilan "It works!"

Jika Anda mengakses domain Anda di browser dan masih memuat halaman default CloudLinux:
```text
It works!
Python v3.11.xx
```
Artinya file `passenger_asgi.py` Anda telah **di-overwrite (ditimpa)** oleh cPanel dengan script default bawaan saat pembuatan Python App.

### Solusinya:
Buka file **`passenger_asgi.py`** melalui File Manager cPanel, hapus semua isinya, dan kembalikan ke kode berikut ini:

```python
import os
import sys

# Batasi thread sebelum numpy/joblib diimport untuk mencegah crash RLIMIT_NPROC di cPanel
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application
```

Simpan file tersebut, lalu kembali ke menu **Setup Python App** dan klik **Restart**. Buka kembali domain Anda, halaman API Flask serta dokumentasi Swagger di `/docs` akan aktif dengan sempurna!
