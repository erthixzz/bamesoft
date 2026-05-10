<script lang="ts">
  import { toasts, type ToastKind } from '$lib/stores/toasts';
  import { fly } from 'svelte/transition';
  import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-svelte';

  type IconType = typeof CheckCircle2;
  const palette: Record<ToastKind, { bar: string; Icon: IconType; iconCls: string }> = {
    success: { bar: 'bg-emerald-500', Icon: CheckCircle2, iconCls: 'text-emerald-500' },
    error: { bar: 'bg-red-500', Icon: AlertCircle, iconCls: 'text-red-500' },
    info: { bar: 'bg-brand-500', Icon: Info, iconCls: 'text-brand-500' },
    warning: { bar: 'bg-amber-500', Icon: AlertTriangle, iconCls: 'text-amber-500' },
  };
</script>

<div class="pointer-events-none fixed bottom-5 right-5 z-[100] flex flex-col-reverse gap-2">
  {#each $toasts as t (t.id)}
    <div
      role="status"
      transition:fly={{ x: 40, duration: 220 }}
      class="pointer-events-auto relative flex w-[320px] items-start gap-3 overflow-hidden rounded-xl
             border border-slate-200 bg-white px-4 py-3 shadow-lg shadow-slate-900/5"
    >
      <svelte:component this={palette[t.kind].Icon} class={`mt-0.5 h-5 w-5 shrink-0 ${palette[t.kind].iconCls}`} />
      <p class="flex-1 text-sm leading-snug text-slate-800">{t.message}</p>
      <button
        class="text-slate-400 transition hover:text-slate-700"
        on:click={() => toasts.dismiss(t.id)}
        aria-label="Cerrar"
      >
        <X class="h-4 w-4" />
      </button>

      <!-- Barra de progreso animada (CSS-only) -->
      <span
        class="pointer-events-none absolute inset-x-0 bottom-0 h-1 origin-left"
      >
        <span
          class={`block h-full ${palette[t.kind].bar} toast-progress`}
          style={`animation-duration: ${t.durationMs}ms`}
        ></span>
      </span>
    </div>
  {/each}
</div>

<style>
  @keyframes shrink {
    from { transform: scaleX(1); }
    to   { transform: scaleX(0); }
  }
  :global(.toast-progress) {
    width: 100%;
    transform-origin: left;
    animation-name: shrink;
    animation-timing-function: linear;
    animation-fill-mode: forwards;
  }
</style>
