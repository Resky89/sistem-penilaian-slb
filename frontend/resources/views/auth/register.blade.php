@extends('layouts.auth')

@section('title', 'Register - SIPACA-SLB')

@section('content')
<div class="auth-card">
    <h1 class="auth-card__title">Register</h1>

    <form action="#" method="POST">
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
