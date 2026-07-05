<script lang="ts">
  /** Select propio · estilo Bamesoft, sin <select> nativo.
   *  API compatible: label, value (bindable), options, placeholder, required, error.
   *  El popup se renderiza en <body> (portal) con position:fixed para no ser
   *  recortado ni desplazado por ancestros con overflow/transform. */
  import { onMount, createEventDispatcher } from 'svelte';
  import { Check, ChevronDown } from 'lucide-svelte';
  import { portal } from '$lib/actions/portal';

  export let label = '';
  export let value: string = '';
  export let options: { value: string; label: string }[] = [];
  export let placeholder = '— Selecciona —';
  export let required = false;
  export let error: string | null = null;
  export let disabled = false;

  const dispatch = createEventDispatcher<{ change: string }>();

  let open = false;
  let triggerEl: HTMLButtonElement;
  let listEl: HTMLDivElement;
  let popTop = 0;
  let popLeft = 0;
  let popWidth = 0;
  let dropUp = false;
  let active = -1; // índice resaltado por teclado

  $: selected = options.find((o) => o.value === value) ?? null;

  function positionPopup() {
    if (!triggerEl) return;
    const r = triggerEl.getBoundingClientRect();
    const estH = Math.min(options.length * 40 + 8, 264);
    const spaceBelow = window.innerHeight - r.bottom;
    dropUp = spaceBelow < estH + 12 && r.top > estH;
    popTop = dropUp ? r.top - estH - 6 : r.bottom + 6;
    popLeft = r.left;
    popWidth = r.width;
  }

  let openedAt = 0; // marca de tiempo de apertura (para ignorar el click fantasma móvil)
  let isMobile = false; // en móvil se abre como hoja inferior (bottom sheet)

  function openMenu() {
    if (disabled) return;
    isMobile = typeof window !== 'undefined' && window.matchMedia('(max-width: 767px)').matches;
    if (!isMobile) positionPopup();
    active = options.findIndex((o) => o.value === value);
    open = true;
    openedAt = Date.now();
  }
  function close() {
    open = false;
    active = -1;
  }
  function toggle() {
    open ? close() : openMenu();
  }

  /** Cierre por tocar fuera: en móvil, el mismo tap que abre genera un "click
   *  fantasma" sobre el backdrop recién montado; lo ignoramos ~350 ms. */
  function backdropClose() {
    if (Date.now() - openedAt < 350) return;
    close();
  }

  function pick(v: string) {
    value = v;
    dispatch('change', v);
    close();
    triggerEl?.focus();
  }

  function onKey(e: KeyboardEvent) {
    if (disabled) return;
    if (!open) {
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
        e.preventDefault();
        openMenu();
      }
      return;
    }
    if (e.key === 'Escape') {
      e.preventDefault();
      close();
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      active = Math.min(active + 1, options.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      active = Math.max(active - 1, 0);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (active >= 0 && active < options.length) pick(options[active].value);
    }
  }

  function onReposition() {
    if (open) positionPopup(); // reposicionar (no cerrar) al hacer scroll/resize
  }

  onMount(() => {
    window.addEventListener('scroll', onReposition, true);
    window.addEventListener('resize', onReposition);
    return () => {
      window.removeEventListener('scroll', onReposition, true);
      window.removeEventListener('resize', onReposition);
    };
  });
</script>

