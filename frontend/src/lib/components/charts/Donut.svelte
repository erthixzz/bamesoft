<script lang="ts">
  /** Gráfica de dona (SVG) con leyenda. `data`: [{label, value, color}]. */
  export let data: { label: string; value: number; color: string }[] = [];
  export let size = 150;
  export let unit = '';

  $: total = data.reduce((s, d) => s + d.value, 0);
  const R = 42;
  const C = 2 * Math.PI * R; // circunferencia (viewBox 0..100)

  // Segmentos como dash-offset acumulado.
  $: segments = (() => {
    let acc = 0;
    return data
      .filter((d) => d.value > 0)
      .map((d) => {
        const frac = total ? d.value / total : 0;
        const seg = { ...d, len: frac * C, off: acc, pct: Math.round(frac * 100) };
        acc += frac * C;
        return seg;
      });
  })();
</script>

<div class="flex items-center gap-4">
  <div class="relative shrink-0" style="width:{size}px;height:{size}px;">
    <svg viewBox="0 0 100 100" width={size} height={size} class="-rotate-90">
      <circle cx="50" cy="50" r={R} fill="none" stroke="#eef2f7" stroke-width="11" />
      {#each segments as s}
        <circle
          cx="50" cy="50" r={R} fill="none" stroke={s.color} stroke-width="11" stroke-linecap="round"
          stroke-dasharray="{s.len} {C - s.len}" stroke-dashoffset={-s.off}
        />
      {/each}
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center">
      <span class="text-2xl font-black tabular-nums text-slate-900">{total}</span>
      {#if unit}<span class="text-[10px] font-medium uppercase tracking-wide text-slate-400">{unit}</span>{/if}
    </div>
  </div>
  <ul class="min-w-0 flex-1 space-y-1.5">
    {#each segments as s}
      <li class="flex items-center gap-2 text-sm">
        <span class="h-2.5 w-2.5 shrink-0 rounded-full" style="background:{s.color}"></span>
        <span class="min-w-0 flex-1 truncate text-slate-600">{s.label}</span>
        <span class="tabular-nums font-semibold text-slate-800">{s.value}</span>
        <span class="w-9 text-right text-xs tabular-nums text-slate-400">{s.pct}%</span>
      </li>
    {:else}
      <li class="text-sm text-slate-400">Sin datos en el rango.</li>
    {/each}
  </ul>
</div>
