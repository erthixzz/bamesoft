<script lang="ts">
  /** Tarjeta del sistema de diseño Bamesoft.
   *  Soporta cabecera con ícono + acento de color (opcional, retrocompatible)
   *  para un look más profesional/biomédico en vez de un bloque plano. */
  import type { ComponentType } from 'svelte';

  export let title: string | null = null;
  export let description: string | null = null;
  export let icon: ComponentType | null = null;
  export let accent: 'brand' | 'cyan' | 'emerald' | 'amber' | 'rose' | 'violet' | 'slate' = 'brand';
  export let interactive = false;

  const accentCls: Record<typeof accent, string> = {
    brand: 'from-brand-500 to-cyan-500',
    cyan: 'from-cyan-500 to-sky-500',
    emerald: 'from-emerald-500 to-teal-500',
    amber: 'from-amber-500 to-orange-500',
    rose: 'from-rose-500 to-pink-500',
    violet: 'from-violet-500 to-purple-500',
    slate: 'from-slate-500 to-slate-400',
  };
</script>

<div class="card {interactive ? 'card-interactive' : ''}">
  {#if title}
    <header class="mb-4 flex items-start justify-between gap-4">
      <div class="flex min-w-0 items-center gap-3">
        {#if icon}
          <div
            class={`grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-gradient-to-br ${accentCls[accent]} text-white shadow-sm`}
          >
            <svelte:component this={icon} class="h-[18px] w-[18px]" />
          </div>
        {/if}
        <div class="min-w-0">
          <h3 class="truncate text-base font-semibold text-slate-900">{title}</h3>
          {#if description}
            <p class="truncate text-sm text-slate-500">{description}</p>
          {/if}
        </div>
      </div>
      <slot name="actions" />
    </header>
  {/if}
  <slot />
</div>
