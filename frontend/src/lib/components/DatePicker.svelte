<script lang="ts">
  /** DatePicker propio · estilo Bamesoft, sin dependencias.
   *  Soporta `mode="date"` y `mode="datetime"`.
   *  Valor enlazado: ISO YYYY-MM-DD o YYYY-MM-DDTHH:MM.
   */
  import { onMount } from 'svelte';
  import { Calendar, ChevronLeft, ChevronRight, Clock, X } from 'lucide-svelte';
  import { tooltip } from '$lib/actions/tooltip';
  import { portal } from '$lib/actions/portal';

  export let label = '';
  export let value: string = ''; // YYYY-MM-DD o YYYY-MM-DDTHH:MM
  export let mode: 'date' | 'datetime' = 'date';
  export let placeholder: string = mode === 'datetime' ? 'Selecciona fecha y hora' : 'Selecciona fecha';
  export let required = false;
  export let error: string | null = null;
  export let min: string | null = null;

  let open = false;
  let containerEl: HTMLDivElement;
  let triggerEl: HTMLButtonElement;
  let popupEl: HTMLDivElement;
  let popTop = 0;
  let popLeft = 0;
  let viewYear: number;
  let viewMonth: number; // 0-11
  let timeStr = '08:00';

  const POP_W = 320;
  const POP_H = 360; // alto aproximado para decidir arriba/abajo

  function positionPopup() {
    if (!triggerEl) return;
    const r = triggerEl.getBoundingClientRect();
    const spaceBelow = window.innerHeight - r.bottom;
    // Si no cabe abajo pero sí arriba, lo mostramos encima del campo.
    popTop = spaceBelow < POP_H + 12 && r.top > POP_H ? r.top - POP_H - 8 : r.bottom + 6;
    popLeft = Math.max(8, Math.min(r.left, window.innerWidth - POP_W - 8));
  }

  const WEEKDAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  const MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
  ];

  function parseValue(): { y: number; m: number; d: number; t?: string } | null {
    if (!value) return null;
    const [datePart, time] = value.split('T');
    const [y, m, d] = datePart.split('-').map(Number);
    if (!y || !m || !d) return null;
    return { y, m: m - 1, d, t: time?.slice(0, 5) };
  }

  function initView() {
    const parsed = parseValue();
    const today = new Date();
    viewYear = parsed?.y ?? today.getFullYear();
    viewMonth = parsed?.m ?? today.getMonth();
    if (parsed?.t) timeStr = parsed.t;
  }

  $: parsed = parseValue();
  $: display = formatDisplay(parsed);

  function formatDisplay(p: ReturnType<typeof parseValue>): string {
    if (!p) return '';
    const dStr = `${String(p.d).padStart(2, '0')} ${MONTHS[p.m].slice(0, 3).toLowerCase()} ${p.y}`;
    return mode === 'datetime' && p.t ? `${dStr} · ${p.t}` : dStr;
  }

  function daysInMonth(y: number, m: number): number {
    return new Date(y, m + 1, 0).getDate();
  }

  function firstWeekday(y: number, m: number): number {
    // Lunes = 0
    const d = new Date(y, m, 1).getDay();
    return (d + 6) % 7;
  }

  type Cell = { day: number; current: boolean; date: Date };
  function buildGrid(y: number, m: number): Cell[] {
    const cells: Cell[] = [];
    const firstW = firstWeekday(y, m);
    const dim = daysInMonth(y, m);
    const prevDim = daysInMonth(y, m - 1);

    for (let i = firstW - 1; i >= 0; i--) {
      const day = prevDim - i;
      cells.push({ day, current: false, date: new Date(y, m - 1, day) });
    }
    for (let d = 1; d <= dim; d++) {
      cells.push({ day: d, current: true, date: new Date(y, m, d) });
    }
    while (cells.length < 42) {
      const last = cells[cells.length - 1].date;
      const next = new Date(last.getFullYear(), last.getMonth(), last.getDate() + 1);
      cells.push({ day: next.getDate(), current: false, date: next });
    }
    return cells;
  }

  $: grid = buildGrid(viewYear ?? new Date().getFullYear(), viewMonth ?? new Date().getMonth());

  function isSameDay(a: Date, b: { y: number; m: number; d: number } | null): boolean {
    if (!b) return false;
    return a.getFullYear() === b.y && a.getMonth() === b.m && a.getDate() === b.d;
  }

  function isToday(d: Date): boolean {
    const t = new Date();
    return d.getFullYear() === t.getFullYear() && d.getMonth() === t.getMonth() && d.getDate() === t.getDate();
  }

  function isBefore(a: Date, isoMin: string | null): boolean {
    if (!isoMin) return false;
    const [y, m, d] = isoMin.split('-').map(Number);
    return a < new Date(y, m - 1, d);
  }

  function pad(n: number): string {
    return String(n).padStart(2, '0');
  }

  function selectDate(d: Date) {
    const iso = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    if (mode === 'datetime') {
      value = `${iso}T${timeStr}`;
    } else {
      value = iso;
      open = false;
    }
  }

  function applyTime() {
    applyLive();
    open = false;
  }

  function clear() {
    value = '';
    open = false;
  }

  function prevMonth() {
    if (viewMonth === 0) {
      viewMonth = 11;
      viewYear--;
    } else viewMonth--;
  }
  function nextMonth() {
    if (viewMonth === 11) {
      viewMonth = 0;
      viewYear++;
    } else viewMonth++;
  }

  function toggle() {
    if (!open) {
      initView();
      positionPopup();
    }
    open = !open;
  }

  // Hora (modo datetime) — listas de selección.
  function pad2(n: number): string {
    return String(n).padStart(2, '0');
  }
  const HOURS = Array.from({ length: 24 }, (_, i) => i);
  const MINUTES = Array.from({ length: 12 }, (_, i) => i * 5); // paso de 5
  $: [th, tm] = (timeStr || '08:00').split(':').map(Number);

  /** Aplica la hora al valor en vivo (si ya hay día elegido o usando hoy). */
  function applyLive() {
    const t = new Date();
    const base = parsed ?? { y: t.getFullYear(), m: t.getMonth(), d: t.getDate() };
    value = `${base.y}-${pad(base.m + 1)}-${pad(base.d)}T${timeStr}`;
  }
  function setH(h: number) {
    timeStr = `${pad2(h)}:${pad2(tm)}`;
    applyLive();
  }
  function setM(m: number) {
    timeStr = `${pad2(th)}:${pad2(m)}`;
    applyLive();
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false;
  }

  function onReposition() {
    if (open) positionPopup(); // reposicionar (no cerrar) al hacer scroll/resize
  }

  onMount(() => {
    window.addEventListener('keydown', onKey);
    window.addEventListener('scroll', onReposition, true);
    window.addEventListener('resize', onReposition);
    return () => {
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('scroll', onReposition, true);
      window.removeEventListener('resize', onReposition);
    };
  });
