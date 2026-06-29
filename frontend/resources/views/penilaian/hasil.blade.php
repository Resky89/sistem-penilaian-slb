@extends('layouts.app')

@section('title', 'Hasil Klasifikasi - SIPACA-SLB')

@section('content')
<div class="page-header">
    <h1 class="page-header__title">Hasil Klasifikasi & Analisis Siswa</h1>
</div>

<div id="loading-container" class="text-center" style="padding: 3rem 0;">
    <p style="color: var(--color-text-secondary);">Memuat hasil klasifikasi dan analisis SHAP...</p>
</div>

<div id="content-container" style="display: none;">
    {{-- Data Siswa --}}
    <div class="info-box">
        <h2 class="info-box__title">Data Siswa</h2>
        <div class="info-box__grid">
            <div class="info-box__item">
                <span class="info-box__label">NIS:</span>
                <span class="info-box__value" id="siswa-nis">-</span>
            </div>
            <div class="info-box__item">
                <span class="info-box__label">Nama:</span>
                <span class="info-box__value" id="siswa-nama">-</span>
            </div>
            <div class="info-box__item">
                <span class="info-box__label">Kelas:</span>
                <span class="info-box__value" id="siswa-kelas">-</span>
            </div>
            <div class="info-box__item">
                <span class="info-box__label">Semester:</span>
                <span class="info-box__value" id="siswa-semester">-</span>
            </div>
            <div class="info-box__item">
                <span class="info-box__label">Ketunaan:</span>
                <span class="info-box__value" id="siswa-ketunaan">-</span>
            </div>
            <div class="info-box__item">
                <span class="info-box__label">Nama Sekolah:</span>
                <span class="info-box__value" id="siswa-sekolah">-</span>
            </div>
            <div class="info-box__item">
                <span class="info-box__label">Tahun Ajaran:</span>
                <span class="info-box__value" id="siswa-tahun-ajaran">-</span>
            </div>
        </div>
    </div>

    {{-- Detail Nilai Akademik (Mata Pelajaran) & Penilaian SHAP --}}
    <div class="info-box mt-2">
        <h2 class="info-box__title">Hasil Perkembangan Mata Pelajaran (Rapor)</h2>
        <p style="color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-bottom: 1.5rem; line-height: 1.5;">
            Tabel di bawah menampilkan status perkembangan yang diprediksi oleh model Random Forest untuk setiap mata pelajaran, 
            lengkap dengan penjelasan kontribusi fitur (SHAP) yang mendasari keputusan model.
        </p>
        <div class="table-wrapper">
            <table class="table">
                <thead>
                    <tr>
                        <th style="width: 220px;">Mata Pelajaran</th>
                        <th style="width: 80px; text-align: center;">Nilai</th>
                        <th style="width: 150px; text-align: center;">Status Perkembangan</th>
                        <th>Penjelasan SHAP &amp; Deskripsi</th>
                    </tr>
                </thead>
                <tbody id="academic-scores-body">
                    <!-- Rendered dynamically -->
                </tbody>
            </table>
        </div>
    </div>

    {{-- Detail Portofolio & Penilaian SHAP --}}
    <div class="info-box mt-2">
        <h2 class="info-box__title">Hasil Perkembangan Aspek Portofolio</h2>
        <p style="color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-bottom: 1.5rem; line-height: 1.5;">
            Hasil analisis dan klasifikasi status perkembangan pada aspek portofolio siswa beserta penjelasan kontribusi fiturnya.
        </p>
        <div id="portfolio-narrative-container" style="display: flex; flex-direction: column; gap: 1.25rem;">
            <!-- Rendered dynamically -->
        </div>
    </div>
</div>

