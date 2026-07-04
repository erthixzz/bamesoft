<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import Button from '$lib/components/Button.svelte';
  import Select from '$lib/components/Select.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type {
    ComplianceReport,
    EquipmentReport,
    OperationsReport,
    ProductivityReport,
    ServicesReport,
  } from '$lib/modules/reports/types';
  import type { CaseCompletion, CaseStatus, CaseType } from '$lib/api/types';
  import { TYPE_LABEL, COMPLETION_LABEL, STATUS_META, elapsedBetween } from '$lib/modules/cases/ui';
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
  } from 'lucide-svelte';

  let compliance: ComplianceReport | null = null;
  let prod: ProductivityReport | null = null;
  let ops: OperationsReport | null = null;
  let eqReport: EquipmentReport | null = null;
  let services: ServicesReport | null = null;
  let loading = true;

  // Rango por defecto: últimos 30 días.
  const today = new Date();
  const past = new Date(today.getTime() - 30 * 86400000);
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  let dateFrom = iso(past);
  let dateTo = iso(today);

  // Apartados
  type Tab = 'resumen' | 'ingenieros' | 'equipos' | 'servicios';
  let tab: Tab = 'resumen';
  const TABS: { key: Tab; label: string; icon: typeof Gauge }[] = [
    { key: 'resumen', label: 'Resumen', icon: Gauge },
    { key: 'ingenieros', label: 'Por ingeniero', icon: Users },
    { key: 'equipos', label: 'Por equipo', icon: Stethoscope },
    { key: 'servicios', label: 'Servicios', icon: ClipboardList },
  ];

  // Filtros del apartado Servicios (sobre los datos ya cargados).
  let fEngineer = '';
  let fEquipment = '';

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
      (!fEquipment || s.equipment_label === fEquipment),
  );

  async function load() {
    loading = true;
    try {
      const range = { date_from: dateFrom, date_to: dateTo };
      [compliance, prod, ops, eqReport, services] = await Promise.all([
        reportsApi.compliance(),
        reportsApi.productivity(range),
        reportsApi.operations(range),
        reportsApi.equipment(range),
        reportsApi.services(range),
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

  $: kpis = ops
    ? [
        { label: 'Reportadas', value: ops.reported_total, tone: 'text-brand-700' },
        { label: 'Cerradas', value: ops.closed_total, tone: 'text-emerald-700' },
        { label: 'Completas', value: ops.complete_total, tone: 'text-emerald-700' },
        { label: 'Incompletas', value: ops.incomplete_total, tone: 'text-amber-700' },
        { label: 'En espera', value: ops.waiting_now, tone: 'text-orange-700' },
        { label: 'FCR', value: prod ? `${prod.fcr_pct}%` : '—', tone: 'text-brand-700' },
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
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {#each kpis as k}
        <Card>
          <p class="text-xs font-medium uppercase tracking-wide text-slate-400">{k.label}</p>
          <p class="mt-1 text-2xl font-bold tabular-nums {k.tone}">{k.value}</p>
        </Card>
      {/each}
    </div>

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
                  <td class="pr-3 tabular-nums font-semibold text-slate-800">{r.cases_total}</td>
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
      <div class="mb-4 grid gap-3 sm:grid-cols-2 lg:max-w-2xl">
        <Select bind:value={fEngineer} options={engineerOptions} placeholder="Todos los ingenieros" />
        <Select bind:value={fEquipment} options={equipmentOptions} placeholder="Todos los equipos" />
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
                <th class="pr-3">Resultado</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              {#each filteredServices as s (s.case_id)}
                <tr>
                  <td class="whitespace-nowrap py-3 pr-3 text-slate-500">{formatDateTime(s.opened_at)}</td>
                  <td class="pr-3">
                    <a class="font-mono text-xs font-semibold text-brand-700 hover:underline" href={`/cases/${s.code}`}>{s.code}</a>
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
