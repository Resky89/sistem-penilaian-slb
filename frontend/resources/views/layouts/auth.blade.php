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
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
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
    @stack('scripts')
</body>
</html>
