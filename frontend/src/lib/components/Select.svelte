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

  function openMenu() {
    if (disabled) return;
    positionPopup();
    active = options.findIndex((o) => o.value === value);
    open = true;
  }
  function close() {
    open = false;
    active = -1;
  }
  function toggle() {
    open ? close() : openMenu();
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
    <!-- Backdrop transparente: cierra al click fuera (z-index inline, sin depender de JIT) -->
    <button
      type="button"
      class="fixed inset-0 cursor-default"
      style="z-index:9998;"
      aria-label="Cerrar lista"
      on:click={close}
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
        {#if o.value === value}
          <Check class="h-4 w-4 shrink-0 text-brand-600" />
        {/if}
      </button>
    {/each}
    </div>
  </div>
{/if}
