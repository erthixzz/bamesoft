<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { fly, fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { fetchPublicEquipment } from '$lib/modules/public/api';
  import type { PublicEquipment } from '$lib/modules/public/types';
  import { formatDate } from '$lib/utils/format';
  import {
    Activity,
    AlertTriangle,
    Building2,
    CalendarClock,
    CheckCircle2,
    CircleSlash,
    Cpu,
    Gauge,
    MapPin,
    ShieldCheck,
    Wrench,
    XCircle,
    Hash,
  } from 'lucide-svelte';

  let data: PublicEquipment | null = null;
  let error: string | null = null;
  let loading = true;

  $: code = $page.params.code ?? '';
  $: token = $page.url.searchParams.get('t') ?? '';

  onMount(async () => {
    if (!token) {
      error = 'Falta el token del QR. Vuelve a escanear el código.';
      loading = false;
      return;
    }
    try {
      data = await fetchPublicEquipment(code, token);
    } catch (e) {
      error = e instanceof Error ? e.message : 'No se pudo cargar la información.';
    } finally {
      loading = false;
    }
  });

  // ---- Mapas de etiquetas / colores ----
  const EQ_STATUS: Record<string, { label: string; cls: string; dot: string }> = {
    operational: { label: 'Operativo', cls: 'bg-emerald-50 text-emerald-700 ring-emerald-200', dot: 'bg-emerald-500' },
    under_maintenance: { label: 'En mantenimiento', cls: 'bg-amber-50 text-amber-700 ring-amber-200', dot: 'bg-amber-500' },
    out_of_service: { label: 'Fuera de servicio', cls: 'bg-rose-50 text-rose-700 ring-rose-200', dot: 'bg-rose-500' },
    retired: { label: 'Retirado', cls: 'bg-slate-100 text-slate-600 ring-slate-300', dot: 'bg-slate-400' },
  };
  $: eqStatus = data ? (EQ_STATUS[data.status] ?? { label: data.status, cls: 'bg-slate-100 text-slate-600 ring-slate-300', dot: 'bg-slate-400' }) : null;

  const CASE_STATUS: Record<string, { label: string; cls: string }> = {
    open: { label: 'Abierto', cls: 'bg-amber-50 text-amber-700' },
    assigned: { label: 'Asignado', cls: 'bg-blue-50 text-blue-700' },
    in_progress: { label: 'En progreso', cls: 'bg-brand-50 text-brand-700' },
    waiting_parts: { label: 'Esperando repuestos', cls: 'bg-orange-50 text-orange-700' },
    waiting_client: { label: 'Esperando cliente', cls: 'bg-purple-50 text-purple-700' },
    closed: { label: 'Cerrado', cls: 'bg-emerald-50 text-emerald-700' },
    cancelled: { label: 'Cancelado', cls: 'bg-slate-100 text-slate-500' },
  };
  const CASE_TYPE: Record<string, string> = {
    corrective: 'Correctivo',
    preventive: 'Preventivo',
    calibration: 'Calibración',
    installation: 'Instalación',
    inspection: 'Inspección',
  };
  const PRIORITY: Record<string, { label: string; cls: string }> = {
    low: { label: 'Baja', cls: 'bg-slate-100 text-slate-600' },
    medium: { label: 'Media', cls: 'bg-blue-50 text-blue-700' },
    high: { label: 'Alta', cls: 'bg-orange-50 text-orange-700' },
    critical: { label: 'Crítica', cls: 'bg-rose-50 text-rose-700' },
  };

  function caseStatus(s: string) {
    return CASE_STATUS[s] ?? { label: s, cls: 'bg-slate-100 text-slate-600' };
  }
  function priority(p: string) {
    return PRIORITY[p] ?? { label: p, cls: 'bg-slate-100 text-slate-600' };
  }

  function isExpired(d: string | null): boolean {
    return !!d && new Date(d).getTime() < Date.now();
  }
</script>

<svelte:head>
  <title>{data ? `${data.code} · ${data.name}` : 'Equipo'} — Bamesoft</title>
  <meta name="robots" content="noindex" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-100">
  <!-- Barra de marca -->
  <header class="sticky top-0 z-10 border-b border-slate-200/70 bg-white/80 backdrop-blur-xl">
    <div class="mx-auto flex max-w-2xl items-center gap-2.5 px-4 py-3">
      <span class="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 text-sm font-black text-white shadow-sm">
        B
      </span>
      <div class="leading-tight">
        <p class="text-sm font-black tracking-tight text-slate-900">Bamesoft</p>
        <p class="text-[10px] font-bold uppercase tracking-[0.15em] text-brand-700">Ficha de equipo</p>
      </div>
    </div>
  </header>

  <main class="mx-auto max-w-2xl px-4 pb-16 pt-5">
    {#if loading}
      <!-- Skeleton -->
      <div class="space-y-4" in:fade>
        <div class="h-40 animate-pulse rounded-3xl bg-slate-200/70"></div>
        <div class="grid grid-cols-3 gap-3">
          {#each Array(3) as _}
            <div class="h-20 animate-pulse rounded-2xl bg-slate-200/70"></div>
          {/each}
        </div>
        <div class="h-48 animate-pulse rounded-2xl bg-slate-200/70"></div>
      </div>
    {:else if error}
      <div
        in:fly={{ y: 16, duration: 400 }}
        class="mt-10 rounded-3xl border border-rose-200 bg-rose-50/70 p-8 text-center"
      >
        <div class="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-rose-100 text-rose-600">
          <AlertTriangle class="h-7 w-7" />
        </div>
        <h1 class="text-lg font-bold text-slate-900">No se pudo abrir la ficha</h1>
        <p class="mt-2 text-sm text-slate-600">{error}</p>
      </div>
    {:else if data}
      <!-- HERO del equipo -->
      <section
        in:fly={{ y: 18, duration: 500, easing: cubicOut }}
        class="relative overflow-hidden rounded-3xl border border-white/60 bg-gradient-to-br from-brand-600 via-brand-500 to-cyan-500 p-6 text-white shadow-xl shadow-brand-600/20"
      >
        <div class="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/15 blur-2xl"></div>

        <div class="relative flex items-start gap-4">
          {#if data.image_url}
            <img src={data.image_url} alt={data.name} class="h-16 w-16 shrink-0 rounded-2xl object-cover ring-2 ring-white/40" />
          {:else}
            <div class="grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-white/15 ring-2 ring-white/30">
              <Cpu class="h-8 w-8" />
            </div>
          {/if}
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-1.5 text-xs font-semibold text-white/80">
              <Hash class="h-3.5 w-3.5" />
              {data.code}
            </div>
            <h1 class="mt-0.5 text-2xl font-bold leading-tight">{data.name}</h1>
            {#if eqStatus}
              <span class="mt-2 inline-flex items-center gap-1.5 rounded-full bg-white/15 px-2.5 py-1 text-xs font-bold ring-1 ring-white/25 backdrop-blur">
                <span class="h-1.5 w-1.5 rounded-full {eqStatus.dot}"></span>
                {eqStatus.label}
              </span>
            {/if}
          </div>
        </div>

        <div class="relative mt-4 flex flex-wrap gap-x-4 gap-y-1.5 text-sm text-white/90">
          {#if data.clinic_name}
            <span class="inline-flex items-center gap-1.5"><Building2 class="h-4 w-4 text-white/70" />{data.clinic_name}</span>
          {/if}
          {#if data.location_name}
            <span class="inline-flex items-center gap-1.5"><MapPin class="h-4 w-4 text-white/70" />{data.location_name}</span>
          {/if}
        </div>
      </section>

      <!-- Stats rápidas -->
      <section in:fly={{ y: 16, duration: 500, delay: 80, easing: cubicOut }} class="mt-4 grid grid-cols-3 gap-3">
        <div class="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
          <Wrench class="mx-auto mb-1 h-5 w-5 text-amber-500" />
          <p class="text-2xl font-black tabular-nums text-slate-900">{data.cases_open}</p>
          <p class="text-[11px] font-medium text-slate-500">casos abiertos</p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
          <CalendarClock class="mx-auto mb-1 h-5 w-5 text-brand-500" />
          <p class="text-2xl font-black tabular-nums text-slate-900">{data.maintenance.length}</p>
          <p class="text-[11px] font-medium text-slate-500">mantenimientos</p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
          <Gauge class="mx-auto mb-1 h-5 w-5 text-emerald-500" />
          <p class="text-2xl font-black tabular-nums text-slate-900">{data.calibrations.length}</p>
          <p class="text-[11px] font-medium text-slate-500">calibraciones</p>
        </div>
      </section>

      <!-- Especificaciones -->
      <section in:fly={{ y: 16, duration: 500, delay: 140, easing: cubicOut }} class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 class="mb-3 flex items-center gap-2 text-sm font-bold text-slate-900">
          <Activity class="h-4 w-4 text-brand-600" /> Información general
        </h2>
        <dl class="grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
          {#each [
            ['Marca', data.brand],
            ['Modelo', data.model],
            ['Serial', data.serial_number],
            ['Fabricante', data.manufacturer],
            ['Clase de riesgo', data.risk_class],
            ['Categoría', data.category_name],
            ['Adquisición', data.acquisition_date ? formatDate(data.acquisition_date) : null],
            ['Garantía', data.warranty_until ? formatDate(data.warranty_until) : null],
          ] as [label, value]}
            <div class="min-w-0">
              <dt class="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</dt>
              <dd class="truncate font-semibold text-slate-800">{value ?? '—'}</dd>
            </div>
          {/each}
        </dl>
      </section>

      <!-- Casos -->
      {#if data.cases.length > 0}
        <section in:fly={{ y: 16, duration: 500, delay: 200, easing: cubicOut }} class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-3 flex items-center gap-2 text-sm font-bold text-slate-900">
            <Wrench class="h-4 w-4 text-amber-500" /> Casos
            <span class="text-slate-400">({data.cases_total})</span>
          </h2>
          <ul class="space-y-2.5">
            {#each data.cases as c}
              <li class="rounded-xl border border-slate-100 bg-slate-50/60 p-3">
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <p class="truncate text-sm font-semibold text-slate-900">{c.title}</p>
                    <p class="mt-0.5 text-xs text-slate-500">
                      {c.code} · {CASE_TYPE[c.type] ?? c.type}
                      {#if c.opened_at}· {formatDate(c.opened_at)}{/if}
                    </p>
                  </div>
                  <div class="flex shrink-0 flex-col items-end gap-1">
                    <span class="rounded-full px-2 py-0.5 text-[10px] font-bold {caseStatus(c.status).cls}">{caseStatus(c.status).label}</span>
                    <span class="rounded-full px-2 py-0.5 text-[10px] font-semibold {priority(c.priority).cls}">{priority(c.priority).label}</span>
                  </div>
                </div>
              </li>
            {/each}
          </ul>
        </section>
      {/if}

      <!-- Mantenimientos -->
      {#if data.maintenance.length > 0}
        <section in:fly={{ y: 16, duration: 500, delay: 260, easing: cubicOut }} class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-3 flex items-center gap-2 text-sm font-bold text-slate-900">
            <CalendarClock class="h-4 w-4 text-brand-600" /> Mantenimientos preventivos
          </h2>
          <ul class="space-y-2.5">
            {#each data.maintenance as m}
              <li class="flex items-center justify-between gap-2 rounded-xl border border-slate-100 bg-slate-50/60 p-3">
                <div class="min-w-0">
                  <p class="truncate text-sm font-semibold text-slate-900">{m.name}</p>
                  <p class="text-xs text-slate-500">cada {m.frequency_days} días</p>
                </div>
                <div class="shrink-0 text-right">
                  <p class="text-[10px] uppercase tracking-wide text-slate-400">Próximo</p>
                  <p class="text-sm font-semibold {isExpired(m.next_due_at) ? 'text-rose-600' : 'text-slate-800'}">
                    {m.next_due_at ? formatDate(m.next_due_at) : '—'}
                  </p>
                </div>
              </li>
            {/each}
          </ul>
        </section>
      {/if}

      <!-- Calibraciones -->
      {#if data.calibrations.length > 0}
        <section in:fly={{ y: 16, duration: 500, delay: 320, easing: cubicOut }} class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-3 flex items-center gap-2 text-sm font-bold text-slate-900">
            <ShieldCheck class="h-4 w-4 text-emerald-600" /> Calibraciones
          </h2>
          <ul class="space-y-2.5">
            {#each data.calibrations as c}
              <li class="flex items-center justify-between gap-2 rounded-xl border border-slate-100 bg-slate-50/60 p-3">
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-slate-900">{formatDate(c.performed_at)}</p>
                  <p class="truncate text-xs text-slate-500">
                    {c.standard ?? 'Sin norma'}
                    {#if c.expires_at}· vence {formatDate(c.expires_at)}{/if}
                  </p>
                </div>
                {#if c.passed}
                  <span class="inline-flex shrink-0 items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700">
                    <CheckCircle2 class="h-3.5 w-3.5" /> Pasó
                  </span>
                {:else}
                  <span class="inline-flex shrink-0 items-center gap-1 rounded-full bg-rose-50 px-2.5 py-1 text-xs font-bold text-rose-700">
                    <XCircle class="h-3.5 w-3.5" /> Falló
                  </span>
                {/if}
              </li>
            {/each}
          </ul>
        </section>
      {/if}

      <!-- Notas -->
      {#if data.notes}
        <section in:fly={{ y: 16, duration: 500, delay: 380, easing: cubicOut }} class="mt-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-2 text-sm font-bold text-slate-900">Notas</h2>
          <p class="whitespace-pre-wrap text-sm leading-relaxed text-slate-600">{data.notes}</p>
        </section>
      {/if}

      <!-- Sin actividad -->
      {#if data.cases.length === 0 && data.maintenance.length === 0 && data.calibrations.length === 0}
        <section in:fade class="mt-4 rounded-2xl border border-dashed border-slate-300 bg-white/60 p-8 text-center">
          <CircleSlash class="mx-auto mb-2 h-8 w-8 text-slate-300" />
          <p class="text-sm font-medium text-slate-500">Este equipo aún no tiene casos, mantenimientos ni calibraciones registrados.</p>
        </section>
      {/if}

      <p class="mt-8 text-center text-xs text-slate-400">
        Información protegida · <span class="font-semibold text-slate-500">Bamesoft Solutions</span>
      </p>
    {/if}
  </main>
</div>
