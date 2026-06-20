<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Clock, Cpu, Pencil, ArrowUpRight, AlarmClock, Loader2 } from 'lucide-svelte';
  import Select from '$lib/components/Select.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case } from '$lib/modules/cases/types';
  import type { User } from '$lib/modules/users/types';
  import {
    PRIORITY_META,
    STATUS_META,
    STATUS_GROUP_OPTIONS,
    statusGroupKey,
    groupToStatus,
    TYPE_LABEL,
    caseAgeHours,
    formatAge,
    isAging,
    isActive,
    slaInfo,
  } from '$lib/modules/cases/ui';
  import { toasts } from '$lib/stores/toasts';

  export let c: Case;
  export let equipmentName = '';
  export let engineers: User[] = [];

  const dispatch = createEventDispatcher<{ changed: Case; edit: Case }>();

  let busy = false;

  // Valores locales de los selects en línea (se resincronizan si cambia `c`).
  // El estado se muestra resumido por grupo (Esp. repuestos/cliente → "En espera").
  let statusVal = statusGroupKey(c.status);
  let assigneeVal = c.assigned_to ?? '';
  $: statusVal = statusGroupKey(c.status);
  $: assigneeVal = c.assigned_to ?? '';

  $: prio = PRIORITY_META[c.priority];
  $: stat = STATUS_META[c.status];
  $: sla = slaInfo(c);
  $: aging = isAging(c);
  $: ageStr = formatAge(caseAgeHours(c));
  $: alarm = isActive(c) && (sla.state === 'overdue' || aging); // semáforo rojo
  $: engineerOptions = engineers.map((u) => ({ value: u.id, label: u.full_name }));

  async function persist(patch: Partial<Case>) {
    busy = true;
    try {
      const updated = await casesApi.update(c.id, patch as never);
      dispatch('changed', updated);
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo actualizar');
      // revertir selects a lo último conocido
      statusVal = c.status;
      assigneeVal = c.assigned_to ?? '';
    } finally {
      busy = false;
    }
  }

  function onStatusChange(v: string) {
    const next = groupToStatus(v, c.status);
    if (next !== c.status) persist({ status: next });
  }
  function onAssigneeChange(v: string) {
    if ((v || null) !== (c.assigned_to ?? null)) persist({ assigned_to: (v || null) as never });
  }
</script>

<article
  class="group relative flex flex-col gap-3 overflow-hidden rounded-2xl border bg-white/90 p-3.5 shadow-sm backdrop-blur transition
    {alarm ? 'border-rose-200' : prio.pulse ? 'border-amber-200' : 'border-slate-200'}
    hover:-translate-y-0.5 hover:shadow-md"
  class:animate-glow-breathe={alarm}
  style={alarm ? `--glow:${sla.state === 'overdue' ? 'rgba(244,63,94,.5)' : prio.glow}` : ''}
>
  <!-- Barra de acento de estado a la izquierda -->
  <span class="absolute inset-y-0 left-0 w-1" style="background:{stat.color}"></span>

  <!-- Cabecera: semáforo + código + tipo -->
  <div class="flex items-start justify-between gap-2 pl-1.5">
    <div class="flex min-w-0 items-center gap-2">
      <span class="relative grid h-3 w-3 shrink-0 place-items-center">
        <span
          class="h-3 w-3 rounded-full {prio.pulse ? 'animate-pulse-ring' : ''}"
          style="background:{prio.color}; --glow:{prio.glow}"
        ></span>
      </span>
      <a
        href={`/cases/${c.id}`}
        class="truncate font-mono text-sm font-bold text-slate-900 hover:text-brand-700 hover:underline"
      >
        {c.code}
      </a>
      <span class="shrink-0 rounded-md px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide {stat.tint} {stat.text}">
        {TYPE_LABEL[c.type]}
      </span>
    </div>
    {#if busy}
      <Loader2 class="h-4 w-4 shrink-0 animate-spin text-brand-500" />
    {/if}
  </div>

  <!-- Título + equipo -->
  <div class="min-w-0 pl-1.5">
    <a href={`/cases/${c.id}`} class="line-clamp-2 text-sm font-semibold text-slate-800 hover:text-brand-700">
      {c.title}
    </a>
    {#if equipmentName}
      <p class="mt-1 flex items-center gap-1.5 text-xs text-slate-500">
        <Cpu class="h-3.5 w-3.5 shrink-0 text-slate-400" />
        <span class="truncate">{equipmentName}</span>
      </p>
    {/if}
  </div>

  <!-- Controles en línea: estado + asignado -->
  <div class="grid grid-cols-2 gap-2 pl-1.5">
    <Select
      bind:value={statusVal}
      options={STATUS_GROUP_OPTIONS}
      disabled={busy}
      on:change={(e) => onStatusChange(e.detail)}
    />
    <Select
      bind:value={assigneeVal}
      options={engineerOptions}
      placeholder="Sin asignar"
      disabled={busy}
      on:change={(e) => onAssigneeChange(e.detail)}
    />
  </div>

  <!-- Pie: edad + SLA + acciones -->
  <div class="flex items-center justify-between gap-2 pl-1.5">
    <div class="flex min-w-0 items-center gap-1.5">
      <span
        class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-medium tabular-nums
          {aging ? 'bg-rose-50 text-rose-600' : 'bg-slate-100 text-slate-500'}"
        title="Tiempo desde la apertura"
      >
        <Clock class="h-3 w-3" />{ageStr}
      </span>
      {#if sla.state !== 'none'}
        <span
          class="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-medium
            {sla.state === 'overdue'
              ? 'bg-rose-100 text-rose-700 animate-blink'
              : sla.state === 'soon'
                ? 'bg-amber-100 text-amber-700'
                : 'bg-emerald-50 text-emerald-600'}"
          title="SLA"
        >
          <AlarmClock class="h-3 w-3" />{sla.label}
        </span>
      {/if}
    </div>

    <div class="flex shrink-0 items-center gap-1">
      <button
        type="button"
        class="grid h-7 w-7 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-600"
        on:click={() => dispatch('edit', c)}
        aria-label="Editar caso"
        title="Editar"
      >
        <Pencil class="h-4 w-4" />
      </button>
      <a
        href={`/cases/${c.id}`}
        class="grid h-7 w-7 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-600"
        aria-label="Abrir detalle"
        title="Abrir"
      >
        <ArrowUpRight class="h-4 w-4" />
      </a>
    </div>
  </div>
</article>
