<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type { DashboardKPIs } from '$lib/modules/reports/types';
  import { setPageTitle } from '$lib/stores/page';
  import { Wrench, AlertTriangle, Activity, CheckCircle2 } from 'lucide-svelte';

  let kpis: DashboardKPIs | null = null;
  let error: string | null = null;

  onMount(async () => {
    setPageTitle('Dashboard');
    try {
      kpis = await reportsApi.dashboard();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error cargando KPIs';
    }
  });
</script>

<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
  <Card title="Equipos">
    <div class="flex items-center gap-3">
      <Activity class="h-6 w-6 text-brand-600" />
      <div>
        <p class="text-2xl font-bold">{kpis?.equipment_total ?? '—'}</p>
        <p class="text-xs text-slate-500">
          {kpis?.equipment_operational ?? 0} operativos · {kpis?.equipment_out_of_service ?? 0} fuera
        </p>
      </div>
    </div>
  </Card>

  <Card title="Casos abiertos">
    <div class="flex items-center gap-3">
      <Wrench class="h-6 w-6 text-amber-500" />
      <div>
        <p class="text-2xl font-bold">{(kpis?.cases_open ?? 0) + (kpis?.cases_in_progress ?? 0)}</p>
        <p class="text-xs text-slate-500">
          {kpis?.cases_open ?? 0} abiertos · {kpis?.cases_in_progress ?? 0} en progreso
        </p>
      </div>
    </div>
  </Card>

  <Card title="Mant. preventivo (30d)">
    <div class="flex items-center gap-3">
      <AlertTriangle class="h-6 w-6 text-yellow-500" />
      <div>
        <p class="text-2xl font-bold">{kpis?.preventive_due_30d ?? 0}</p>
        <p class="text-xs text-slate-500">por vencer</p>
      </div>
    </div>
  </Card>

  <Card title="Calibraciones (30d)">
    <div class="flex items-center gap-3">
      <CheckCircle2 class="h-6 w-6 text-emerald-500" />
      <div>
        <p class="text-2xl font-bold">{kpis?.calibrations_due_30d ?? 0}</p>
        <p class="text-xs text-slate-500">por vencer</p>
      </div>
    </div>
  </Card>
</div>

{#if error}
  <p class="mt-4 text-sm text-danger-600">{error}</p>
{/if}

<div class="mt-6 grid gap-4 lg:grid-cols-3">
  <Card title="Tiempo promedio de cierre" description="Últimos 30 días">
    <p class="text-3xl font-bold">
      {kpis?.avg_close_time_hours?.toFixed(1) ?? '—'} <span class="text-base font-normal text-slate-500">h</span>
    </p>
  </Card>
  <Card title="Casos cerrados (30d)">
    <p class="text-3xl font-bold">{kpis?.cases_closed_30d ?? 0}</p>
  </Card>
  <Card title="Acceso rápido">
    <div class="flex flex-col gap-2">
      <a class="btn-secondary" href="/equipment/scan">📷 Escanear QR</a>
      <a class="btn-secondary" href="/cases">🛠️ Ver casos</a>
      <a class="btn-secondary" href="/alerts">🔔 Alertas</a>
    </div>
  </Card>
</div>
