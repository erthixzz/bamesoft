<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  export let open = false;
  export let title = '';
  export let size: 'sm' | 'md' | 'lg' | 'xl' = 'md';

  const dispatch = createEventDispatcher();
  function close() {
    open = false;
    dispatch('close');
  }

  const widths = {
    sm: 'max-w-sm',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  } as const;
</script>

<svelte:window on:keydown={(e) => open && e.key === 'Escape' && close()} />

{#if open}
  <!-- `dvh` y no `vh`: en móvil `vh` se mide contra la pantalla completa, así que
       al abrirse el teclado el pie del modal (con el botón de guardar) quedaba
       debajo de él y no había forma de alcanzarlo. `dvh` sigue al viewport real.
       `pb-[env(safe-area-inset-bottom)]` evita la barra gestual de iOS. -->
  <div
    class="fixed inset-0 z-50 flex max-h-[100dvh] items-end justify-center overflow-hidden bg-slate-900/40 p-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:items-center sm:p-4"
    on:click|self={close}
    role="presentation"
    transition:fade={{ duration: 150 }}
  >
    <div
      class="flex max-h-[85dvh] w-full {widths[size]} flex-col overflow-hidden rounded-2xl bg-white shadow-xl"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      transition:fly={{ y: 20, duration: 200 }}
    >
      <header class="flex shrink-0 items-center justify-between border-b border-slate-200 px-4 py-3 sm:px-5">
        <h3 class="text-base font-semibold text-slate-900">{title}</h3>
        <button class="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700" on:click={close} aria-label="Cerrar">
          ✕
        </button>
      </header>
      <div class="min-h-0 flex-1 overflow-y-auto overscroll-contain p-4 sm:p-5"><slot /></div>
      {#if $$slots.footer}
        <footer class="shrink-0 border-t border-slate-200 bg-slate-50 px-4 py-3 sm:px-5"><slot name="footer" /></footer>
      {/if}
    </div>
  </div>
{/if}
