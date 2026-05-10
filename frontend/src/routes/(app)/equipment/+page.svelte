<script lang="ts">
  import { onMount } from 'svelte';
  import Table from '$lib/components/Table.svelte';
  import Input from '$lib/components/Input.svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import StatusBadge from '$lib/modules/equipment/components/StatusBadge.svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import { formatDate } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { QrCode, Search, PlusCircle } from 'lucide-svelte';

  let rows: Equipment[] = [];
  let q = '';
  let loading = false;

  const columns = [
    { key: 'code', label: 'Código' },
    { key: 'name', label: 'Equipo' },
    { key: 'brand', label: 'Marca / Modelo' },
    { key: 'serial_number', label: 'Serial' },
    { key: 'status', label: 'Estado' },
    { key: 'created_at', label: 'Alta' },
  ];

  async function load() {
    loading = true;
    try {
      rows = await equipmentApi.list({ q });
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error cargando equipos');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Equipos');
    load();
  });
</script>

<PageHeader title="Equipos" subtitle="Inventario de equipos médicos" icon={QrCode} gradient="brand">
  <svelte:fragment slot="actions">
    <a class="btn-secondary" href="/equipment/scan">📷 Escanear QR</a>
    <a class="btn-primary" href="/equipment/new">
      <PlusCircle class="h-4 w-4" /> Nuevo equipo
    </a>
  </svelte:fragment>
</PageHeader>

<Card>
  <div class="mb-4 max-w-md">
    <Input placeholder="Buscar por código, nombre, serial o marca…" bind:value={q} on:input={load} />
  </div>

  {#if loading && rows.length === 0}
    <Spinner label="Cargando equipos…" />
  {:else if rows.length === 0}
    <EmptyState
      icon={Search}
      title={q ? 'Sin resultados' : 'Aún no hay equipos'}
      description={q
        ? 'Prueba con otro término de búsqueda.'
        : 'Registra el primer equipo de tu inventario para comenzar.'}
    >
      <svelte:fragment slot="actions">
        <a class="btn-primary" href="/equipment/new">+ Crear equipo</a>
      </svelte:fragment>
    </EmptyState>
  {:else}
    <Table {columns} {rows}>
      <svelte:fragment slot="cell" let:row let:column>
        {#if column === 'status'}
          <StatusBadge status={row.status} />
        {:else if column === 'brand'}
          {row.brand ?? '—'} <span class="text-slate-400">/</span> {row.model ?? '—'}
        {:else if column === 'created_at'}
          {formatDate(row.created_at)}
        {:else if column === 'code'}
          <a class="font-medium text-brand-700 hover:underline" href={`/equipment/${row.id}`}>
            {row.code}
          </a>
        {:else}
          {row[column] ?? '—'}
        {/if}
      </svelte:fragment>
    </Table>
  {/if}
</Card>
