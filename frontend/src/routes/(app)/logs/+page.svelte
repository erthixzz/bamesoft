<script lang="ts">
  /** Bitácora / Logs — dashboard de auditoría: quién hizo qué, cuándo y cuántas
   *  veces. Solo visible para admins (cap 'audit'). Scoped por clínica en el
   *  backend. */
  import { onMount } from 'svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import Card from '$lib/components/Card.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Button from '$lib/components/Button.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import Select from '$lib/components/Select.svelte';
  import Input from '$lib/components/Input.svelte';
  import BarList from '$lib/components/charts/BarList.svelte';
  import { auditApi } from '$lib/modules/audit/api';
  import type { AuditActor, AuditLog, AuditSummary } from '$lib/modules/audit/types';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import type { UserRole } from '$lib/api/types';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { formatDateTime, timeFromNow } from '$lib/utils/format';
  import {
    ScrollText,
    Activity,
    Users,
    Boxes,
    Clock,
    Plus,
    Pencil,
    Trash2,
    History,
    X,
  } from 'lucide-svelte';

  let summary: AuditSummary | null = null;
  let logs: AuditLog[] = [];
  let loading = true;

  const today = new Date();
  const past = new Date(today.getTime() - 30 * 86400000);
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  let dateFrom = iso(past);
  let dateTo = iso(today);

  const ENTITY_LABELS: Record<string, string> = {
    cases: 'Casos',
    equipment: 'Equipos',
    users: 'Usuarios',
    sectors: 'Unidades',
    clinics: 'Compañías',
    documents: 'Documentos',
    alerts: 'Alertas',
    calibrations: 'Calibraciones',
    maintenance: 'Mantenimiento',
    standards: 'Normas',
    access: 'Control de acceso',
    reports: 'Reportes',
  };
  let entityFilter = '';
  $: entityOptions = [
    { value: '', label: 'Todos los módulos' },
    ...Object.entries(ENTITY_LABELS).map(([value, label]) => ({ value, label })),
  ];

  // --- Filtros de búsqueda -------------------------------------------------
  // El método HTTP es el dato que guarda la bitácora; aquí se traduce a la
  // palabra que usaría un administrador ("eliminó", no "DELETE").
  const METHOD_OPTIONS = [
    { value: '', label: 'Cualquier operación' },
    { value: 'POST', label: 'Creaciones' },
    { value: 'PATCH', label: 'Modificaciones' },
    { value: 'DELETE', label: 'Eliminaciones' },
  ];
  let methodFilter = '';

  let actors: AuditActor[] = [];
  let actorFilter = '';
  $: actorOptions = [
    { value: '', label: 'Cualquier persona' },
    ...actors.map((a) => ({ value: a.id, label: a.name })),
  ];

  let q = '';
  let total = 0;
  const PAGE_SIZE = 200;

  $: hayFiltros = !!(q.trim() || actorFilter || methodFilter || entityFilter);
  $: hayMas = total > logs.length;

  /** Espera a que el usuario deje de teclear antes de consultar. */
  let debounce: ReturnType<typeof setTimeout>;
  function onSearch() {
    clearTimeout(debounce);
    debounce = setTimeout(reloadLogs, 300);
  }

  function limpiarFiltros() {
    q = '';
    actorFilter = '';
    methodFilter = '';
    entityFilter = '';
    reloadLogs();
  }

  const roleLabel = (r?: string | null) => (r ? (ROLE_LABELS[r as UserRole] ?? r) : '—');
  const entityLabel = (e?: string | null) => (e ? (ENTITY_LABELS[e] ?? e) : 'Otro');

  // Ícono por método para las filas.
  function methodMeta(m: string) {
    switch (m) {
      case 'POST':
        return { icon: Plus, cls: 'bg-emerald-50 text-emerald-600' };
      case 'DELETE':
        return { icon: Trash2, cls: 'bg-rose-50 text-rose-600' };
      default:
        return { icon: Pencil, cls: 'bg-amber-50 text-amber-600' };
    }
  }

  /** Parámetros de consulta según los filtros activos. */
  function queryParams() {
    return {
      from: dateFrom,
      to: dateTo,
      entity: entityFilter || undefined,
      method: methodFilter || undefined,
      actor_id: actorFilter || undefined,
      q: q.trim() || undefined,
      limit: PAGE_SIZE,
    };
  }

  async function load() {
    loading = true;
    try {
      const [s, page, a] = await Promise.all([
        auditApi.summary({ from: dateFrom, to: dateTo }),
        auditApi.logs(queryParams()),
        auditApi.actors().catch(() => [] as AuditActor[]),
      ]);
      summary = s;
      logs = page.items;
      total = page.total;
      actors = a;
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo cargar la bitácora');
    } finally {
      loading = false;
    }
  }

  let searching = false;

  async function reloadLogs() {
    searching = true;
    try {
      const page = await auditApi.logs(queryParams());
      logs = page.items;
      total = page.total;
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo filtrar');
    } finally {
      searching = false;
    }
  }

  onMount(() => {
    setPageTitle('Bitácora');
    load();
  });

  $: kpis = summary
    ? [
        { label: 'Acciones', value: summary.total, icon: Activity, tone: 'text-brand-700' },
        { label: 'Usuarios activos', value: summary.actors, icon: Users, tone: 'text-violet-700' },
        {
          label: 'Módulos tocados',
          value: summary.by_entity.length,
          icon: Boxes,
          tone: 'text-cyan-700',
        },
        {
          label: 'Acción más frecuente',
          value: summary.by_action[0]?.count ?? 0,
          hint: summary.by_action[0]?.label ?? '—',
          icon: History,
          tone: 'text-emerald-700',
        },
      ]
    : [];

  $: actorBars = (summary?.by_actor ?? []).map((r) => ({ label: r.label, value: r.count }));
  $: actionBars = (summary?.by_action ?? []).map((r) => ({ label: r.label, value: r.count }));
  $: entityBars = (summary?.by_entity ?? []).map((r) => ({ label: r.label, value: r.count }));
  $: maxDay = Math.max(1, ...(summary?.by_day ?? []).map((d) => d.count));
