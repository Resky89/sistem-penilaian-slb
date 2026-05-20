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
    <x-button type="primary" onclick="openModal('modal-create')">
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
                    <button class="btn btn--ghost" title="Edit"
                            onclick="openEditModal('{{ $siswa['nis'] }}', '{{ $siswa['nama'] }}', '{{ $siswa['jk'] }}', '{{ $siswa['disabilitas'] }}')">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352 4.352-1.321a2 2 0 0 0 .83-.497z"/></svg>
                    </button>
                    <button class="btn btn--danger" title="Hapus" style="padding: 0.5rem;"
                            onclick="openDeleteModal('{{ $siswa['nis'] }}', '{{ $siswa['nama'] }}')">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                    </button>
                </div>
            </td>
        </tr>
    @endforeach
</x-table>

{{-- Modal Tambah Siswa --}}
<x-modal id="modal-create" title="Tambah Siswa Baru">
    <form id="form-create-siswa">
        <x-input name="create-nis" label="NIS" placeholder="Masukkan NIS" required />
        <x-input name="create-nama" label="Nama Lengkap" placeholder="Masukkan nama lengkap" required />
        <div class="form-group">
            <label for="create-jk" class="form-label">Jenis Kelamin</label>
            <select id="create-jk" name="create-jk" class="form-select" required>
                <option value="" disabled selected>Pilih jenis kelamin</option>
                <option value="Laki-laki">Laki-laki</option>
                <option value="Perempuan">Perempuan</option>
            </select>
        </div>
        <div class="form-group">
            <label for="create-disabilitas" class="form-label">Jenis Disabilitas</label>
            <select id="create-disabilitas" name="create-disabilitas" class="form-select" required>
                <option value="" disabled selected>Pilih jenis disabilitas</option>
                <option value="Tunagrahita">Tunagrahita</option>
                <option value="Tunarungu">Tunarungu</option>
                <option value="Tunanetra">Tunanetra</option>
                <option value="Tunadaksa">Tunadaksa</option>
                <option value="Tunalaras">Tunalaras</option>
                <option value="Autisme">Autisme</option>
            </select>
        </div>
    </form>

    <x-slot name="footer">
        <x-button type="secondary" onclick="closeModal('modal-create')">Batal</x-button>
        <x-button type="primary" onclick="submitCreate()">Simpan</x-button>
    </x-slot>
</x-modal>

{{-- Modal Edit Siswa --}}
<x-modal id="modal-edit" title="Edit Data Siswa">
    <form id="form-edit-siswa">
        <x-input name="edit-nis" label="NIS" placeholder="Masukkan NIS" required />
        <x-input name="edit-nama" label="Nama Lengkap" placeholder="Masukkan nama lengkap" required />
        <div class="form-group">
            <label for="edit-jk" class="form-label">Jenis Kelamin</label>
            <select id="edit-jk" name="edit-jk" class="form-select" required>
                <option value="" disabled>Pilih jenis kelamin</option>
                <option value="Laki-laki">Laki-laki</option>
                <option value="Perempuan">Perempuan</option>
            </select>
        </div>
        <div class="form-group">
            <label for="edit-disabilitas" class="form-label">Jenis Disabilitas</label>
            <select id="edit-disabilitas" name="edit-disabilitas" class="form-select" required>
                <option value="" disabled>Pilih jenis disabilitas</option>
                <option value="Tunagrahita">Tunagrahita</option>
                <option value="Tunarungu">Tunarungu</option>
                <option value="Tunanetra">Tunanetra</option>
                <option value="Tunadaksa">Tunadaksa</option>
                <option value="Tunalaras">Tunalaras</option>
                <option value="Autisme">Autisme</option>
            </select>
        </div>
    </form>

    <x-slot name="footer">
        <x-button type="secondary" onclick="closeModal('modal-edit')">Batal</x-button>
        <x-button type="primary" onclick="submitEdit()">Perbarui</x-button>
    </x-slot>
</x-modal>

{{-- Modal Hapus Siswa --}}
<x-modal id="modal-delete" title="Hapus Siswa" size="sm">
    <div class="text-center">
        <div class="confirm-icon confirm-icon--danger">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
        </div>
        <p class="confirm-text">
            Apakah Anda yakin ingin menghapus data siswa
            <strong id="delete-nama-siswa"></strong>?
            Tindakan ini tidak dapat dibatalkan.
        </p>
    </div>

    <x-slot name="footer">
        <x-button type="secondary" onclick="closeModal('modal-delete')">Batal</x-button>
        <x-button type="danger" onclick="submitDelete()">Hapus</x-button>
    </x-slot>
</x-modal>
@endsection

@push('scripts')
<script>
    // --- Modal Helpers ---
    function openModal(id) {
        document.getElementById(id).classList.add('modal-overlay--active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(id) {
        document.getElementById(id).classList.remove('modal-overlay--active');
        document.body.style.overflow = '';
    }

    // Close modal on overlay click
    document.querySelectorAll('.modal-overlay').forEach(function (overlay) {
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) {
                closeModal(overlay.id);
            }
        });
    });

    // Close modal on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay--active').forEach(function (overlay) {
                closeModal(overlay.id);
            });
        }
    });

    // --- Edit Modal ---
    function openEditModal(nis, nama, jk, disabilitas) {
        document.getElementById('edit-nis').value = nis;
        document.getElementById('edit-nama').value = nama;
        document.getElementById('edit-jk').value = jk;
        document.getElementById('edit-disabilitas').value = disabilitas;
        openModal('modal-edit');
    }

    // --- Delete Modal ---
    let deleteTargetNis = '';

    function openDeleteModal(nis, nama) {
        deleteTargetNis = nis;
        document.getElementById('delete-nama-siswa').textContent = nama;
        openModal('modal-delete');
    }

    // --- Form Submissions (UI-only demo) ---
    function submitCreate() {
        var form = document.getElementById('form-create-siswa');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        showToast('success', 'Data siswa berhasil ditambahkan.');
        form.reset();
        closeModal('modal-create');
    }

    function submitEdit() {
        var form = document.getElementById('form-edit-siswa');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        showToast('success', 'Data siswa berhasil diperbarui.');
        closeModal('modal-edit');
    }

    function submitDelete() {
        showToast('success', 'Data siswa NIS ' + deleteTargetNis + ' berhasil dihapus.');
        closeModal('modal-delete');
    }
</script>
@endpush
