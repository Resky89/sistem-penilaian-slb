@extends('layouts.app')

@section('title', 'Form Penilaian - SIPACA-SLB')

@section('content')
<div class="page-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
    <h1 class="page-header__title">Form Penilaian</h1>
    <a href="{{ route('penilaian.index') }}" class="btn btn--outline" style="display: inline-flex; align-items: center; gap: 0.5rem; text-decoration: none;">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        Kembali ke Daftar
    </a>
</div>

<form id="form-penilaian">
    @csrf
    <div class="alert-general" style="display: none; margin-bottom: 1.5rem; padding: 0.75rem 1rem; border-radius: var(--radius-md); background-color: #fef2f2; border: 1px solid #fecaca; color: var(--color-danger); font-size: var(--font-size-sm); font-weight: 500;"></div>

    {{-- Top Action Bar --}}
    <div class="form-top-action" style="display: flex; gap: 1rem; flex-wrap: wrap; align-items: flex-start;">

        {{-- Student Search Combobox --}}
        <div style="flex: 2; min-width: 240px;">
            <label for="student-search-input" class="form-label">Siswa</label>
            <div class="student-search" id="student-search-widget" role="combobox" aria-haspopup="listbox" aria-expanded="false">
                {{-- Hidden input membawa ID terpilih ke form submission --}}
                <input type="hidden" id="selected-student-id" name="siswa_id">

                <div class="student-search__input-wrapper">
                    {{-- Search icon --}}
                    <span class="student-search__icon" aria-hidden="true">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                        </svg>
                    </span>

                    <input
                        type="text"
                        id="student-search-input"
                        class="student-search__input"
                        placeholder="Cari nama atau NIS siswa..."
                        autocomplete="off"
                        aria-label="Cari siswa"
                        aria-autocomplete="list"
                        aria-controls="student-search-dropdown"
                        role="searchbox"
                    >

                    {{-- Clear button --}}
                    <button type="button" class="student-search__clear" id="student-search-clear" aria-label="Hapus pilihan">
                        <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
                        </svg>
                    </button>
                </div>

                {{-- Dropdown --}}
                <div class="student-search__dropdown" id="student-search-dropdown" role="listbox" aria-label="Daftar siswa"></div>

                {{-- Selected pill --}}
                <div class="student-search__selected-pill" id="student-selected-pill">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24"
                         fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 6 9 17l-5-5"/>
                    </svg>
                    <span id="student-selected-label">-</span>
                </div>
            </div>
        </div>

        {{-- Tahun Ajaran --}}
        <div style="flex: 1; min-width: 150px;">
            <label for="tahun-ajaran" class="form-label">Tahun Ajaran</label>
            <input type="text" id="tahun-ajaran" class="form-input" value="2025/2026" required placeholder="Contoh: 2025/2026">
        </div>

        {{-- Semester --}}
        <div style="flex: 1; min-width: 120px;">
            <label for="semester" class="form-label">Semester</label>
            <select id="semester" class="form-select" required>
                <option value="Odd">Ganjil</option>
                <option value="Even">Genap</option>
            </select>
        </div>

        {{-- Submit --}}
        <div style="padding-top: 1.5rem;">
            <button type="submit" class="btn btn--primary" style="height: 42px;" id="btn-submit">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>
                    <path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/>
                    <path d="M7 3v4a1 1 0 0 0 1 1h7"/>
                </svg>
                Simpan &amp; Prediksi
            </button>
        </div>
    </div>

    {{-- Tabs --}}
    <div class="tabs" role="tablist" style="margin-top: 1.5rem;">
        <button type="button" class="tabs__item tabs__item--active" data-tab="akademik" role="tab" aria-selected="true">
            Akademik (Rapor)
        </button>
        <button type="button" class="tabs__item" data-tab="portofolio" role="tab" aria-selected="false">
            Portofolio
        </button>
    </div>

    {{-- ===== Tab: Akademik ===== --}}
    <div class="tab-content tab-content--active" id="tab-akademik" role="tabpanel">
        <p style="color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-bottom: 1.25rem;">
            Isi nilai (0–100) dan deskripsi perkembangan untuk setiap mata pelajaran.
            Kolom <em>Ekskul Pramuka</em> hanya memerlukan deskripsi.
        </p>

        @php
        $mapelRapor = [
            ['id' => 'pai',  'label' => 'Pendidikan Agama Islam dan Budi Pekerti',  'has_score' => true],
            ['id' => 'pkn',  'label' => 'Pendidikan Pancasila dan Kewarganegaraan',  'has_score' => true],
            ['id' => 'ind',  'label' => 'Bahasa Indonesia',    'has_score' => true],
            ['id' => 'mat',  'label' => 'Matematika',          'has_score' => true],
            ['id' => 'ipas', 'label' => 'Ilmu Pengetahuan Alam dan Sosial',                'has_score' => true],
            ['id' => 'ing',  'label' => 'Bahasa Inggris',      'has_score' => true],
            ['id' => 'art',  'label' => 'Seni Budaya',         'has_score' => true],
            ['id' => 'pjok', 'label' => 'Pendidikan Jasmani, Olahraga, dan Kesehatan',               'has_score' => true],
            ['id' => 'sun',  'label' => 'Bahasa Sunda',            'has_score' => true],
            ['id' => 'pro',  'label' => 'Program Khusus',      'has_score' => true],
            ['id' => 'pramuka', 'label' => 'Ekskul Pramuka',   'has_score' => false],
        ];
        @endphp

        @foreach ($mapelRapor as $m)
        <div class="subject-section">
            <h3 class="subject-section__title">{{ $m['label'] }}</h3>
            <div style="display: grid; grid-template-columns: {{ $m['has_score'] ? '180px 1fr' : '1fr' }}; gap: 1rem; align-items: start;">

                @if ($m['has_score'])
                <div class="form-group">
                    <label class="form-label" for="score-{{ $m['id'] }}">Nilai Akhir (0–100)</label>
                    <input type="number" id="score-{{ $m['id'] }}" name="{{ $m['id'] }}_score"
                           class="form-input" placeholder="85" min="0" max="100" step="0.1">
                </div>
                @endif

                <div class="form-group">
                    <label class="form-label" for="desc-{{ $m['id'] }}">Deskripsi Perkembangan</label>
                    <textarea id="desc-{{ $m['id'] }}" name="{{ $m['id'] }}_desc"
                              class="form-input" rows="3"
                              placeholder="{{ $m['has_score'] ? 'Tuliskan deskripsi perkembangan siswa pada mata pelajaran ini...' : 'Tuliskan catatan kegiatan dan perkembangan siswa dalam ekskul pramuka...' }}"></textarea>
                </div>

            </div>
        </div>
        @endforeach
    </div>

    {{-- ===== Tab: Portofolio ===== --}}
    <div class="tab-content" id="tab-portofolio" role="tabpanel">
        <p style="color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-bottom: 1.25rem;">
            Isi deskripsi perkembangan siswa pada setiap aspek portofolio.
        </p>

        @php
        $portofolio = [
            ['id' => 'konsentrasi', 'label' => 'Konsentrasi'],
            ['id' => 'motorik',     'label' => 'Motorik'],
            ['id' => 'interaksi',   'label' => 'Interaksi dan Komunikasi'],
            ['id' => 'emosi',       'label' => 'Emosi'],
            ['id' => 'bina_diri',   'label' => 'Bina Diri'],
            ['id' => 'membaca',     'label' => 'Membaca'],
            ['id' => 'menulis',     'label' => 'Menulis'],
            ['id' => 'berhitung',   'label' => 'Berhitung'],
        ];
        @endphp

        @foreach ($portofolio as $p)
        <div class="subject-section">
            <h3 class="subject-section__title">{{ $p['label'] }}</h3>
            <div class="form-group">
                <label class="form-label" for="desc-{{ $p['id'] }}">Deskripsi Perkembangan</label>
                <textarea id="desc-{{ $p['id'] }}" name="{{ $p['id'] }}_desc"
                          class="form-input" rows="3"
                          placeholder="Tuliskan deskripsi perkembangan siswa pada aspek ini..."></textarea>
            </div>
        </div>
        @endforeach
    </div>

