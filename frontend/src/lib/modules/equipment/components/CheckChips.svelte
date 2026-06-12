<script lang="ts">
  /** Grupo de casillas tipo "chip" multi-selección, estilo Bamesoft.
   *  Enlaza un array de strings (los `value` seleccionados). */
  import { Check } from 'lucide-svelte';

  export let label = '';
  export let options: { value: string; label: string }[] = [];
  export let value: string[] = [];
  export let readonly = false;

  function toggle(v: string) {
    if (readonly) return;
    value = value.includes(v) ? value.filter((x) => x !== v) : [...value, v];
  }
</script>

<div>
  {#if label}
    <span class="mb-1.5 block text-sm font-medium text-slate-700">{label}</span>
  {/if}
  <div class="flex flex-wrap gap-2">
    {#each options as o}
      {@const active = value.includes(o.value)}
      <button
        type="button"
        disabled={readonly}
        on:click={() => toggle(o.value)}
        class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium transition
          {active
            ? 'border-brand-500 bg-brand-50 text-brand-700'
            : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50'}
          {readonly ? 'cursor-default' : ''}"
      >
        {#if active}<Check class="h-3.5 w-3.5" />{/if}
        {o.label}
      </button>
    {/each}
  </div>
</div>
