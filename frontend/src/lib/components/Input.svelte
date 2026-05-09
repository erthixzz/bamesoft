<script lang="ts">
  export let label = '';
  export let value: string | number = '';
  export let type: string = 'text';
  export let placeholder = '';
  export let required = false;
  export let error: string | null = null;
  export let id: string | null = null;
</script>

<label class="block">
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">{label}</span>
  {/if}
  <input
    {id}
    {type}
    {placeholder}
    {required}
    class="input"
    bind:value
    on:input
    on:change
  />
  {#if error}
    <span class="mt-1 block text-xs text-danger-600">{error}</span>
  {/if}
</label>
