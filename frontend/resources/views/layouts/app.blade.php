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
        const API_URL = "http://localhost:8001/api";
        
        // Auth Guard
        if (!localStorage.getItem('jwt_token')) {
            window.location.href = '{{ route("login") }}';
        }

        // --- Fetch Interceptor & Silent Refresh ---
        const originalFetch = window.fetch;
        let isRefreshing = false;
        let refreshSubscribers = [];

        function subscribeTokenRefresh(cb) {
            refreshSubscribers.push(cb);
        }

        function onRefreshed(token) {
            refreshSubscribers.forEach(cb => cb(token));
            refreshSubscribers = [];
        }

        function handleLogoutRedirect() {
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('jwt_refresh_token');
            localStorage.removeItem('user_name');
            window.location.href = '{{ route("login") }}';
        }

        window.fetch = async function (url, options = {}) {
            let token = localStorage.getItem('jwt_token');
            if (token && url.toString().startsWith(API_URL)) {
                options.headers = options.headers || {};
                if (!options.headers['Authorization']) {
                    options.headers['Authorization'] = `Bearer ${token}`;
                }
            }

            try {
                let response = await originalFetch(url, options);

                // Jika token expired (401 Unauthorized) dan bukan request login/refresh itu sendiri
                if (response.status === 401 && 
                    url.toString().startsWith(API_URL) && 
                    !url.toString().includes('/auth/refresh') && 
                    !url.toString().includes('/auth/login')) {
                    
                    const refreshToken = localStorage.getItem('jwt_refresh_token');
                    if (!refreshToken) {
                        handleLogoutRedirect();
                        return response;
                    }

                    if (!isRefreshing) {
                        isRefreshing = true;
                        try {
                            const refreshRes = await originalFetch(`${API_URL}/auth/refresh`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ refresh_token: refreshToken })
                            });
                            
                            const refreshData = await refreshRes.json();
                            if (refreshData.success && refreshData.data.access_token) {
                                const newAccessToken = refreshData.data.access_token;
                                const newRefreshToken = refreshData.data.refresh_token;
                                
                                localStorage.setItem('jwt_token', newAccessToken);
                                if (newRefreshToken) {
                                    localStorage.setItem('jwt_refresh_token', newRefreshToken);
                                }
                                
                                isRefreshing = false;
                                onRefreshed(newAccessToken);
                            } else {
                                isRefreshing = false;
                                handleLogoutRedirect();
                                return response;
                            }
                        } catch (refreshErr) {
                            isRefreshing = false;
                            handleLogoutRedirect();
                            return response;
                        }
                    }

                    // Menunggu refresh token selesai dan mengulangi request asli
                    return new Promise((resolve) => {
                        subscribeTokenRefresh((newToken) => {
                            options.headers = options.headers || {};
                            options.headers['Authorization'] = `Bearer ${newToken}`;
                            resolve(originalFetch(url, options));
                        });
                    });
                }

                return response;
            } catch (error) {
                throw error;
            }
        };
    </script>
</head>
<body>
    {{-- Top Bar --}}
    <header class="topbar">
        <span class="topbar__brand">SIPACA-SLB</span>
        <div class="topbar__user">
            <span id="user-display-name">Guru SLB</span>
            <div class="topbar__avatar" id="user-display-avatar">G</div>
        </div>
    </header>

    {{-- Sidebar --}}
    <aside class="sidebar" id="sidebar">
        <ul class="sidebar__nav">
            <li>
                <a href="{{ route('dashboard') }}"
                   class="sidebar__link {{ request()->routeIs('dashboard') ? 'sidebar__link--active' : '' }}">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                    Home
                </a>
            </li>
            <li>
                <a href="{{ route('siswa.index') }}"
                   class="sidebar__link {{ request()->routeIs('siswa.*') ? 'sidebar__link--active' : '' }}">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                    Data Siswa
                </a>
            </li>
            <li>
                <a href="{{ route('penilaian.index') }}"
                   class="sidebar__link {{ request()->routeIs('penilaian.*') ? 'sidebar__link--active' : '' }}">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838.838-2.872a2 2 0 0 1 .506-.855z"/></svg>
                    Penilaian
                </a>
            </li>
        </ul>
        <div class="sidebar__footer">
            <a href="#" class="sidebar__logout" id="btn-sidebar-logout">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
                Logout
            </a>
        </div>
    </aside>

    {{-- Main Content --}}
    <main class="main-content fade-in">
        @yield('content')
    </main>

    @stack('scripts')

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

        // Tampilkan info user aktif dan kelola logout
        document.addEventListener('DOMContentLoaded', function() {
            const userName = localStorage.getItem('user_name') || 'Guru SLB';
            const userDisplay = document.getElementById('user-display-name');
            const avatarDisplay = document.getElementById('user-display-avatar');
            if (userDisplay) userDisplay.textContent = userName;
            if (avatarDisplay) avatarDisplay.textContent = userName.charAt(0).toUpperCase();

            document.getElementById('btn-sidebar-logout')?.addEventListener('click', async function(e) {
                e.preventDefault();
                const token = localStorage.getItem('jwt_token');
                try {
                    await fetch(`${API_URL}/auth/logout`, {
                        method: 'POST',
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                } catch (err) {
                    console.error('API logout request failed:', err);
                }
                localStorage.removeItem('jwt_token');
                localStorage.removeItem('user_name');
                window.location.href = '{{ route("login") }}';
            });
        });
    </script>
</body>
</html>
