<script lang="ts">
  export let label = '';
  export let value: string = '';
  export let type: string = 'text';
  export let placeholder = '';
  export let required = false;
  export let error: string | null = null;
  export let id: string | null = null;

  // Svelte no permite `bind:value` cuando `type` es dinámico, así que
  // sincronizamos manualmente el valor en el handler de input.
  function onInput(e: Event) {
    value = (e.currentTarget as HTMLInputElement).value;
  }
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
    {value}
    class="input"
    on:input={onInput}
    on:input
    on:change
  />
  {#if error}
    <span class="mt-1 block text-xs text-danger-600">{error}</span>
  {/if}
</label>
