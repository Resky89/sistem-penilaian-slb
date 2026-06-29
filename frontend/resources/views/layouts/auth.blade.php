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
    </script>
</head>
<body>
    <div class="auth-wrapper">
        @yield('content')
    </div>
    @stack('scripts')
</body>
</html>
