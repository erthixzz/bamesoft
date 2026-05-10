<script lang="ts">
  /** DatePicker propio · estilo Bamesoft, sin dependencias.
   *  Soporta `mode="date"` y `mode="datetime"`.
   *  Valor enlazado: ISO YYYY-MM-DD o YYYY-MM-DDTHH:MM.
   */
  import { onMount } from 'svelte';
  import { Calendar, ChevronLeft, ChevronRight, X } from 'lucide-svelte';

  export let label = '';
  export let value: string = ''; // YYYY-MM-DD o YYYY-MM-DDTHH:MM
  export let mode: 'date' | 'datetime' = 'date';
  export let placeholder: string = mode === 'datetime' ? 'Selecciona fecha y hora' : 'Selecciona fecha';
  export let required = false;
  export let error: string | null = null;
  export let min: string | null = null;

  let open = false;
  let containerEl: HTMLDivElement;
  let viewYear: number;
  let viewMonth: number; // 0-11
  let timeStr = '08:00';

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
    if (!parsed) return;
    const iso = `${parsed.y}-${pad(parsed.m + 1)}-${pad(parsed.d)}`;
    value = `${iso}T${timeStr}`;
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
    if (!open) initView();
    open = !open;
  }

  function onDocClick(e: MouseEvent) {
    if (open && containerEl && !containerEl.contains(e.target as Node)) open = false;
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false;
  }

  onMount(() => {
    window.addEventListener('mousedown', onDocClick);
    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('mousedown', onDocClick);
      window.removeEventListener('keydown', onKey);
    };
  });
</script>

<div class="relative" bind:this={containerEl}>
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">{label}</span>
  {/if}

  <button
    type="button"
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
    <div
      class="absolute left-0 z-50 mt-2 w-[320px] rounded-xl border border-slate-200 bg-white p-3 shadow-xl"
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
            class="grid h-9 place-items-center rounded-lg text-sm transition
              {!cell.current ? 'text-slate-300' : 'text-slate-700 hover:bg-brand-50'}
              {selected ? '!bg-brand-600 !text-white' : ''}
              {today && !selected ? 'ring-1 ring-brand-300' : ''}
              {disabled ? 'cursor-not-allowed opacity-40 hover:!bg-transparent' : ''}"
            disabled={disabled}
            on:click={() => selectDate(cell.date)}
          >
            {cell.day}
          </button>
        {/each}
      </div>

      {#if mode === 'datetime'}
        <div class="mt-3 flex items-center gap-2 border-t border-slate-100 pt-3">
          <span class="text-sm text-slate-500">Hora</span>
          <input
            type="time"
            class="input flex-1"
            bind:value={timeStr}
          />
          <button type="button" class="btn-primary" on:click={applyTime} disabled={!parsed}>
            OK
          </button>
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
  {/if}
</div>