</script>

<div class="relative" bind:this={containerEl}>
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">{label}</span>
  {/if}

  <button
    type="button"
    bind:this={triggerEl}
    class="input flex w-full items-center justify-between gap-2 text-left {value ? 'text-slate-800' : 'text-slate-400'}"
    on:click={toggle}
    aria-haspopup="dialog"
    aria-expanded={open}
  >
    <span class="truncate">{display || placeholder}</span>
    <span class="flex items-center gap-1">
      {#if value}
        <button
          type="button"
          class="text-slate-400 hover:text-slate-700"
          on:click|stopPropagation={clear}
          use:tooltip={{ text: 'Limpiar', placement: 'bottom' }}
          aria-label="Limpiar"
          tabindex="-1"
        >
          <X class="h-4 w-4" />
        </button>
      {/if}
      <Calendar class="h-4 w-4 text-slate-400" />
    </span>
  </button>

  <!-- Input oculto para satisfacer required en formularios -->
  {#if required}
    <input class="sr-only" tabindex="-1" {value} required />
  {/if}

  {#if error}
    <span class="mt-1 block text-xs text-danger-600">{error}</span>
  {/if}

  {#if open}
    <div use:portal>
      <!-- Backdrop transparente: cierra al click fuera (z-index inline, sin depender de JIT) -->
      <button
        type="button"
        class="fixed inset-0 cursor-default"
        style="z-index:9998;"
        aria-label="Cerrar calendario"
        on:click={() => (open = false)}
      ></button>
      <div
        bind:this={popupEl}
        class="fixed max-h-[88vh] w-[320px] overflow-y-auto rounded-2xl border border-slate-200 bg-white p-3 shadow-2xl"
        style="top:{popTop}px; left:{popLeft}px; z-index:9999;"
        role="dialog"
      >
      <header class="mb-2 flex items-center justify-between">
        <button type="button" class="rounded-md p-1 text-slate-500 hover:bg-slate-100" on:click={prevMonth} aria-label="Mes anterior">
          <ChevronLeft class="h-4 w-4" />
        </button>
        <p class="text-sm font-semibold text-slate-800">
          {MONTHS[viewMonth]} {viewYear}
        </p>
        <button type="button" class="rounded-md p-1 text-slate-500 hover:bg-slate-100" on:click={nextMonth} aria-label="Mes siguiente">
          <ChevronRight class="h-4 w-4" />
        </button>
      </header>

      <div class="grid grid-cols-7 gap-1 text-center text-[11px] font-medium uppercase text-slate-400">
        {#each WEEKDAYS as w}<div>{w}</div>{/each}
      </div>

      <div class="mt-1 grid grid-cols-7 gap-1">
        {#each grid as cell (cell.date.toISOString())}
          {@const selected = isSameDay(cell.date, parsed)}
          {@const today = isToday(cell.date)}
          {@const disabled = isBefore(cell.date, min)}
          <button
            type="button"
            class="grid h-9 place-items-center rounded-lg text-sm font-medium transition
              {selected
                ? 'bg-brand-600 font-bold text-white shadow-md ring-2 ring-brand-300 hover:bg-brand-700'
                : !cell.current
                  ? 'text-slate-300 hover:bg-slate-50'
                  : today
                    ? 'text-brand-700 ring-1 ring-brand-300 hover:bg-brand-50'
                    : 'text-slate-700 hover:bg-brand-50'}
              {disabled ? 'cursor-not-allowed opacity-40 hover:bg-transparent' : ''}"
            disabled={disabled}
            on:click={() => selectDate(cell.date)}
          >
            {cell.day}
          </button>
        {/each}
      </div>

      {#if mode === 'datetime'}
        <div class="mt-3 border-t border-slate-100 pt-3">
          <div class="mb-2 flex items-center gap-1.5 text-sm font-medium text-slate-600">
            <Clock class="h-4 w-4 text-brand-500" /> Hora
            <span class="ml-auto rounded-md bg-brand-50 px-2 py-0.5 text-sm font-bold tabular-nums text-brand-700">
              {pad2(th)}:{pad2(tm)}
            </span>
          </div>
          <div class="flex items-stretch justify-center gap-1.5">
            <!-- Columna de horas -->
            <div class="h-[152px] w-[68px] overflow-y-auto rounded-lg border border-slate-200 bg-slate-50/50 p-1">
              {#each HOURS as h}
                <button
                  type="button"
                  class="block w-full rounded-md px-2 py-1.5 text-center text-sm tabular-nums transition
                    {h === th ? 'bg-brand-600 font-semibold text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-slate-900'}"
                  on:click={() => setH(h)}
                >
                  {pad2(h)}
                </button>
              {/each}
            </div>
            <div class="flex items-center text-xl font-bold text-slate-300">:</div>
            <!-- Columna de minutos -->
            <div class="h-[152px] w-[68px] overflow-y-auto rounded-lg border border-slate-200 bg-slate-50/50 p-1">
              {#each MINUTES as m}
                <button
                  type="button"
                  class="block w-full rounded-md px-2 py-1.5 text-center text-sm tabular-nums transition
                    {m === tm ? 'bg-brand-600 font-semibold text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-slate-900'}"
                  on:click={() => setM(m)}
                >
                  {pad2(m)}
                </button>
              {/each}
            </div>
          </div>
          <button type="button" class="btn-primary mt-3 w-full" on:click={applyTime}>OK</button>
        </div>
      {/if}

      <footer class="mt-2 flex items-center justify-between border-t border-slate-100 pt-2">
        <button type="button" class="text-xs text-slate-500 hover:text-slate-700" on:click={() => {
          const today = new Date();
          viewYear = today.getFullYear();
          viewMonth = today.getMonth();
          if (mode === 'date') selectDate(today);
        }}>Hoy</button>
        <button type="button" class="text-xs text-slate-500 hover:text-slate-700" on:click={() => (open = false)}>
          Cerrar
        </button>
      </footer>
      </div>
    </div>
  {/if}
</div>
