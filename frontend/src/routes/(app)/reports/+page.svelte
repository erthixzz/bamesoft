<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { reportsApi } from '$lib/modules/reports/api';
  import type { ComplianceReport } from '$lib/modules/reports/types';
  import { setPageTitle } from '$lib/stores/page';

  let report: ComplianceReport | null = null;

  onMount(async () => {
    setPageTitle('Reportes');
    report = await reportsApi.compliance();
  });
</script>

<Card title="Cumplimiento por norma">
  <table class="w-full text-sm">
    <thead class="text-left text-xs uppercase text-slate-500">
      <tr>
        <th class="py-2">Código</th><th>Norma</th><th>Equipos</th><th>Cobertura</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-slate-100">
      {#each report?.items ?? [] as r}
        <tr>
          <td class="py-2 font-medium">{r.standard_code}</td>
          <td>{r.standard_name}</td>
          <td>{r.equipment_with} / {r.equipment_total}</td>
          <td>
            <div class="flex items-center gap-2">
              <div class="h-2 w-32 rounded-full bg-slate-100">
                <div class="h-2 rounded-full bg-brand-500" style="width: {Math.min(100, r.coverage_pct)}%"></div>
              </div>
              <span class="tabular-nums text-slate-700">{r.coverage_pct.toFixed(1)}%</span>
            </div>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
</Card>
