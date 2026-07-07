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
        Tambah Penilaian
    </x-button>
</div>

{{-- Tabel Penilaian --}}
<x-table :headers="['NIS', 'Nama Siswa', 'Ketunaan', 'Status Perkembangan', 'Aksi']">
    <tbody id="penilaian-table-body">
        <tr>
            <td colspan="5" class="text-center">Memuat data penilaian...</td>
        </tr>
    </tbody>
</x-table>

{{-- Modal Hapus Penilaian --}}
<x-modal id="modal-delete-assessment" title="Hapus Penilaian" size="sm">
    <div class="text-center">
        <div class="confirm-icon confirm-icon--danger">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
        </div>
        <p class="confirm-text">
            Apakah Anda yakin ingin menghapus data penilaian terakhir untuk siswa
            <strong id="delete-nama-siswa"></strong>?
            Tindakan ini tidak dapat dibatalkan.
        </p>
    </div>

    <x-slot name="footer">
        <x-button type="secondary" onclick="closeModal('modal-delete-assessment')">Batal</x-button>
        <x-button type="danger" onclick="submitDeleteAssessment()">Hapus</x-button>
    </x-slot>
</x-modal>
@endsection

@push('scripts')
<script>
    let allStudents = [];
    let allAssessments = [];

    // --- Modal Helpers ---
    function openModal(id) {
        const el = document.getElementById(id);
        if (el) {
            el.classList.add('modal-overlay--active');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeModal(id) {
        const el = document.getElementById(id);
        if (el) {
            el.classList.remove('modal-overlay--active');
            document.body.style.overflow = '';
        }
    }

    // Close modal on overlay click
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeModal(this.id);
                }
            });
        });
    });

    async function loadPenilaianData() {
        const token = localStorage.getItem('jwt_token');
        const tableBody = document.getElementById('penilaian-table-body');

        try {
            // Fetch students & assessments in parallel
            const [studentsRes, assessmentsRes] = await Promise.all([
                fetch(`${API_URL}/students`, { headers: { 'Authorization': `Bearer ${token}` } }),
                fetch(`${API_URL}/assessments`, { headers: { 'Authorization': `Bearer ${token}` } })
            ]);

            const studentsData = await studentsRes.json();
            const assessmentsData = await assessmentsRes.json();

            if (studentsData.success && assessmentsData.success) {
                allStudents = studentsData.data;
                allAssessments = assessmentsData.data;
                renderPenilaianTable();
            } else {
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Gagal memuat data dari server.</td></tr>`;
            }
        } catch (err) {
            console.error(err);
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Gagal menghubungi server API.</td></tr>`;
        }
    }

    function renderPenilaianTable() {
        const tableBody = document.getElementById('penilaian-table-body');
        if (allStudents.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Tidak ada data siswa. Silakan tambahkan siswa terlebih dahulu di menu Data Siswa.</td></tr>';
            return;
        }

        tableBody.innerHTML = '';
        allStudents.forEach(student => {
            // Find latest assessment for this student
            const studentAssessments = allAssessments.filter(a => a.student_id === student.id);
            // Sort by date or id descending
            studentAssessments.sort((a, b) => b.id - a.id);
            
            const latestAssessment = studentAssessments[0];
            let statusBadge = '<span class="badge badge--gray">Belum Dinilai</span>';
            let actionButtons = '';

            if (latestAssessment && latestAssessment.prediction) {
                const status = latestAssessment.prediction.development_status;
                let badgeClass = 'badge--gray';
                
                if (status === 'Baik') {
                    badgeClass = 'badge--success';
                } else if (status === 'Cukup') {
                    badgeClass = 'badge--primary';
                } else if (status === 'Perlu Bimbingan') {
                    badgeClass = 'badge--warning';
                }

                statusBadge = `<span class="badge ${badgeClass}">${escapeHtml(status)}</span>`;
                
                // Button to view details
                actionButtons += `
                    <a href="${'{{ route("penilaian.hasil") }}'}?student_id=${student.id}" class="btn btn--ghost" title="Lihat Hasil Klasifikasi" style="padding: 0.5rem;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/></svg>
                    </a>
                `;

                // Button to edit
                actionButtons += `
                    <a href="${'{{ route("penilaian.form") }}'}?edit_id=${latestAssessment.id}" class="btn btn--ghost" title="Edit Penilaian Terakhir" style="padding: 0.5rem; color: #1d4ed8;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
                    </a>
                `;

                // Button to delete
                actionButtons += `
                    <button onclick="confirmDeleteAssessment(${latestAssessment.id}, ${student.id})" class="btn btn--ghost" title="Hapus Penilaian Terakhir" style="padding: 0.5rem; color: var(--color-danger);">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                    </button>
                `;
            }

            // Add a button to perform a new assessment only if student has not been assessed yet
            if (!latestAssessment) {
                actionButtons += `
                    <a href="${'{{ route("penilaian.form") }}'}?student_id=${student.id}" class="btn btn--ghost" title="Input Penilaian Baru" style="padding: 0.5rem; color: var(--color-primary);">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14"/><path d="M5 12h14"/></svg>
                    </a>
                `;
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${escapeHtml(student.student_number)}</td>
                <td>${escapeHtml(student.full_name)}</td>
                <td>${escapeHtml(student.disability_category)}</td>
                <td>${statusBadge}</td>
                <td>
                    <div class="table__actions">
                        ${actionButtons}
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }

    // --- Search Helper ---
    document.getElementById('search-penilaian').addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase();
        const filtered = allStudents.filter(student => 
            student.full_name.toLowerCase().includes(query) || 
            student.student_number.toLowerCase().includes(query) ||
            student.disability_category.toLowerCase().includes(query)
        );
        
        // Temporarily override allStudents to render filtered list
        const originalAllStudents = allStudents;
        allStudents = filtered;
        renderPenilaianTable();
        allStudents = originalAllStudents;
    });

    let currentDeleteAssessmentId = null;

    function confirmDeleteAssessment(id, studentId) {
        currentDeleteAssessmentId = id;
        const student = allStudents.find(s => s.id === studentId);
        const studentName = student ? student.full_name : '';
        
        const deleteNameEl = document.getElementById('delete-nama-siswa');
        if (deleteNameEl) {
            deleteNameEl.textContent = studentName;
        }
        
        openModal('modal-delete-assessment');
    }

    async function submitDeleteAssessment() {
        if (!currentDeleteAssessmentId) return;
        
        const token = localStorage.getItem('jwt_token');
        try {
            const res = await fetch(`${API_URL}/assessments/${currentDeleteAssessmentId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await res.json();
            
            closeModal('modal-delete-assessment');
            
            if (data.success) {
                showToast('success', 'Penilaian berhasil dihapus!');
                loadPenilaianData();
            } else {
                showToast('error', data.message || 'Gagal menghapus penilaian.');
            }
        } catch (err) {
            console.error(err);
            closeModal('modal-delete-assessment');
            showToast('error', 'Terjadi kesalahan jaringan.');
        } finally {
            currentDeleteAssessmentId = null;
        }
    }

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

    document.addEventListener('DOMContentLoaded', loadPenilaianData);
</script>
@endpush