</form>
@endsection

@push('scripts')
<script>
document.addEventListener('DOMContentLoaded', function () {

    /* ===================================================
       1. TAB SWITCHING
    =================================================== */
    const tabs     = document.querySelectorAll('.tabs__item');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            const target = this.getAttribute('data-tab');
            tabs.forEach(t => { t.classList.remove('tabs__item--active'); t.setAttribute('aria-selected', 'false'); });
            contents.forEach(c => c.classList.remove('tab-content--active'));
            this.classList.add('tabs__item--active');
            this.setAttribute('aria-selected', 'true');
            document.getElementById('tab-' + target).classList.add('tab-content--active');
        });
    });

    /* ===================================================
       2. STUDENT SEARCH COMBOBOX WITH DEBOUNCE
    =================================================== */
    const token = localStorage.getItem('jwt_token');

    // Parse URL query parameters
    const urlParams = new URLSearchParams(window.location.search);
    const queryStudentId = urlParams.get('student_id');
    const editId = urlParams.get('edit_id');

    // Custom API Error Class for Normalization
    class ApiError extends Error {
        constructor(message, status, payload = null) {
            super(message);
            this.name = "ApiError";
            this.status = status;
            this.payload = payload;
        }
    }

    // Centralized API Request Helper (Best Practice)
    async function apiRequest(url, options = {}) {
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        };
        const config = {
            ...options,
            headers
        };

        try {
            const res = await fetch(url, config);
            let payload = null;
            if (res.status !== 204) {
                const text = await res.text();
                if (text) {
                    try {
                        payload = JSON.parse(text);
                    } catch (e) {
                        payload = { success: false, message: text };
                    }
                }
            }

            if (!res.ok) {
                throw new ApiError(
                    payload?.message || `Request failed with status ${res.status}`,
                    res.status,
                    payload
                );
            }
            return payload;
        } catch (err) {
            if (err instanceof ApiError) throw err;
            throw new ApiError('Terjadi kesalahan jaringan atau server tidak merespons.', 0);
        }
    }

    // State
    let allStudents   = [];   // cache semua siswa dari API
    let selectedId    = null;
    let focusedIndex  = -1;

    // DOM refs
    const widget       = document.getElementById('student-search-widget');
    const searchInput  = document.getElementById('student-search-input');
    const hiddenInput  = document.getElementById('selected-student-id');
    const dropdown     = document.getElementById('student-search-dropdown');
    const clearBtn     = document.getElementById('student-search-clear');
    const pill         = document.getElementById('student-selected-pill');
    const pillLabel    = document.getElementById('student-selected-label');

    // --- Helper: debounce ---
    function debounce(fn, delay) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    // --- Helper: highlight matching text ---
    function highlight(text, query) {
        if (!query) return escapeHtml(text);
        const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        return escapeHtml(text).replace(
            new RegExp(escaped, 'gi'),
            m => `<mark class="student-search__highlight">${m}</mark>`
        );
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // --- Get initials for avatar ---
    function initials(name) {
        return name.trim().split(/\s+/).slice(0, 2).map(w => w[0].toUpperCase()).join('');
    }

    // --- Render dropdown list ---
    function renderDropdown(students, query) {
        dropdown.innerHTML = '';
        focusedIndex = -1;

        if (students.length === 0) {
            dropdown.innerHTML = `<div class="student-search__empty">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                     fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
                     style="display:block;margin:0 auto 0.5rem;color:var(--color-text-muted)">
                    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M8 11h6"/>
                </svg>
                Siswa tidak ditemukan
            </div>`;
            openDropdown();
            return;
        }

        students.forEach(function (student, idx) {
            const el = document.createElement('div');
            el.className = 'student-search__option';
            el.setAttribute('role', 'option');
            el.setAttribute('data-id', student.id);
            el.setAttribute('tabindex', '-1');
            el.innerHTML = `
                <div class="student-search__avatar">${escapeHtml(initials(student.full_name))}</div>
                <div>
                    <div class="student-search__option-name">${highlight(student.full_name, query)}</div>
                    <div class="student-search__option-meta">
                        NIS: ${highlight(student.student_number, query)}
                        &nbsp;·&nbsp; Kelas ${escapeHtml(student.class_level)}
                    </div>
                </div>`;
            el.addEventListener('mousedown', function (e) {
                e.preventDefault(); // agar input blur tidak trigger dulu
                selectStudent(student);
            });
            dropdown.appendChild(el);
        });

        openDropdown();
    }

    // --- Filter lokal dari cache ---
    function filterStudents(query) {
        if (!query.trim()) return allStudents;
        const q = query.toLowerCase();
        return allStudents.filter(s =>
            s.full_name.toLowerCase().includes(q) ||
            s.student_number.toLowerCase().includes(q)
        );
    }

    // --- Open / close dropdown ---
    function openDropdown() {
        dropdown.classList.add('open');
        widget.setAttribute('aria-expanded', 'true');
    }

    function closeDropdown() {
        dropdown.classList.remove('open');
        widget.setAttribute('aria-expanded', 'false');
        focusedIndex = -1;
    }

    // --- Select a student ---
    function selectStudent(student) {
        selectedId = student.id;
        hiddenInput.value = student.id;

        searchInput.value = `${student.full_name} — ${student.student_number}`;
        pillLabel.textContent = `${student.full_name} (${student.student_number}) · Kelas ${student.class_level}`;

        pill.classList.add('visible');
        clearBtn.classList.add('visible');
        closeDropdown();
    }

    // --- Clear selection ---
    function clearSelection() {
        selectedId = null;
        hiddenInput.value = '';
        searchInput.value = '';
        pill.classList.remove('visible');
        clearBtn.classList.remove('visible');
        closeDropdown();
        searchInput.focus();
    }

    // --- Keyboard navigation ---
    function updateFocusedOption(newIndex) {
        const options = dropdown.querySelectorAll('.student-search__option');
        options.forEach(o => o.classList.remove('active'));
        if (newIndex >= 0 && newIndex < options.length) {
            options[newIndex].classList.add('active');
            options[newIndex].scrollIntoView({ block: 'nearest' });
        }
        focusedIndex = newIndex;
    }

    // --- Debounced search (300ms) ---
    const handleSearch = debounce(function (query) {
        const filtered = filterStudents(query);
        renderDropdown(filtered, query);
    }, 300);

    // --- Load all students on init (single API call, then filter locally) ---
    async function loadStudents() {
        dropdown.innerHTML = `<div class="student-search__loading">
            <div class="student-search__spinner"></div> Memuat daftar siswa...
        </div>`;
        openDropdown();

        try {
            const data = await apiRequest(`${API_URL}/students`);
            if (data.success) {
                allStudents = data.data;

                // Auto-select if query param student_id exists
                if (queryStudentId) {
                    const found = allStudents.find(s => String(s.id) === queryStudentId);
                    if (found) { selectStudent(found); return; }
                }
            }
        } catch (err) {
            console.error(err);
            showToast('error', err.message || 'Gagal memuat daftar siswa.');
        }

        closeDropdown();
    }

    // --- Load assessment data for editing ---
    async function loadAssessmentForEdit(id) {
        showToast('info', 'Memuat data penilaian lama...');
        
        try {
            // Load students list first for selection matching
            const dataS = await apiRequest(`${API_URL}/students`);
            if (dataS.success) {
                allStudents = dataS.data;
            }

            const data = await apiRequest(`${API_URL}/assessments/${id}`);
            
            if (data.success) {
                const assessment = data.data;
                
                // Select student
                if (assessment.student) {
                    selectStudent(assessment.student);
                    // Disable changing student when in edit mode
                    clearBtn.style.display = 'none';
                    searchInput.disabled = true;
                    searchInput.placeholder = 'Pilihan siswa terkunci saat edit';
                }
                
                // Set metadata
                document.getElementById('tahun-ajaran').value = assessment.academic_year;
                document.getElementById('semester').value = assessment.semester;
                
                // Populate mapel fields
                const mapelFields = ['pai', 'pkn', 'ind', 'mat', 'ipas', 'ing', 'art', 'pjok', 'sun', 'pro'];
                mapelFields.forEach(field => {
                    const scoreVal = assessment[`${field}_score`];
                    const descVal = assessment[`${field}_desc`];
                    
                    const scoreEl = document.getElementById(`score-${field}`);
                    const descEl = document.getElementById(`desc-${field}`);
                    
                    if (scoreEl && scoreVal !== null) scoreEl.value = scoreVal;
                    if (descEl && descVal !== null) descEl.value = descVal;
                });
                
                // Populate portfolio fields
                const portofolioFields = ['pramuka', 'konsentrasi', 'motorik', 'interaksi', 'emosi', 'bina_diri', 'membaca', 'menulis', 'berhitung'];
                portofolioFields.forEach(field => {
                    const descVal = assessment[`${field}_desc`];
                    const descEl = document.getElementById(`desc-${field}`);
                    if (descEl && descVal !== null) descEl.value = descVal;
                });

                showToast('success', 'Data penilaian lama berhasil dimuat.');
            }
        } catch (err) {
            console.error(err);
            showToast('error', err.message || 'Terjadi kesalahan saat memuat data penilaian.');
        }
    }

    // --- Event Listeners ---
    searchInput.addEventListener('focus', function () {
        if (!selectedId) {
            // Jika belum ada cache, muat dari API dulu
            if (allStudents.length === 0) {
                loadStudents();
            } else {
                renderDropdown(filterStudents(this.value), this.value);
            }
        }
    });

    searchInput.addEventListener('input', function () {
        selectedId = null;
        hiddenInput.value = '';
        pill.classList.remove('visible');
        clearBtn.classList.toggle('visible', this.value.length > 0);

        if (allStudents.length === 0) {
            loadStudents();
        } else {
            handleSearch(this.value);
        }
    });

    searchInput.addEventListener('keydown', function (e) {
        const options = dropdown.querySelectorAll('.student-search__option');
        if (!dropdown.classList.contains('open')) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            updateFocusedOption(Math.min(focusedIndex + 1, options.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            updateFocusedOption(Math.max(focusedIndex - 1, 0));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (focusedIndex >= 0 && options[focusedIndex]) {
                const id = options[focusedIndex].getAttribute('data-id');
                const found = allStudents.find(s => String(s.id) === id);
                if (found) selectStudent(found);
            }
        } else if (e.key === 'Escape') {
            closeDropdown();
        }
    });

    searchInput.addEventListener('blur', function () {
        // Delay agar mousedown pada option bisa terjadi dulu
        setTimeout(closeDropdown, 180);
    });

    clearBtn.addEventListener('click', clearSelection);

    // Close on outside click
    document.addEventListener('click', function (e) {
        if (!widget.contains(e.target)) closeDropdown();
    });

    /* ===================================================
       3. FORM SUBMISSION
    =================================================== */
    document.getElementById('form-penilaian').addEventListener('submit', async function (e) {
        e.preventDefault();
        clearFormErrors(this);

        const studentId = hiddenInput.value;
        if (!studentId) {
            showToast('warning', 'Harap pilih siswa terlebih dahulu.');
            searchInput.focus();
            return;
        }

        const academicYear = document.getElementById('tahun-ajaran').value.trim();
        const semesterVal  = document.getElementById('semester').value;
        const today        = new Date().toISOString().split('T')[0];

        const mapelFields      = ['pai', 'pkn', 'ind', 'mat', 'ipas', 'ing', 'art', 'pjok', 'sun', 'pro'];
        const portofolioFields = ['pramuka', 'konsentrasi', 'motorik', 'interaksi', 'emosi', 'bina_diri', 'membaca', 'menulis', 'berhitung'];

        const payload = {
            student_id:      parseInt(studentId),
            academic_year:   academicYear,
            semester:        semesterVal,
            assessment_date: today
        };

        let hasData = false;

        // Kumpulkan nilai mapel (score + desc)
        mapelFields.forEach(field => {
            const scoreEl = document.getElementById(`score-${field}`);
            const descEl  = document.getElementById(`desc-${field}`);
            const scoreVal = scoreEl && scoreEl.value !== '' ? parseFloat(scoreEl.value) : null;
            const descVal  = descEl  && descEl.value.trim()  !== '' ? descEl.value.trim()  : null;

            if (scoreVal !== null) { payload[`${field}_score`] = scoreVal; hasData = true; }
            if (descVal  !== null) { payload[`${field}_desc`]  = descVal;  hasData = true; }
        });

        // Kumpulkan deskripsi portofolio
        portofolioFields.forEach(field => {
            const descEl  = document.getElementById(`desc-${field}`);
            const descVal = descEl && descEl.value.trim() !== '' ? descEl.value.trim() : null;
            if (descVal !== null) { payload[`${field}_desc`] = descVal; hasData = true; }
        });

        if (!hasData) {
            showToast('warning', 'Harap isi minimal satu nilai atau deskripsi penilaian.');
            return;
        }

        const submitBtn = document.getElementById('btn-submit');
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
                 style="animation:spin 1s linear infinite">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
            </svg>
            ${editId ? 'Memproses Pembaruan...' : 'Menganalisis &amp; Menyimpan...'}`;

        const mapping = {
            student_id: 'student-search-input',
            academic_year: 'tahun-ajaran',
            semester: 'semester'
        };
        mapelFields.forEach(field => {
            mapping[`${field}_score`] = `score-${field}`;
            mapping[`${field}_desc`] = `desc-${field}`;
        });
        portofolioFields.forEach(field => {
            mapping[`${field}_desc`] = `desc-${field}`;
        });

        try {
            const url = editId ? `${API_URL}/assessments/${editId}` : `${API_URL}/assessments`;
            const method = editId ? 'PUT' : 'POST';

            const data = await apiRequest(url, {
                method: method,
                body: JSON.stringify(payload)
            });

            if (data.success) {
                showToast('success', editId ? 'Penilaian berhasil diperbarui!' : 'Penilaian berhasil disimpan dan dianalisis!');
                sessionStorage.setItem('latest_assessment_result', JSON.stringify(data.data));
                window.location.href = `{{ route("penilaian.hasil") }}?student_id=${studentId}`;
            }
        } catch (err) {
            console.error(err);
            if (err instanceof ApiError && err.payload) {
                showFormErrors(this, err.payload, mapping);
            } else {
                showFormErrors(this, { message: err.message });
            }
            showToast('error', err.message || 'Gagal memproses penilaian.');
            resetSubmitBtn(submitBtn);
        }
    });

    function resetSubmitBtn(btn) {
        btn.disabled = false;
        btn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/>
                <path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"/>
                <path d="M7 3v4a1 1 0 0 0 1 1h7"/>
            </svg>
            ${editId ? 'Perbarui &amp; Prediksi' : 'Simpan &amp; Prediksi'}`;
    }

    // Auto-select student from URL query parameter or edit assessment on page load
    if (editId) {
        // Change title in form view to edit mode
        document.querySelector('.page-header__title').textContent = 'Edit Penilaian';
        loadAssessmentForEdit(editId);
    } else if (queryStudentId) {
        loadStudents();
    }

});
</script>
@endpush