<div class="block">
  {#if label}
    <span class="mb-1 block text-sm font-medium text-slate-700">{label}</span>
  {/if}

  <button
    type="button"
    bind:this={triggerEl}
    {disabled}
    class="input flex w-full items-center justify-between gap-2 text-left {selected
      ? 'text-slate-800'
      : 'text-slate-400'} {disabled ? 'cursor-not-allowed opacity-60' : 'cursor-pointer'}"
    class:ring-1={open}
    class:ring-brand-500={open}
    class:border-brand-500={open}
    on:click={toggle}
    on:keydown={onKey}
    aria-haspopup="listbox"
    aria-expanded={open}
  >
    <span class="truncate">{selected ? selected.label : placeholder}</span>
    <ChevronDown class="h-4 w-4 shrink-0 text-slate-400 transition-transform duration-200 {open ? 'rotate-180' : ''}" />
  </button>

  {#if required}
    <input class="sr-only" tabindex="-1" {value} required aria-hidden="true" />
  {/if}

  {#if error}
    <span class="mt-1 block text-xs text-danger-600">{error}</span>
  {/if}
</div>

{#if open}
  <div use:portal>
    {#if isMobile}
      <!-- Móvil: hoja inferior (bottom sheet), fiable y con toques grandes -->
      <button
        type="button"
        class="fixed inset-0 bg-slate-900/40 backdrop-blur-[1px]"
        style="z-index:9998;"
        aria-label="Cerrar lista"
        on:click={backdropClose}
      ></button>
      <div
        role="listbox"
        tabindex="-1"
        class="fixed inset-x-0 bottom-0 max-h-[75vh] overflow-y-auto rounded-t-2xl border-t border-slate-200 bg-white pb-[max(12px,env(safe-area-inset-bottom))] pt-2 shadow-2xl"
        style="z-index:9999;"
      >
        <div class="mx-auto mb-2 h-1.5 w-10 rounded-full bg-slate-300"></div>
        {#if label}
          <p class="px-4 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
        {/if}
        {#if placeholder && !required}
          <button
            type="button"
            role="option"
            aria-selected={!selected}
            class="flex w-full items-center gap-2 px-4 py-3.5 text-left text-base text-slate-500 active:bg-slate-100"
            on:click={() => pick('')}
          >
            {placeholder}
          </button>
        {/if}
        {#each options as o (o.value)}
          <button
            type="button"
            role="option"
            aria-selected={o.value === value}
            class="flex w-full items-center justify-between gap-2 px-4 py-3.5 text-left text-base active:bg-slate-100
              {o.value === value ? 'bg-brand-50 font-semibold text-brand-700' : 'text-slate-700'}"
            on:click={() => pick(o.value)}
          >
            <span class="truncate">{o.label}</span>
            {#if o.value === value}<Check class="h-5 w-5 shrink-0 text-brand-600" />{/if}
          </button>
        {/each}
      </div>
    {:else}
      <!-- Escritorio: menú anclado al campo -->
      <button
        type="button"
        class="fixed inset-0 cursor-default"
        style="z-index:9998;"
        aria-label="Cerrar lista"
        on:click={backdropClose}
      ></button>
      <div
        bind:this={listEl}
        role="listbox"
        tabindex="-1"
        class="fixed max-h-[264px] overflow-y-auto rounded-xl border border-slate-200 bg-white p-1.5 shadow-2xl shadow-slate-900/15"
        style="top:{popTop}px; left:{popLeft}px; width:{popWidth}px; z-index:9999;"
      >
        {#if placeholder && !required}
          <button
            type="button"
            role="option"
            aria-selected={!selected}
            class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-slate-400 transition hover:bg-slate-50"
            on:click={() => pick('')}
          >
            {placeholder}
          </button>
        {/if}
        {#each options as o, i (o.value)}
          <button
            type="button"
            role="option"
            aria-selected={o.value === value}
            class="flex w-full items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm transition
              {o.value === value ? 'bg-brand-50 font-medium text-brand-700' : 'text-slate-700'}
              {i === active && o.value !== value ? 'bg-slate-100' : ''}
              {i === active ? '' : 'hover:bg-slate-50'}"
            on:click={() => pick(o.value)}
            on:mouseenter={() => (active = i)}
          >
            <span class="truncate">{o.label}</span>
            {#if o.value === value}<Check class="h-4 w-4 shrink-0 text-brand-600" />{/if}
          </button>
        {/each}
      </div>
    {/if}
  </div>
{/if}
