<script lang="ts">
  export let label = '';
  export let value: string = '';
  export let placeholder = '';
  export let rows = 3;
  export let required = false;
  export let error: string | null = null;
</script>

<label class="block">
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">
      {label}{#if required}<span class="text-danger-500"> *</span>{/if}
    </span>
  {/if}
  <textarea
    class="input {error ? 'border-danger-400 focus:border-danger-500 focus:ring-danger-500/40' : ''}"
    {rows}
    {placeholder}
    bind:value
    on:input
    on:change
  ></textarea>
  {#if error}
    <span class="mt-1 block text-xs text-danger-600">{error}</span>
  {/if}
</label>
