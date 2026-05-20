@extends('layouts.app')

@section('title', 'Form Penilaian - SIPACA-SLB')

@section('content')
<div class="page-header">
    <h1 class="page-header__title">Form Penilaian</h1>
</div>

<form action="#" method="POST">
    @csrf

    {{-- Top Action: Pilih Siswa & Simpan --}}
    <div class="form-top-action">
        <div class="form-top-action__select">
            <select name="siswa_id" class="form-select" id="pilih-siswa">
                <option value="">Pilih Siswa</option>
                <option value="1">Jhon Doe - 1234567890</option>
                <option value="2">Jane Doe - 1234567891</option>
                <option value="3">Ahmad Fauzi - 1234567892</option>
                <option value="4">Siti Aisyah - 1234567893</option>
            </select>
        </div>
        <button type="submit" class="btn btn--primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/><path d="M7 3v4a1 1 0 0 0 1 1h7"/></svg>
            Simpan
        </button>
    </div>

    {{-- Tabs: Akademik & Portofolio --}}
    <div class="tabs" role="tablist">
        <button type="button" class="tabs__item tabs__item--active" data-tab="akademik" role="tab" aria-selected="true">Akademik</button>
        <button type="button" class="tabs__item" data-tab="portofolio" role="tab" aria-selected="false">Portofolio</button>
    </div>

    {{-- Tab Content: Akademik --}}
    <div class="tab-content tab-content--active" id="tab-akademik" role="tabpanel">
        @php
            $mataPelajaran = [
                'Pendidikan Agama dan Budi Pekerti',
                'Pendidikan Pancasila dan Kewarganegaraan',
                'Bahasa Indonesia',
                'Matematika',
                'Seni Budaya dan Prakarya',
            ];
        @endphp

        @foreach($mataPelajaran as $index => $mapel)
            <div class="subject-section">
                <h3 class="subject-section__title">{{ $mapel }}</h3>
                <x-input
                    name="akademik_nilai_{{ $index }}"
                    placeholder="Masukkan Nilai Akhir"
                />
                <x-textarea
                    name="akademik_capaian_{{ $index }}"
                    placeholder="Masukkan capaian pembelajaran"
                    :rows="3"
                />
            </div>
        @endforeach
    </div>

    {{-- Tab Content: Portofolio --}}
    <div class="tab-content" id="tab-portofolio" role="tabpanel">
        @php
            $aspekPortofolio = [
                'Konsentrasi',
                'Motorik',
                'Interaksi dan Komunikasi',
                'Perawatan Diri',
                'Kemampuan Belajar',
            ];
        @endphp

        @foreach($aspekPortofolio as $index => $aspek)
            <div class="subject-section">
                <h3 class="subject-section__title">{{ $aspek }}</h3>
                <x-textarea
                    name="portofolio_deskripsi_{{ $index }}"
                    placeholder="Masukkan deskripsi perkembangan"
                    :rows="4"
                />
            </div>
        @endforeach
    </div>
</form>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', function () {
        const tabs = document.querySelectorAll('.tabs__item');
        const contents = document.querySelectorAll('.tab-content');

        tabs.forEach(function (tab) {
            tab.addEventListener('click', function () {
                const target = this.getAttribute('data-tab');

                tabs.forEach(function (t) {
                    t.classList.remove('tabs__item--active');
                    t.setAttribute('aria-selected', 'false');
                });
                contents.forEach(function (c) {
                    c.classList.remove('tab-content--active');
                });

                this.classList.add('tabs__item--active');
                this.setAttribute('aria-selected', 'true');
                document.getElementById('tab-' + target).classList.add('tab-content--active');
            });
        });
    });
</script>
@endpush
