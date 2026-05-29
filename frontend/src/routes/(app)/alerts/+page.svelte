<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Badge from '$lib/components/Badge.svelte';
  import Button from '$lib/components/Button.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import { alertsApi } from '$lib/modules/alerts/api';
  import type { Alert } from '$lib/modules/alerts/types';
  import type { CtxItem } from '$lib/stores/contextMenu';
  import { contextmenu } from '$lib/actions/contextmenu';
  import { formatDate, timeFromNow } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { AlertTriangle, BellRing, PlusCircle, Sparkles, Check, CheckCheck, Copy } from 'lucide-svelte';

  let rows: Alert[] = [];
  let loading = false;
  let firstLoad = true;

  async function load() {
    loading = true;
    try {
      rows = await alertsApi.list();
    } finally {
      loading = false;
      firstLoad = false;
    }
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

  async function copy(text: string, label = 'Copiado') {
    try {
      await navigator.clipboard.writeText(text);
      toasts.success(label);
    } catch {
      toasts.error('No se pudo copiar');
    }
  }

  const rowMenu = (a: Alert): CtxItem[] => [
    ...(!a.acknowledged_at
      ? [{ label: 'Reconocer', icon: Check, onClick: () => ack(a.id) } as CtxItem]
      : []),
    ...(!a.resolved_at
      ? [{ label: 'Resolver', icon: CheckCheck, onClick: () => resolve(a.id) } as CtxItem]
      : []),
    { divider: true },
    { label: 'Copiar mensaje', icon: Copy, onClick: () => copy(a.message, 'Mensaje copiado') },
  ];

  onMount(() => {
    setPageTitle('Alertas');
    load();
  });
</script>

<PageHeader title="Alertas" subtitle="Vencimientos de mantenimiento, calibraciones y SLAs" icon={AlertTriangle} gradient="rose">
  <svelte:fragment slot="actions">
    <Button variant="secondary" on:click={sweep} {loading}>
      <Sparkles class="h-4 w-4" /> Generar automáticas
    </Button>
    <a class="btn-primary" href="/alerts/new">
      <PlusCircle class="h-4 w-4" /> Nueva alerta
    </a>
  </svelte:fragment>
</PageHeader>

{#if loading && firstLoad}
  <Card><Spinner label="Cargando alertas…" /></Card>
{:else if rows.length === 0}
  <Card>
    <EmptyState
      icon={BellRing}
      title="Sin alertas activas"
      description="Cuando un equipo tenga mantenimiento o calibración por vencer, aparecerá aquí. Puedes generar las automáticas o crear una manual."
    >
      <svelte:fragment slot="actions">
        <Button variant="secondary" on:click={sweep}>Generar automáticas</Button>
        <a class="btn-primary" href="/alerts/new">+ Nueva alerta</a>
      </svelte:fragment>
    </EmptyState>
  </Card>
{:else}
  <div class="grid gap-3">
    {#each rows as a}
      <div use:contextmenu={rowMenu(a)} class="cursor-context-menu">
      <Card>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <Badge tone={tone(a.severity)}>{a.severity}</Badge>
              <span class="text-xs uppercase text-slate-500">{a.type}</span>
            </div>
            <p class="mt-1 font-medium">{a.title}</p>
            <p class="text-sm text-slate-600">{a.message}</p>
            <p class="mt-1 text-xs text-slate-400">
              {timeFromNow(a.created_at)} · vence {formatDate(a.due_at)}
            </p>
          </div>
          <div class="flex flex-wrap gap-2 sm:shrink-0">
            {#if !a.acknowledged_at}
              <Button variant="secondary" on:click={() => ack(a.id)}>Reconocer</Button>
            {/if}
            {#if !a.resolved_at}
              <Button on:click={() => resolve(a.id)}>Resolver</Button>
            {/if}
          </div>
        </div>
      </Card>
      </div>
    {/each}
  </div>
{/if}
