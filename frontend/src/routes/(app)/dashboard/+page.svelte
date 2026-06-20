<script lang="ts">
  import { onMount } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  import { fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import Card from '$lib/components/Card.svelte';
  import Select from '$lib/components/Select.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import CaseBoardCard from '$lib/modules/cases/components/CaseBoardCard.svelte';
  import CaseEditModal from '$lib/modules/cases/components/CaseEditModal.svelte';
  import CaseLegendModal from '$lib/modules/cases/components/CaseLegendModal.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case } from '$lib/modules/cases/types';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { usersApi } from '$lib/modules/users/api';
  import type { User } from '$lib/modules/users/types';
  import {
    PRIORITY_META,
    STATUS_GROUPS,
    STATUS_GROUP_OPTIONS,
    PRIORITY_OPTIONS,
    isActive,
    isAging,
    slaInfo,
  } from '$lib/modules/cases/ui';
  import type { CasePriority } from '$lib/api/types';
  import { tooltip } from '$lib/actions/tooltip';
  import { setPageTitle } from '$lib/stores/page';
  import { profile } from '$lib/stores/auth';
  import {
    QrCode,
    PlusCircle,
    Building2,
    LayoutGrid,
    Search,
    Wrench,
    Activity,
    UserMinus,
    AlarmClock,
    Timer,
    BarChart3,
    SignalHigh,
    HelpCircle,
  } from 'lucide-svelte';

  let cases: Case[] = [];
  let engineers: User[] = [];
  let equipmentNameById: Record<string, string> = {};
  let loading = true;
  let error: string | null = null;

  // Filtros
  let fStatusGroup = '';
  let fAssignee = '';
  let fPriority = '';
  let search = '';

  // Modales
  let editOpen = false;
  let editCase: Case | null = null;
  let legendOpen = false;

  const anim = tweened(0, { duration: 1000, easing: cubicOut });
  $: a = $anim;

  onMount(async () => {
    setPageTitle('Dashboard');
    try {
      const [cs, us, eq] = await Promise.all([
        casesApi.list({ limit: 200 }),
        usersApi.list().catch(() => [] as User[]),
        equipmentApi.list({ limit: 300 }).catch(() => []),
      ]);
      cases = cs;
      engineers = us.filter(
        (u) => u.active !== false && ['admin', 'engineer', 'service', 'support'].includes(u.role),
      );
      equipmentNameById = Object.fromEntries(eq.map((e) => [e.id, `${e.code} · ${e.name}`]));
      anim.set(1);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error cargando el panel';
    } finally {
      loading = false;
    }
  });

  function greeting() {
    const h = new Date().getHours();
    if (h < 12) return 'Buenos días';
    if (h < 19) return 'Buenas tardes';
    return 'Buenas noches';
  }

  // Reemplaza un caso tras un cambio en línea o en el modal (dispara reactividad).
  function upsert(updated: Case) {
    cases = cases.map((c) => (c.id === updated.id ? updated : c));
  }
  function openEdit(c: Case) {
    editCase = c;
    editOpen = true;
  }

  // ---- KPIs (todo derivado de `cases` → en tiempo real) ----
  $: activeCases = cases.filter(isActive);
  $: kActive = activeCases.length;
  $: kInProgress = cases.filter((c) => c.status === 'in_progress').length;
  $: kUnassigned = activeCases.filter((c) => !c.assigned_to).length;
  $: kSlaRisk = activeCases.filter((c) => {
    const s = slaInfo(c).state;
    return s === 'overdue' || s === 'soon';
  }).length;

  // Tiempo prom. de cierre (live): media de (closed_at − opened_at) de los casos
  // cerrados en los últimos 30 días. 0 si no hay ninguno.
  $: closedRecent = cases.filter(
    (c) =>
      c.status === 'closed' &&
      c.opened_at &&
      c.closed_at &&
      (Date.now() - new Date(c.closed_at).getTime()) / 86_400_000 <= 30,
  );
  $: avgClose = closedRecent.length
    ? closedRecent.reduce(
        (s, c) => s + (new Date(c.closed_at!).getTime() - new Date(c.opened_at!).getTime()) / 3_600_000,
        0,
      ) / closedRecent.length
    : 0;

  $: kpiCards = [
    { icon: Activity, label: 'Casos activos', value: kActive, tone: 'brand', sub: `${cases.length} en total` },
    { icon: Wrench, label: 'En progreso', value: kInProgress, tone: 'amber', sub: 'siendo atendidos' },
    {
      icon: UserMinus,
      label: 'Sin asignar',
      value: kUnassigned,
      tone: kUnassigned > 0 ? 'rose' : 'emerald',
      sub: kUnassigned > 0 ? 'requieren ingeniero' : 'todo asignado',
    },
    {
      icon: AlarmClock,
      label: 'SLA en riesgo',
      value: kSlaRisk,
      tone: kSlaRisk > 0 ? 'rose' : 'emerald',
      sub: kSlaRisk > 0 ? 'vencidos o por vencer' : 'al día',
    },
  ];

  const TONES: Record<string, string> = {
    brand: 'bg-brand-50 text-brand-600',
    amber: 'bg-amber-50 text-amber-600',
    rose: 'bg-rose-50 text-rose-600',
    emerald: 'bg-emerald-50 text-emerald-600',
  };

  // ---- Gráfica: casos por estado (agrupado, sin ceros) ----
  $: byStatus = STATUS_GROUPS.map((g) => ({
    ...g,
    value: cases.filter((c) => g.statuses.includes(c.status)).length,
  })).filter((g) => g.value > 0);
  $: statusMax = Math.max(1, ...byStatus.map((s) => s.value));

  // ---- Gráfica: por prioridad ----
  $: byPriority = (Object.keys(PRIORITY_META) as CasePriority[])
    .slice()
    .reverse()
    .map((key) => ({ key, ...PRIORITY_META[key], value: cases.filter((c) => c.priority === key).length }));
  $: prioTotal = Math.max(1, byPriority.reduce((acc, p) => acc + p.value, 0));

  // ---- Filtrado + orden por urgencia ----
  function urgency(c: Case): number {
    let score = isActive(c) ? 1000 : 0;
    const s = slaInfo(c).state;
    if (s === 'overdue') score += 500;
    else if (s === 'soon') score += 200;
    if (isAging(c)) score += 100;
    score += PRIORITY_META[c.priority].rank * 10;
    return score;
  }

  $: activeGroupStatuses = STATUS_GROUPS.find((g) => g.key === fStatusGroup)?.statuses ?? null;
  $: filtered = cases
    .filter((c) => {
      if (activeGroupStatuses && !activeGroupStatuses.includes(c.status)) return false;
      if (fPriority && c.priority !== fPriority) return false;
      if (fAssignee === '__unassigned__') {
        if (c.assigned_to) return false;
      } else if (fAssignee && c.assigned_to !== fAssignee) return false;
      if (search.trim()) {
        const q = search.trim().toLowerCase();
        const hay = `${c.code} ${c.title} ${equipmentNameById[c.equipment_id] ?? ''}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    })
    .sort((x, y) => urgency(y) - urgency(x));

  $: assigneeFilterOptions = [
    { value: '__unassigned__', label: '— Sin asignar —' },
    ...engineers.map((u) => ({ value: u.id, label: u.full_name })),
  ];

  $: hasFilters = !!(fStatusGroup || fAssignee || fPriority || search.trim());
  function clearFilters() {
    fStatusGroup = '';
    fAssignee = '';
    fPriority = '';
    search = '';
  }
</script>

<!-- HERO slim -->
<div
  in:fly={{ y: 14, duration: 450, easing: cubicOut }}
  class="relative mb-3 overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-r from-slate-900 via-brand-800 to-brand-600 px-4 py-3 text-white shadow-lg sm:px-5"
>
  <div
    class="pointer-events-none absolute inset-0 opacity-[0.15]"
    style="background-image:linear-gradient(to right,rgba(255,255,255,.4) 1px,transparent 1px),linear-gradient(to bottom,rgba(255,255,255,.4) 1px,transparent 1px);background-size:30px 30px"
  ></div>
  <div class="pointer-events-none absolute -right-16 -top-20 h-52 w-52 rounded-full bg-cyan-400/20 blur-3xl"></div>

  <div class="relative flex flex-wrap items-center justify-between gap-3">
    <div class="min-w-0">
      <p class="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-white/70">
        <SignalHigh class="h-3.5 w-3.5" /> {greeting()} · Centro de casos
      </p>
      <h1 class="flex flex-wrap items-center gap-x-2 gap-y-1 text-lg font-bold leading-tight sm:text-xl">
        <span class="truncate">{$profile?.full_name ?? 'Bienvenido'}</span>
        {#if $profile?.clinic_name}
          <span class="inline-flex max-w-full items-center gap-1.5 rounded-full bg-white/15 py-0.5 pl-1.5 pr-2.5 text-xs font-semibold ring-1 ring-white/25 backdrop-blur">
            <span class="grid h-4 w-4 shrink-0 place-items-center rounded-full bg-white/25"><Building2 class="h-2.5 w-2.5" /></span>
            <span class="truncate">{$profile.clinic_name}</span>
          </span>
        {/if}
      </h1>
    </div>
    <div class="flex flex-wrap gap-2">
      <a class="inline-flex items-center gap-2 rounded-lg bg-white/10 px-3 py-1.5 text-sm font-medium backdrop-blur transition hover:bg-white/20" href="/equipment/scan">
        <QrCode class="h-4 w-4" /> Escanear QR
      </a>
      <a class="inline-flex items-center gap-2 rounded-lg bg-white px-3 py-1.5 text-sm font-semibold text-brand-700 shadow-sm transition hover:bg-slate-50" href="/cases/new">
        <PlusCircle class="h-4 w-4" /> Nuevo caso
      </a>
    </div>
  </div>
</div>

{#if error}
  <p class="mb-3 rounded-lg border border-danger-500 bg-red-50 p-3 text-sm text-danger-600">{error}</p>
{/if}

<!-- KPIs (en tiempo real) -->
<div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
  {#each kpiCards as kpi, i (kpi.label)}
    <div in:fly={{ y: 12, duration: 400, delay: 50 + i * 60, easing: cubicOut }}>
      <Card>
        <div class="flex items-start gap-3">
          <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl {TONES[kpi.tone]}">
            <svelte:component this={kpi.icon} class="h-5 w-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs uppercase tracking-wider text-slate-500">{kpi.label}</p>
            <p class="text-2xl font-bold tabular-nums text-slate-900">{Math.round(kpi.value * a)}</p>
            <p class="truncate text-xs text-slate-400">{kpi.sub}</p>
          </div>
        </div>
      </Card>
    </div>
  {/each}
</div>

<!-- Layout principal: casos (izq) + gráficas (der) -->
<div class="mt-3 grid gap-3 lg:grid-cols-3">
  <!-- CENTRO DE CASOS -->
  <div in:fly={{ y: 14, duration: 450, delay: 200, easing: cubicOut }} class="lg:col-span-2">
    <Card>
      <header class="mb-4 flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div class="flex items-center gap-2">
          <LayoutGrid class="h-4 w-4 text-brand-600" />
          <h3 class="text-base font-semibold text-slate-900">Casos</h3>
          <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold tabular-nums text-slate-600">
            {filtered.length}{hasFilters ? ` / ${cases.length}` : ''}
          </span>
          <button
            type="button"
            class="grid h-6 w-6 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-600"
            on:click={() => (legendOpen = true)}
            use:tooltip={{ text: 'Guía: estados y prioridades', placement: 'top' }}
            aria-label="Guía de estados"
          >
            <HelpCircle class="h-4 w-4" />
          </button>
        </div>

        <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
          <label class="relative col-span-2 sm:col-span-1">
            <Search class="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input class="input pl-8" placeholder="Buscar…" bind:value={search} aria-label="Buscar caso" />
          </label>
          <Select bind:value={fStatusGroup} options={STATUS_GROUP_OPTIONS} placeholder="Estado" />
          <Select bind:value={fAssignee} options={assigneeFilterOptions} placeholder="Ingeniero" />
          <Select bind:value={fPriority} options={PRIORITY_OPTIONS} placeholder="Prioridad" />
        </div>
        {#if hasFilters}
          <button type="button" class="self-start text-xs font-medium text-slate-500 hover:text-brand-600" on:click={clearFilters}>
            Limpiar filtros
          </button>
        {/if}
      </header>

      {#if loading}
        <Spinner label="Cargando casos…" />
      {:else if cases.length === 0}
        <EmptyState
          icon={Wrench}
          title="Aún no hay casos"
          description="Crea el primer caso para reportar una falla, programar un mantenimiento o registrar una calibración."
        >
          <svelte:fragment slot="actions">
            <a class="btn-primary" href="/cases/new">+ Crear caso</a>
          </svelte:fragment>
        </EmptyState>
      {:else if filtered.length === 0}
        <div class="py-10 text-center">
          <p class="text-sm text-slate-500">Ningún caso coincide con los filtros.</p>
          <button type="button" class="mt-2 text-sm font-medium text-brand-600 hover:underline" on:click={clearFilters}>Quitar filtros</button>
        </div>
      {:else}
        <div class="grid gap-3 sm:grid-cols-2 2xl:grid-cols-3">
          {#each filtered as c (c.id)}
            <div animate:flip={{ duration: 250, easing: cubicOut }}>
              <CaseBoardCard
                {c}
                equipmentName={equipmentNameById[c.equipment_id] ?? ''}
                {engineers}
                on:changed={(e) => upsert(e.detail)}
                on:edit={(e) => openEdit(e.detail)}
              />
            </div>
          {/each}
        </div>
      {/if}
    </Card>
  </div>

  <!-- COLUMNA DE GRÁFICAS -->
  <div in:fly={{ y: 14, duration: 450, delay: 280, easing: cubicOut }} class="space-y-3">
    <!-- Casos por estado -->
    <Card>
      <header class="mb-3 flex items-center gap-2">
        <BarChart3 class="h-4 w-4 text-brand-600" />
        <h3 class="text-sm font-semibold text-slate-900">Casos por estado</h3>
      </header>
      {#if byStatus.length === 0}
        <p class="py-4 text-center text-xs text-slate-400">Sin casos registrados.</p>
      {:else}
        <div class="space-y-2.5">
          {#each byStatus as s}
            <button
              type="button"
              class="flex w-full items-center gap-2 text-left"
              class:opacity-40={fStatusGroup && fStatusGroup !== s.key}
              on:click={() => (fStatusGroup = fStatusGroup === s.key ? '' : s.key)}
              use:tooltip={{ text: fStatusGroup === s.key ? `Quitar filtro: ${s.label}` : `Filtrar por ${s.label}`, placement: 'left' }}
            >
              <span class="h-2.5 w-2.5 shrink-0 rounded-full" style="background:{s.color}"></span>
              <span class="w-24 shrink-0 truncate text-xs font-medium text-slate-600">{s.label}</span>
              <span class="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-100">
                <span class="block h-full rounded-full" style="width:{(s.value / statusMax) * 100 * a}%; background:{s.color}"></span>
              </span>
              <span class="w-6 shrink-0 text-right text-xs font-bold tabular-nums text-slate-900">{s.value}</span>
            </button>
          {/each}
        </div>
      {/if}
    </Card>

    <!-- Por prioridad -->
    <Card>
      <header class="mb-3 flex items-center gap-2">
        <SignalHigh class="h-4 w-4 text-brand-600" />
        <h3 class="text-sm font-semibold text-slate-900">Por prioridad</h3>
      </header>
      <div class="space-y-2.5">
        {#each byPriority as p}
          <button
            type="button"
            class="flex w-full items-center gap-2 text-left"
            class:opacity-40={fPriority && fPriority !== p.key}
            on:click={() => (fPriority = fPriority === p.key ? '' : p.key)}
            use:tooltip={{ text: fPriority === p.key ? `Quitar filtro: ${p.label}` : `Filtrar por ${p.label}`, placement: 'left' }}
          >
            <span
              class="h-2.5 w-2.5 shrink-0 rounded-full {p.pulse && p.value > 0 ? 'animate-pulse-ring' : ''}"
              style="background:{p.color}; --glow:{p.glow}"
            ></span>
            <span class="w-14 shrink-0 text-xs font-medium text-slate-600">{p.label}</span>
            <span class="h-2.5 flex-1 overflow-hidden rounded-full bg-slate-100">
              <span class="block h-full rounded-full" style="width:{(p.value / prioTotal) * 100 * a}%; background:{p.color}"></span>
            </span>
            <span class="w-6 shrink-0 text-right text-xs font-bold tabular-nums text-slate-900">{p.value}</span>
          </button>
        {/each}
      </div>
    </Card>

    <!-- Tiempo prom. de cierre (live) -->
    <Card>
      <div class="flex items-center gap-3">
        <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-slate-100 text-slate-700">
          <Timer class="h-5 w-5" />
        </div>
        <div>
          <p class="text-xs uppercase tracking-wider text-slate-500">Tiempo prom. de cierre</p>
          <p class="text-2xl font-bold tabular-nums text-slate-900">
            {(avgClose * a).toFixed(1)}<span class="text-sm font-normal text-slate-500"> h</span>
          </p>
          <p class="text-xs text-slate-400">
            {closedRecent.length ? `${closedRecent.length} cerrados · últimos 30 días` : 'sin casos cerrados aún'}
          </p>
        </div>
      </div>
    </Card>
  </div>
</div>

<CaseEditModal bind:open={editOpen} value={editCase} {engineers} on:saved={(e) => upsert(e.detail)} />
<CaseLegendModal bind:open={legendOpen} />
