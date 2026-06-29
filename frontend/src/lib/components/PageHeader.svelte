<script lang="ts">
  /** Cabecera de página estandarizada: icono + título + subtítulo + acciones. */
  import type { ComponentType } from 'svelte';

  export let title: string;
  export let subtitle: string | null = null;
  export let icon: ComponentType | null = null;
  export let gradient: 'brand' | 'cyan' | 'emerald' | 'amber' | 'rose' = 'brand';

  const gradientCls: Record<typeof gradient, string> = {
    brand:   'from-brand-600 to-cyan-500 shadow-brand-600/25',
    cyan:    'from-cyan-600 to-sky-500 shadow-cyan-600/25',
    emerald: 'from-emerald-600 to-teal-500 shadow-emerald-600/25',
    amber:   'from-amber-500 to-orange-500 shadow-amber-500/25',
    rose:    'from-rose-600 to-pink-500 shadow-rose-600/25',
  };
</script>

<div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
  <div class="flex items-center gap-3">
    {#if icon}
      <div class={`grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${gradientCls[gradient]} text-white shadow-md ring-1 ring-white/50`}>
        <svelte:component this={icon} class="h-5 w-5" />
      </div>
    {/if}
    <div class="min-w-0">
      <h1 class="truncate text-xl font-bold text-slate-900 sm:text-2xl">{title}</h1>
      {#if subtitle}
        <p class="truncate text-sm text-slate-500">{subtitle}</p>
      {/if}
    </div>
  </div>
  {#if $$slots.actions}
    <div class="flex flex-wrap gap-2 sm:shrink-0">
      <slot name="actions" />
    </div>
  {/if}
</div>
