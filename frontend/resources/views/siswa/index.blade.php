@extends('layouts.app')

@section('title', 'Data Siswa - SIPACA-SLB')

@section('content')
<div class="page-header">
    <h1 class="page-header__title">Data Siswa</h1>
</div>

{{-- Action Bar --}}
<div class="action-bar">
    <div class="action-bar__search">
        <span class="action-bar__search-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </span>
        <input type="text" class="form-input" placeholder="Cari siswa..." id="search-siswa">
    </div>
    <x-button type="primary" tag="a" :href="'#'">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        Tambah
    </x-button>
</div>

{{-- Tabel Data Siswa --}}
<x-table :headers="['NIS', 'Nama', 'Jenis Kelamin', 'Disabilitas', 'Aksi']">
    @php
        $dummySiswa = [
            ['nis' => '1234567890', 'nama' => 'Jhon Doe', 'jk' => 'Laki-laki', 'disabilitas' => 'Tunagrahita'],
            ['nis' => '1234567891', 'nama' => 'Jane Doe', 'jk' => 'Perempuan', 'disabilitas' => 'Tunagrahita'],
            ['nis' => '1234567892', 'nama' => 'Ahmad Fauzi', 'jk' => 'Laki-laki', 'disabilitas' => 'Tunarungu'],
            ['nis' => '1234567893', 'nama' => 'Siti Aisyah', 'jk' => 'Perempuan', 'disabilitas' => 'Tunanetra'],
        ];
    @endphp

    @foreach($dummySiswa as $siswa)
        <tr>
            <td>{{ $siswa['nis'] }}</td>
            <td>{{ $siswa['nama'] }}</td>
            <td>{{ $siswa['jk'] }}</td>
            <td>{{ $siswa['disabilitas'] }}</td>
            <td>
                <div class="table__actions">
                    {{-- Edit --}}
                    <button class="btn btn--ghost" title="Edit">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352 4.352-1.321a2 2 0 0 0 .83-.497z"/></svg>
                    </button>
                    {{-- Hapus --}}
                    <button class="btn btn--danger" title="Hapus" style="padding: 0.5rem;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                    </button>
                </div>
            </td>
        </tr>
    @endforeach
</x-table>
@endsection
