<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="SIPACA-SLB - Sistem Penilaian dan Klasifikasi Anak SLB">
    <title>@yield('title', 'SIPACA-SLB')</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{{ asset('css/app.css') }}?v={{ filemtime(public_path('css/app.css')) }}">
    <script>
        const API_URL = "{{ config('services.api.url') }}";

        function clearFormErrors(form) {
            if (typeof form === 'string') {
                form = document.getElementById(form);
            }
            if (!form) return;
            
            form.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(el => {
                el.classList.remove('is-invalid');
            });
            
            form.querySelectorAll('.invalid-feedback').forEach(el => {
                el.style.display = 'none';
                el.textContent = '';
            });
            
            const generalAlert = form.querySelector('.alert-general');
            if (generalAlert) {
                generalAlert.style.display = 'none';
                generalAlert.textContent = '';
            }
        }

        function showFormErrors(form, data, fieldMapping = {}) {
            if (typeof form === 'string') {
                form = document.getElementById(form);
            }
            if (!form) return;
            
            clearFormErrors(form);
            
            if (data.error_code === 'VALIDATION_ERROR' && Array.isArray(data.details)) {
                data.details.forEach(err => {
                    let fieldName = err.field;
                    if (fieldMapping[fieldName]) {
                        fieldName = fieldMapping[fieldName];
                    }
                    
                    let inputEl = form.querySelector(`#${fieldName}`) || form.querySelector(`[name="${fieldName}"]`);
                    if (!inputEl) {
                        inputEl = form.querySelector(`[name$="${fieldName}"]`);
                    }
                    
                    if (inputEl) {
                        inputEl.classList.add('is-invalid');
                        let feedbackEl = form.querySelector(`#error-${inputEl.id || inputEl.name}`);
                        if (!feedbackEl) {
                            feedbackEl = document.createElement('div');
                            feedbackEl.id = `error-${inputEl.id || inputEl.name}`;
                            feedbackEl.className = 'invalid-feedback';
                            feedbackEl.style.cssText = 'font-size: 0.8rem; color: var(--color-danger); margin-top: 4px; font-weight: 500;';
                            inputEl.parentNode.appendChild(feedbackEl);
                        }
                        feedbackEl.textContent = err.message;
                        feedbackEl.style.display = 'block';
                    }
                });
            } else {
                const generalAlert = form.querySelector('.alert-general');
                if (generalAlert) {
                    generalAlert.textContent = data.message || 'Terjadi kesalahan sistem.';
                    generalAlert.style.display = 'block';
                } else if (typeof showToast === 'function') {
                    showToast('error', data.message || 'Terjadi kesalahan sistem.');
                } else {
                    alert(data.message || 'Terjadi kesalahan sistem.');
                }
            }
        }
    </script>
</head>
<body>
    <div class="auth-wrapper">
        @yield('content')
    </div>

    {{-- Toast Container --}}
    <div class="toast-container" id="toast-container"></div>

    <script>
        var TOAST_ICONS = {
            success: '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/></svg>',
            error: '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>',
            warning: '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>',
            info: '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>'
        };

        var TOAST_TITLES = {
            success: 'Berhasil',
            error: 'Gagal',
            warning: 'Peringatan',
            info: 'Informasi'
        };

        function showToast(type, message, duration) {
            duration = duration || 4000;
            var container = document.getElementById('toast-container');
            if (!container) return;

            var toast = document.createElement('div');
            toast.className = 'toast toast--' + type;
            toast.innerHTML =
                '<span class="toast__icon">' + TOAST_ICONS[type] + '</span>' +
                '<div class="toast__content">' +
                    '<div class="toast__title">' + TOAST_TITLES[type] + '</div>' +
                    '<div class="toast__message">' + message + '</div>' +
                '</div>' +
                '<button class="toast__close" aria-label="Tutup">' +
                    '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>' +
                '</button>' +
                '<div class="toast__progress" style="animation-duration:' + duration + 'ms"></div>';

            container.appendChild(toast);

            var closeBtn = toast.querySelector('.toast__close');
            closeBtn.addEventListener('click', function () { removeToast(toast); });

            setTimeout(function () { removeToast(toast); }, duration);
        }

        function removeToast(toast) {
            if (toast.classList.contains('toast--removing')) return;
            toast.classList.add('toast--removing');
            toast.addEventListener('animationend', function () { toast.remove(); });
        }
    </script>
    @stack('scripts')
</body>
</html>
