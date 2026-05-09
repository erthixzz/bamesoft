<script lang="ts">
  /* eslint-disable @typescript-eslint/no-explicit-any */
  export let columns: { key: string; label: string; class?: string }[];
  export let rows: any[] = [];
  export let empty = 'Sin datos';
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
          <tr class="hover:bg-slate-50">
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
