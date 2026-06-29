@extends('layouts.auth')

@section('title', 'Login - SIPACA-SLB')

@section('content')
<div class="auth-card">
    <h1 class="auth-card__title">Login</h1>

    <form id="form-login" method="POST">
        @csrf
        <x-input name="username" label="Username" placeholder="Masukkan username" :required="true" />
        <x-input type="password" name="password" label="Password" placeholder="Masukkan password" :required="true" />

        <div class="mt-2">
            <button type="submit" class="btn btn--primary btn--block">Login</button>
        </div>

        <div class="mt-1">
            <a href="{{ route('register') }}" class="btn btn--secondary btn--block">Register</a>
        </div>
    </form>
</div>
@endsection

@push('scripts')
<script>
    // Redirect jika sudah login
    if (localStorage.getItem('jwt_token')) {
        window.location.href = '{{ route("dashboard") }}';
    }

    document.getElementById('form-login').addEventListener('submit', async function(e) {
        e.preventDefault();
        const usernameVal = document.getElementById('username').value;
        const passwordVal = document.getElementById('password').value;

        const button = this.querySelector('button[type="submit"]');
        button.disabled = true;
        button.textContent = 'Memproses...';

        try {
            const res = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: usernameVal, password: passwordVal })
            });
            const data = await res.json();
            if (data.success) {
                localStorage.setItem('jwt_token', data.data.access_token);
                if (data.data.refresh_token) {
                    localStorage.setItem('jwt_refresh_token', data.data.refresh_token);
                }
                
                // Ambil profil lengkap dari /auth/me untuk mendapatkan nama lengkap asli
                const meRes = await fetch(`${API_URL}/auth/me`, {
                    headers: { 'Authorization': `Bearer ${data.data.access_token}` }
                });
                const meData = await meRes.json();
                
                if (meData.success) {
                    localStorage.setItem('user_name', meData.data.full_name);
                } else {
                    localStorage.setItem('user_name', usernameVal);
                }
                
                window.location.href = '{{ route("dashboard") }}';
            } else {
                alert(data.message || 'Login gagal. Periksa kembali username dan password Anda.');
                button.disabled = false;
                button.textContent = 'Login';
            }
        } catch (err) {
            console.error(err);
            alert('Gagal menghubungkan ke server backend API.');
            button.disabled = false;
            button.textContent = 'Login';
        }
    });
</script>
@endpush
