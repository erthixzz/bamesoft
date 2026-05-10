<script lang="ts">
  import { onMount } from 'svelte';
  import Table from '$lib/components/Table.svelte';
  import CaseStatusBadge from '$lib/modules/cases/components/CaseStatusBadge.svelte';
  import PriorityBadge from '$lib/modules/cases/components/PriorityBadge.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case } from '$lib/modules/cases/types';
  import { formatDate } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';

  let rows: Case[] = [];
  const columns = [
    { key: 'code', label: 'Código' },
    { key: 'title', label: 'Título' },
    { key: 'type', label: 'Tipo' },
    { key: 'priority', label: 'Prioridad' },
    { key: 'status', label: 'Estado' },
    { key: 'opened_at', label: 'Apertura' },
  ];

  onMount(async () => {
    setPageTitle('Casos');
    try {
      rows = await casesApi.list();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error');
    }
  });
</script>

<div class="mb-4 flex justify-end">
  <a class="btn-primary" href="/cases/new">+ Nuevo caso</a>
</div>

<Table {columns} {rows}>
  <svelte:fragment slot="cell" let:row let:column>
    {#if column === 'status'}
      <CaseStatusBadge status={row.status} />
    {:else if column === 'priority'}
      <PriorityBadge priority={row.priority} />
    {:else if column === 'opened_at'}
      {formatDate(row.opened_at)}
    {:else if column === 'code'}
      <a class="font-medium text-brand-700 hover:underline" href={`/cases/${row.id}`}>{row.code}</a>
    {:else}
      {row[column] ?? '—'}
    {/if}
  </svelte:fragment>
</Table>
