<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Badge from '$lib/components/Badge.svelte';
  import Button from '$lib/components/Button.svelte';
  import { alertsApi } from '$lib/modules/alerts/api';
  import type { Alert } from '$lib/modules/alerts/types';
  import { formatDate, timeFromNow } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';

  let rows: Alert[] = [];
  let loading = false;

  async function load() {
    rows = await alertsApi.list();
  }

  async function sweep() {
    loading = true;
    try {
      const r = await alertsApi.sweep();
      toasts.success(`Generadas: ${r.preventive} preventivas · ${r.calibrations} calibraciones`);
      await load();
    } finally {
      loading = false;
    }
  }

  async function ack(id: string) {
    await alertsApi.ack(id);
    await load();
  }
  async function resolve(id: string) {
    await alertsApi.resolve(id);
    await load();
  }

  function tone(sev: Alert['severity']): 'red' | 'yellow' | 'blue' {
    return sev === 'critical' ? 'red' : sev === 'warning' ? 'yellow' : 'blue';
  }

  onMount(() => {
    setPageTitle('Alertas');
    load();
  });
</script>

<div class="mb-4 flex justify-end gap-2">
  <Button variant="secondary" on:click={sweep} {loading}>Generar automáticas</Button>
  <a class="btn-primary" href="/alerts/new">+ Nueva alerta</a>
</div>

<div class="grid gap-3">
  {#each rows as a}
    <Card>
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2">
            <Badge tone={tone(a.severity)}>{a.severity}</Badge>
            <span class="text-xs uppercase text-slate-500">{a.type}</span>
          </div>
          <p class="mt-1 font-medium">{a.title}</p>
          <p class="text-sm text-slate-600">{a.message}</p>
          <p class="mt-1 text-xs text-slate-400">
            {timeFromNow(a.created_at)} · vence {formatDate(a.due_at)}
          </p>
        </div>
        <div class="flex gap-2">
          {#if !a.acknowledged_at}
            <Button variant="secondary" on:click={() => ack(a.id)}>Reconocer</Button>
          {/if}
          {#if !a.resolved_at}
            <Button on:click={() => resolve(a.id)}>Resolver</Button>
          {/if}
        </div>
      </div>
    </Card>
  {:else}
    <p class="text-slate-500">No hay alertas activas.</p>
  {/each}
</div>
