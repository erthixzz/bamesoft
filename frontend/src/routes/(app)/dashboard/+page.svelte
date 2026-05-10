<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type { DashboardKPIs } from '$lib/modules/reports/types';
  import { setPageTitle } from '$lib/stores/page';
  import { profile } from '$lib/stores/auth';
  import {
    Wrench,
    AlertTriangle,
    Activity,
    CheckCircle2,
    QrCode,
    BarChart3,
    Clock,
    PlusCircle,
    ArrowRight,
  } from 'lucide-svelte';

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

  function greeting() {
    const h = new Date().getHours();
    if (h < 12) return 'Buenos días';
    if (h < 19) return 'Buenas tardes';
    return 'Buenas noches';
  }
</script>

<!-- HERO de bienvenida -->
<div class="mb-6 overflow-hidden rounded-2xl border border-white/60 bg-gradient-to-br from-brand-600 via-brand-500 to-cyan-500 p-6 text-white shadow-lg sm:p-8">
  <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
    <div class="min-w-0">
      <p class="text-xs font-semibold uppercase tracking-wider text-white/80">{greeting()}</p>
      <h1 class="mt-1 truncate text-2xl font-bold sm:text-3xl">
        {$profile?.full_name ?? 'Bienvenido'}
      </h1>
      {#if $profile?.clinic_name}
        <p class="mt-1 text-sm text-white/80">
          🏥 {$profile.clinic_name}
        </p>
      {/if}
    </div>
    <div class="flex flex-wrap gap-2">
      <a class="inline-flex items-center gap-2 rounded-lg bg-white/10 px-4 py-2 text-sm font-medium backdrop-blur transition hover:bg-white/20" href="/equipment/scan">
        <QrCode class="h-4 w-4" /> Escanear QR
      </a>
      <a class="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-brand-700 shadow-sm transition hover:bg-slate-50" href="/cases/new">
        <PlusCircle class="h-4 w-4" /> Nuevo caso
      </a>
    </div>
  </div>
</div>

<!-- KPIs principales -->
<div class="grid gap-3 sm:gap-4 sm:grid-cols-2 lg:grid-cols-4">
  <Card>
    <div class="flex items-start gap-3">
      <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-brand-50 text-brand-600">
        <Activity class="h-5 w-5" />
      </div>
      <div class="min-w-0">
        <p class="text-xs uppercase tracking-wider text-slate-500">Equipos</p>
        <p class="text-2xl font-bold text-slate-900">{kpis?.equipment_total ?? '—'}</p>
        <p class="truncate text-xs text-slate-500">
          <span class="text-emerald-600">{kpis?.equipment_operational ?? 0} operativos</span>
          <span class="text-slate-400"> · </span>
          <span class="text-rose-600">{kpis?.equipment_out_of_service ?? 0} fuera</span>
        </p>
      </div>
    </div>
  </Card>

  <Card>
    <div class="flex items-start gap-3">
      <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-amber-50 text-amber-600">
        <Wrench class="h-5 w-5" />
      </div>
      <div class="min-w-0">
        <p class="text-xs uppercase tracking-wider text-slate-500">Casos abiertos</p>
        <p class="text-2xl font-bold text-slate-900">{(kpis?.cases_open ?? 0) + (kpis?.cases_in_progress ?? 0)}</p>
        <p class="truncate text-xs text-slate-500">
          {kpis?.cases_open ?? 0} abiertos · {kpis?.cases_in_progress ?? 0} en progreso
        </p>
      </div>
    </div>
  </Card>

  <Card>
    <div class="flex items-start gap-3">
      <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-yellow-50 text-yellow-600">
        <AlertTriangle class="h-5 w-5" />
      </div>
      <div class="min-w-0">
        <p class="text-xs uppercase tracking-wider text-slate-500">Mant. preventivo (30d)</p>
        <p class="text-2xl font-bold text-slate-900">{kpis?.preventive_due_30d ?? 0}</p>
        <p class="truncate text-xs text-slate-500">por vencer</p>
      </div>
    </div>
  </Card>

  <Card>
    <div class="flex items-start gap-3">
      <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-600">
        <CheckCircle2 class="h-5 w-5" />
      </div>
      <div class="min-w-0">
        <p class="text-xs uppercase tracking-wider text-slate-500">Calibraciones (30d)</p>
        <p class="text-2xl font-bold text-slate-900">{kpis?.calibrations_due_30d ?? 0}</p>
        <p class="truncate text-xs text-slate-500">por vencer</p>
      </div>
    </div>
  </Card>
</div>

{#if error}
  <p class="mt-4 text-sm text-danger-600">{error}</p>
{/if}

<!-- Bloque secundario -->
<div class="mt-4 grid gap-3 sm:gap-4 lg:grid-cols-3">
  <Card>
    <div class="flex items-center gap-3">
      <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-700">
        <Clock class="h-5 w-5" />
      </div>
      <div>
        <p class="text-xs uppercase tracking-wider text-slate-500">Tiempo promedio de cierre</p>
        <p class="text-2xl font-bold text-slate-900">
          {kpis?.avg_close_time_hours?.toFixed(1) ?? '—'} <span class="text-sm font-normal text-slate-500">h</span>
        </p>
        <p class="text-xs text-slate-400">Últimos 30 días</p>
      </div>
    </div>
  </Card>

  <Card>
    <div class="flex items-center gap-3">
      <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-600">
        <BarChart3 class="h-5 w-5" />
      </div>
      <div>
        <p class="text-xs uppercase tracking-wider text-slate-500">Cerrados (30d)</p>
        <p class="text-2xl font-bold text-slate-900">{kpis?.cases_closed_30d ?? 0}</p>
        <p class="text-xs text-slate-400">Casos finalizados</p>
      </div>
    </div>
  </Card>

  <Card title="Acceso rápido">
    <div class="space-y-2">
      {#each [['/equipment/scan', '📷', 'Escanear QR'], ['/cases', '🛠️', 'Ver casos'], ['/alerts', '🔔', 'Alertas']] as [href, icon, label]}
        <a href={href} class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700">
          <span class="flex items-center gap-2">
            <span class="text-lg">{icon}</span>
            {label}
          </span>
          <ArrowRight class="h-4 w-4" />
        </a>
      {/each}
    </div>
  </Card>
</div>
