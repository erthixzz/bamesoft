<script lang="ts">
  import { onMount } from 'svelte';
  import Table from '$lib/components/Table.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import StatusBadge from '$lib/modules/equipment/components/StatusBadge.svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { Sector } from '$lib/modules/sectors/types';
  import type { CtxItem } from '$lib/stores/contextMenu';
  import { formatDate } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { QrCode, Search, PlusCircle, Eye, Pencil, Copy, RefreshCw, Layers } from 'lucide-svelte';

  let rows: Equipment[] = [];
  let sectors: Sector[] = [];
  let q = '';
  let sectorFilter = '';
  let groupByUnit = false;
  let loading = false;

  $: sectorName = Object.fromEntries(sectors.map((s) => [s.id, s.name]));
  $: sectorOptions = [
    { value: '', label: 'Todas las unidades' },
    ...sectors.map((s) => ({ value: s.id, label: s.name })),
  ];

  const columns = [
    { key: 'code', label: 'Código' },
    { key: 'name', label: 'Equipo' },
    { key: 'sector_id', label: 'Unidad de servicio' },
    { key: 'brand', label: 'Marca / Modelo' },
    { key: 'status', label: 'Estado' },
    { key: 'created_at', label: 'Alta' },
  ];

  /** Filas agrupadas por unidad de servicio (para la vista agrupada). */
  $: groups = (() => {
    const map = new Map<string, Equipment[]>();
    for (const r of rows) {
      const key = r.sector_id ?? '__none__';
      (map.get(key) ?? map.set(key, []).get(key)!).push(r);
    }
    return [...map.entries()].map(([key, items]) => ({
      key,
      label: key === '__none__' ? 'Sin unidad asignada' : (sectorName[key] ?? 'Unidad'),
      items,
    }));
  })();

  async function load() {
    loading = true;
    try {
      rows = await equipmentApi.list({ q, sector_id: sectorFilter || undefined });
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error cargando equipos');
    } finally {
      loading = false;
    }
  }

  async function copy(text: string, label = 'Copiado') {
    try {
      await navigator.clipboard.writeText(text);
      toasts.success(label);
    } catch {
      toasts.error('No se pudo copiar');
    }
  }

  async function regenerateQr(row: Equipment) {
    try {
      await equipmentApi.regenerateQr(row.id);
      toasts.success(`QR regenerado para ${row.code}`);
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error regenerando QR');
    }
  }

  const rowMenu = (row: Equipment): CtxItem[] => [
    { label: 'Ver detalle', icon: Eye, href: `/equipment/${row.code}` },
    { label: 'Editar', icon: Pencil, href: `/equipment/${row.code}?edit=1` },
    { divider: true },
    { label: 'Copiar código', icon: Copy, onClick: () => copy(row.code, 'Código copiado') },
    { label: 'Regenerar QR', icon: RefreshCw, onClick: () => regenerateQr(row) },
  ];

  onMount(async () => {
    setPageTitle('Equipos');
    sectors = await sectorsApi.list().catch(() => []);
    await load();
  });
</script>

<PageHeader title="Equipos" subtitle="Inventario de equipos médicos por unidad de servicio" icon={QrCode} gradient="brand">
  <svelte:fragment slot="actions">
    <a class="btn-secondary" href="/equipment/scan">📷 Escanear QR</a>
    <a class="btn-primary" href="/equipment/new">
      <PlusCircle class="h-4 w-4" /> Nuevo equipo
    </a>
  </svelte:fragment>
</PageHeader>

<Card>
  <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
    <div class="flex-1">
      <Input placeholder="Buscar por código, nombre, serial o marca…" bind:value={q} on:input={load} />
    </div>
    <div class="w-full sm:w-56">
      <Select bind:value={sectorFilter} options={sectorOptions} placeholder="Todas las unidades" on:change={load} />
    </div>
    <button
      type="button"
      class="btn-secondary {groupByUnit ? 'ring-1 ring-brand-500' : ''}"
      on:click={() => (groupByUnit = !groupByUnit)}
    >
      <Layers class="h-4 w-4" /> Agrupar por unidad
    </button>
  </div>

  {#if loading && rows.length === 0}
    <Spinner label="Cargando equipos…" />
  {:else if rows.length === 0}
    <EmptyState
      icon={Search}
      title={q || sectorFilter ? 'Sin resultados' : 'Aún no hay equipos'}
      description={q || sectorFilter
        ? 'Prueba con otro término o cambia el filtro de unidad.'
        : 'Registra el primer equipo de tu inventario para comenzar.'}
    >
      <svelte:fragment slot="actions">
        <a class="btn-primary" href="/equipment/new">+ Crear equipo</a>
      </svelte:fragment>
    </EmptyState>
  {:else if groupByUnit}
    {#each groups as g (g.key)}
      <div class="mb-6">
        <h3 class="mb-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
          <Layers class="h-4 w-4 text-brand-600" />
          {g.label}
          <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500">{g.items.length}</span>
        </h3>
        <Table {columns} rows={g.items} {rowMenu}>
          <svelte:fragment slot="cell" let:row let:column>
            {#if column === 'status'}
              <StatusBadge status={row.status} />
            {:else if column === 'sector_id'}
              {row.sector_id ? (sectorName[row.sector_id] ?? '—') : '—'}
            {:else if column === 'brand'}
              {row.brand ?? '—'} <span class="text-slate-400">/</span> {row.model ?? '—'}
            {:else if column === 'created_at'}
              {formatDate(row.created_at)}
            {:else if column === 'code'}
              <a class="font-medium text-brand-700 hover:underline" href={`/equipment/${row.code}`}>{row.code}</a>
            {:else}
              {row[column] ?? '—'}
            {/if}
          </svelte:fragment>
        </Table>
      </div>
    {/each}
  {:else}
    <Table {columns} {rows} {rowMenu}>
      <svelte:fragment slot="cell" let:row let:column>
        {#if column === 'status'}
          <StatusBadge status={row.status} />
        {:else if column === 'sector_id'}
          {row.sector_id ? (sectorName[row.sector_id] ?? '—') : '—'}
        {:else if column === 'brand'}
          {row.brand ?? '—'} <span class="text-slate-400">/</span> {row.model ?? '—'}
        {:else if column === 'created_at'}
          {formatDate(row.created_at)}
        {:else if column === 'code'}
          <a class="font-medium text-brand-700 hover:underline" href={`/equipment/${row.code}`}>
            {row.code}
          </a>
        {:else}
          {row[column] ?? '—'}
        {/if}
      </svelte:fragment>
    </Table>
  {/if}
</Card>
