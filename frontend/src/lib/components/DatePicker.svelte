<script lang="ts">
  /** DatePicker propio · estilo Bamesoft, sin dependencias externas.
   *  Soporta `mode="date"` y `mode="datetime"`.
   *  Valor enlazado (bind:value): ISO "YYYY-MM-DD" o "YYYY-MM-DDTHH:MM".
   *  Responsive: popover anclado en escritorio, hoja centrada en móvil.
   */
  import { onMount, tick } from 'svelte';
  import { Calendar, ChevronLeft, ChevronRight, Clock, X, Minus, Plus } from 'lucide-svelte';
  import { portal } from '$lib/actions/portal';

  export let label = '';
  export let value = ''; // YYYY-MM-DD o YYYY-MM-DDTHH:MM
  export let mode: 'date' | 'datetime' = 'date';
  export let placeholder = mode === 'datetime' ? 'Selecciona fecha y hora' : 'Selecciona fecha';
  export let required = false;
  export let error: string | null = null;
  export let min: string | null = null;
  export let disabled = false;

  let open = false;
  let triggerEl: HTMLButtonElement;
  let popupEl: HTMLDivElement;

  // Posición del popover (escritorio).
  let popTop = 0;
  let popLeft = 0;
  let sheet = false; // móvil → hoja centrada

  let viewYear = new Date().getFullYear();
  let viewMonth = new Date().getMonth(); // 0-11
  let hh = 8;
  let mm = 0;
  let timeInput = '08:00';

  const WEEKDAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  const MONTHS = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
  ];

  const pad = (n: number) => String(n).padStart(2, '0');

  // ---- Parseo del valor enlazado ----
  type Parsed = { y: number; m: number; d: number; hh: number; mm: number };
  function parse(v: string): Parsed | null {
    if (!v) return null;
    const [datePart, timePart] = v.split('T');
    const [y, m, d] = datePart.split('-').map(Number);
    if (!y || !m || !d) return null;
    const [h = 0, mi = 0] = (timePart ?? '').split(':').map(Number);
    return { y, m: m - 1, d, hh: h, mm: mi };
  }

  $: parsed = parse(value);
  $: display = formatDisplay(parsed);

  function formatDisplay(p: Parsed | null): string {
    if (!p) return '';
    const dStr = `${pad(p.d)} ${MONTHS[p.m].slice(0, 3).toLowerCase()} ${p.y}`;
    return mode === 'datetime' ? `${dStr} · ${pad(p.hh)}:${pad(p.mm)}` : dStr;
  }

  // ---- Construcción de la cuadrícula (reactiva sobre value/min) ----
  type Cell = { day: number; current: boolean; date: Date; selected: boolean; today: boolean; off: boolean };

  function daysInMonth(y: number, m: number) {
    return new Date(y, m + 1, 0).getDate();
  }
  function firstWeekday(y: number, m: number) {
    return (new Date(y, m, 1).getDay() + 6) % 7; // Lunes = 0
  }
  function sameDay(a: Date, p: Parsed | null) {
    return !!p && a.getFullYear() === p.y && a.getMonth() === p.m && a.getDate() === p.d;
  }
  function isToday(a: Date) {
    const t = new Date();
    return a.getFullYear() === t.getFullYear() && a.getMonth() === t.getMonth() && a.getDate() === t.getDate();
  }
  function beforeMin(a: Date, isoMin: string | null) {
    if (!isoMin) return false;
    const [y, m, d] = isoMin.split('-').map(Number);
    const lim = new Date(y, m - 1, d);
    lim.setHours(0, 0, 0, 0);
    const aa = new Date(a);
    aa.setHours(0, 0, 0, 0);
    return aa < lim;
  }

  function buildGrid(y: number, m: number, p: Parsed | null, isoMin: string | null): Cell[] {
    const cells: Cell[] = [];
    const make = (date: Date, day: number, current: boolean): Cell => ({
      day, current, date,
      selected: sameDay(date, p),
      today: isToday(date),
      off: beforeMin(date, isoMin),
    });
    const firstW = firstWeekday(y, m);
    const prevDim = daysInMonth(y, m - 1);
    for (let i = firstW - 1; i >= 0; i--) {
      const day = prevDim - i;
      cells.push(make(new Date(y, m - 1, day), day, false));
    }
    const dim = daysInMonth(y, m);
    for (let d = 1; d <= dim; d++) cells.push(make(new Date(y, m, d), d, true));
    while (cells.length < 42) {
      const last = cells[cells.length - 1].date;
      const nx = new Date(last.getFullYear(), last.getMonth(), last.getDate() + 1);
      cells.push(make(nx, nx.getDate(), false));
    }
    return cells;
  }

  // Reactivo sobre value (parsed), mes/año visibles y min.
  $: grid = buildGrid(viewYear, viewMonth, parsed, min);

  // ---- Acciones ----
  function emit(p: { y: number; m: number; d: number }) {
    const datePart = `${p.y}-${pad(p.m + 1)}-${pad(p.d)}`;
    value = mode === 'datetime' ? `${datePart}T${pad(hh)}:${pad(mm)}` : datePart;
  }

  function pickDay(cell: Cell) {
    if (cell.off) return;
    const d = cell.date;
    viewYear = d.getFullYear();
    viewMonth = d.getMonth();
    emit({ y: d.getFullYear(), m: d.getMonth(), d: d.getDate() });
    if (mode === 'date') open = false;
  }

  function reEmitTime() {
    // Re-emite con el día ya elegido (o hoy si aún no hay).
    const base = parsed ?? (() => { const t = new Date(); return { y: t.getFullYear(), m: t.getMonth(), d: t.getDate() }; })();
    emit(base);
  }

  function clampTime() {
    hh = Math.max(0, Math.min(23, hh || 0));
    mm = Math.max(0, Math.min(59, mm || 0));
    timeInput = `${pad(hh)}:${pad(mm)}`;
  }

  function onTimeInput() {
    const digits = timeInput.replace(/\D/g, '').slice(0, 4);
    timeInput = digits.length >= 3 ? `${digits.slice(0, 2)}:${digits.slice(2)}` : digits;
    const mt = /^(\d{1,2}):(\d{2})$/.exec(timeInput);
    if (mt) {
      hh = Math.min(23, Number(mt[1]));
      mm = Math.min(59, Number(mt[2]));
      reEmitTime();
    }
  }
  function commitTime() {
    const mt = /^(\d{1,2}):?(\d{0,2})$/.exec(timeInput.trim());
    if (mt) {
      hh = Math.min(23, Number(mt[1] || 0));
      mm = Math.min(59, Number(mt[2] || 0));
    }
    clampTime();
    reEmitTime();
  }
  function stepH(n: number) {
    hh = (hh + n + 24) % 24;
    clampTime();
    reEmitTime();
  }
  function stepM(n: number) {
    mm = (mm + n + 60) % 60;
    clampTime();
    reEmitTime();
  }

  function clear() {
    value = '';
    open = false;
  }

  function goToday() {
    const t = new Date();
    viewYear = t.getFullYear();
    viewMonth = t.getMonth();
    emit({ y: t.getFullYear(), m: t.getMonth(), d: t.getDate() });
    if (mode === 'date') open = false;
  }

  function prevMonth() {
    if (viewMonth === 0) { viewMonth = 11; viewYear--; } else viewMonth--;
  }
  function nextMonth() {
    if (viewMonth === 11) { viewMonth = 0; viewYear++; } else viewMonth++;
  }

  // ---- Apertura / posicionamiento ----
  function syncFromValue() {
    const p = parse(value);
    const t = new Date();
    viewYear = p?.y ?? t.getFullYear();
    viewMonth = p?.m ?? t.getMonth();
    if (p) { hh = p.hh; mm = p.mm; }
    timeInput = `${pad(hh)}:${pad(mm)}`;
  }

  async function position() {
    sheet = window.innerWidth < 480;
    if (sheet) return;
    await tick();
    if (!triggerEl || !popupEl) return;
    const r = triggerEl.getBoundingClientRect();
    const ph = popupEl.offsetHeight || 380;
    const pw = popupEl.offsetWidth || 320;
    const spaceBelow = window.innerHeight - r.bottom;
    popTop = spaceBelow < ph + 12 && r.top > ph ? r.top - ph - 6 : r.bottom + 6;
    popLeft = Math.max(8, Math.min(r.left, window.innerWidth - pw - 8));
  }

  async function toggle() {
    if (disabled) return;
    if (!open) {
      syncFromValue();
      open = true;
      await position();
    } else {
      open = false;
    }
  }

  function onDocClick(e: MouseEvent) {
    if (!open) return;
    const t = e.target as Node | null;
    if (popupEl && t && popupEl.contains(t)) return;
    if (triggerEl && t && triggerEl.contains(t)) return;
    open = false;
  }
  function onKey(e: KeyboardEvent) {
    if (e.key === 'Escape') open = false;
  }
  function onReposition() {
    if (open) position();
  }

  onMount(() => {
    window.addEventListener('click', onDocClick);
    window.addEventListener('keydown', onKey);
    window.addEventListener('resize', onReposition);
    window.addEventListener('scroll', onReposition, true);
    return () => {
      window.removeEventListener('click', onDocClick);
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('resize', onReposition);
      window.removeEventListener('scroll', onReposition, true);
    };
  });
