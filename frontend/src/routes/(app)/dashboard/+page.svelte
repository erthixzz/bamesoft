<script lang="ts">
  import { onMount } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  import { fly } from 'svelte/transition';
  import Card from '$lib/components/Card.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type { DashboardKPIs, ComplianceReport } from '$lib/modules/reports/types';
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
    Building2,
    ShieldCheck,
    PieChart,
  } from 'lucide-svelte';

  let kpis: DashboardKPIs | null = null;
  let compliance: ComplianceReport | null = null;
  let error: string | null = null;

  // Una sola tween 0→1 que dirige todas las animaciones (contadores, dona, barras).
  const anim = tweened(0, { duration: 1400, easing: cubicOut });

  onMount(async () => {
    setPageTitle('Dashboard');
    try {
      kpis = await reportsApi.dashboard();
      anim.set(1);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error cargando KPIs';
    }
    // El cumplimiento es opcional: si falla, simplemente no mostramos esa gráfica.
    try {
      compliance = await reportsApi.compliance();
    } catch {
      /* opcional */
    }
  });

  function greeting() {
    const h = new Date().getHours();
    if (h < 12) return 'Buenos días';
    if (h < 19) return 'Buenas tardes';
    return 'Buenas noches';
  }

  // Valores animados (cuentan hacia arriba con $anim).
  $: a = $anim;
  $: cu = (v: number | null | undefined) => Math.round((v ?? 0) * a);

  // ---- Dona: estado de equipos ----
  const DONUT_C = 2 * Math.PI * 52; // circunferencia (r = 52)
  $: donut = (() => {
    const total = kpis?.equipment_total ?? 0;
    const op = kpis?.equipment_operational ?? 0;
    const out = kpis?.equipment_out_of_service ?? 0;
    const other = Math.max(0, total - op - out);
    const raw = [
      { label: 'Operativos', value: op, color: '#10b981' },
      { label: 'Fuera de servicio', value: out, color: '#f43f5e' },
      { label: 'Otros estados', value: other, color: '#94a3b8' },
    ].filter((s) => s.value > 0);

    let acc = 0;
    const segs = raw.map((s) => {
      const frac = total ? s.value / total : 0;
      const seg = {
        ...s,
        frac,
        dash: frac * DONUT_C * a,
        offset: -acc * DONUT_C * a,
        pct: Math.round(frac * 100),
      };
      acc += frac;
      return seg;
    });
    return { total, segs };
  })();

  // ---- Barras: casos por estado ----
  $: caseBars = (() => {
    const items = [
      { label: 'Abiertos', value: kpis?.cases_open ?? 0, color: 'from-amber-400 to-amber-600' },
      { label: 'En progreso', value: kpis?.cases_in_progress ?? 0, color: 'from-brand-400 to-brand-600' },
      { label: 'Cerrados 30d', value: kpis?.cases_closed_30d ?? 0, color: 'from-emerald-400 to-emerald-600' },
    ];
    const max = Math.max(1, ...items.map((i) => i.value));
    return items.map((i) => ({ ...i, h: (i.value / max) * 100 * a, display: Math.round(i.value * a) }));
  })();
</script>

<!-- HERO de bienvenida -->
<div
  in:fly={{ y: 18, duration: 600, easing: cubicOut }}
  class="mb-3 overflow-hidden rounded-2xl border border-white/60 bg-gradient-to-br from-brand-600 via-brand-500 to-cyan-500 p-4 text-white shadow-lg sm:mb-4 sm:p-5"
