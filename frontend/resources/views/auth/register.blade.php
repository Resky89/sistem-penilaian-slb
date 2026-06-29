@extends('layouts.auth')

@section('title', 'Register - SIPACA-SLB')

@section('content')
<div class="auth-card">
    <h1 class="auth-card__title">Register</h1>

    <form id="form-register" method="POST">
        @csrf
        <x-input name="nama_lengkap" label="Nama Lengkap" placeholder="Masukkan nama lengkap" :required="true" />
        <x-input name="username" label="Username" placeholder="Masukkan username" :required="true" />
        <x-input type="password" name="password" label="Password" placeholder="Masukkan password" :required="true" />

        <div class="mt-2">
            <button type="submit" class="btn btn--primary btn--block">Register</button>
        </div>
    </form>

    <div class="auth-card__footer">
        Sudah punya akun? <a href="{{ route('login') }}">Masuk</a>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.getElementById('form-register').addEventListener('submit', async function(e) {
        e.preventDefault();
        const fullNameVal = document.getElementById('nama_lengkap').value;
        const usernameVal = document.getElementById('username').value;
        const passwordVal = document.getElementById('password').value;

        const button = this.querySelector('button[type="submit"]');
        button.disabled = true;
        button.textContent = 'Memproses...';

        try {
            const res = await fetch(`${API_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    full_name: fullNameVal, 
                    username: usernameVal, 
                    password: passwordVal 
                })
            });
            const data = await res.json();
            if (data.success) {
                alert('Registrasi berhasil! Silakan masuk dengan akun baru Anda.');
                window.location.href = '{{ route("login") }}';
            } else {
                alert(data.message || 'Registrasi gagal. Coba gunakan username lain.');
                button.disabled = false;
                button.textContent = 'Register';
            }
        } catch (err) {
            console.error(err);
            alert('Gagal menghubungkan ke server backend API.');
            button.disabled = false;
            button.textContent = 'Register';
        }
    });
</script>
@endpush
