<script lang="ts">
  /** Lista de resultados del buscador global (compartida desktop/móvil). */
  import { createEventDispatcher } from 'svelte';
  import type { ComponentType } from 'svelte';
  import type { SearchResult, SearchType } from '$lib/modules/search/types';
  import { CornerDownLeft } from 'lucide-svelte';

  export let groups: { type: SearchType; label: string; icon: ComponentType; tone: string; items: SearchResult[] }[] = [];
  export let ordered: SearchResult[] = [];
  export let active = -1;
  export let loading = false;
  export let q = '';

  const dispatch = createEventDispatcher<{ pick: SearchResult; hover: number }>();
</script>

{#if loading && ordered.length === 0}
  <p class="px-4 py-6 text-center text-sm text-slate-400">Buscando…</p>
{:else if ordered.length === 0}
  <p class="px-4 py-6 text-center text-sm text-slate-400">Sin resultados para «{q.trim()}»</p>
{:else}
  {#each groups as g (g.type)}
    <p class="px-3 pb-1 pt-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">{g.label}</p>
    {#each g.items as r (r.type + r.id)}
      {@const idx = ordered.indexOf(r)}
      <button
        type="button"
        class="flex w-full items-center gap-3 px-3 py-2 text-left transition {idx === active ? 'bg-brand-50' : 'hover:bg-slate-50'}"
        on:click={() => dispatch('pick', r)}
        on:mouseenter={() => dispatch('hover', idx)}
      >
        <span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg {g.tone}">
          <svelte:component this={g.icon} class="h-4 w-4" />
        </span>
        <span class="min-w-0 flex-1">
          <span class="block truncate text-sm font-medium text-slate-800">{r.title}</span>
          {#if r.subtitle}
            <span class="block truncate text-xs text-slate-400">{r.subtitle}</span>
          {/if}
        </span>
        {#if idx === active}
          <CornerDownLeft class="h-3.5 w-3.5 shrink-0 text-slate-300" />
        {/if}
      </button>
    {/each}
  {/each}
{/if}