</script>

<div class="relative">
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">{label}</span>
  {/if}

  <button
    type="button"
    bind:this={triggerEl}
    {disabled}
    class="input flex w-full items-center justify-between gap-2 text-left
      {value ? 'text-slate-800' : 'text-slate-400'}
      {error ? 'border-danger-400 ring-1 ring-danger-200' : ''}
      {disabled ? 'cursor-not-allowed opacity-60' : ''}"
    on:click={toggle}
    aria-haspopup="dialog"
    aria-expanded={open}
  >
    <span class="truncate">{display || placeholder}</span>
    <span class="flex shrink-0 items-center gap-1">
      {#if value && !disabled}
        <span
          role="button"
          tabindex="-1"
          aria-label="Limpiar"
          class="rounded p-0.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          on:click|stopPropagation={clear}
          on:keydown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), clear())}
        >
          <X class="h-4 w-4" />
        </span>
      {/if}
      <Calendar class="h-4 w-4 text-slate-400" />
    </span>
  </button>

  {#if required}
    <input class="sr-only" tabindex="-1" {value} required />
  {/if}

  {#if error}
    <span class="mt-1 block text-xs text-danger-600">{error}</span>
  {/if}
</div>

{#if open}
  <div use:portal>
    {#if sheet}
      <button
        type="button"
        aria-label="Cerrar"
        class="fixed inset-0 bg-slate-900/40"
        style="z-index:9998;"
        on:click={() => (open = false)}
      ></button>
    {/if}

    <div
      bind:this={popupEl}
      role="dialog"
      aria-modal={sheet}
      class="w-[300px] rounded-2xl border border-slate-200 bg-white p-3 shadow-2xl
        {sheet ? 'fixed bottom-3 left-1/2 max-h-[90vh] -translate-x-1/2 overflow-y-auto' : 'fixed'}"
      style={sheet ? 'z-index:9999;' : `top:${popTop}px; left:${popLeft}px; z-index:9999;`}
    >
      <!-- Cabecera de mes -->
      <header class="mb-2 flex items-center justify-between">
        <button type="button" class="rounded-lg p-1.5 text-slate-500 transition hover:bg-slate-100" on:click={prevMonth} aria-label="Mes anterior">
          <ChevronLeft class="h-4 w-4" />
        </button>
        <p class="text-sm font-semibold text-slate-800">{MONTHS[viewMonth]} {viewYear}</p>
        <button type="button" class="rounded-lg p-1.5 text-slate-500 transition hover:bg-slate-100" on:click={nextMonth} aria-label="Mes siguiente">
          <ChevronRight class="h-4 w-4" />
        </button>
      </header>

      <!-- Días de la semana -->
      <div class="grid grid-cols-7 gap-1 text-center text-[11px] font-semibold uppercase tracking-wide text-slate-400">
        {#each WEEKDAYS as w}<div>{w}</div>{/each}
      </div>

      <!-- Cuadrícula -->
      <div class="mt-1 grid grid-cols-7 gap-1">
        {#each grid as cell}
          <button
            type="button"
            disabled={cell.off}
            on:click={() => pickDay(cell)}
            class="grid h-9 w-full place-items-center rounded-lg text-sm font-medium transition
              {cell.selected
                ? 'bg-brand-600 text-white shadow ring-2 ring-brand-200 hover:bg-brand-700'
                : cell.off
                  ? 'cursor-not-allowed text-slate-300'
                  : !cell.current
                    ? 'text-slate-300 hover:bg-slate-100'
                    : cell.today
                      ? 'text-brand-700 ring-1 ring-brand-300 hover:bg-brand-50'
                      : 'text-slate-700 hover:bg-brand-50'}"
          >
            {cell.day}
          </button>
        {/each}
      </div>

      <!-- Hora (solo datetime) -->
      {#if mode === 'datetime'}
        <div class="mt-3 border-t border-slate-100 pt-3">
          <div class="flex items-center justify-between gap-3">
            <span class="flex items-center gap-1.5 text-sm font-medium text-slate-600">
              <Clock class="h-4 w-4 text-brand-500" /> Hora
            </span>
            <div class="flex items-center gap-2">
              <!-- Stepper horas -->
              <div class="flex items-center gap-1">
                <button type="button" class="grid h-7 w-7 place-items-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100" on:click={() => stepH(-1)} aria-label="Menos hora">
                  <Minus class="h-3.5 w-3.5" />
                </button>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="5"
                  placeholder="HH:MM"
                  bind:value={timeInput}
                  on:input={onTimeInput}
                  on:blur={commitTime}
                  on:keydown={(e) => e.key === 'Enter' && commitTime()}
                  aria-label="Hora (HH:MM)"
                  class="w-16 rounded-lg border border-slate-200 bg-brand-50 px-2 py-1 text-center text-sm font-bold tabular-nums text-brand-700 outline-none focus:border-brand-400 focus:bg-white focus:ring-2 focus:ring-brand-100"
                />
                <button type="button" class="grid h-7 w-7 place-items-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100" on:click={() => stepH(1)} aria-label="Más hora">
                  <Plus class="h-3.5 w-3.5" />
                </button>
              </div>
              <!-- Stepper minutos (paso de 5) -->
              <div class="flex items-center gap-1">
                <button type="button" class="grid h-7 w-7 place-items-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100" on:click={() => stepM(-5)} aria-label="Menos minutos">
                  <Minus class="h-3.5 w-3.5" />
                </button>
                <span class="w-9 text-center text-sm font-bold tabular-nums text-slate-700">{pad(mm)}</span>
                <button type="button" class="grid h-7 w-7 place-items-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100" on:click={() => stepM(5)} aria-label="Más minutos">
                  <Plus class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      {/if}

      <!-- Pie -->
      <footer class="mt-3 flex items-center justify-between border-t border-slate-100 pt-2">
        <button type="button" class="text-xs font-medium text-slate-500 transition hover:text-brand-600" on:click={goToday}>Hoy</button>
        <div class="flex items-center gap-3">
          {#if value}
            <button type="button" class="text-xs font-medium text-slate-500 transition hover:text-danger-600" on:click={clear}>Limpiar</button>
          {/if}
          <button type="button" class="rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-brand-700" on:click={() => (open = false)}>Listo</button>
        </div>
      </footer>
    </div>
  </div>
{/if}
