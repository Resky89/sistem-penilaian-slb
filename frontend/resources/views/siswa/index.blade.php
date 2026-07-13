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
        Tambah Siswa
    </x-button>
</div>

{{-- Tabel Data Siswa --}}
<x-table :headers="['NIS', 'Nama', 'Kelas', 'Semester', 'Ketunaan', 'Sekolah', 'Tahun Ajaran', 'Aksi']">
    <tbody id="siswa-table-body">
        <tr>
            <td colspan="8" class="text-center">Memuat data siswa...</td>
        </tr>
    </tbody>
</x-table>

{{-- Modal Tambah Siswa --}}
<x-modal id="modal-create" title="Tambah Siswa Baru">
    <form id="form-create-siswa">
        <div class="alert-general" style="display: none; margin-bottom: 1rem; padding: 0.75rem; border-radius: var(--radius-md); background-color: #fef2f2; border: 1px solid #fecaca; color: var(--color-danger); font-size: var(--font-size-sm); font-weight: 500;"></div>

        <x-input name="create-nis" label="NIS" placeholder="Masukkan NIS" required />
        <x-input name="create-nama" label="Nama Lengkap" placeholder="Masukkan nama lengkap" required />
        <x-input name="create-class" label="Tingkat Kelas" placeholder="Masukkan tingkat kelas (contoh: IV-A)" required />
        <div class="form-group">
            <label for="create-semester" class="form-label">Semester Aktif</label>
            <select id="create-semester" name="create-semester" class="form-select" required>
                <option value="" disabled selected>Pilih semester</option>
                <option value="Odd">Ganjil</option>
                <option value="Even">Genap</option>
            </select>
            <div class="invalid-feedback" id="error-create-semester" style="display: none; font-size: 0.8rem; color: var(--color-danger); margin-top: 4px; font-weight: 500;"></div>
        </div>
        <div class="form-group">
            <label for="create-disabilitas" class="form-label">Jenis Ketunaan</label>
            <select id="create-disabilitas" name="create-disabilitas" class="form-select" required>
                <option value="" disabled selected>Pilih ketunaan</option>
                <option value="Tunagrahita">Tunagrahita</option>
                <option value="Autisme">Autisme</option>
            </select>
            <div class="invalid-feedback" id="error-create-disabilitas" style="display: none; font-size: 0.8rem; color: var(--color-danger); margin-top: 4px; font-weight: 500;"></div>
        </div>
        <x-input name="create-school" label="Nama Sekolah" placeholder="Masukkan nama sekolah" required />
        <x-input name="create-academic-year" label="Tahun Ajaran" placeholder="Contoh: 2025/2026" required />
    </form>

    <x-slot name="footer">
        <x-button type="secondary" onclick="closeModal('modal-create')">Batal</x-button>
        <x-button type="primary" onclick="submitCreate()">Simpan</x-button>
    </x-slot>
</x-modal>

