@extends('layouts.app')

@section('title', 'Hasil Klasifikasi - SIPACA-SLB')

@section('content')
<div class="page-header">
    <h1 class="page-header__title">Hasil Klasifikasi Siswa</h1>
</div>

{{-- Data Siswa --}}
<div class="info-box">
    <h2 class="info-box__title">Data Siswa</h2>
    <div class="info-box__grid">
        <div class="info-box__item">
            <span class="info-box__label">NISN:</span>
            <span class="info-box__value">1234567890</span>
        </div>
        <div class="info-box__item">
            <span class="info-box__label">Kelas:</span>
            <span class="info-box__value">VI-A</span>
        </div>
        <div class="info-box__item">
            <span class="info-box__label">Nama:</span>
            <span class="info-box__value">Jhon Doe</span>
        </div>
        <div class="info-box__item">
            <span class="info-box__label">Semester:</span>
            <span class="info-box__value">Ganjil 2025/2026</span>
        </div>
    </div>
</div>

{{-- Hasil Penilaian --}}
<div class="result-box">
    <h2 class="result-box__title">Hasil Penilaian</h2>
    <div class="result-box__content">
        <p>Berdasarkan analisis data akademik dan portofolio menggunakan algoritma Random Forest, siswa <strong>Jhon Doe</strong> terklasifikasikan dalam kategori:</p>

        <div style="margin: 1.5rem 0; padding: 1rem 1.5rem; background: var(--color-primary-light); border-left: 4px solid var(--color-primary); border-radius: var(--radius-md);">
            <p style="font-size: var(--font-size-lg); font-weight: 700; color: var(--color-primary); margin-bottom: 0.25rem;">Kategori: Perlu Bimbingan Khusus</p>
            <p style="font-size: var(--font-size-sm); color: var(--color-text-secondary);">Tingkat Kepercayaan Model: 87.5%</p>
        </div>

        <p><strong>Ringkasan Akademik:</strong></p>
        <p>Siswa menunjukkan pemahaman dasar pada mata pelajaran Pendidikan Agama dan Budi Pekerti, serta Bahasa Indonesia. Namun, pada mata pelajaran Matematika dan Seni Budaya, siswa memerlukan pendampingan lebih intensif untuk mencapai capaian pembelajaran yang ditargetkan.</p>

        <p style="margin-top: 1rem;"><strong>Ringkasan Portofolio:</strong></p>
        <p>Aspek konsentrasi siswa menunjukkan perkembangan yang stabil. Pada aspek motorik, siswa mampu melakukan aktivitas dasar dengan sedikit bantuan. Interaksi dan komunikasi masih perlu ditingkatkan, terutama dalam lingkungan kelompok besar.</p>

        <p style="margin-top: 1rem;"><strong>Rekomendasi:</strong></p>
        <ul style="padding-left: 1.25rem; margin-top: 0.5rem;">
            <li>Memberikan pendampingan individual pada mata pelajaran Matematika.</li>
            <li>Melatih interaksi sosial melalui kegiatan kelompok kecil secara bertahap.</li>
            <li>Melanjutkan program penguatan motorik halus.</li>
        </ul>
    </div>
</div>

<div class="mt-2">
    <x-button type="secondary" tag="a" :href="route('penilaian.index')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
        Kembali ke Penilaian
    </x-button>
</div>
@endsection
