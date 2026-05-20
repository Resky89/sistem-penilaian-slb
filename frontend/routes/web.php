<?php

use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| UI Routes (Tanpa Backend - Static Views Only)
|--------------------------------------------------------------------------
*/

// Auth
Route::get('/login', fn() => view('auth.login'))->name('login');
Route::get('/register', fn() => view('auth.register'))->name('register');

// Dashboard
Route::get('/', fn() => view('dashboard'))->name('dashboard');

// Data Siswa
Route::get('/siswa', fn() => view('siswa.index'))->name('siswa.index');

// Penilaian
Route::get('/penilaian', fn() => view('penilaian.index'))->name('penilaian.index');
Route::get('/penilaian/form', fn() => view('penilaian.form'))->name('penilaian.form');
Route::get('/penilaian/hasil', fn() => view('penilaian.hasil'))->name('penilaian.hasil');
