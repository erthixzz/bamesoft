<script lang="ts">
  import { toasts } from '$lib/stores/toasts';

  const toneMap = {
    success: 'border-emerald-300 bg-emerald-50 text-emerald-800',
    error: 'border-red-300 bg-red-50 text-red-800',
    info: 'border-brand-300 bg-brand-50 text-brand-800',
    warning: 'border-amber-300 bg-amber-50 text-amber-800',
  } as const;
</script>

<div class="pointer-events-none fixed right-5 top-5 z-[100] flex flex-col gap-2">
  {#each $toasts as t (t.id)}
    <div
      class="pointer-events-auto min-w-[260px] max-w-sm rounded-lg border px-4 py-3 text-sm shadow {toneMap[
        t.kind
      ]}"
    >
      {t.message}
    </div>
  {/each}
</div>
