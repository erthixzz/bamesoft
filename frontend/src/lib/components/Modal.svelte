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

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/40 p-3 sm:items-center sm:p-4"
    on:click|self={close}
    on:keydown={(e) => e.key === 'Escape' && close()}
    role="dialog"
    aria-modal="true"
    tabindex="-1"
    transition:fade={{ duration: 150 }}
  >
    <div
      class="flex max-h-[90vh] w-full {widths[size]} flex-col rounded-2xl bg-white shadow-xl"
      transition:fly={{ y: 20, duration: 200 }}
    >
      <header class="flex items-center justify-between border-b border-slate-200 px-4 py-3 sm:px-5">
        <h3 class="text-base font-semibold text-slate-900">{title}</h3>
        <button class="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700" on:click={close} aria-label="Cerrar">
          ✕
        </button>
      </header>
      <div class="overflow-y-auto p-4 sm:p-5"><slot /></div>
      {#if $$slots.footer}
        <footer class="border-t border-slate-200 bg-slate-50 px-4 py-3 sm:px-5"><slot name="footer" /></footer>
      {/if}
    </div>
  </div>
{/if}
