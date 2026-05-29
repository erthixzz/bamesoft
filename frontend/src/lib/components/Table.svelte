<script lang="ts">
  /* eslint-disable @typescript-eslint/no-explicit-any */
  import { contextmenu } from '$lib/actions/contextmenu';
  import type { CtxItem } from '$lib/stores/contextMenu';

  export let columns: { key: string; label: string; class?: string }[];
  export let rows: any[] = [];
  export let empty = 'Sin datos';
  /** Devuelve las acciones del menú contextual (click derecho / long-press) por fila. */
  export let rowMenu: ((row: any) => CtxItem[]) | null = null;
</script>

<div class="overflow-x-auto rounded-xl border border-slate-200 bg-white">
  <table class="w-full text-sm">
    <thead class="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
      <tr>
        {#each columns as c}
          <th class="px-4 py-3 font-medium {c.class ?? ''}">{c.label}</th>
        {/each}
      </tr>
    </thead>
    <tbody class="divide-y divide-slate-100">
      {#if rows.length === 0}
        <tr><td colspan={columns.length} class="px-4 py-8 text-center text-slate-400">{empty}</td></tr>
      {:else}
        {#each rows as row, i (i)}
          <tr
            class="transition-colors hover:bg-brand-50/40 {rowMenu ? 'cursor-context-menu' : ''}"
            use:contextmenu={rowMenu ? rowMenu(row) : []}
          >
            {#each columns as c}
              <td class="px-4 py-3 align-middle {c.class ?? ''}">
                <slot name="cell" {row} column={c.key}>
                  {row[c.key] ?? ''}
                </slot>
              </td>
            {/each}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>
