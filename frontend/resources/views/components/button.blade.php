@props([
    'type' => 'primary',
    'tag' => 'button',
    'href' => '#',
])

@if($tag === 'a')
    <a href="{{ $href }}" class="btn btn--{{ $type }}" {{ $attributes }}>
        {{ $slot }}
    </a>
@else
    <button type="{{ $attributes->get('type', 'button') }}" class="btn btn--{{ $type }}" {{ $attributes }}>
        {{ $slot }}
    </button>
@endif
