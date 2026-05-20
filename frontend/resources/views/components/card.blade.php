@props(['class' => ''])

<div class="card {{ $class }}">
    <div class="card__body">
        {{ $slot }}
    </div>
</div>
