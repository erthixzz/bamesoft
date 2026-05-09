<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import Card from '$lib/components/Card.svelte';
  import StatusBadge from '$lib/modules/equipment/components/StatusBadge.svelte';
  import CaseStatusBadge from '$lib/modules/cases/components/CaseStatusBadge.svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { casesApi } from '$lib/modules/cases/api';
  import { calibrationsApi } from '$lib/modules/calibrations/api';
  import { maintenanceApi } from '$lib/modules/maintenance/api';
  import { documentsApi } from '$lib/modules/documents/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { Case } from '$lib/modules/cases/types';
  import type { Calibration } from '$lib/modules/calibrations/types';
  import type { MaintenanceSchedule } from '$lib/modules/maintenance/types';
  import type { Doc } from '$lib/modules/documents/types';
  import { formatDate } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';

  let id = '';
  let eq: Equipment | null = null;
  let cases: Case[] = [];
  let cals: Calibration[] = [];
  let pms: MaintenanceSchedule[] = [];
  let docs: Doc[] = [];
  let loading = true;
  let error: string | null = null;

  $: id = $page.params.id ?? '';
  $: setPageTitle(eq ? `${eq.code} · ${eq.name}` : 'Equipo');

  onMount(async () => {
    try {
      eq = await equipmentApi.get(id);
      [cases, cals, pms, docs] = await Promise.all([
        casesApi.list({ equipment_id: id }),
        calibrationsApi.forEquipment(id),
        maintenanceApi.forEquipment(id),
        documentsApi.forEquipment(id),
      ]);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error';
    } finally {
      loading = false;
    }
  });
</script>

{#if loading}
  <p class="text-slate-500">Cargando…</p>
{:else if error || !eq}
  <p class="text-danger-600">{error ?? 'No se encontró'}</p>
{:else}
  <div class="grid gap-4 lg:grid-cols-3">
    <Card title="Información general">
      <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <dt class="text-slate-500">Código</dt><dd class="font-medium">{eq.code}</dd>
        <dt class="text-slate-500">Estado</dt><dd><StatusBadge status={eq.status} /></dd>
        <dt class="text-slate-500">Marca</dt><dd>{eq.brand ?? '—'}</dd>
        <dt class="text-slate-500">Modelo</dt><dd>{eq.model ?? '—'}</dd>
        <dt class="text-slate-500">Serial</dt><dd>{eq.serial_number ?? '—'}</dd>
        <dt class="text-slate-500">Riesgo</dt><dd>{eq.risk_class ?? '—'}</dd>
        <dt class="text-slate-500">Adquirido</dt><dd>{formatDate(eq.acquisition_date)}</dd>
        <dt class="text-slate-500">Garantía</dt><dd>{formatDate(eq.warranty_until)}</dd>
      </dl>
    </Card>

    <Card title="QR">
      <img alt="QR" src={equipmentApi.qrPngUrl(eq.id)} class="mx-auto h-40 w-40" />
      <p class="mt-2 break-all text-center text-xs text-slate-500">token: {eq.qr_token}</p>
    </Card>

    <Card title="Notas">
      <p class="whitespace-pre-wrap text-sm text-slate-700">{eq.notes ?? 'Sin notas.'}</p>
    </Card>
  </div>

  <div class="mt-6 grid gap-4 lg:grid-cols-2">
    <Card title={`Casos (${cases.length})`}>
      <ul class="space-y-2">
        {#each cases as c}
          <li class="flex items-center justify-between border-b border-slate-100 py-2 last:border-0">
            <a class="text-sm font-medium text-brand-700 hover:underline" href={`/cases/${c.id}`}>
              {c.code} · {c.title}
            </a>
            <CaseStatusBadge status={c.status} />
          </li>
        {:else}
          <li class="text-sm text-slate-400">Sin casos.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Mantenimientos preventivos (${pms.length})`}>
      <ul class="space-y-2 text-sm">
        {#each pms as p}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{p.name} · cada {p.frequency_days}d</span>
            <span class="text-slate-500">próximo: {formatDate(p.next_due_at)}</span>
          </li>
        {:else}
          <li class="text-slate-400">Sin programación.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Calibraciones (${cals.length})`}>
      <ul class="space-y-2 text-sm">
        {#each cals as c}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{formatDate(c.performed_at)} · {c.standard ?? '—'}</span>
            <span class={c.passed ? 'text-emerald-600' : 'text-danger-600'}>
              {c.passed ? 'Pasó' : 'Falló'}
            </span>
          </li>
        {:else}
          <li class="text-slate-400">Sin registros.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Documentos (${docs.length})`}>
      <ul class="space-y-2 text-sm">
        {#each docs as d}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{d.title} <span class="text-xs text-slate-400">({d.type})</span></span>
            <span class="text-slate-500">{formatDate(d.created_at)}</span>
          </li>
        {:else}
          <li class="text-slate-400">Sin documentos.</li>
        {/each}
      </ul>
    </Card>
  </div>
{/if}
