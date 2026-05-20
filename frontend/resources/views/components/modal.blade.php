@props([
    'id' => '',
    'title' => '',
    'size' => 'md',
])

<div class="modal-overlay" id="{{ $id }}" role="dialog" aria-modal="true" aria-labelledby="{{ $id }}-title">
    <div class="modal modal--{{ $size }}">
        <div class="modal__header">
            <h2 class="modal__title" id="{{ $id }}-title">{{ $title }}</h2>
            <button type="button" class="modal__close" onclick="closeModal('{{ $id }}')" aria-label="Tutup">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
        </div>
        <div class="modal__body">
            {{ $slot }}
        </div>
        @isset($footer)
            <div class="modal__footer">
                {{ $footer }}
            </div>
        @endisset
    </div>
</div>