<div class="mt-2" style="display: flex; gap: 1rem;">
    <x-button type="secondary" tag="a" :href="route('penilaian.index')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
        Kembali ke Penilaian
    </x-button>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', async function () {
        const token = localStorage.getItem('jwt_token');
        const urlParams = new URLSearchParams(window.location.search);
        const studentId = urlParams.get('student_id');

        let assessment = null;

        // Cek cache sessionStorage
        const cachedResult = sessionStorage.getItem('latest_assessment_result');
        if (cachedResult) {
            const parsed = JSON.parse(cachedResult);
            if (!studentId || parseInt(studentId) === parsed.student_id) {
                assessment = parsed;
                sessionStorage.removeItem('latest_assessment_result');
            }
        }

        // Fetch dari API
        if (!assessment && studentId) {
            try {
                const res = await fetch(`${API_URL}/assessments/student/${studentId}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await res.json();
                if (data.success && data.data && data.data.length > 0) {
                    data.data.sort((a, b) => b.id - a.id);
                    assessment = data.data[0];
                }
            } catch (err) {
                console.error(err);
            }
        }

        if (!assessment) {
            document.getElementById('loading-container').innerHTML = `
                <p class="text-danger">Data penilaian tidak ditemukan. Pastikan siswa telah dinilai terlebih dahulu.</p>
            `;
            return;
        }

        document.getElementById('loading-container').style.display = 'none';
        document.getElementById('content-container').style.display = 'block';

        // --- Render Info Siswa ---
        const student = assessment.student;
        document.getElementById('siswa-nis').textContent = student.student_number;
        document.getElementById('siswa-nama').textContent = student.full_name;
        document.getElementById('siswa-kelas').textContent = student.class_level;
        document.getElementById('siswa-semester').textContent = assessment.semester === 'Odd' ? 'Ganjil' : 'Genap';
        document.getElementById('siswa-ketunaan').textContent = student.disability_category;
        document.getElementById('siswa-sekolah').textContent = student.school_name;
        document.getElementById('siswa-tahun-ajaran').textContent = student.academic_year;

        // --- Ambil Hasil Prediksi Individu dari SHAP Explanation ---
        const pred = assessment.prediction;
        const individualPredictions = (pred && pred.shap_explanation && pred.shap_explanation.predictions) 
            ? pred.shap_explanation.predictions 
            : [];

        // Helper: Kembalikan class CSS dan label untuk badge status
        function getStatusBadge(status) {
            let style = "display: inline-block; font-size: 11px; font-weight: 700; padding: 0.25rem 0.625rem; border-radius: 9999px; text-align: center;";
            if (status === 'Baik') {
                style += "background-color: #dcfce7; color: #15803d; border: 1px solid #bbf7d0;";
            } else if (status === 'Cukup') {
                style += "background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;";
            } else if (status === 'Perlu Bimbingan') {
                style += "background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a;";
            } else {
                style += "background-color: #f1f5f9; color: #475569; border: 1px solid #e2e8f0;";
            }
            return `<span style="${style}">${escapeHtml(status || 'N/A')}</span>`;
        }

        // Helper: Render Mini SHAP Chart
        function renderShapChart(shap) {
            if (!shap || !shap.features || shap.features.length === 0) {
                return `<p style="font-size: var(--font-size-xs); color: var(--color-text-muted); margin-top: 0.5rem; font-style: italic;">Tidak ada kontribusi fitur SHAP signifikan.</p>`;
            }

            let html = `
            <div style="margin-top: 0.75rem; border-top: 1px dashed #e2e8f0; padding-top: 0.75rem;">
                <span style="font-size: var(--font-size-xs); font-weight: 600; color: var(--color-text-secondary); display: block; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">xAI SHAP - Kontribusi Fitur:</span>
                <div style="display: flex; flex-direction: column; gap: 0.375rem;">
            `;

            const maxVal = Math.max(...shap.values.map(Math.abs), 0.01);

            shap.features.forEach((feature, idx) => {
                const val = shap.values[idx];
                const absPct = Math.min((Math.abs(val) / maxVal) * 50, 50); // Maksimal 50% dari tengah

                html += `
                <div style="display: flex; align-items: center; min-height: 24px;">
                    <div style="width: 140px; font-size: 11px; font-weight: 500; color: var(--color-text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(feature)}">
                        ${escapeHtml(feature)}
                    </div>
                    <div style="flex: 1; position: relative; height: 10px; background: #f1f5f9; border-radius: 2px; overflow: hidden; margin: 0 0.5rem;">
                        <div style="position: absolute; left: 50%; top: 0; bottom: 0; width: 1px; background: #cbd5e1;"></div>
                        ${val >= 0
                            ? `<div style="position: absolute; left: 50%; width: ${absPct}%; height: 100%; background: #10b981; border-radius: 0 2px 2px 0;"></div>`
                            : `<div style="position: absolute; right: 50%; width: ${absPct}%; height: 100%; background: #ef4444; border-radius: 2px 0 0 2px;"></div>`
                        }
                    </div>
                    <div style="width: 55px; text-align: right; font-size: 10px; font-family: monospace; font-weight: 600; color: var(--color-text-secondary);">
                        ${val >= 0 ? '+' : ''}${val.toFixed(4)}
                    </div>
                </div>
                `;
            });

            html += `
                </div>
            </div>
            `;
            return html;
        }

        // --- Render Tabel Akademik ---
        const academicBody = document.getElementById('academic-scores-body');
        academicBody.innerHTML = '';
        
        const academicPredictions = individualPredictions.filter(p => 
            p.subject !== "Ekskul Pramuka" &&
            p.subject !== "Konsentrasi" &&
            p.subject !== "Motorik" &&
            p.subject !== "Interaksi dan Komunikasi" &&
            p.subject !== "Emosi" &&
            p.subject !== "Bina Diri" &&
            p.subject !== "Membaca" &&
            p.subject !== "Menulis" &&
            p.subject !== "Berhitung"
        );

        // Tambahkan Ekskul Pramuka ke Rapor/Akademik
        const pramukaPred = individualPredictions.find(p => p.subject === "Ekskul Pramuka");
        if (pramukaPred) {
            academicPredictions.push(pramukaPred);
        }

        if (academicPredictions.length > 0) {
            academicPredictions.forEach(p => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 600; vertical-align: top; padding-top: 0.875rem;">${escapeHtml(p.subject)}</td>
                    <td style="text-align: center; font-weight: 700; vertical-align: top; padding-top: 0.875rem;">${p.score !== null && p.score !== undefined ? p.score : '-'}</td>
                    <td style="text-align: center; vertical-align: top; padding-top: 0.875rem;">${getStatusBadge(p.status)}</td>
                    <td style="padding-bottom: 1rem;">
                        <div style="color: var(--color-text); line-height: 1.5; font-size: var(--font-size-sm); background: #f8fafc; padding: 0.75rem; border-radius: var(--radius-sm); border: 1px solid #e2e8f0;">
                            ${escapeHtml(p.desc || '-')}
                        </div>
                        ${renderShapChart(p.shap)}
                    </td>
                `;
                academicBody.appendChild(tr);
            });
        } else {
            academicBody.innerHTML = '<tr><td colspan="4" class="text-center">Tidak ada nilai akademik yang dicatat.</td></tr>';
        }

        // --- Render Catatan Portofolio ---
        const portfolioContainer = document.getElementById('portfolio-narrative-container');
        portfolioContainer.innerHTML = '';

        const portfolioPredictions = individualPredictions.filter(p => 
            p.subject !== "Ekskul Pramuka" && (
                p.subject === "Konsentrasi" ||
                p.subject === "Motorik" ||
                p.subject === "Interaksi dan Komunikasi" ||
                p.subject === "Emosi" ||
                p.subject === "Bina Diri" ||
                p.subject === "Membaca" ||
                p.subject === "Menulis" ||
                p.subject === "Berhitung"
            )
        );

        if (portfolioPredictions.length > 0) {
            portfolioPredictions.forEach(p => {
                const itemDiv = document.createElement('div');
                itemDiv.style.cssText = 'background: #f8fafc; padding: 1.5rem; border: 1px solid #e2e8f0; border-radius: var(--radius-md);';
                itemDiv.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                        <h4 style="font-weight: 700; color: var(--color-text); margin: 0;">${escapeHtml(p.subject)}</h4>
                        ${getStatusBadge(p.status)}
                    </div>
                    <p style="color: var(--color-text-secondary); line-height: 1.6; font-size: var(--font-size-sm); background: #ffffff; padding: 0.875rem; border-radius: var(--radius-sm); border: 1px solid #e2e8f0; margin-bottom: 0.5rem;">
                        ${escapeHtml(p.desc)}
                    </p>
                    ${renderShapChart(p.shap)}
                `;
                portfolioContainer.appendChild(itemDiv);
            });
        } else {
            portfolioContainer.innerHTML = '<p style="color: var(--color-text-secondary);">Tidak ada aspek portofolio yang dicatat.</p>';
        }
    });

    function escapeHtml(text) {
        if (!text && text !== 0) return '';
        const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }
</script>
@endpush
