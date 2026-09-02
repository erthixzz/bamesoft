<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import Button from '$lib/components/Button.svelte';
  import Select from '$lib/components/Select.svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Donut from '$lib/components/charts/Donut.svelte';
  import BarList from '$lib/components/charts/BarList.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type {
    BreakdownReport,
    ComplianceReport,
    EquipmentReport,
    OperationsReport,
    ProductivityReport,
    ServicesReport,
    ServiceRow,
    TecnovigilanciaReport,
  } from '$lib/modules/reports/types';
  import type {
    CaseCompletion,
    CasePriority,
    CaseStatus,
    CaseType,
    TecnovigilanciaStage,
  } from '$lib/api/types';
  import {
    TYPE_LABEL,
    TYPE_OPTIONS,
    COMPLETION_LABEL,
    SATISFACTION_BY_SCORE,
    SATISFACTION_GROUP_META,
    SATISFACTION_QUESTION,
    satisfactionColor,
    satisfactionLabel,
    TECNOVIGILANCIA_STAGE_META,
    TECNOVIGILANCIA_STAGE_OPTIONS,
    tecnovigilanciaStageLabel,
    tecnovigilanciaStageMeta,
    STATUS_META,
    PRIORITY_META,
    elapsedBetween,
  } from '$lib/modules/cases/ui';
  import { setPageTitle } from '$lib/stores/page';
  import { formatDate, formatDateTime } from '$lib/utils/format';
  import {
    BarChart3,
    FileBarChart,
    Users,
    PhoneCall,
    Gauge,
    Stethoscope,
    ClipboardList,
    ArrowRight,
    PieChart,
    Building2,
    CalendarRange,
    Info,
    ShieldAlert,
    SmilePlus,
  } from 'lucide-svelte';

  let compliance: ComplianceReport | null = null;
  let prod: ProductivityReport | null = null;
  let ops: OperationsReport | null = null;
  let eqReport: EquipmentReport | null = null;
  let services: ServicesReport | null = null;
  let breakdown: BreakdownReport | null = null;
  let tecno: TecnovigilanciaReport | null = null;
  let loading = true;

  // Rango por defecto: últimos 30 días.
  const today = new Date();
  const past = new Date(today.getTime() - 30 * 86400000);
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  let dateFrom = iso(past);
  let dateTo = iso(today);

  // Apartados
  type Tab =
    | 'resumen'
    | 'analitica'
    | 'satisfaccion'
    | 'tecnovigilancia'
    | 'ingenieros'
    | 'equipos'
    | 'servicios';
  let tab: Tab = 'resumen';
  const TABS: { key: Tab; label: string; icon: typeof Gauge }[] = [
    { key: 'resumen', label: 'Resumen', icon: Gauge },
    { key: 'analitica', label: 'Analítica', icon: PieChart },
    { key: 'satisfaccion', label: 'Satisfacción', icon: SmilePlus },
    { key: 'tecnovigilancia', label: 'Tecnovigilancia', icon: ShieldAlert },
    { key: 'ingenieros', label: 'Por ingeniero', icon: Users },
    { key: 'equipos', label: 'Por equipo', icon: Stethoscope },
    { key: 'servicios', label: 'Servicios', icon: ClipboardList },
  ];

  // ---- Datos para gráficas (mapeados a etiqueta/color) ----
  const TYPE_COLORS: Record<string, string> = {
    corrective: '#f97316',
    preventive: '#10b981',
    calibration: '#8b5cf6',
    installation: '#0ea5e9',
    inspection: '#eab308',
  };
  $: statusChart = (breakdown?.by_status ?? []).map((d) => ({
    label: STATUS_META[d.label as CaseStatus]?.label ?? d.label,
    value: d.value,
    color: STATUS_META[d.label as CaseStatus]?.color ?? '#94a3b8',
  }));
  $: typeChart = (breakdown?.by_type ?? []).map((d) => ({
    label: TYPE_LABEL[d.label as CaseType] ?? d.label,
    value: d.value,
    color: TYPE_COLORS[d.label] ?? '#64748b',
  }));
  $: priorityChart = (breakdown?.by_priority ?? []).map((d) => ({
    label: PRIORITY_META[d.label as CasePriority]?.label ?? d.label,
    value: d.value,
    color: PRIORITY_META[d.label as CasePriority]?.color ?? '#94a3b8',
  }));
  $: completionChart = ops
    ? [
        { label: 'Completos', value: ops.complete_total, color: '#10b981' },
        { label: 'Incompletos', value: ops.incomplete_total, color: '#f59e0b' },
        {
          label: 'Sin cierre',
          value: Math.max(0, ops.reported_total - ops.complete_total - ops.incomplete_total),
          color: '#cbd5e1',
        },
      ]
    : [];
  $: sectorBars = (breakdown?.by_sector ?? []).map((d) => ({ label: d.label, value: d.value }));
  $: monthlyBars = (breakdown?.monthly ?? []).map((d) => ({ label: d.label, value: d.value }));
  $: engineerLoad = (prod?.items ?? []).map((r) => ({ label: r.engineer_name, value: r.attended }));
  $: engineerFcr = (prod?.items ?? []).map((r) => ({ label: r.engineer_name, value: r.fcr_pct }));

  // Distribución Likert 1-7 (siempre los 7 puntos, con su color de la escala).
  $: satisfactionChart = (breakdown?.by_satisfaction ?? []).map((d) => {
    const score = Number(d.label);
    return {
      label: `${score} · ${satisfactionLabel(score)}`,
      value: d.value,
      color: satisfactionColor(score),
    };
  });
  $: satisfactionGroupChart = prod
    ? [
        {
          label: SATISFACTION_GROUP_META.positive.label,
          value: prod.sat_positive,
          color: SATISFACTION_GROUP_META.positive.color,
        },
        {
          label: SATISFACTION_GROUP_META.neutral.label,
          value: prod.sat_neutral,
          color: SATISFACTION_GROUP_META.neutral.color,
        },
        {
          label: SATISFACTION_GROUP_META.negative.label,
          value: prod.sat_negative,
          color: SATISFACTION_GROUP_META.negative.color,
        },
      ]
    : [];
  $: tecnoStageChart = (tecno?.by_stage ?? []).map((d) => ({
    label: tecnovigilanciaStageLabel(d.label),
    value: d.value,
    color: TECNOVIGILANCIA_STAGE_META[d.label as TecnovigilanciaStage]?.color ?? '#94a3b8',
  }));
  $: tecnoEquipmentBars = (tecno?.by_equipment ?? []).map((d) => ({
    label: d.label,
    value: d.value,
  }));
  /** % de satisfechos (5-7) sobre las respuestas recibidas. */
  $: satPositivePct =
    prod && prod.sat_count ? Math.round((prod.sat_positive / prod.sat_count) * 100) : 0;

  // Filtros del apartado Servicios (sobre los datos ya cargados).
  let fEngineer = '';
  let fEquipment = '';
  let fType = '';
  /** '' = todas · 'positive'|'neutral'|'negative' = grupo · '1'…'7' = puntaje exacto. */
  let fSatisfaction = '';
  /** '' = todos · 'yes' = solo tecnovigilancia · 'no' = sin tecnovigilancia. */
  let fTecno = '';
  /** Filtro por etapa dentro del apartado Tecnovigilancia. */
  let fTecnoStage = '';

  const SATISFACTION_FILTER_OPTIONS = [
    { value: 'positive', label: 'Satisfechos (5-7)' },
    { value: 'neutral', label: 'Neutrales (4)' },
    { value: 'negative', label: 'Insatisfechos (1-3)' },
    ...Object.values(SATISFACTION_BY_SCORE).map((s) => ({
      value: String(s.score),
      label: `${s.score} — ${s.label}`,
    })),
  ];

  const TECNO_FILTER_OPTIONS = [
    { value: 'yes', label: 'Solo tecnovigilancia' },
    { value: 'no', label: 'Sin tecnovigilancia' },
  ];

  /** ¿La fila cae dentro del filtro de satisfacción elegido? */
  function matchesSatisfaction(s: ServiceRow): boolean {
    if (!fSatisfaction) return true;
    const score = s.satisfaction_score ?? null;
    if (score == null) return false;
    const group = SATISFACTION_GROUP_META[fSatisfaction as keyof typeof SATISFACTION_GROUP_META];
    if (group) return group.scores.includes(score as (typeof group.scores)[number]);
    return score === Number(fSatisfaction);
  }

  // Modal de "drill-down": lista de casos detrás de una tarjeta (KPI clicable).
  let modalOpen = false;
  let modalTitle = '';
  let modalRows: ServiceRow[] = [];
  function openCasesModal(title: string, filter: (s: ServiceRow) => boolean) {
    modalTitle = title;
    modalRows = (services?.items ?? []).filter(filter);
    modalOpen = true;
  }

  // Reincidencia de equipos: un equipo con muchos casos en el rango "reincide".
  const RECURRENCE_MIN = 3;
  // El backend ya ordena por casos desc, así que el primero es el más reincidente.
  $: topEquipment =
    eqReport && eqReport.items.length && eqReport.items[0].cases_total > 0
      ? eqReport.items[0]
      : null;

  $: maxDaily = ops ? Math.max(1, ...ops.daily.map((d) => Math.max(d.reported, d.closed))) : 1;
  $: maxReporter = ops ? Math.max(1, ...ops.by_reporter.map((r) => r.count)) : 1;

  const h = (v: number | null) => (v == null ? '—' : `${v} h`);
  const typeLabel = (t: string) => TYPE_LABEL[t as CaseType] ?? t;
  const statusLabel = (s: string) => STATUS_META[s as CaseStatus]?.label ?? s;
  const complLabel = (c: string | null) => (c ? (COMPLETION_LABEL[c as CaseCompletion] ?? c) : null);

  $: engineerOptions = services
    ? [...new Set(services.items.map((s) => s.engineer_name).filter(Boolean) as string[])].map(
        (n) => ({ value: n, label: n }),
      )
    : [];
  $: equipmentOptions = services
    ? [...new Set(services.items.map((s) => s.equipment_label))].map((n) => ({ value: n, label: n }))
    : [];
  $: filteredServices = (services?.items ?? []).filter(
    (s) =>
      (!fEngineer || s.engineer_name === fEngineer) &&
      (!fEquipment || s.equipment_label === fEquipment) &&
      (!fType || s.type === fType) &&
      (!fTecno || (fTecno === 'yes' ? s.is_tecnovigilancia : !s.is_tecnovigilancia)) &&
      matchesSatisfaction(s),
  );

  $: filteredTecno = (tecno?.items ?? []).filter((r) => !fTecnoStage || r.stage === fTecnoStage);

  async function load() {
    loading = true;
    try {
      const range = { date_from: dateFrom, date_to: dateTo };
      [compliance, prod, ops, eqReport, services, breakdown, tecno] = await Promise.all([
        reportsApi.compliance(),
        reportsApi.productivity(range),
        reportsApi.operations(range),
        reportsApi.equipment(range),
        reportsApi.services(range),
        reportsApi.breakdown(range),
        reportsApi.tecnovigilancia(range),
      ]);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Reportes');
    load();
  });

  /** Desde "Por ingeniero": saltar a Servicios filtrado por ese ingeniero. */
  function viewEngineerServices(name: string) {
    fEngineer = name;
    fEquipment = '';
    tab = 'servicios';
  }

  // Tooltip del KPI: se ve al pasar el mouse (hover) y se puede "fijar" con clic
  // (útil en móvil / para dejarlo abierto).
  let openHint: number | null = null;
  let hoverHint: number | null = null;
  function toggleHint(i: number) {
    openHint = openHint === i ? null : i;
  }
  $: shownHint = openHint ?? hoverHint;

  type Kpi = {
    label: string;
    value: string | number;
    tone: string;
    hint: string;
    drill?: { title: string; filter: (s: ServiceRow) => boolean };
  };
  let kpis: Kpi[] = [];
  $: kpis = ops
    ? [
        {
          label: 'Reportadas',
          value: ops.reported_total,
          tone: 'text-brand-700',
          hint: 'Total de casos reportados (creados) en el rango. Se reparten sin perder ninguno entre En proceso + En espera + Cerradas + Anuladas.',
        },
        {
          label: 'En proceso',
          value: ops.active_total,
          tone: 'text-sky-700',
          hint: 'Casos activos que aún se están atendiendo (abiertos, asignados o en trabajo). Todavía no cerrados.',
        },
        {
          label: 'En espera',
          value: ops.waiting_total,
          tone: 'text-orange-700',
          hint: 'Casos detenidos esperando repuestos o respuesta del cliente (dentro del rango).',
        },
        {
          label: 'Cerradas',
          value: ops.closed_total,
          tone: 'text-emerald-700',
          hint: 'Casos cuyo servicio ya finalizó y se cerraron dentro del rango.',
        },
        {
          label: 'Anuladas',
          value: ops.cancelled_total,
          tone: 'text-slate-500',
          hint: 'Casos cancelados (no se realizó el servicio) dentro del rango.',
        },
        {
          label: 'Completas',
          value: ops.complete_total,
          tone: 'text-emerald-700',
          hint: 'De las CERRADAS, cuántas quedaron completas (el equipo quedó funcionando/OK). Nunca supera a “Cerradas”.',
          drill: { title: 'Casos completos', filter: (s: ServiceRow) => s.completion === 'complete' },
        },
        {
          label: 'Incompletas',
          value: ops.incomplete_total,
          tone: 'text-amber-700',
          hint: 'De las CERRADAS, cuántas quedaron incompletas (p. ej. faltó un repuesto y algo quedó pendiente).',
          drill: { title: 'Casos incompletos', filter: (s: ServiceRow) => s.completion === 'incomplete' },
        },
        {
          label: 'FCR',
          value: prod ? `${prod.fcr_pct}%` : '—',
          tone: 'text-brand-700',
          hint: 'FCR (First Call Resolution): % de casos resueltos completos “a la primera” — cerrados y completos ÷ total atendidos. Mientras más alto, mejor.',
        },
        {
          label: 'Satisfacción prom.',
          value: prod?.sat_avg != null ? `${prod.sat_avg} / 7` : '—',
          tone: 'text-brand-700',
          hint: `Promedio de la escala Likert de 7 puntos («${SATISFACTION_QUESTION}») sobre ${prod?.sat_count ?? 0} respuesta(s) de casos cerrados. 1 = Muy insatisfecho, 7 = Muy satisfecho.`,
        },
        {
          label: 'Satisfechos (5-7)',
          value: prod?.sat_positive ?? 0,
          tone: 'text-emerald-700',
          hint: `${SATISFACTION_GROUP_META.positive.hint} Equivale al ${satPositivePct}% de las respuestas. Haz clic para ver los casos.`,
          drill: {
            title: 'Satisfechos (5-7)',
            filter: (s: ServiceRow) => (s.satisfaction_score ?? 0) >= 5,
          },
        },
        {
          label: 'Neutrales (4)',
          value: prod?.sat_neutral ?? 0,
          tone: 'text-slate-600',
          hint: `${SATISFACTION_GROUP_META.neutral.hint} Haz clic para ver los casos.`,
          drill: {
            title: 'Neutrales (4)',
            filter: (s: ServiceRow) => s.satisfaction_score === 4,
          },
        },
        {
          label: 'Insatisfechos (1-3)',
          value: prod?.sat_negative ?? 0,
          tone: 'text-danger-700',
          hint: `${SATISFACTION_GROUP_META.negative.hint} Son los casos a revisar primero. Haz clic para verlos.`,
          drill: {
            title: 'Insatisfechos (1-3)',
            filter: (s: ServiceRow) =>
              s.satisfaction_score != null && s.satisfaction_score <= 3,
          },
        },
        {
          label: 'Tecnovigilancia',
          value: tecno?.total ?? 0,
          tone: 'text-danger-700',
          hint: 'Casos marcados como evento adverso o incidente en el que el equipo causó (o pudo causar) daño al paciente o al operador. Haz clic para ver cuáles.',
          drill: {
            title: 'Casos de tecnovigilancia',
            filter: (s: ServiceRow) => s.is_tecnovigilancia,
          },
        },
      ]
    : [];
