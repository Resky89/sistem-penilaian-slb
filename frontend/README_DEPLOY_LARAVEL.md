# Panduan Deployment Frontend Laravel ke cPanel (ArenHost)

Panduan ini menjelaskan langkah demi langkah untuk melakukan deploy aplikasi frontend **Laravel** Anda ke cPanel shared hosting pada subdomain **`https://sipaca-slb.reskyprabowo.biz.id/`**.

---

## 🔍 Hasil Analisis Proyek Frontend Anda

Berdasarkan pemeriksaan struktur berkas proyek Anda:
1. **Tidak Memerlukan Database:** Proyek frontend ini murni berupa tampilan statis (Blade views) yang berkomunikasi secara langsung ke Flask backend API menggunakan pemanggilan Javascript `fetch()` dari browser. Laravel di sisi server tidak mengoperasikan database sama sekali.
2. **Tidak Memerlukan Node.js di Server:** File stylesheet CSS Tailwind Anda sudah ter-compile secara lokal di dalam folder `public/css/app.css` (dimuat via `asset('css/app.css')` pada layout utama). Anda **tidak perlu menginstal Node.js / menjalankan `npm run build`** di server produksi cPanel Anda.

Dengan demikian, proses deployment menjadi jauh lebih ringan dan cepat!

---

## 📋 Langkah 1: Membuat Subdomain di cPanel

1. Masuk ke **cPanel** akun hosting Anda.
2. Cari dan buka menu **Domains** atau **Subdomains**.
3. Buat subdomain baru:
   * **Subdomain:** `sipaca-slb`
   * **Domain:** `reskyprabowo.biz.id`
4. **Document Root:** Biarkan mengarah ke folder induk proyek Anda (default cPanel):
   ```text
   /home/reskypra/sipaca-slb.reskyprabowo.biz.id
   ```

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

## 🛠️ Langkah 2.5: Membuat Konfigurasi Redirect `.htaccess`

Karena Document Root subdomain Anda mengarah ke folder induk (bukan ke `/public`), Anda harus mengalihkan traffic secara otomatis ke dalam folder `/public` lewat file `.htaccess` luar:

1. Di **File Manager** cPanel, masuk ke folder utama `/home/reskypra/sipaca-slb.reskyprabowo.biz.id/`.
2. Buat file baru bernama **`.htaccess`** (diawali dengan titik).
3. Isi file `.htaccess` tersebut dengan kode berikut ini, lalu simpan:
   ```apache
   <IfModule mod_rewrite.c>
       RewriteEngine On
       # Alihkan seluruh request traffic ke dalam folder public secara diam-diam
       RewriteRule ^(.*)$ public/$1 [L]
   </IfModule>
   ```

---

## ⚙️ Langkah 3: Konfigurasi Environment File (`.env`)

1. Melalui **File Manager** cPanel di folder `/home/reskypra/sipaca-slb.reskyprabowo.biz.id/`, buat file baru bernama **`.env`** (atau salin dari `.env.example` lalu ubah namanya).
2. Edit file `.env` tersebut dan cukup isikan konfigurasi sederhana berikut (karena Anda tidak menggunakan database di frontend):

   ```env
   APP_NAME="SIPACA SLB"
   APP_ENV=production
   APP_DEBUG=false
   APP_URL=https://sipaca-slb.reskyprabowo.biz.id

   LOG_CHANNEL=stack
   LOG_LEVEL=error

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
3. **PENTING: Sesuaikan Versi PHP di cPanel:**
   Sebelum menginstal package PHP, pastikan Anda sudah mengatur versi PHP aktif di cPanel Anda ke **PHP 8.2 atau 8.3**:
   * Buka menu **Select PHP Version** (atau **PHP Selector**) di cPanel.
   * Pilih **8.2** atau **8.3** dari dropdown menu, lalu klik **Set as current** (Terapkan sebagai default).

4. **Instal Library PHP (Composer):**
    Jalankan perintah standard berikut untuk mengunduh semua library PHP:
    ```bash
    composer install --no-dev --optimize-autoloader
    ```

    > [!TIP]
    > **Catatan jika versi PHP di terminal belum ter-refresh:**
    > Jika setelah mengubah versi PHP ke 8.2 Anda masih mendapati error mismatch versi, silakan tutup terminal cPanel Anda dan buka kembali (atau jalankan perintah `hash -r` di terminal) untuk me-refresh session path PHP yang baru. Jika tetap kesulitan, Anda bisa menambahkan flag pengabaian: `composer install --ignore-platform-reqs --no-dev --optimize-autoloader`.

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
2. Uji fungsi login, registrasi, dan penambahan data untuk memastikan frontend Laravel berkomunikasi dengan mulus ke API Flask di subdomain `https://slb.reskyprabowo.biz.id/`.
3. Jika terjadi masalah, Anda bisa memeriksa file log di:
   ```text
   /home/reskypra/sipaca-slb.reskyprabowo.biz.id/storage/logs/laravel.log
   ```
