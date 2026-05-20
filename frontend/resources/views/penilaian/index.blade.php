@extends('layouts.app')

@section('title', 'Penilaian - SIPACA-SLB')

@section('content')
<div class="page-header">
    <h1 class="page-header__title">Penilaian</h1>
</div>

{{-- Action Bar --}}
<div class="action-bar">
    <div class="action-bar__search">
        <span class="action-bar__search-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </span>
        <input type="text" class="form-input" placeholder="Cari siswa..." id="search-penilaian">
    </div>
    <x-button type="primary" tag="a" :href="route('penilaian.form')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        Tambah
    </x-button>
</div>

{{-- Tabel Penilaian --}}
<x-table :headers="['NIS', 'Nama', 'Jenis Kelamin', 'Disabilitas', 'Aksi']">
    @php
        $dummyPenilaian = [
            ['nis' => '1234567890', 'nama' => 'Jhon Doe', 'jk' => 'Laki-laki', 'disabilitas' => 'Tunagrahita'],
            ['nis' => '1234567891', 'nama' => 'Jane Doe', 'jk' => 'Perempuan', 'disabilitas' => 'Tunagrahita'],
        ];
    @endphp

    @foreach($dummyPenilaian as $item)
        <tr>
            <td>{{ $item['nis'] }}</td>
            <td>{{ $item['nama'] }}</td>
            <td>{{ $item['jk'] }}</td>
            <td>{{ $item['disabilitas'] }}</td>
            <td>
                <div class="table__actions">
                    {{-- Lihat Detail --}}
                    <a href="{{ route('penilaian.hasil') }}" class="btn btn--ghost" title="Lihat Hasil">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
                    </a>
                </div>
            </td>
        </tr>
    @endforeach
</x-table>
@endsection
