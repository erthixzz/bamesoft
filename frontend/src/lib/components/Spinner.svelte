<script lang="ts">
  /** Spinner reutilizable.
   *  - `inline`  para botones / pequeñas líneas
   *  - `card`    bloque centrado con texto
   *  - `overlay` cubre la pantalla con backdrop semitransparente
   */
  export let label: string = 'Cargando…';
  export let variant: 'inline' | 'card' | 'overlay' = 'card';
  export let size: 'sm' | 'md' | 'lg' = 'md';

  const sizeMap = { sm: 'h-4 w-4', md: 'h-6 w-6', lg: 'h-10 w-10' } as const;
</script>

{#if variant === 'inline'}
  <span class="inline-flex items-center gap-2 text-sm text-slate-500">
    <span class={`inline-block ${sizeMap[size]} animate-spin rounded-full border-[2.5px] border-slate-200 border-t-brand-600`}></span>
    {#if label}{label}{/if}
  </span>
{:else if variant === 'overlay'}
  <div class="fixed inset-0 z-[90] grid place-items-center bg-white/60 backdrop-blur-sm">
    <div class="flex flex-col items-center gap-3 rounded-xl bg-white px-6 py-5 shadow-lg ring-1 ring-slate-200">
      <span class={`${sizeMap.lg} animate-spin rounded-full border-[3px] border-slate-200 border-t-brand-600`}></span>
      <span class="text-sm font-medium text-slate-700">{label}</span>
    </div>
  </div>
{:else}
  <div class="flex flex-col items-center justify-center gap-3 py-10">
    <span class={`${sizeMap[size]} animate-spin rounded-full border-[3px] border-slate-200 border-t-brand-600`}></span>
    {#if label}<span class="text-sm text-slate-500">{label}</span>{/if}
  </div>
{/if}
