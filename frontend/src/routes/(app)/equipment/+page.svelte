<script lang="ts">
  import { onMount } from 'svelte';
  import Table from '$lib/components/Table.svelte';
  import Input from '$lib/components/Input.svelte';
  import StatusBadge from '$lib/modules/equipment/components/StatusBadge.svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import { formatDate } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';

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

<div class="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
  <div class="w-full sm:max-w-sm sm:flex-1">
    <Input placeholder="Buscar por código, nombre, serial…" bind:value={q} on:input={load} />
  </div>
  <div class="flex flex-wrap gap-2 sm:ml-auto">
    <a class="btn-secondary flex-1 sm:flex-none" href="/equipment/scan">📷 Escanear QR</a>
    <a class="btn-primary flex-1 sm:flex-none" href="/equipment/new">+ Nuevo equipo</a>
  </div>
</div>

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