</script>

<PageHeader title="Bitácora" subtitle="Auditoría: quién hizo qué, cuándo y cuántas veces" icon={ScrollText} gradient="brand">
  <svelte:fragment slot="actions">
    <div class="flex flex-wrap items-end gap-2">
      <div class="w-36"><DatePicker label="Desde" bind:value={dateFrom} /></div>
      <div class="w-36"><DatePicker label="Hasta" bind:value={dateTo} /></div>
      <Button on:click={load}>Aplicar</Button>
    </div>
  </svelte:fragment>
</PageHeader>

{#if loading}
  <Spinner label="Cargando bitácora…" />
{:else}
  <div class="animate-fade-up space-y-4">
    <!-- KPIs -->
    <div class="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {#each kpis as k}
        <Card>
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="text-xs font-medium uppercase tracking-wide text-slate-400">{k.label}</p>
              <p class="mt-1 text-2xl font-bold tabular-nums {k.tone}">{k.value}</p>
              {#if k.hint}
                <p class="mt-0.5 truncate text-xs text-slate-500" title={k.hint}>{k.hint}</p>
              {/if}
            </div>
            <span class="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-slate-50 text-slate-400">
              <svelte:component this={k.icon} class="h-5 w-5" />
            </span>
          </div>
        </Card>
      {/each}
    </div>

    <!-- Gráficas de agregados -->
    <div class="grid gap-4 lg:grid-cols-3">
      <Card title="Quién hizo más" description="Acciones por usuario en el rango." icon={Users} accent="violet">
        {#if actorBars.length}
          <BarList data={actorBars} accent="#8b5cf6" />
        {:else}
          <EmptyState icon={Users} title="Sin actividad" description="No hay acciones registradas." />
        {/if}
      </Card>

      <Card title="Acciones más frecuentes" description="Qué se hizo más veces." icon={Activity} accent="emerald">
        {#if actionBars.length}
          <BarList data={actionBars} accent="#10b981" />
        {:else}
          <EmptyState icon={Activity} title="Sin datos" description="Nada que mostrar." />
        {/if}
      </Card>

      <Card title="Actividad por módulo" description="Dónde se concentró el trabajo." icon={Boxes} accent="cyan">
        {#if entityBars.length}
          <BarList data={entityBars} accent="#06b6d4" />
        {:else}
          <EmptyState icon={Boxes} title="Sin datos" description="Nada que mostrar." />
        {/if}
      </Card>
    </div>

    <!-- Timeline por día -->
    <Card title="Actividad por día" description="Acciones registradas por fecha." icon={Clock} accent="brand">
      {#if summary && summary.by_day.length}
        <div class="flex items-end gap-1.5 overflow-x-auto pb-2" style="height:150px;">
          {#each summary.by_day as d}
            <div class="flex h-full flex-col items-center justify-end gap-1">
              <div
                class="w-4 rounded-t bg-gradient-to-t from-brand-600 to-cyan-400"
                style="height:{(d.count / maxDay) * 100}%"
                title="{d.count} acciones"
              ></div>
              <span class="whitespace-nowrap text-[10px] text-slate-400">{d.day.slice(5)}</span>
            </div>
          {/each}
        </div>
      {:else}
        <EmptyState icon={Clock} title="Sin actividad" description="No hay acciones en el rango." />
      {/if}
    </Card>

    <!-- Detalle: registro cronológico con búsqueda -->
    <Card title="Registro cronológico" description="Busca quién hizo qué y cuándo." icon={History} accent="slate">
      <!-- Buscador: lo primero, porque es la razón de entrar aquí -->
      <div class="mb-3">
        <Input
          bind:value={q}
          on:input={onSearch}
          placeholder="Buscar por persona, acción o código del registro…"
        />
      </div>

      <div class="mb-4 grid gap-2 sm:grid-cols-3">
        <Select bind:value={actorFilter} options={actorOptions} on:change={reloadLogs} />
        <Select bind:value={methodFilter} options={METHOD_OPTIONS} on:change={reloadLogs} />
        <Select bind:value={entityFilter} options={entityOptions} on:change={reloadLogs} />
      </div>

      <div class="mb-3 flex flex-wrap items-center gap-3 text-xs text-slate-500">
        {#if searching}
          <span>Buscando…</span>
        {:else}
          <span>
            <strong class="font-semibold text-slate-700">{total}</strong>
            {total === 1 ? 'acción encontrada' : 'acciones encontradas'}
            {#if hayMas}
              · mostrando las {logs.length} más recientes
            {/if}
          </span>
        {/if}

        {#if hayFiltros}
          <button
            type="button"
            on:click={limpiarFiltros}
            class="inline-flex items-center gap-1 font-medium text-brand-600 hover:underline"
          >
            <X class="h-3.5 w-3.5" /> Limpiar filtros
          </button>
        {/if}
      </div>

      {#if logs.length === 0}
        <EmptyState
          icon={ScrollText}
          title={hayFiltros ? 'Sin coincidencias' : 'Sin registros'}
          description={hayFiltros
            ? 'Prueba con otros términos o amplía el rango de fechas.'
            : 'Todavía no hay acciones registradas en este periodo.'}
        />
      {:else}
        <ul class="divide-y divide-slate-100">
          {#each logs as log}
            {@const m = methodMeta(log.method)}
            <li class="flex items-start gap-3 py-2.5">
              <span class="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-lg {m.cls}">
                <svelte:component this={m.icon} class="h-4 w-4" />
              </span>
              <div class="min-w-0 flex-1">
                <p class="text-sm text-slate-800">
                  <span class="font-semibold">{log.actor_name ?? 'Sistema'}</span>
                  <span class="text-slate-600"> · {log.action}</span>
                </p>
                {#if log.detail}
                  <p class="mt-0.5 text-xs font-medium text-slate-600">{log.detail}</p>
                {/if}
                <p class="mt-0.5 flex flex-wrap items-center gap-x-2 text-xs text-slate-400">
                  <span>{roleLabel(log.actor_role)}</span>
                  <span>·</span>
                  <span class="rounded bg-slate-100 px-1.5 py-0.5 font-medium text-slate-500">{entityLabel(log.entity)}</span>
                  <span>·</span>
                  <span title={formatDateTime(log.created_at)}>{timeFromNow(log.created_at)}</span>
                </p>
              </div>
              <span class="shrink-0 text-[10px] font-medium tabular-nums text-slate-300">{log.method}</span>
            </li>
          {/each}
        </ul>
      {/if}
    </Card>
  </div>
{/if}
