@extends('layouts.auth')

@section('title', 'Register - SIPACA-SLB')

@section('content')
<div class="auth-card">
    <h1 class="auth-card__title">Register</h1>

    <form id="form-register" method="POST">
        @csrf
        <div class="alert-general" style="display: none; margin-bottom: 1rem; padding: 0.75rem; border-radius: var(--radius-md); background-color: #fef2f2; border: 1px solid #fecaca; color: var(--color-danger); font-size: var(--font-size-sm); font-weight: 500;"></div>

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
        clearFormErrors(this);

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
                showFormErrors(this, data, { 'full_name': 'nama_lengkap' });
                button.disabled = false;
                button.textContent = 'Register';
            }
        } catch (err) {
            console.error(err);
            showFormErrors(this, { message: 'Gagal menghubungkan ke server backend API.' });
            button.disabled = false;
            button.textContent = 'Register';
        }
    });
</script>
@endpush
