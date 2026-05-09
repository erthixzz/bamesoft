<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  export let open = false;
  export let title = '';

  const dispatch = createEventDispatcher();
  function close() {
    open = false;
    dispatch('close');
  }
</script>

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4"
    on:click|self={close}
    role="dialog"
    aria-modal="true"
  >
    <div class="w-full max-w-lg rounded-xl bg-white shadow-xl">
      <header class="flex items-center justify-between border-b border-slate-200 px-5 py-3">
        <h3 class="text-base font-semibold text-slate-900">{title}</h3>
        <button class="text-slate-400 hover:text-slate-700" on:click={close}>✕</button>
      </header>
      <div class="p-5"><slot /></div>
      {#if $$slots.footer}
        <footer class="border-t border-slate-200 bg-slate-50 px-5 py-3"><slot name="footer" /></footer>
      {/if}
    </div>
  </div>
{/if}
