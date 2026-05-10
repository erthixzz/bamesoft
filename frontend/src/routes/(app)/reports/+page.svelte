<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type { ComplianceReport } from '$lib/modules/reports/types';
  import { setPageTitle } from '$lib/stores/page';
  import { BarChart3, FileBarChart } from 'lucide-svelte';

  let report: ComplianceReport | null = null;
  let loading = true;

  onMount(async () => {
    setPageTitle('Reportes');
    try {
      report = await reportsApi.compliance();
    } finally {
      loading = false;
    }
  });
</script>

<PageHeader title="Reportes" subtitle="Cumplimiento normativo y trazabilidad" icon={BarChart3} gradient="emerald" />

<Card title="Cumplimiento por norma" description="Cobertura de las normas aplicables al inventario.">
  {#if loading}
    <Spinner label="Calculando reportes…" />
  {:else if !report || report.items.length === 0}
    <EmptyState
      icon={FileBarChart}
      title="Sin normas mapeadas"
      description="Una vez que vincules tus equipos a las normas correspondientes (ISO 13485, IEC 60601, INVIMA…), aquí verás el porcentaje de cumplimiento."
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
          {#each report.items as r}
            <tr>
              <td class="py-3 pr-3 font-medium text-slate-800">{r.standard_code}</td>
              <td class="pr-3 text-slate-600">{r.standard_name}</td>
              <td class="pr-3 tabular-nums text-slate-600">{r.equipment_with} / {r.equipment_total}</td>
              <td>
                <div class="flex items-center gap-3">
                  <div class="h-2 w-32 overflow-hidden rounded-full bg-slate-100">
                    <div
                      class="h-2 rounded-full bg-gradient-to-r from-brand-500 to-cyan-500"
                      style="width: {Math.min(100, r.coverage_pct)}%"
                    ></div>
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