>
  <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
    <div class="min-w-0">
      <p class="text-xs font-semibold uppercase tracking-wider text-white/80">{greeting()}</p>
      <h1 class="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xl font-bold sm:text-2xl">
        <span class="truncate">{$profile?.full_name ?? 'Bienvenido'}</span>
        {#if $profile?.clinic_name}
          <span
            class="inline-flex max-w-full items-center gap-1.5 rounded-full bg-white/15 py-1 pl-1.5 pr-2.5 text-xs font-semibold ring-1 ring-white/25 backdrop-blur"
          >
            <span class="grid h-4 w-4 shrink-0 place-items-center rounded-full bg-white/25">
              <Building2 class="h-2.5 w-2.5" />
            </span>
            <span class="truncate">{$profile.clinic_name}</span>
          </span>
        {/if}
      </h1>
    </div>
    <div class="flex flex-wrap gap-2">
      <a
        class="inline-flex items-center gap-2 rounded-lg bg-white/10 px-3.5 py-2 text-sm font-medium backdrop-blur transition hover:bg-white/20"
        href="/equipment/scan"
      >
        <QrCode class="h-4 w-4" /> Escanear QR
      </a>
      <a
        class="inline-flex items-center gap-2 rounded-lg bg-white px-3.5 py-2 text-sm font-medium text-brand-700 shadow-sm transition hover:bg-slate-50"
        href="/cases/new"
      >
        <PlusCircle class="h-4 w-4" /> Nuevo caso
      </a>
    </div>
  </div>
</div>

<!-- KPIs principales -->
<div class="grid gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-4">
  <div in:fly={{ y: 16, duration: 500, delay: 80, easing: cubicOut }}>
    <Card>
      <div class="flex items-start gap-3">
        <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-brand-50 text-brand-600">
          <Activity class="h-5 w-5" />
        </div>
        <div class="min-w-0">
          <p class="text-xs uppercase tracking-wider text-slate-500">Equipos</p>
          <p class="text-2xl font-bold tabular-nums text-slate-900">{kpis ? cu(kpis.equipment_total) : '—'}</p>
          <p class="truncate text-xs text-slate-500">
            <span class="text-emerald-600">{cu(kpis?.equipment_operational)} operativos</span>
            <span class="text-slate-400"> · </span>
            <span class="text-rose-600">{cu(kpis?.equipment_out_of_service)} fuera</span>
          </p>
        </div>
      </div>
    </Card>
  </div>

  <div in:fly={{ y: 16, duration: 500, delay: 150, easing: cubicOut }}>
    <Card>
      <div class="flex items-start gap-3">
        <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-amber-50 text-amber-600">
          <Wrench class="h-5 w-5" />
        </div>
        <div class="min-w-0">
          <p class="text-xs uppercase tracking-wider text-slate-500">Casos abiertos</p>
          <p class="text-2xl font-bold tabular-nums text-slate-900">
            {cu((kpis?.cases_open ?? 0) + (kpis?.cases_in_progress ?? 0))}
          </p>
          <p class="truncate text-xs text-slate-500">
            {cu(kpis?.cases_open)} abiertos · {cu(kpis?.cases_in_progress)} en progreso
          </p>
        </div>
      </div>
    </Card>
  </div>

  <div in:fly={{ y: 16, duration: 500, delay: 220, easing: cubicOut }}>
    <Card>
      <div class="flex items-start gap-3">
        <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-yellow-50 text-yellow-600">
          <AlertTriangle class="h-5 w-5" />
        </div>
        <div class="min-w-0">
          <p class="text-xs uppercase tracking-wider text-slate-500">Mant. preventivo (30d)</p>
          <p class="text-2xl font-bold tabular-nums text-slate-900">{cu(kpis?.preventive_due_30d)}</p>
          <p class="truncate text-xs text-slate-500">por vencer</p>
        </div>
      </div>
    </Card>
  </div>

  <div in:fly={{ y: 16, duration: 500, delay: 290, easing: cubicOut }}>
    <Card>
      <div class="flex items-start gap-3">
        <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-600">
          <CheckCircle2 class="h-5 w-5" />
        </div>
        <div class="min-w-0">
          <p class="text-xs uppercase tracking-wider text-slate-500">Calibraciones (30d)</p>
          <p class="text-2xl font-bold tabular-nums text-slate-900">{cu(kpis?.calibrations_due_30d)}</p>
          <p class="truncate text-xs text-slate-500">por vencer</p>
        </div>
      </div>
    </Card>
  </div>
</div>

{#if error}
  <p class="mt-4 text-sm text-danger-600">{error}</p>
{/if}

<!-- GRÁFICAS -->
<div class="mt-3 grid gap-3 sm:mt-4 sm:gap-4 lg:grid-cols-3">
  <!-- Dona: estado de equipos -->
  <div in:fly={{ y: 16, duration: 500, delay: 360, easing: cubicOut }}>
    <Card>
      <header class="mb-4 flex items-center gap-2">
        <PieChart class="h-4 w-4 text-brand-600" />
        <h3 class="text-base font-semibold text-slate-900">Estado de equipos</h3>
      </header>

      {#if donut.total === 0}
        <p class="py-8 text-center text-sm text-slate-400">Sin equipos registrados aún.</p>
      {:else}
        <div class="flex items-center gap-5">
          <div class="relative h-32 w-32 shrink-0">
            <svg viewBox="0 0 120 120" class="h-full w-full -rotate-90">
              <circle cx="60" cy="60" r="52" fill="none" stroke="#f1f5f9" stroke-width="14" />
              {#each donut.segs as s}
                <circle
                  cx="60"
                  cy="60"
                  r="52"
                  fill="none"
                  stroke={s.color}
                  stroke-width="14"
                  stroke-linecap="round"
                  stroke-dasharray="{s.dash} {DONUT_C}"
                  stroke-dashoffset={s.offset}
                />
              {/each}
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span class="text-2xl font-bold tabular-nums text-slate-900">{cu(donut.total)}</span>
              <span class="text-[10px] uppercase tracking-wider text-slate-500">equipos</span>
            </div>
          </div>

          <ul class="min-w-0 flex-1 space-y-2">
            {#each donut.segs as s}
              <li class="flex items-center gap-2 text-sm">
                <span class="h-2.5 w-2.5 shrink-0 rounded-full" style="background:{s.color}"></span>
                <span class="min-w-0 flex-1 truncate text-slate-600">{s.label}</span>
                <span class="shrink-0 font-semibold tabular-nums text-slate-900">{s.value}</span>
                <span class="shrink-0 text-xs text-slate-400">({s.pct}%)</span>
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    </Card>
  </div>

  <!-- Barras: casos por estado -->
  <div in:fly={{ y: 16, duration: 500, delay: 430, easing: cubicOut }}>
    <Card>
      <header class="mb-4 flex items-center gap-2">
        <BarChart3 class="h-4 w-4 text-brand-600" />
        <h3 class="text-base font-semibold text-slate-900">Casos por estado</h3>
      </header>

      <div class="flex h-32 items-end justify-around gap-4 px-2">
        {#each caseBars as b}
          <div class="flex h-full flex-1 flex-col items-center justify-end gap-2">
            <span class="text-sm font-bold tabular-nums text-slate-900">{b.display}</span>
            <div class="flex w-full max-w-[3.5rem] flex-1 items-end">
              <div
                class="w-full rounded-t-lg bg-gradient-to-t {b.color}"
                style="height:{b.h}%; min-height:4px"
              ></div>
            </div>
            <span class="text-center text-[11px] font-medium leading-tight text-slate-500">{b.label}</span>
          </div>
        {/each}
      </div>
    </Card>
  </div>

  <!-- Tiempo de cierre + acceso rápido -->
  <div in:fly={{ y: 16, duration: 500, delay: 500, easing: cubicOut }} class="space-y-3 sm:space-y-4">
    <Card>
      <div class="flex items-center gap-3">
        <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-700">
          <Clock class="h-5 w-5" />
        </div>
        <div>
          <p class="text-xs uppercase tracking-wider text-slate-500">Tiempo promedio de cierre</p>
          <p class="text-2xl font-bold tabular-nums text-slate-900">
            {kpis?.avg_close_time_hours != null ? (kpis.avg_close_time_hours * a).toFixed(1) : '—'}
            <span class="text-sm font-normal text-slate-500">h</span>
          </p>
          <p class="text-xs text-slate-400">Últimos 30 días</p>
        </div>
      </div>
    </Card>

    <Card title="Acceso rápido">
      <div class="space-y-2">
        {#each [['/equipment/scan', '📷', 'Escanear QR'], ['/cases', '🛠️', 'Ver casos'], ['/alerts', '🔔', 'Alertas']] as [href, icon, label]}
          <a
            {href}
            class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700"
          >
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
</div>

<!-- Cumplimiento por norma (datos reales del endpoint compliance) -->
{#if compliance && compliance.items.length > 0}
  <div in:fly={{ y: 16, duration: 500, delay: 570, easing: cubicOut }} class="mt-3 sm:mt-4">
    <Card>
      <header class="mb-4 flex items-center gap-2">
        <ShieldCheck class="h-4 w-4 text-brand-600" />
        <h3 class="text-base font-semibold text-slate-900">Cumplimiento por norma</h3>
      </header>

      <div class="space-y-3.5">
        {#each compliance.items as item}
          {@const pct = Math.round(item.coverage_pct * a)}
          <div>
            <div class="mb-1 flex items-baseline justify-between gap-2">
              <span class="min-w-0 truncate text-sm font-medium text-slate-700">
                <span class="font-semibold text-slate-900">{item.standard_code}</span>
                <span class="text-slate-400"> · </span>{item.standard_name}
              </span>
              <span class="shrink-0 text-sm font-bold tabular-nums text-slate-900">{pct}%</span>
            </div>
            <div class="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
              <div
                class="h-full rounded-full bg-gradient-to-r {item.coverage_pct >= 80
                  ? 'from-emerald-400 to-emerald-600'
                  : item.coverage_pct >= 50
                    ? 'from-amber-400 to-amber-500'
                    : 'from-rose-400 to-rose-600'}"
                style="width:{item.coverage_pct * a}%"
              ></div>
            </div>
            <p class="mt-1 text-xs text-slate-400">
              {item.equipment_with} de {item.equipment_total} equipos
            </p>
          </div>
        {/each}
      </div>
    </Card>
  </div>
{/if}
