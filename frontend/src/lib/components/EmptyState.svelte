<script lang="ts">
  import type { ComponentType } from 'svelte';
  import { Inbox } from 'lucide-svelte';

  export let icon: ComponentType = Inbox;
  export let title: string;
  export let description: string | null = null;
</script>

<div class="flex flex-col items-center justify-center gap-3 px-4 py-12 text-center">
  <div class="grid h-20 w-20 place-items-center rounded-2xl bg-gradient-to-br from-slate-100 to-slate-50 text-slate-400 ring-1 ring-slate-200">
    <svelte:component this={icon} class="h-9 w-9" />
  </div>
  <p class="text-lg font-semibold text-slate-700">{title}</p>
  {#if description}
    <p class="max-w-md text-sm text-slate-500">{description}</p>
  {/if}
  {#if $$slots.actions}
    <div class="mt-2 flex flex-wrap justify-center gap-2">
      <slot name="actions" />
    </div>
  {/if}
</div>
