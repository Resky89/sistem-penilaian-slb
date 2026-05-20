@extends('layouts.app')

@section('title', 'Dashboard - SIPACA-SLB')

@section('content')
<div class="page-header">
    <h1 class="page-header__title">Selamat Datang, Guru!</h1>
    <p class="page-header__subtitle">Berikut ringkasan data penilaian siswa Anda.</p>
</div>

<div class="stat-grid">
    {{-- Total Siswa --}}
    <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <p class="stat-card__label">Total Siswa</p>
        <p class="stat-card__value">24</p>
    </div>

    {{-- Penilaian Selesai --}}
    <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--success">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <p class="stat-card__label">Penilaian Selesai</p>
        <p class="stat-card__value">18</p>
    </div>

    {{-- Perlu Bimbingan --}}
    <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--warning">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        </div>
        <p class="stat-card__label">Perlu Bimbingan</p>
        <p class="stat-card__value">6</p>
    </div>
</div>
@endsection
