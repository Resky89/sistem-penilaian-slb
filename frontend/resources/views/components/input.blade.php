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
    <input
        type="{{ $type }}"
        id="{{ $name }}"
        name="{{ $name }}"
        value="{{ $value }}"
        placeholder="{{ $placeholder }}"
        class="form-input"
        {{ $required ? 'required' : '' }}
        {{ $attributes }}
    >
    <div class="invalid-feedback" id="error-{{ $name }}" style="display: none; font-size: 0.8rem; color: var(--color-danger); margin-top: 4px; font-weight: 500;"></div>
</div>
