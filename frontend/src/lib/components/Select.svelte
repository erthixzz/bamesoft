<script lang="ts">
  export let label = '';
  export let value: string = '';
  export let options: { value: string; label: string }[] = [];
  export let placeholder = '— Selecciona —';
  export let required = false;
  export let error: string | null = null;
</script>

<label class="block">
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">{label}</span>
  {/if}
  <select class="input" bind:value {required} on:change>
    <option value="">{placeholder}</option>
    {#each options as o}
      <option value={o.value}>{o.label}</option>
    {/each}
  </select>
  {#if error}
    <span class="mt-1 block text-xs text-danger-600">{error}</span>
  {/if}
</label>
