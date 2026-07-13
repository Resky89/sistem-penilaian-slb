@props([
    'type' => 'text',
    'name' => '',
    'label' => '',
    'placeholder' => '',
    'value' => '',
    'required' => false,
])

<div class="form-group">
    @if($label)
        <label for="{{ $name }}" class="form-label">{{ $label }}</label>
    @endif
    <div style="position: relative;">
        <input
            type="{{ $type }}"
            id="{{ $name }}"
            name="{{ $name }}"
            value="{{ $value }}"
            placeholder="{{ $placeholder }}"
            class="form-input"
            {{ $type === 'password' ? 'style=padding-right:2.5rem;' : '' }}
            {{ $required ? 'required' : '' }}
            {{ $attributes }}
        >
        @if($type === 'password')
            <button type="button" id="toggle-{{ $name }}" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); background: none; border: none; padding: 0.25rem; cursor: pointer; color: var(--color-text-secondary); display: flex; align-items: center; justify-content: center; outline: none;" tabindex="-1" aria-label="Tampilkan Password">
                {{-- Eye Close Icon by default --}}
                <svg id="eye-icon-{{ $name }}" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/>
                    <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/>
                    <path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/>
                    <line x1="2" y1="2" x2="22" y2="22"/>
                </svg>
            </button>
            <script>
                document.getElementById('toggle-{{ $name }}').addEventListener('click', function() {
                    const input = document.getElementById('{{ $name }}');
                    const icon = document.getElementById('eye-icon-{{ $name }}');
                    if (input.type === 'password') {
                        input.type = 'text';
                        icon.innerHTML = '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>';
                    } else {
                        input.type = 'password';
                        icon.innerHTML = '<path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.52 13.52 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/>';
                    }
                });
            </script>
        @endif
    </div>
    <div class="invalid-feedback" id="error-{{ $name }}" style="display: none; font-size: 0.8rem; color: var(--color-danger); margin-top: 4px; font-weight: 500;"></div>
</div>
