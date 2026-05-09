<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import Card from '$lib/components/Card.svelte';
  import Input from '$lib/components/Input.svelte';
  import Button from '$lib/components/Button.svelte';
  import CaseStatusBadge from '$lib/modules/cases/components/CaseStatusBadge.svelte';
  import PriorityBadge from '$lib/modules/cases/components/PriorityBadge.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case, CaseActivity } from '$lib/modules/cases/types';
  import { formatDateTime, timeFromNow } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';

  let id = '';
  let c: Case | null = null;
  let activities: CaseActivity[] = [];
  let newNote = '';

  $: id = $page.params.id ?? '';
  $: setPageTitle(c ? `Caso ${c.code}` : 'Caso');

  async function reload() {
    [c, activities] = await Promise.all([casesApi.get(id), casesApi.activities(id)]);
  }

  onMount(reload);

  async function addNote() {
    if (!newNote.trim()) return;
    try {
      await casesApi.addActivity(id, 'note', newNote);
      newNote = '';
      await reload();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error');
    }
  }
</script>

{#if c}
  <div class="grid gap-4 lg:grid-cols-3">
    <Card title={c.title} description={c.description ?? ''}>
      <div class="flex flex-wrap gap-3">
        <CaseStatusBadge status={c.status} />
        <PriorityBadge priority={c.priority} />
        <span class="badge bg-slate-100 text-slate-700">Tipo: {c.type}</span>
      </div>
      <dl class="mt-4 grid grid-cols-2 gap-y-1 text-sm">
        <dt class="text-slate-500">Abierto</dt><dd>{formatDateTime(c.opened_at)}</dd>
        <dt class="text-slate-500">SLA</dt><dd>{formatDateTime(c.sla_due_at)}</dd>
        <dt class="text-slate-500">Cerrado</dt><dd>{formatDateTime(c.closed_at)}</dd>
      </dl>
    </Card>

    <Card title="Bitácora" description="Histórico de actividades del caso">
      <ul class="space-y-3">
        {#each activities as a}
          <li class="border-l-2 border-brand-200 pl-3">
            <p class="text-sm font-medium">{a.action}</p>
            {#if a.notes}
              <p class="text-sm text-slate-600">{a.notes}</p>
            {/if}
            <p class="text-xs text-slate-400">{timeFromNow(a.created_at)}</p>
          </li>
        {:else}
          <li class="text-sm text-slate-400">Sin actividad aún.</li>
        {/each}
      </ul>
    </Card>

    <Card title="Añadir nota">
      <Input bind:value={newNote} placeholder="Escribe una nota…" />
      <div class="mt-3"><Button on:click={addNote}>Añadir</Button></div>
    </Card>
  </div>
{/if}
