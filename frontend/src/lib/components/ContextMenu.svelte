<script lang="ts">
  import { goto } from '$app/navigation';
  import { scale } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { contextMenu, closeContextMenu, type CtxItem } from '$lib/stores/contextMenu';

  let menuW = 0;
  let menuH = 0;

  // Posición ajustada para no salirse de la pantalla.
  $: vw = typeof window !== 'undefined' ? window.innerWidth : 1024;
  $: vh = typeof window !== 'undefined' ? window.innerHeight : 768;
  $: x = Math.min($contextMenu.x, vw - menuW - 8);
  $: y = Math.min($contextMenu.y, vh - menuH - 8);

  async function run(item: CtxItem) {
    if (item.disabled || item.divider) return;
    closeContextMenu();
    if (item.href) {
      await goto(item.href);
      return;
    }
    await item.onClick?.();
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') closeContextMenu();
  }
</script>

<svelte:window
  on:keydown={onKeydown}
  on:resize={closeContextMenu}
  on:scroll={closeContextMenu}
/>

{#if $contextMenu.open}
  <!-- Capa transparente que cierra al hacer click fuera (también con click derecho fuera) -->
  <button
    type="button"
    class="fixed inset-0 z-[90] cursor-default"
    aria-label="Cerrar menú"
    on:click={closeContextMenu}
    on:contextmenu|preventDefault={closeContextMenu}
  ></button>

  <div
    bind:clientWidth={menuW}
    bind:clientHeight={menuH}
    transition:scale={{ duration: 130, start: 0.94, easing: cubicOut }}
    style="left:{Math.max(8, x)}px; top:{Math.max(8, y)}px"
    class="fixed z-[100] min-w-[12rem] max-w-[16rem] origin-top-left overflow-hidden rounded-xl border border-slate-200 bg-white/95 p-1.5 shadow-xl shadow-slate-900/15 backdrop-blur-xl"
    role="menu"
  >
    {#each $contextMenu.items as item}
      {#if item.divider}
        <div class="my-1 h-px bg-slate-100" role="separator"></div>
      {:else}
        <button
          type="button"
          role="menuitem"
          disabled={item.disabled}
          class="group flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-left text-sm font-medium transition
            disabled:cursor-not-allowed disabled:opacity-40
            {item.danger
            ? 'text-rose-600 hover:bg-rose-50'
            : 'text-slate-700 hover:bg-brand-50 hover:text-brand-700'}"
          on:click={() => run(item)}
        >
          {#if item.icon}
            <svelte:component
              this={item.icon}
              class="h-4 w-4 shrink-0 {item.danger
                ? 'text-rose-400 group-hover:text-rose-600'
                : 'text-slate-400 group-hover:text-brand-600'}"
            />
          {/if}
          <span class="truncate">{item.label}</span>
        </button>
      {/if}
    {/each}
  </div>
{/if}
