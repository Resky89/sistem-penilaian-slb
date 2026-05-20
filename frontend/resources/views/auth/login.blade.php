@extends('layouts.auth')

@section('title', 'Login - SIPACA-SLB')

@section('content')
<div class="auth-card">
    <h1 class="auth-card__title">Login</h1>

    <form action="#" method="POST">
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