</script>

<PageHeader title="Reportes" subtitle="KPIs, productividad y trazabilidad" icon={BarChart3} gradient="emerald">
  <svelte:fragment slot="actions">
    <div class="flex flex-wrap items-end gap-2">
      <div class="w-36"><DatePicker label="Desde" bind:value={dateFrom} /></div>
      <div class="w-36"><DatePicker label="Hasta" bind:value={dateTo} /></div>
      <Button on:click={load}>Aplicar</Button>
    </div>
  </svelte:fragment>
</PageHeader>

<!-- Apartados -->
<div class="mb-4 flex w-fit max-w-full flex-wrap gap-1 overflow-x-auto rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
  {#each TABS as t (t.key)}
    <button
      type="button"
      class="inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-medium transition
        {tab === t.key ? 'bg-gradient-to-br from-brand-600 to-brand-500 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}"
      on:click={() => (tab = t.key)}
    >
      <svelte:component this={t.icon} class="h-4 w-4" />
      {t.label}
    </button>
  {/each}
</div>

{#if loading}
  <Spinner label="Calculando reportes…" />
{:else if tab === 'resumen'}
  <!-- ══ RESUMEN ══ -->
  <div class="animate-fade-up">
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      {#each kpis as k, i}
        <Card interactive={!!k.drill}>
          <div class="relative">
            <div class="flex items-start justify-between gap-1">
              <p class="text-xs font-medium uppercase tracking-wide text-slate-400">{k.label}</p>
              <button
                type="button"
                class="-mr-1 -mt-1 grid h-6 w-6 shrink-0 place-items-center rounded-full text-slate-300 transition hover:bg-slate-100 hover:text-brand-600 {shownHint === i ? 'bg-brand-50 text-brand-600' : ''}"
                on:click={() => toggleHint(i)}
                on:mouseenter={() => (hoverHint = i)}
                on:mouseleave={() => (hoverHint = null)}
                on:focus={() => (hoverHint = i)}
                on:blur={() => (hoverHint = null)}
                aria-label="Qué significa {k.label}"
              >
                <Info class="h-3.5 w-3.5" />
              </button>
            </div>
            {#if k.drill}
              {@const d = k.drill}
              <button
                type="button"
                class="mt-1 flex items-center gap-1.5 text-2xl font-bold tabular-nums {k.tone} transition hover:opacity-70"
                on:click={() => openCasesModal(d.title, d.filter)}
                title="Ver casos"
              >
                {k.value}
                <ArrowRight class="h-4 w-4 opacity-50" />
              </button>
            {:else}
              <p class="mt-1 text-2xl font-bold tabular-nums {k.tone}">{k.value}</p>
            {/if}

            {#if shownHint === i}
              <div
                class="animate-fade-up absolute left-0 right-0 top-full z-30 mt-2 rounded-xl border border-slate-200 bg-white p-3 text-xs leading-relaxed text-slate-600 shadow-lg shadow-slate-900/10"
                role="tooltip"
              >
                {k.hint}
              </div>
            {/if}
          </div>
        </Card>
      {/each}
    </div>
    {#if openHint !== null}
      <!-- Capa para cerrar el tooltip al tocar fuera -->
      <button
        type="button"
        class="fixed inset-0 z-20 cursor-default"
        aria-label="Cerrar explicación"
        on:click={() => (openHint = null)}
      ></button>
    {/if}

    <!-- Reconciliación: nada se pierde — cada caso reportado cae en un estado. -->
    {#if ops}
      <p class="mt-3 flex flex-wrap items-center gap-x-1.5 gap-y-1 rounded-xl border border-slate-200 bg-slate-50/70 px-3.5 py-2 text-xs text-slate-500">
        <span class="font-semibold text-slate-700">Reportadas {ops.reported_total}</span>
        <span class="text-slate-400">=</span>
        <span class="font-medium text-sky-700">En proceso {ops.active_total}</span>
        <span class="text-slate-400">+</span>
        <span class="font-medium text-orange-700">En espera {ops.waiting_total}</span>
        <span class="text-slate-400">+</span>
        <span class="font-medium text-emerald-700">Cerradas {ops.closed_total}</span>
        <span class="text-slate-400">+</span>
        <span class="font-medium text-slate-500">Anuladas {ops.cancelled_total}</span>
      </p>
    {/if}

    <div class="mt-4 grid gap-4 lg:grid-cols-2">
      <Card title="Llamadas por día" description="Casos reportados (azul) vs. cerrados (verde)." icon={PhoneCall} accent="cyan">
        {#if !ops || ops.daily.length === 0}
          <EmptyState icon={PhoneCall} title="Sin actividad" description="No hay casos reportados en el rango seleccionado." />
        {:else}
          <div class="flex items-end gap-2 overflow-x-auto pb-2" style="height:180px;">
            {#each ops.daily as d}
              <div class="flex h-full flex-col items-center justify-end gap-1">
                <div class="flex h-full items-end gap-0.5">
                  <div class="w-3 rounded-t bg-brand-500" style="height:{(d.reported / maxDaily) * 100}%" title="Reportadas: {d.reported}"></div>
                  <div class="w-3 rounded-t bg-emerald-500" style="height:{(d.closed / maxDaily) * 100}%" title="Cerradas: {d.closed}"></div>
                </div>
                <span class="whitespace-nowrap text-[10px] text-slate-400">{formatDate(d.day)}</span>
              </div>
            {/each}
          </div>
        {/if}
      </Card>

      <Card title="Quién atendió la llamada" description="Casos reportados por usuario en el rango." icon={Users} accent="violet">
        {#if !ops || ops.by_reporter.length === 0}
          <EmptyState icon={Users} title="Sin reportantes" description="No hay casos reportados en el rango." />
        {:else}
          <ul class="space-y-2">
            {#each ops.by_reporter as r}
              <li>
                <div class="mb-1 flex items-center justify-between text-sm">
                  <span class="truncate text-slate-700">{r.name}</span>
                  <span class="tabular-nums text-slate-500">{r.count}</span>
                </div>
                <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                  <div class="h-2 rounded-full bg-gradient-to-r from-brand-500 to-cyan-500" style="width:{(r.count / maxReporter) * 100}%"></div>
                </div>
              </li>
            {/each}
          </ul>
        {/if}
      </Card>
    </div>

    <div class="mt-4">
      <Card title="Cumplimiento por norma" description="Cobertura de las normas aplicables al inventario." icon={FileBarChart} accent="brand">
        {#if !compliance || compliance.items.length === 0}
          <EmptyState icon={FileBarChart} title="Sin normas mapeadas" description="Vincula tus equipos a las normas (ISO 13485, IEC 60601, INVIMA…) para ver el cumplimiento." />
        {:else}
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="text-left text-xs uppercase text-slate-500">
                <tr class="border-b border-slate-200">
                  <th class="py-2 pr-3">Código</th><th class="pr-3">Norma</th><th class="pr-3">Equipos</th><th>Cobertura</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                {#each compliance.items as r}
                  <tr>
                    <td class="py-3 pr-3 font-medium text-slate-800">{r.standard_code}</td>
                    <td class="pr-3 text-slate-600">{r.standard_name}</td>
                    <td class="pr-3 tabular-nums text-slate-600">{r.equipment_with} / {r.equipment_total}</td>
                    <td>
                      <div class="flex items-center gap-3">
                        <div class="h-2 w-32 overflow-hidden rounded-full bg-slate-100">
                          <div class="h-2 rounded-full bg-gradient-to-r from-brand-500 to-cyan-500" style="width: {Math.min(100, r.coverage_pct)}%"></div>
                        </div>
                        <span class="tabular-nums text-slate-700">{r.coverage_pct.toFixed(1)}%</span>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </Card>
    </div>
  </div>
{:else if tab === 'analitica'}
  <!-- ══ ANALÍTICA (gráficas) ══ -->
  <div class="animate-fade-up space-y-4">
    <div class="grid gap-4 lg:grid-cols-3">
      <Card title="Casos por estado" icon={PieChart} accent="brand">
        <Donut data={statusChart} unit="casos" />
      </Card>
      <Card title="Casos por tipo" icon={PieChart} accent="violet">
        <Donut data={typeChart} unit="casos" />
      </Card>
      <Card title="Completitud del servicio" icon={PieChart} accent="emerald">
        <Donut data={completionChart} unit="casos" />
      </Card>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <Card title="Casos por unidad de servicio" icon={Building2} accent="cyan">
        <BarList data={sectorBars} accent="#06b6d4" />
      </Card>
      <Card title="Tendencia mensual" description="Casos reportados por mes" icon={CalendarRange} accent="brand">
        <BarList data={monthlyBars} accent="#1971f5" />
      </Card>
      <Card title="Prioridad" icon={PieChart} accent="rose">
        <Donut data={priorityChart} unit="casos" size={130} />
      </Card>
      <Card title="Carga por ingeniero" description="Casos atendidos en el rango" icon={Users} accent="emerald">
        <BarList data={engineerLoad} accent="#10b981" />
      </Card>
      <Card title="FCR por ingeniero" description="% resueltos completos a la primera" icon={Gauge} accent="violet">
        <BarList data={engineerFcr} suffix="%" accent="#8b5cf6" />
      </Card>
      <Card title="Satisfacción (escala 1-7)" description={SATISFACTION_QUESTION} icon={SmilePlus} accent="emerald">
        <Donut data={satisfactionChart} unit="respuestas" />
      </Card>
      <Card title="Tecnovigilancia por etapa" description="Eventos adversos con el dispositivo" icon={ShieldAlert} accent="rose">
        <Donut data={tecnoStageChart} unit="casos" size={130} />
      </Card>
    </div>
  </div>
{:else if tab === 'satisfaccion'}
  <!-- ══ SATISFACCIÓN (Likert 1-7) ══ -->
  <div class="animate-fade-up space-y-4">
    <Card
      title={SATISFACTION_QUESTION}
      description="Escala Likert de 7 puntos que responde quien recibe el servicio al cerrar el caso."
      icon={SmilePlus}
      accent="emerald"
    >
      {#if !prod || prod.sat_count === 0}
        <EmptyState
          icon={SmilePlus}
          title="Sin calificaciones en el rango"
          description="Ningún caso cerrado en estas fechas tiene calificación de satisfacción."
        />
      {:else}
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Promedio</p>
            <p
              class="mt-1 text-2xl font-bold tabular-nums"
              style="color:{satisfactionColor(Math.round(prod.sat_avg ?? 4))}"
            >
              {prod.sat_avg ?? '—'} <span class="text-base text-slate-400">/ 7</span>
            </p>
            <p class="mt-0.5 text-xs text-slate-500">
              {satisfactionLabel(Math.round(prod.sat_avg ?? 0))}
            </p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Respuestas</p>
            <p class="mt-1 text-2xl font-bold tabular-nums text-slate-800">{prod.sat_count}</p>
            <p class="mt-0.5 text-xs text-slate-500">casos cerrados y calificados</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">% satisfechos</p>
            <p class="mt-1 text-2xl font-bold tabular-nums text-emerald-700">{satPositivePct}%</p>
            <p class="mt-0.5 text-xs text-slate-500">calificaron 5, 6 o 7</p>
          </div>
          <div class="rounded-xl border border-slate-200 bg-slate-50/70 px-4 py-3">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Insatisfechos</p>
            <p class="mt-1 text-2xl font-bold tabular-nums text-danger-700">{prod.sat_negative}</p>
            <p class="mt-0.5 text-xs text-slate-500">calificaron 1, 2 o 3</p>
          </div>
        </div>

        <!-- Distribución punto a punto: la forma de la escala se lee de un vistazo -->
        <div class="mt-5">
          <h4 class="section-label mb-2">Distribución de la escala</h4>
          <ul class="space-y-2">
            {#each satisfactionChart as d}
              {@const total = satisfactionChart.reduce((a, b) => a + b.value, 0) || 1}
              <li>
                <div class="mb-1 flex items-center justify-between gap-2 text-sm">
                  <span class="truncate text-slate-700">{d.label}</span>
                  <span class="shrink-0 tabular-nums text-slate-500">
                    {d.value} · {Math.round((d.value / total) * 100)}%
                  </span>
                </div>
                <div class="h-2.5 overflow-hidden rounded-full bg-slate-100">
                  <div
                    class="h-2.5 rounded-full transition-all"
                    style="width:{(d.value / total) * 100}%;background:{d.color}"
                  ></div>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    </Card>

    <div class="grid gap-4 lg:grid-cols-2">
      <Card title="Satisfechos vs. insatisfechos" icon={PieChart} accent="emerald">
        <Donut data={satisfactionGroupChart} unit="respuestas" />
      </Card>
      <Card
        title="Satisfacción por ingeniero"
        description="Promedio sobre 7 en el rango"
        icon={Users}
        accent="violet"
      >
        {#if !prod || prod.items.length === 0}
          <EmptyState icon={Users} title="Sin datos" description="No hay casos atendidos en el rango." />
        {:else}
          <ul class="space-y-2">
            {#each prod.items.filter((r) => r.sat_avg != null) as r}
              <li>
                <div class="mb-1 flex items-center justify-between gap-2 text-sm">
                  <span class="truncate text-slate-700">{r.engineer_name}</span>
                  <span class="shrink-0 tabular-nums text-slate-500">
                    {r.sat_avg} / 7 · {r.sat_count} resp.
                  </span>
                </div>
                <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                  <div
                    class="h-2 rounded-full"
                    style="width:{((r.sat_avg ?? 0) / 7) * 100}%;background:{satisfactionColor(
                      Math.round(r.sat_avg ?? 0),
                    )}"
                  ></div>
                </div>
              </li>
            {:else}
              <li class="value-pending text-sm">Ningún ingeniero tiene calificaciones en el rango.</li>
            {/each}
          </ul>
        {/if}
      </Card>
    </div>
  </div>
{:else if tab === 'tecnovigilancia'}
  <!-- ══ TECNOVIGILANCIA ══ -->
  <div class="animate-fade-up space-y-4">
    <div class="grid gap-3 sm:grid-cols-3">
      <Card>
        <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Eventos en el rango</p>
        <p class="mt-1 text-2xl font-bold tabular-nums text-danger-700">{tecno?.total ?? 0}</p>
      </Card>
      <Card>
        <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Proceso abierto</p>
        <p class="mt-1 text-2xl font-bold tabular-nums text-amber-700">{tecno?.open_total ?? 0}</p>
      </Card>
      <Card>
        <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Cerrados</p>
        <p class="mt-1 text-2xl font-bold tabular-nums text-emerald-700">
          {(tecno?.total ?? 0) - (tecno?.open_total ?? 0)}
        </p>
      </Card>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <Card title="Etapa del proceso" icon={PieChart} accent="rose">
        <Donut data={tecnoStageChart} unit="casos" />
      </Card>
      <Card
        title="Equipos con más eventos"
        description="Dónde se concentra el riesgo"
        icon={Stethoscope}
        accent="amber"
      >
        {#if tecnoEquipmentBars.length === 0}
          <EmptyState
            icon={Stethoscope}
            title="Sin eventos"
            description="Ningún equipo registra tecnovigilancia en el rango."
          />
        {:else}
          <BarList data={tecnoEquipmentBars} accent="#dc2626" />
        {/if}
      </Card>
    </div>

    <Card
      title="Casos de tecnovigilancia"
      description="Eventos adversos o incidentes en los que el equipo causó, o pudo causar, daño."
      icon={ShieldAlert}
      accent="rose"
    >
      <div class="mb-4 sm:max-w-xs">
        <Select
          bind:value={fTecnoStage}
          options={TECNOVIGILANCIA_STAGE_OPTIONS}
          placeholder="Todas las etapas"
        />
      </div>

      {#if filteredTecno.length === 0}
        <EmptyState
          icon={ShieldAlert}
          title="Sin casos de tecnovigilancia"
          description="No hay eventos marcados en el rango y la etapa seleccionados. Se marcan desde el detalle de cada caso."
        />
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="text-left text-xs uppercase text-slate-500">
              <tr class="border-b border-slate-200">
                <th class="py-2 pr-3">Caso</th>
                <th class="pr-3">Equipo</th>
                <th class="pr-3">Unidad</th>
                <th class="pr-3">Etapa</th>
                <th class="pr-3">¿Qué pasó?</th>
                <th class="pr-3">Ingeniero</th>
                <th class="pr-3">Marcado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              {#each filteredTecno as r (r.case_id)}
                {@const m = tecnovigilanciaStageMeta(r.stage)}
                <tr>
                  <td class="py-3 pr-3">
                    <a class="font-mono text-xs font-semibold text-brand-700 hover:underline" href={`/cases/${r.code}`}>
                      {r.code}
                    </a>
                    <div class="max-w-[200px] truncate text-slate-600" title={r.title}>{r.title}</div>
                  </td>
                  <td class="max-w-[170px] truncate pr-3 text-slate-600" title={r.equipment_label}>
                    {r.equipment_label}
                  </td>
                  <td class="pr-3 text-slate-600">{r.sector_name ?? '—'}</td>
                  <td class="whitespace-nowrap pr-3">
                    {#if m}
                      <span class="badge {m.tint} {m.text}">{m.label}</span>
                    {:else}
                      <span class="value-pending">Sin etapa</span>
                    {/if}
                  </td>
                  <td class="max-w-[260px] truncate pr-3 text-slate-600" title={r.description ?? ''}>
                    {#if r.description}{r.description}{:else}<span class="value-pending">Sin descripción</span>{/if}
                  </td>
                  <td class="pr-3 text-slate-600">
                    {#if r.engineer_name}{r.engineer_name}{:else}<span class="value-pending">Sin asignar</span>{/if}
                  </td>
                  <td class="whitespace-nowrap pr-3 text-slate-500">
                    {r.marked_at ? formatDate(r.marked_at) : formatDate(r.opened_at)}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        <p class="mt-3 text-xs text-slate-400">
          {filteredTecno.length} de {tecno?.total ?? 0} eventos en el rango
          {#if (tecno?.total ?? 0) >= 300}· mostrando los 300 más recientes{/if}
        </p>
      {/if}
    </Card>
  </div>
{:else if tab === 'ingenieros'}
  <!-- ══ POR INGENIERO ══ -->
  <div class="animate-fade-up">
    <Card title="Productividad por ingeniero" description="Atención, completitud, tiempos de respuesta y FCR en el rango." icon={Users} accent="emerald">
      {#if !prod || prod.items.length === 0}
        <EmptyState icon={Users} title="Sin datos en el rango" description="No hay casos atendidos por ingenieros en las fechas seleccionadas." />
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="text-left text-xs uppercase text-slate-500">
              <tr class="border-b border-slate-200">
                <th class="py-2 pr-3">Ingeniero</th>
                <th class="pr-3">Atendidos</th>
                <th class="pr-3">Completos</th>
                <th class="pr-3">Incompletos</th>
                <th class="pr-3">Respuesta</th>
                <th class="pr-3">A inicio</th>
                <th class="pr-3">Trabajo</th>
                <th class="pr-3">FCR</th>
                <th class="pr-3" title={SATISFACTION_QUESTION}>Satisf. prom.</th>
                <th class="pr-3" title="Satisfechos (5-7) / Neutrales (4) / Insatisfechos (1-3)">
                  Reparto
                </th>
                <th class="pr-3"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              {#each prod.items as r}
                <tr>
                  <td class="py-3 pr-3 font-medium text-slate-800">{r.engineer_name}</td>
                  <td class="pr-3 tabular-nums text-slate-600">{r.attended}</td>
                  <td class="pr-3 tabular-nums text-emerald-700">{r.completed}</td>
                  <td class="pr-3 tabular-nums text-amber-700">{r.incomplete}</td>
                  <td class="pr-3 tabular-nums text-slate-600">{h(r.avg_response_hours)}</td>
                  <td class="pr-3 tabular-nums text-slate-600">{h(r.avg_to_start_hours)}</td>
                  <td class="pr-3 tabular-nums text-slate-600">{h(r.avg_work_hours)}</td>
                  <td class="pr-3 tabular-nums text-brand-700">{r.fcr_pct}%</td>
                  <td class="pr-3 tabular-nums">
                    {#if r.sat_avg != null}
                      <span
                        class="inline-flex items-center gap-1.5 whitespace-nowrap font-semibold"
                        style="color:{satisfactionColor(Math.round(r.sat_avg))}"
                        title="{r.sat_count} respuesta(s)"
                      >
                        {r.sat_avg} / 7
                      </span>
                    {:else}
                      <span class="value-pending">Sin calificar</span>
                    {/if}
                  </td>
                  <td class="pr-3 tabular-nums">
                    <span class="inline-flex items-center gap-2 whitespace-nowrap text-xs">
                      <span class="text-emerald-700" title="Satisfechos (5-7)">▲ {r.sat_positive}</span>
                      <span class="text-slate-500" title="Neutrales (4)">■ {r.sat_neutral}</span>
                      <span class="text-danger-700" title="Insatisfechos (1-3)">▼ {r.sat_negative}</span>
                    </span>
                  </td>
                  <td class="pr-3">
                    <button
                      type="button"
                      class="inline-flex items-center gap-1 text-xs font-medium text-brand-600 hover:underline"
                      on:click={() => viewEngineerServices(r.engineer_name)}
                    >
                      Ver servicios <ArrowRight class="h-3 w-3" />
                    </button>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </Card>
  </div>
{:else if tab === 'equipos'}
  <!-- ══ POR EQUIPO ══ -->
  <div class="animate-fade-up">
    <Card title="Servicio por equipo" description="Cuántos casos tuvo cada equipo, qué tipo de trabajo y cuánto se demoró." icon={Stethoscope} accent="brand">
      {#if !eqReport || eqReport.items.length === 0}
        <EmptyState icon={Stethoscope} title="Sin servicios en el rango" description="Ningún equipo tuvo casos en las fechas seleccionadas." />
      {:else}
        {#if topEquipment}
          <div class="mb-4 flex flex-wrap items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
            <ShieldAlert class="h-5 w-5 shrink-0 text-amber-600" />
            <div class="min-w-0 text-sm">
              <span class="font-semibold text-amber-800">Equipo con más casos (reincidencia):</span>
              <a class="font-medium text-amber-900 hover:underline" href={`/equipment/${topEquipment.code}`}>
                {topEquipment.code} · {topEquipment.name}
              </a>
              <span class="text-amber-700">— {topEquipment.cases_total} casos en el rango.</span>
            </div>
          </div>
        {/if}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="text-left text-xs uppercase text-slate-500">
              <tr class="border-b border-slate-200">
                <th class="py-2 pr-3">Equipo</th>
                <th class="pr-3">Unidad</th>
                <th class="pr-3">Casos</th>
                <th class="pr-3">Completos</th>
                <th class="pr-3">Incompletos</th>
                <th class="pr-3">Correct. / Prev.</th>
                <th class="pr-3">T. prom. trabajo</th>
                <th class="pr-3">Min. operación</th>
                <th class="pr-3">Último servicio</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              {#each eqReport.items as r (r.equipment_id)}
                <tr>
                  <td class="py-3 pr-3">
                    <a class="font-medium text-brand-700 hover:underline" href={`/equipment/${r.code}`}>
                      {r.code} · {r.name}
                    </a>
                  </td>
                  <td class="pr-3 text-slate-600">{r.sector_name ?? '—'}</td>
                  <td class="pr-3 tabular-nums font-semibold text-slate-800">
                    <span class="inline-flex items-center gap-1.5">
                      {r.cases_total}
                      {#if r.cases_total >= RECURRENCE_MIN}
                        <span class="badge bg-amber-50 text-amber-700" title="Equipo reincidente ({r.cases_total} casos)">
                          <ShieldAlert class="mr-0.5 inline h-3 w-3" /> Reincidente
                        </span>
                      {/if}
                    </span>
                  </td>
                  <td class="pr-3 tabular-nums text-emerald-700">{r.completed}</td>
                  <td class="pr-3 tabular-nums text-amber-700">{r.incomplete}</td>
                  <td class="pr-3 tabular-nums text-slate-600">{r.corrective} / {r.preventive}</td>
                  <td class="pr-3 tabular-nums text-slate-600">{h(r.avg_work_hours)}</td>
                  <td class="pr-3 tabular-nums text-slate-600">{r.total_operation_minutes}</td>
                  <td class="pr-3 text-slate-500">{r.last_service_at ? formatDate(r.last_service_at) : '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </Card>
  </div>
{:else if tab === 'servicios'}
  <!-- ══ SERVICIOS (detalle) ══ -->
  <div class="animate-fade-up">
    <Card title="Historial de servicios" description="Cada servicio: qué se hizo, quién atendió y cuánto se demoró." icon={ClipboardList} accent="amber">
      <div class="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Select bind:value={fEngineer} options={engineerOptions} placeholder="Todos los ingenieros" />
        <Select bind:value={fEquipment} options={equipmentOptions} placeholder="Todos los equipos" />
        <Select bind:value={fType} options={TYPE_OPTIONS} placeholder="Todos los tipos de actividad" />
        <Select
          bind:value={fSatisfaction}
          options={SATISFACTION_FILTER_OPTIONS}
          placeholder="Toda la satisfacción (1-7)"
        />
        <Select bind:value={fTecno} options={TECNO_FILTER_OPTIONS} placeholder="Tecnovigilancia: todos" />
      </div>

      {#if filteredServices.length === 0}
        <EmptyState icon={ClipboardList} title="Sin servicios" description="No hay servicios que coincidan con los filtros y el rango de fechas." />
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="text-left text-xs uppercase text-slate-500">
              <tr class="border-b border-slate-200">
                <th class="py-2 pr-3">Fecha</th>
                <th class="pr-3">Caso</th>
                <th class="pr-3">Equipo</th>
                <th class="pr-3">Ingeniero</th>
                <th class="pr-3">Tipo</th>
                <th class="pr-3">Qué se hizo</th>
                <th class="pr-3">Respuesta</th>
                <th class="pr-3">Trabajo</th>
                <th class="pr-3" title={SATISFACTION_QUESTION}>Satisfacción</th>
                <th class="pr-3">Resultado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              {#each filteredServices as s (s.case_id)}
                <tr>
                  <td class="whitespace-nowrap py-3 pr-3 text-slate-500">{formatDateTime(s.opened_at)}</td>
                  <td class="pr-3">
                    <a class="font-mono text-xs font-semibold text-brand-700 hover:underline" href={`/cases/${s.code}`}>{s.code}</a>
                    {#if s.is_tecnovigilancia}
                      <span
                        class="badge ml-1 bg-danger-50 text-danger-700"
                        title="Tecnovigilancia · {tecnovigilanciaStageLabel(s.tecnovigilancia_stage)}"
                      >
                        <ShieldAlert class="inline h-3 w-3" />
                      </span>
                    {/if}
                  </td>
                  <td class="max-w-[180px] truncate pr-3 text-slate-600" title={s.equipment_label}>{s.equipment_label}</td>
                  <td class="pr-3 text-slate-600">
                    {#if s.engineer_name}{s.engineer_name}{:else}<span class="value-pending">Sin asignar</span>{/if}
                  </td>
                  <td class="pr-3 text-slate-600">{typeLabel(s.type)}</td>
                  <td class="max-w-[220px] truncate pr-3 text-slate-600" title={s.work_performed ?? s.title}>
                    {#if s.work_performed}{s.work_performed}{:else}<span class="value-pending">Sin registrar</span>{/if}
                  </td>
                  <td class="whitespace-nowrap pr-3 tabular-nums text-slate-600">{elapsedBetween(s.assigned_at, s.accepted_at)}</td>
                  <td class="whitespace-nowrap pr-3 tabular-nums text-slate-600">{elapsedBetween(s.work_started_at, s.finished_at)}</td>
                  <td class="whitespace-nowrap pr-3">
                    {#if s.satisfaction_score}
                      <span
                        class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700"
                        title="{s.satisfaction_score} — {satisfactionLabel(s.satisfaction_score)}"
                      >
                        <span
                          class="grid h-5 w-5 place-items-center rounded-full text-[10px] font-bold text-white"
                          style="background:{satisfactionColor(s.satisfaction_score)}"
                        >
                          {s.satisfaction_score}
                        </span>
                        {satisfactionLabel(s.satisfaction_score)}
                      </span>
                    {:else}
                      <span class="value-pending">Sin calificar</span>
                    {/if}
                  </td>
                  <td class="pr-3">
                    {#if complLabel(s.completion)}
                      <span class="badge {s.completion === 'complete' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}">
                        {complLabel(s.completion)}
                      </span>
                    {:else}
                      <span class="badge bg-slate-100 text-slate-600">{statusLabel(s.status)}</span>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
        <p class="mt-3 text-xs text-slate-400">
          {filteredServices.length} de {services?.total ?? 0} servicios en el rango
          {#if (services?.total ?? 0) >= 300}· mostrando los 300 más recientes{/if}
        </p>
      {/if}
    </Card>
  </div>
{/if}

<!-- Modal de detalle: casos detrás de una tarjeta clicable -->
<Modal bind:open={modalOpen} title={modalTitle} size="lg" on:close={() => (modalOpen = false)}>
  {#if modalRows.length === 0}
    <EmptyState icon={ClipboardList} title="Sin casos" description="No hay casos que coincidan en el rango seleccionado." />
  {:else}
    <p class="mb-3 text-sm text-slate-500">{modalRows.length} caso(s). Haz clic en el código para abrirlo.</p>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="text-left text-xs uppercase text-slate-500">
          <tr class="border-b border-slate-200">
            <th class="py-2 pr-3">Caso</th>
            <th class="pr-3">Equipo</th>
            <th class="pr-3">Tipo</th>
            <th class="pr-3">Satisfacción</th>
            <th class="pr-3">Ingeniero</th>
            <th class="pr-3">Fecha</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          {#each modalRows as s (s.case_id)}
            <tr>
              <td class="py-2.5 pr-3">
                <a class="font-mono text-xs font-semibold text-brand-700 hover:underline" href={`/cases/${s.code}`}>{s.code}</a>
                <div class="max-w-[220px] truncate text-slate-600" title={s.title}>{s.title}</div>
              </td>
              <td class="max-w-[160px] truncate pr-3 text-slate-600" title={s.equipment_label}>{s.equipment_label}</td>
              <td class="pr-3 text-slate-600">{typeLabel(s.type)}</td>
              <td class="whitespace-nowrap pr-3">
                {#if s.satisfaction_score}
                  <span
                    class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-700"
                    title="{s.satisfaction_score} — {satisfactionLabel(s.satisfaction_score)}"
                  >
                    <span
                      class="grid h-5 w-5 place-items-center rounded-full text-[10px] font-bold text-white"
                      style="background:{satisfactionColor(s.satisfaction_score)}"
                    >
                      {s.satisfaction_score}
                    </span>
                    {satisfactionLabel(s.satisfaction_score)}
                  </span>
                {:else}
                  <span class="value-pending">—</span>
                {/if}
              </td>
              <td class="pr-3 text-slate-600">
                {#if s.engineer_name}{s.engineer_name}{:else}<span class="value-pending">Sin asignar</span>{/if}
              </td>
              <td class="whitespace-nowrap pr-3 text-slate-500">{formatDate(s.opened_at)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</Modal>
