@props([
    'name' => '',
    'label' => '',
    'placeholder' => '',
    'value' => '',
    'rows' => 4,
    'required' => false,
])

<div class="form-group">
    @if($label)
        <label for="{{ $name }}" class="form-label">{{ $label }}</label>
    @endif
    <textarea
        id="{{ $name }}"
        name="{{ $name }}"
        placeholder="{{ $placeholder }}"
        rows="{{ $rows }}"
        class="form-textarea"
        {{ $required ? 'required' : '' }}
        {{ $attributes }}
    >{{ $value }}</textarea>
</div>
