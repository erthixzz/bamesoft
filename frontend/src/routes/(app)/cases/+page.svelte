<script lang="ts">
  import { onMount } from 'svelte';
  import Table from '$lib/components/Table.svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import CaseStatusBadge from '$lib/modules/cases/components/CaseStatusBadge.svelte';
  import PriorityBadge from '$lib/modules/cases/components/PriorityBadge.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case } from '$lib/modules/cases/types';
  import { formatDate } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { Wrench, PlusCircle } from 'lucide-svelte';

  let rows: Case[] = [];
  let loading = true;
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
    } finally {
      loading = false;
    }
  });
</script>

<PageHeader title="Casos" subtitle="Tickets de mantenimiento, calibración e inspección" icon={Wrench} gradient="amber">
  <svelte:fragment slot="actions">
    <a class="btn-primary" href="/cases/new">
      <PlusCircle class="h-4 w-4" /> Nuevo caso
    </a>
  </svelte:fragment>
</PageHeader>

<Card>
  {#if loading}
    <Spinner label="Cargando casos…" />
  {:else if rows.length === 0}
    <EmptyState
      icon={Wrench}
      title="Aún no hay casos"
      description="Crea el primer caso para reportar una falla, programar un mantenimiento o registrar una calibración."
    >
      <svelte:fragment slot="actions">
        <a class="btn-primary" href="/cases/new">+ Crear caso</a>
      </svelte:fragment>
    </EmptyState>
  {:else}
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
  {/if}
</Card>
