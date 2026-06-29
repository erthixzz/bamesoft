<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import Button from '$lib/components/Button.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type {
    ComplianceReport,
    OperationsReport,
    ProductivityReport,
  } from '$lib/modules/reports/types';
  import { setPageTitle } from '$lib/stores/page';
  import { formatDate } from '$lib/utils/format';
  import { BarChart3, FileBarChart, Users, PhoneCall } from 'lucide-svelte';

  let compliance: ComplianceReport | null = null;
  let prod: ProductivityReport | null = null;
  let ops: OperationsReport | null = null;
  let loading = true;

  // Rango por defecto: últimos 30 días.
  const today = new Date();
  const past = new Date(today.getTime() - 30 * 86400000);
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  let dateFrom = iso(past);
  let dateTo = iso(today);

  $: maxDaily = ops
    ? Math.max(1, ...ops.daily.map((d) => Math.max(d.reported, d.closed)))
    : 1;
  $: maxReporter = ops ? Math.max(1, ...ops.by_reporter.map((r) => r.count)) : 1;

  const h = (v: number | null) => (v == null ? '—' : `${v} h`);

  async function load() {
    loading = true;
    try {
      const range = { date_from: dateFrom, date_to: dateTo };
      [compliance, prod, ops] = await Promise.all([
        reportsApi.compliance(),
        reportsApi.productivity(range),
        reportsApi.operations(range),
      ]);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Reportes');
    load();
  });

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

{#if loading}
  <Spinner label="Calculando reportes…" />
{:else}
  <!-- KPIs -->
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
    {#each kpis as k}
      <Card>
        <p class="text-xs font-medium uppercase tracking-wide text-slate-400">{k.label}</p>
        <p class="mt-1 text-2xl font-bold tabular-nums {k.tone}">{k.value}</p>
      </Card>
    {/each}
  </div>

  <!-- Productividad por ingeniero -->
  <div class="mt-4">
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
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </Card>
  </div>

  <div class="mt-4 grid gap-4 lg:grid-cols-2">
    <!-- Llamadas por día -->
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

    <!-- Quién reportó la llamada -->
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

  <!-- Cumplimiento normativo -->
  <div class="mt-4">
    <Card title="Cumplimiento por norma" description="Cobertura de las normas aplicables al inventario." icon={FileBarChart} accent="brand">
      {#if !compliance || compliance.items.length === 0}
        <EmptyState
          icon={FileBarChart}
          title="Sin normas mapeadas"
          description="Vincula tus equipos a las normas (ISO 13485, IEC 60601, INVIMA…) para ver el cumplimiento."
        />
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
{/if}
