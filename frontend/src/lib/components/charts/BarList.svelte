<script lang="ts">
  /** Barras horizontales con etiqueta + valor. `data`: [{label, value, color?}]. */
  export let data: { label: string; value: number; color?: string }[] = [];
  export let suffix = '';
  export let accent = '#1971f5';

  $: max = Math.max(1, ...data.map((d) => d.value));
</script>

<ul class="space-y-2.5">
  {#each data as d}
    <li>
      <div class="mb-1 flex items-center justify-between gap-2 text-sm">
        <span class="min-w-0 truncate text-slate-600">{d.label}</span>
        <span class="shrink-0 tabular-nums font-semibold text-slate-800">{d.value}{suffix}</span>
      </div>
      <div class="h-2.5 overflow-hidden rounded-full bg-slate-100">
        <div
          class="h-2.5 rounded-full transition-all"
          style="width:{(d.value / max) * 100}%;background:{d.color ?? accent}"
        ></div>
      </div>
    </li>
  {:else}
    <li class="text-sm text-slate-400">Sin datos en el rango.</li>
  {/each}
</ul>
