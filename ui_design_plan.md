# Perencanaan Desain Tampilan (UI/UX) SIPACA-SLB

Proyek ini menggunakan prinsip **DRY (Don't Repeat Yourself)** dan pendekatan **modular**, sehingga perencanaan ini berfokus pada pembuatan *Reusable Components* (Komponen yang bisa dipakai berulang) di bagian Frontend (menggunakan Laravel Blade).

## 1. Struktur Layout Utama (Master Layout)

Sistem menggunakan satu layout utama (misalnya `app.blade.php`) agar elemen yang sama tidak perlu ditulis ulang di setiap halaman.

*   **Top Bar (Header):** Berisi teks/logo "SIPACA-SLB" di tengah, form pencarian (opsional), dan profil "Guru SLB" beserta ikon di sudut kanan.
*   **Sidebar (Navigasi Kiri):** Menu navigasi statis yang berisi:
    *   Home (Dashboard)
    *   Data Siswa
    *   Penilaian
    *   **Logout Button:** Diletakkan menempel di bagian paling bawah sidebar.
*   **Main Content Area:** Area kosong di sebelah kanan yang akan diisi secara dinamis tergantung halaman yang sedang diakses.

## 2. Rencana Pemetaan Halaman (Pages)

Berdasarkan *mockup/wireframe*, terdapat 6 halaman/tampilan utama dengan fungsionalitas berbeda:

### A. Halaman Otentikasi (Login & Register)
*   **Desain:** Menggunakan layout terpisah tanpa sidebar (misal: `auth.blade.php`). Form akan berada di dalam *Card* (kotak) di tengah layar.
*   **Login:** Input Username, Password, tombol **Login** (utama), dan tombol **Register** (sekunder).
*   **Register:** Input Nama Lengkap, Username, Password, tombol **Login** (sebagai submit pendaftaran), dan teks link "Sudah punya akun? Masuk".

### B. Halaman Home (Dashboard)
*   **Header:** Teks sambutan "Selamat Datang, Guru!".
*   **Statistik Dashboard:** Terdapat 3 *Cards* yang sejajar secara horizontal untuk menampilkan metrik penting:
    *   Total Siswa
    *   Penilaian Selesai
    *   Perlu Bimbingan

### C. Halaman Data Siswa
*   **Header:** Judul halaman "Data Siswa".
*   **Action Bar:** Terdiri dari form pencarian ("Search") di sebelah kiri dan tombol "+ Tambah" di sebelah kanan.
*   **Tabel Data:** Menampilkan kolom (NIS, Nama, Jenis Kelamin, Disabilitas, Aksi).
*   **Kolom Aksi:** Berisi ikon **Edit (Pensil)** dan **Hapus (Tempat Sampah merah)**.

### D. Halaman Penilaian
*   **Header & Action Bar:** Struktur sama persis dengan halaman Data Siswa (menggunakan komponen yang sama).
*   **Tabel Data:** Menampilkan daftar siswa untuk dinilai dengan kolom yang sama.
*   **Kolom Aksi:** Khusus di halaman ini, aksi berisi ikon **Lihat/Detail (Mata)** yang nantinya akan mengarah ke form input hasil tes portofolio/akademik.

### E. Halaman Form Penilaian (Input Data)
Halaman ini dibuka saat guru mengklik ikon Lihat/Detail pada tabel Penilaian.
*   **Header:** Judul "Form Penilaian".
*   **Top Action:** Dropdown "Pilih Siswa" dan tombol "Simpan" di sebelah kanan.
*   **Tabs Navigasi:** Terdapat dua tab utama, yaitu **Akademik** dan **Portofolio**.
    *   **Tab Akademik:** Memuat form input nilai dan capaian pembelajaran untuk setiap mata pelajaran (misal: Pendidikan Agama dan Budi Pekerti, Pendidikan Pancasila dan Kewarganegaraan). Setiap mata pelajaran memiliki *textarea* "Masukkan Nilai Akhir" dan "Masukkan capaian pembelajaran".
    *   **Tab Portofolio:** Memuat form input deskripsi perkembangan berdasarkan aspek (misal: Konsentrasi, Motorik, Interaksi dan Komunikasi). Setiap aspek memiliki *textarea* "Masukkan deskripsi perkembangan".

### F. Halaman Hasil Klasifikasi Siswa
Menampilkan ringkasan data siswa dan output/hasil dari model *Machine Learning*.
*   **Header:** Judul "Hasil Klasifikasi Siswa".
*   **Section Data Siswa:** Kotak informasi yang menampilkan identitas siswa (NISN, Nama, Kelas, Semester).
*   **Section Hasil Penilaian:** Area atau kotak yang menampilkan teks detail berisi kesimpulan hasil klasifikasi dari algoritma.
## 3. Ekstraksi Komponen Modular (Blade Components)

Untuk menghindari redundansi kode HTML dan memastikan kebersihan kode (*clean code*), komponen modular berikut akan dibuat di direktori `frontend/resources/views/components/`:

1.  `<x-card>`: Komponen kotak putih berbingkai (*drop shadow* ringan) untuk form otentikasi dan card ringkasan di dashboard.
2.  `<x-input>`: Komponen form input agar *styling* (border, padding, warna saat fokus) konsisten di seluruh aplikasi.
3.  `<x-button>`: Komponen tombol yang bisa menerima parameter/props tipe warna (contoh: *primary* untuk aksi utama/tambah, *danger* untuk hapus).
4.  `<x-table>`: Komponen dasar tabel yang rapi dan responsif, membungkus `<thead>` dan `<tbody>` sehingga dapat dipakai berulang kali untuk Data Siswa dan Penilaian.

## 4. Arahan Estetika & Aksesibilitas (Best Practices)

*   **Warna (Color Palette):** Menggunakan palet warna modern yang bersih (*clean UI*). Latar belakang keseluruhan menggunakan abu-abu terang, sedangkan *Card* menggunakan warna putih murni agar konten menonjol.
*   **Tipografi:** Menggunakan font *Sans-Serif* modern (seperti *Inter* atau *Roboto*) dengan kontras dan ukuran yang pas agar informasi mudah dibaca oleh guru.
*   **Interaksi (Micro-interactions):** Menambahkan efek transisi halus (*hover state*) pada elemen interaktif seperti tombol, link sidebar, dan baris tabel agar aplikasi terasa lebih hidup dan responsif.
