# Desain Entity-Relationship Diagram (ERD)

**Proyek:** Sistem Penilaian SLB Tunagrahita (Machine Learning - Random Forest)

Dokumen ini menguraikan skema database yang optimal berdasarkan prinsip _clean code_, modularitas, dan DRY (Don't Repeat Yourself). Desain ini mengakomodasi data kuantitatif (nilai rapor) maupun data kualitatif (portofolio).

## 1. Tabel Master (Data Inti)

### `users`

Menyimpan data guru yang memiliki akses ke sistem untuk melakukan penilaian.

- `id` (PK, INT, Auto Increment)
- `full_name` (VARCHAR) - _Nama lengkap guru_
- `username` (VARCHAR, Unique) - _Digunakan untuk login_
- `password` (VARCHAR) - _Password yang sudah di-hash_
- `created_at` (TIMESTAMP)

### `students`

Menyimpan informasi profil siswa berkebutuhan khusus.

- `id` (PK, INT, Auto Increment)
- `student_number` (VARCHAR, Unique) - _Nomor Induk Siswa (NIS)_
- `full_name` (VARCHAR) - _Nama lengkap siswa_
- `gender` (ENUM: 'M', 'F') - _Jenis kelamin (M = Male/Laki-laki, F = Female/Perempuan)_
- `birth_date` (DATE) - _Tanggal lahir_
- `disability_category` (VARCHAR) - _Contoh: 'Tunagrahita Ringan C'_
- `guardian_name` (VARCHAR) - _Nama wali murid_
- `class_level` (VARCHAR) - _Kelas saat ini (Contoh: '1', '2', '3')_
- `semester` (ENUM: 'Odd', 'Even') - _Semester saat ini (Ganjil/Genap)_

### `assessment_aspects`

Tabel referensi modular untuk mata pelajaran atau aspek perkembangan yang dinilai.

- `id` (PK, INT, Auto Increment)
- `aspect_name` (VARCHAR) - _Contoh: 'Matematika', 'Kemampuan Motorik'_
- `aspect_type` (ENUM: 'quantitative', 'qualitative') - _Sangat penting untuk membedakan data yang diproses dengan TF-IDF atau langsung ke algoritma Random Forest._

---

## 2. Tabel Transaksi (Pencatatan Penilaian)

### `assessments`

Tabel _header_ yang mencatat sesi penilaian spesifik untuk seorang siswa.

- `id` (PK, INT, Auto Increment)
- `student_id` (FK, INT) -> _Merujuk ke `students.id`_
- `user_id` (FK, INT) -> _Merujuk ke `users.id` (Guru yang menilai)_
- `academic_year` (VARCHAR) - _Contoh: '2025/2026'_
- `semester` (ENUM: 'Odd', 'Even') - _Semester ganjil atau genap_
- `assessment_date` (DATE) - _Tanggal penilaian dilakukan_
- `created_at` (TIMESTAMP)

### `report_scores` (Data Kuantitatif)

Tabel _child_ dari `assessments` untuk nilai berbentuk angka (Mata pelajaran akademis).

- `id` (PK, INT, Auto Increment)
- `assessment_id` (FK, INT) -> _Merujuk ke `assessments.id`_
- `aspect_id` (FK, INT) -> _Merujuk ke `assessment_aspects.id`_
- `numeric_score` (FLOAT atau INT) - _Contoh nilai: 80, 85.5_

### `portfolio_scores` (Data Kualitatif)

Tabel _child_ dari `assessments` untuk teks naratif/hasil observasi guru (Perilaku, Kemandirian, dll).

- `id` (PK, INT, Auto Increment)
- `assessment_id` (FK, INT) -> _Merujuk ke `assessments.id`_
- `aspect_id` (FK, INT) -> _Merujuk ke `assessment_aspects.id`_
- `narrative_description` (TEXT) - _Teks ini yang akan diproses lebih lanjut oleh algoritma TF-IDF._

---

## 3. Tabel Machine Learning & Analitik

### `prediction`

Menyimpan _output_ dari model Random Forest serta rekomendasi untuk setiap penilaian.

- `id` (PK, INT, Auto Increment)
- `assessment_id` (FK, INT) -> _Merujuk ke `assessments.id`_
- `development_status` (VARCHAR) - _Contoh: 'Perlu Bimbingan', 'Cukup', 'Baik'_
- `probability_score` (FLOAT) - _Opsional: Skor probabilitas / tingkat keyakinan dari model_
- `iep_recommendation` (TEXT) - _Teks rekomendasi untuk Program Pembelajaran Individual (PPI)._

---

## Ringkasan Relasi & Alur Kerja (Workflow)

1. **`users` (1) ke (M) `assessments`**: Satu guru dapat mengirimkan banyak formulir penilaian dari waktu ke waktu.
2. **`students` (1) ke (M) `assessments`**: Satu siswa dapat dihubungkan dengan beberapa penilaian yang dilakukannya (meskipun tanpa ada menu riwayat khusus).
3. **`assessments` (1) ke (M) `report_card_scores` / `portfolio_scores`**: Satu sesi penilaian terdiri dari berbagai skor mata pelajaran dan catatan naratif observasi. Dengan memisahkan data kuantitatif dan kualitatif ke dalam tabel berbeda, sistem menjadi tangguh, mematuhi prinsip DRY, dan memastikan performa tinggi saat memproses teks menggunakan TF-IDF.
4. **`assessments` (1) ke (1) `prediction_results`**: Setelah penilaian selesai diinput, model _machine learning_ akan mengklasifikasikan hasil dan menyimpannya di tabel ini.
