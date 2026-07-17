<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Clock, Cpu, Pencil, ArrowUpRight, AlarmClock, Loader2 } from 'lucide-svelte';
  import Select from '$lib/components/Select.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import { casesApi } from '$lib/modules/cases/api';
  import type { Case } from '$lib/modules/cases/types';
  import type { User } from '$lib/modules/users/types';
  import {
    PRIORITY_META,
    PRIORITY_OPTIONS,
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

  const pad2 = (n: number) => String(n).padStart(2, '0');
  function toLocalInput(iso?: string | null): string {
    if (!iso) return '';
    const d = new Date(iso);
    return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}T${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
  }

  // Valores locales de los selects en línea (se resincronizan si cambia `c`).
  // El estado se muestra resumido por grupo (Esp. repuestos/cliente → "En espera").
  let statusVal = statusGroupKey(c.status);
  let assigneeVal = c.assigned_to ?? '';
  let prioVal = c.priority;
  let slaVal = toLocalInput(c.sla_due_at);
  $: statusVal = statusGroupKey(c.status);
  $: assigneeVal = c.assigned_to ?? '';
  $: prioVal = c.priority;
  $: slaVal = toLocalInput(c.sla_due_at);

  // El SLA es un derecho de gestión (no lo pone el operario): si un caso activo
  // no lo tiene, se resalta para que un admin/ingeniero lo defina desde aquí.
  $: needsSla = isActive(c) && !c.sla_due_at;
  $: needsAssignee = isActive(c) && !c.assigned_to;

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
      statusVal = statusGroupKey(c.status);
      assigneeVal = c.assigned_to ?? '';
      prioVal = c.priority;
      slaVal = toLocalInput(c.sla_due_at);
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
  function onPriorityChange(v: string) {
    if (v && v !== c.priority) persist({ priority: v as never });
  }

  // El DatePicker emite varios 'change' al ajustar la hora → se debouncea.
  let slaTimer: ReturnType<typeof setTimeout>;
  function onSlaChange(v: string) {
    clearTimeout(slaTimer);
    slaTimer = setTimeout(() => {
      const iso = v ? new Date(v).toISOString() : null;
      const cur = c.sla_due_at ? new Date(c.sla_due_at).toISOString() : null;
      if (iso !== cur) persist({ sla_due_at: iso as never });
    }, 500);
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
        href={`/cases/${c.code}`}
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
    <a href={`/cases/${c.code}`} class="line-clamp-2 text-sm font-semibold text-slate-800 hover:text-brand-700">
      {c.title}
    </a>
    {#if equipmentName}
      <p class="mt-1 flex items-center gap-1.5 text-xs text-slate-500">
        <Cpu class="h-3.5 w-3.5 shrink-0 text-slate-400" />
        <span class="truncate">{equipmentName}</span>
      </p>
    {/if}
  </div>

  <!-- Controles en línea: estado · ingeniero · prioridad · SLA -->
  <div class="grid grid-cols-2 gap-x-2 gap-y-2 pl-1.5">
    <div>
      <p class="mb-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">Estado</p>
      <Select
        bind:value={statusVal}
        options={STATUS_GROUP_OPTIONS}
        disabled={busy}
        on:change={(e) => onStatusChange(e.detail)}
      />
    </div>

    <div>
      <p class="mb-0.5 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide {needsAssignee ? 'text-rose-600' : 'text-slate-400'}">
        Ingeniero
        {#if needsAssignee}<span class="animate-blink">•</span>{/if}
      </p>
      <div class="relative rounded-lg {needsAssignee ? 'ring-2 ring-rose-300' : ''}">
        <Select
          bind:value={assigneeVal}
          options={engineerOptions}
          placeholder="Sin asignar"
          disabled={busy}
          on:change={(e) => onAssigneeChange(e.detail)}
        />
      </div>
    </div>

    <div>
      <p class="mb-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-400">Prioridad</p>
      <Select
        bind:value={prioVal}
        options={PRIORITY_OPTIONS}
        disabled={busy}
        on:change={(e) => onPriorityChange(e.detail)}
      />
    </div>

    <div>
      <p class="mb-0.5 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide {needsSla ? 'text-amber-600' : 'text-slate-400'}">
        SLA
        {#if needsSla}<span class="rounded bg-amber-100 px-1 text-[9px] font-bold text-amber-700">falta</span>{/if}
      </p>
      <div class="relative rounded-lg {needsSla ? 'ring-2 ring-amber-300' : ''}">
        <DatePicker
          mode="datetime"
          placeholder="Definir SLA"
          bind:value={slaVal}
          disabled={busy}
          on:change={(e) => onSlaChange(e.detail)}
        />
      </div>
    </div>
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
        href={`/cases/${c.code}`}
        class="grid h-7 w-7 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-600"
        aria-label="Abrir detalle"
        title="Abrir"
      >
        <ArrowUpRight class="h-4 w-4" />
      </a>
    </div>
  </div>
</article>