{{-- Modal Edit Siswa --}}
<x-modal id="modal-edit" title="Edit Data Siswa">
    <form id="form-edit-siswa">
        <div class="alert-general" style="display: none; margin-bottom: 1rem; padding: 0.75rem; border-radius: var(--radius-md); background-color: #fef2f2; border: 1px solid #fecaca; color: var(--color-danger); font-size: var(--font-size-sm); font-weight: 500;"></div>

        <x-input name="edit-nis" label="NIS" placeholder="Masukkan NIS" required />
        <x-input name="edit-nama" label="Nama Lengkap" placeholder="Masukkan nama lengkap" required />
        <x-input name="edit-class" label="Tingkat Kelas" placeholder="Masukkan tingkat kelas" required />
        <div class="form-group">
            <label for="edit-semester" class="form-label">Semester Aktif</label>
            <select id="edit-semester" name="edit-semester" class="form-select" required>
                <option value="" disabled>Pilih semester</option>
                <option value="Odd">Ganjil</option>
                <option value="Even">Genap</option>
            </select>
            <div class="invalid-feedback" id="error-edit-semester" style="display: none; font-size: 0.8rem; color: var(--color-danger); margin-top: 4px; font-weight: 500;"></div>
        </div>
        <div class="form-group">
            <label for="edit-disabilitas" class="form-label">Jenis Ketunaan</label>
            <select id="edit-disabilitas" name="edit-disabilitas" class="form-select" required>
                <option value="" disabled>Pilih ketunaan</option>
                <option value="Tunagrahita">Tunagrahita</option>
                <option value="Autisme">Autisme</option>
            </select>
            <div class="invalid-feedback" id="error-edit-disabilitas" style="display: none; font-size: 0.8rem; color: var(--color-danger); margin-top: 4px; font-weight: 500;"></div>
        </div>
        <x-input name="edit-school" label="Nama Sekolah" placeholder="Masukkan nama sekolah" required />
        <x-input name="edit-academic-year" label="Tahun Ajaran" placeholder="Contoh: 2025/2026" required />
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
            Semua riwayat transaksi penilaian terkait siswa ini akan ikut terhapus secara permanen.
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
    let allStudents = [];
    let currentEditStudentId = null;
    let currentDeleteStudentId = null;

    // --- Modal Helpers ---
    function openModal(id) {
        document.getElementById(id).classList.add('modal-overlay--active');
        document.body.style.overflow = 'hidden';
        if (id === 'modal-create') {
            clearFormErrors('form-create-siswa');
        } else if (id === 'modal-edit') {
            clearFormErrors('form-edit-siswa');
        }
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

    // --- Load Students from API ---
    async function loadStudents() {
        const token = localStorage.getItem('jwt_token');
        const tableBody = document.getElementById('siswa-table-body');
        
        try {
            const res = await fetch(`${API_URL}/students`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            
            if (data.success) {
                allStudents = data.data;
                renderStudents(allStudents);
            } else {
                tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">${data.message || 'Gagal memuat data'}</td></tr>`;
            }
        } catch (err) {
            console.error(err);
            tableBody.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Gagal menghubungi server API.</td></tr>`;
        }
    }

    // --- Render Students to Table ---
    function renderStudents(students) {
        const tableBody = document.getElementById('siswa-table-body');
        if (students.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8" class="text-center">Tidak ada data siswa ditemukan.</td></tr>';
            return;
        }

        tableBody.innerHTML = '';
        students.forEach(student => {
            const semLabel = student.semester === 'Odd' ? 'Ganjil' : 'Genap';
            const tr = document.createElement('tr');
            
            tr.innerHTML = `
                <td>${escapeHtml(student.student_number)}</td>
                <td><strong>${escapeHtml(student.full_name)}</strong></td>
                <td>${escapeHtml(student.class_level)}</td>
                <td>${semLabel}</td>
                <td>${escapeHtml(student.disability_category)}</td>
                <td>${escapeHtml(student.school_name)}</td>
                <td>${escapeHtml(student.academic_year)}</td>
                <td>
                    <div class="table__actions">
                        <button class="btn btn--ghost" title="Edit"
                                onclick="openEditModal(${student.id})">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352 4.352-1.321a2 2 0 0 0 .83-.497z"/></svg>
                        </button>
                        <button class="btn btn--danger" title="Hapus" style="padding: 0.5rem;"
                                onclick="openDeleteModal(${student.id})">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                        </button>
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // --- Search Helper ---
    document.getElementById('search-siswa').addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();
        const filtered = allStudents.filter(student => 
            student.full_name.toLowerCase().includes(query) || 
            student.student_number.toLowerCase().includes(query) ||
            student.disability_category.toLowerCase().includes(query) ||
            student.school_name.toLowerCase().includes(query)
        );
        renderStudents(filtered);
    });

    // --- Form Submissions ---
    async function submitCreate() {
        const form = document.getElementById('form-create-siswa');
        clearFormErrors(form);

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const token = localStorage.getItem('jwt_token');
        const payload = {
            student_number: document.getElementById('create-nis').value,
            full_name: document.getElementById('create-nama').value,
            class_level: document.getElementById('create-class').value,
            semester: document.getElementById('create-semester').value,
            disability_category: document.getElementById('create-disabilitas').value,
            school_name: document.getElementById('create-school').value,
            academic_year: document.getElementById('create-academic-year').value
        };

        const mapping = {
            student_number: 'create-nis',
            full_name: 'create-nama',
            class_level: 'create-class',
            semester: 'create-semester',
            disability_category: 'create-disabilitas',
            school_name: 'create-school',
            academic_year: 'create-academic-year'
        };

        try {
            const res = await fetch(`${API_URL}/students`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                showToast('success', 'Data siswa berhasil ditambahkan.');
                form.reset();
                closeModal('modal-create');
                loadStudents();
            } else {
                showFormErrors(form, data, mapping);
                showToast('error', data.message || 'Gagal menambahkan siswa.');
            }
        } catch (err) {
            console.error(err);
            showFormErrors(form, { message: 'Terjadi kesalahan jaringan.' });
            showToast('error', 'Terjadi kesalahan jaringan.');
        }
    }

    // --- Open Edit Modal ---
    function openEditModal(id) {
        const student = allStudents.find(s => s.id === id);
        if (!student) return;

        currentEditStudentId = id;
        document.getElementById('edit-nis').value = student.student_number;
        document.getElementById('edit-nama').value = student.full_name;
        document.getElementById('edit-class').value = student.class_level;
        document.getElementById('edit-semester').value = student.semester;
        document.getElementById('edit-disabilitas').value = student.disability_category;
        document.getElementById('edit-school').value = student.school_name;
        document.getElementById('edit-academic-year').value = student.academic_year;
        
        openModal('modal-edit');
    }

    // --- Submit Edit ---
    async function submitEdit() {
        const form = document.getElementById('form-edit-siswa');
        clearFormErrors(form);

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const token = localStorage.getItem('jwt_token');
        const payload = {
            student_number: document.getElementById('edit-nis').value,
            full_name: document.getElementById('edit-nama').value,
            class_level: document.getElementById('edit-class').value,
            semester: document.getElementById('edit-semester').value,
            disability_category: document.getElementById('edit-disabilitas').value,
            school_name: document.getElementById('edit-school').value,
            academic_year: document.getElementById('edit-academic-year').value
        };

        const mapping = {
            student_number: 'edit-nis',
            full_name: 'edit-nama',
            class_level: 'edit-class',
            semester: 'edit-semester',
            disability_category: 'edit-disabilitas',
            school_name: 'edit-school',
            academic_year: 'edit-academic-year'
        };

        try {
            const res = await fetch(`${API_URL}/students/${currentEditStudentId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                showToast('success', 'Data siswa berhasil diperbarui.');
                closeModal('modal-edit');
                loadStudents();
            } else {
                showFormErrors(form, data, mapping);
                showToast('error', data.message || 'Gagal memperbarui data.');
            }
        } catch (err) {
            console.error(err);
            showFormErrors(form, { message: 'Terjadi kesalahan jaringan.' });
            showToast('error', 'Terjadi kesalahan jaringan.');
        }
    }

    // --- Open Delete Modal ---
    function openDeleteModal(id) {
        const student = allStudents.find(s => s.id === id);
        if (!student) return;

        currentDeleteStudentId = id;
        document.getElementById('delete-nama-siswa').textContent = student.full_name;
        openModal('modal-delete');
    }

    // --- Submit Delete ---
    async function submitDelete() {
        const token = localStorage.getItem('jwt_token');
        try {
            const res = await fetch(`${API_URL}/students/${currentDeleteStudentId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (data.success) {
                showToast('success', 'Data siswa berhasil dihapus.');
                closeModal('modal-delete');
                loadStudents();
            } else {
                showToast('error', data.message || 'Gagal menghapus data.');
            }
        } catch (err) {
            console.error(err);
            showToast('error', 'Terjadi kesalahan jaringan.');
        }
    }

    // --- Helpers ---
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Inisialisasi
    document.addEventListener('DOMContentLoaded', loadStudents);
</script>
@endpush
