@extends('layouts.app')

@section('title', 'Dashboard - SIPACA-SLB')

@section('content')
<div class="page-header">
    <h1 class="page-header__title">Selamat Datang, <span id="dashboard-user-name">Guru</span>!</h1>
    <p class="page-header__subtitle">Berikut ringkasan data penilaian siswa Anda.</p>
</div>

<div class="stat-grid">
    {{-- Total Siswa --}}
    <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <p class="stat-card__label">Total Siswa</p>
        <p class="stat-card__value" id="stat-total-siswa">-</p>
    </div>

    {{-- Penilaian Selesai --}}
    <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--success">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        </div>
        <p class="stat-card__label">Siswa Sudah Dinilai</p>
        <p class="stat-card__value" id="stat-penilaian-selesai">-</p>
    </div>

    {{-- Perlu Bimbingan --}}
    <div class="stat-card">
        <div class="stat-card__icon stat-card__icon--warning">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        </div>
        <p class="stat-card__label">Perlu Bimbingan</p>
        <p class="stat-card__value" id="stat-perlu-bimbingan">-</p>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', async function() {
        const userName = localStorage.getItem('user_name') || 'Guru';
        document.getElementById('dashboard-user-name').textContent = userName;

        const token = localStorage.getItem('jwt_token');
        if (!token) return;

        try {
            // Fetch students & assessments in parallel
            const [studentsRes, assessmentsRes] = await Promise.all([
                fetch(`${API_URL}/students`, { headers: { 'Authorization': `Bearer ${token}` } }),
                fetch(`${API_URL}/assessments`, { headers: { 'Authorization': `Bearer ${token}` } })
            ]);

            const studentsData = await studentsRes.json();
            const assessmentsData = await assessmentsRes.json();

            if (studentsData.success && assessmentsData.success) {
                const students = studentsData.data;
                const assessments = assessmentsData.data;

                // Total Siswa
                document.getElementById('stat-total-siswa').textContent = students.length;

                // Hitung siswa yang sudah dinilai (minimal memiliki 1 assessment)
                const assessedStudentIds = new Set(assessments.map(a => a.student_id));
                const alreadyAssessedCount = students.filter(s => assessedStudentIds.has(s.id)).length;
                document.getElementById('stat-penilaian-selesai').textContent = alreadyAssessedCount;

                // Hitung siswa yang status perkembangan terbarunya adalah "Perlu Bimbingan"
                let needsGuidanceCount = 0;
                students.forEach(student => {
                    const studentAssessments = assessments.filter(a => a.student_id === student.id);
                    if (studentAssessments.length > 0) {
                        // Sort by assessment ID descending to get the latest
                        studentAssessments.sort((a, b) => b.id - a.id);
                        const latest = studentAssessments[0];
                        if (latest.prediction && latest.prediction.development_status === 'Perlu Bimbingan') {
                            needsGuidanceCount++;
                        }
                    }
                });
                
                document.getElementById('stat-perlu-bimbingan').textContent = needsGuidanceCount;
            }
        } catch (err) {
            console.error('Failed to load dashboard statistics:', err);
        }
    });
</script>
@endpush
