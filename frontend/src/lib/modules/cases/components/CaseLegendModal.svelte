<script lang="ts">
  import Modal from '$lib/components/Modal.svelte';
  import type { CasePriority, CaseStatus } from '$lib/api/types';
  import {
    STATUS_META,
    STATUS_DESCRIPTIONS,
    PRIORITY_META,
    PRIORITY_DESCRIPTIONS,
  } from '$lib/modules/cases/ui';

  export let open = false;

  const statuses = Object.keys(STATUS_META) as CaseStatus[];
  const priorities = (Object.keys(PRIORITY_META) as CasePriority[]).slice().reverse();
</script>

<Modal {open} title="Guía de casos · estados y prioridades" size="lg" on:close={() => (open = false)}>
  <div class="space-y-5">
    <section>
      <h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Estados</h4>
      <ul class="grid gap-2 sm:grid-cols-2">
        {#each statuses as s}
          <li class="flex items-start gap-2.5 rounded-lg border border-slate-100 bg-slate-50/60 p-2.5">
            <span class="mt-0.5 h-3 w-3 shrink-0 rounded-full" style="background:{STATUS_META[s].color}"></span>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-slate-800">{STATUS_META[s].label}</p>
              <p class="text-xs leading-snug text-slate-500">{STATUS_DESCRIPTIONS[s]}</p>
            </div>
          </li>
        {/each}
      </ul>
    </section>

    <section>
      <h4 class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Prioridades</h4>
      <ul class="grid gap-2 sm:grid-cols-2">
        {#each priorities as p}
          <li class="flex items-start gap-2.5 rounded-lg border border-slate-100 bg-slate-50/60 p-2.5">
            <span
              class="mt-0.5 h-3 w-3 shrink-0 rounded-full {PRIORITY_META[p].pulse ? 'animate-pulse-ring' : ''}"
              style="background:{PRIORITY_META[p].color}; --glow:{PRIORITY_META[p].glow}"
            ></span>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-slate-800">{PRIORITY_META[p].label}</p>
              <p class="text-xs leading-snug text-slate-500">{PRIORITY_DESCRIPTIONS[p]}</p>
            </div>
          </li>
        {/each}
      </ul>
    </section>

    <p class="rounded-lg bg-brand-50 p-3 text-xs text-brand-800">
      💡 Las tarjetas y los indicadores <strong>titilan</strong> cuando un caso es de prioridad alta/crítica,
      cuando su SLA está vencido o cuando lleva demasiado tiempo abierto.
    </p>
  </div>
</Modal>
