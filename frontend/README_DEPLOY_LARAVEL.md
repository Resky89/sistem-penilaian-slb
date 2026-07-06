# Panduan Deployment Frontend Laravel ke cPanel (ArenHost)

Panduan ini menjelaskan langkah demi langkah untuk melakukan deploy aplikasi frontend **Laravel 10/11** ke cPanel shared hosting Anda pada subdomain **`https://sipaca-slb.reskyprabowo.biz.id/`**.

---

## 📋 Langkah 1: Membuat Subdomain di cPanel

1. Masuk ke **cPanel** akun hosting Anda.
2. Cari dan buka menu **Domains** atau **Subdomains**.
3. Buat subdomain baru:
   * **Subdomain:** `sipaca-slb`
   * **Domain:** `reskyprabowo.biz.id`
4. **PENTING (Dokumen Root):** Arahkan **Document Root** subdomain tersebut langsung ke folder **`public`** dari proyek Laravel Anda:
   ```text
   /home/reskypra/sipaca-slb.reskyprabowo.biz.id/public
   ```
   *(Sistem keamanan Laravel mengharuskan web server melayani traffic dari folder `public` saja untuk menyembunyikan file kode program inti).*

---

## 📤 Langkah 2: Mengunggah Source Code ke Server

1. **Compress File Proyek:**
   Compress folder `frontend/` lokal Anda menjadi file ZIP (misal: `frontend.zip`).
   > **PENTING:** Jangan sertakan folder `vendor/`, `node_modules/`, `.env` lokal, maupun folder `.git/` ke dalam file ZIP tersebut untuk menghemat waktu upload dan kuota server.

2. **Upload & Ekstrak:**
   * Masuk ke **File Manager** cPanel.
   * Masuk ke folder `/home/reskypra/sipaca-slb.reskyprabowo.biz.id/`.
   * Upload file `frontend.zip` ke folder tersebut.
   * Ekstrak file ZIP tersebut langsung di tempat. Pastikan struktur file Anda (seperti `app/`, `public/`, `artisan`, dll.) berada langsung di dalam folder `/home/reskypra/sipaca-slb.reskyprabowo.biz.id/`.

---

## ⚙️ Langkah 3: Konfigurasi Environment File (`.env`)

1. Melalui **File Manager** cPanel di folder `/home/reskypra/sipaca-slb.reskyprabowo.biz.id/`, buat file baru bernama **`.env`** (atau salin dari `.env.example` lalu ubah namanya).
2. Edit file `.env` tersebut dan isikan konfigurasi produksi berikut:

   ```env
   APP_NAME="SIPACA SLB"
   APP_ENV=production
   APP_DEBUG=false
   APP_URL=https://sipaca-slb.reskyprabowo.biz.id

   LOG_CHANNEL=stack
   LOG_LEVEL=error

   # Koneksi Database MySQL (Sama seperti backend)
   DB_CONNECTION=mysql
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_DATABASE=reskypra_db_penilaian_slb
   DB_USERNAME=reskypra_db_user
   DB_PASSWORD=********  # Password user database MySQL cPanel Anda

   # URL Endpoint Backend API Flask
   # (Pastikan mengarah ke URL subdomain API Anda yang aktif)
   API_URL=https://slb.reskyprabowo.biz.id/api
   ```

   > [!TIP]
   > Nilai `API_URL` ini akan secara otomatis dimuat di halaman web Anda melalui konfigurasi `config/services.api.url` yang didefinisikan dalam `config/services.php`. Dengan menggunakan metode ini, Anda tetap bisa melakukan caching konfigurasi (`php artisan config:cache`) di server produksi dengan aman tanpa kehilangan nilai URL backend.

---

## 💻 Langkah 4: Instalasi Dependencies via Terminal cPanel

1. Buka menu **Terminal** di cPanel Anda (atau login melalui SSH).
2. Masuk ke direktori root frontend Laravel Anda:
   ```bash
   cd /home/reskypra/sipaca-slb.reskyprabowo.biz.id
   ```
3. **Instal Library PHP (Composer):**
   Jalankan perintah berikut untuk menginstal semua package PHP di server tanpa dev-dependency dan dengan optimalisasi pemuatan kelas:
   ```bash
   composer install --no-dev --optimize-autoloader
   ```
4. **Instal & Build Assets Frontend (Vite/NodeJS):**
   Jalankan perintah berikut untuk meng-compile file asset CSS/Javascript (seperti Tailwind CSS) ke bentuk siap produksi:
   ```bash
   npm install
   npm run build
   ```

---

## 🔑 Langkah 5: Generate Key & Konfigurasi Cache

Jalankan serangkaian perintah artisan berikut di terminal cPanel Anda untuk mengamankan aplikasi dan mempercepat performa:

```bash
# 1. Membuat Application Key Laravel
php artisan key:generate

# 2. Membuat Symbolic Link Folder Storage (Untuk akses file gambar/media)
php artisan storage:link

# 3. Membuat Cache Konfigurasi & Route (Sangat penting di Production)
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

---

## 🔒 Langkah 6: Mengatur Permissions Folder

Pastikan folder `storage` dan `bootstrap/cache` memiliki izin akses tulis (write permissions) agar Laravel dapat menyimpan cache dan log dengan lancar. Jalankan perintah ini di terminal:

```bash
chmod -R 775 storage bootstrap/cache
```

---

## 🔍 Langkah 7: Verifikasi Hasil Deployment

1. Buka browser dan akses domain frontend Anda:
   👉 **`https://sipaca-slb.reskyprabowo.biz.id/`**
2. Coba lakukan navigasi halaman, uji fungsi login, dan penambahan data untuk memastikan frontend Laravel berkomunikasi dengan mulus ke API Flask di subdomain `https://slb.reskyprabowo.biz.id/`.
3. Jika terjadi halaman putih/blank atau error 500 pada Laravel, Anda bisa memeriksa file log di:
   ```text
   /home/reskypra/sipaca-slb.reskyprabowo.biz.id/storage/logs/laravel.log
   ```
