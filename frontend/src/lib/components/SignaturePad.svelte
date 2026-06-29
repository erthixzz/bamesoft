<script lang="ts">
  /** Pad de firma · estilo Bamesoft.
   *  Canvas táctil/mouse responsive. Expone `clear()`, `isEmpty()` y
   *  `toDataURL()` (PNG) vía `bind:this`. Soporta alta densidad (DPR). */
  import { onMount, createEventDispatcher } from 'svelte';
  import { Eraser } from 'lucide-svelte';

  export let label = 'Firma';
  export let height = 180;
  export let disabled = false;

  const dispatch = createEventDispatcher<{ change: boolean }>();

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null = null;
  let drawing = false;
  let dirty = false;
  let last: { x: number; y: number } | null = null;

  function setup() {
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.round(rect.width * dpr));
    canvas.height = Math.max(1, Math.round(height * dpr));
    ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.scale(dpr, dpr);
      ctx.lineWidth = 2;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.strokeStyle = '#0f172a';
    }
  }

  function pos(e: PointerEvent) {
    const rect = canvas.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  function start(e: PointerEvent) {
    if (disabled || !ctx) return;
    drawing = true;
    last = pos(e);
    canvas.setPointerCapture(e.pointerId);
  }

  function move(e: PointerEvent) {
    if (!drawing || !ctx || !last) return;
    e.preventDefault();
    const p = pos(e);
    ctx.beginPath();
    ctx.moveTo(last.x, last.y);
    ctx.lineTo(p.x, p.y);
    ctx.stroke();
    last = p;
    if (!dirty) {
      dirty = true;
      dispatch('change', true);
    }
  }

  function end() {
    drawing = false;
    last = null;
  }

  export function clear() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    dirty = false;
    dispatch('change', false);
  }

  export function isEmpty(): boolean {
    return !dirty;
  }

  /** PNG con fondo blanco (para que se vea bien en el PDF/impresión). */
  export function toDataURL(): string | null {
    if (!ctx || !dirty) return null;
    const out = document.createElement('canvas');
    out.width = canvas.width;
    out.height = canvas.height;
    const octx = out.getContext('2d');
    if (!octx) return null;
    octx.fillStyle = '#ffffff';
    octx.fillRect(0, 0, out.width, out.height);
    octx.drawImage(canvas, 0, 0);
    return out.toDataURL('image/png');
  }

  onMount(() => {
    setup();
    const onResize = () => {
      // Reconfigurar el lienzo conserva tamaño pero limpia el trazo.
      setup();
      dirty = false;
      dispatch('change', false);
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  });
</script>

<div class="block">
  {#if label}
    <div class="mb-1 flex items-center justify-between">
      <span class="block text-sm font-medium text-slate-700">{label}</span>
      <button
        type="button"
        class="inline-flex items-center gap-1 text-xs font-medium text-slate-500 hover:text-danger-600 disabled:opacity-50"
        on:click={clear}
        {disabled}
      >
        <Eraser class="h-3.5 w-3.5" /> Limpiar
      </button>
    </div>
  {/if}
  <canvas
    bind:this={canvas}
    class="w-full touch-none rounded-xl border border-slate-300 bg-white {disabled
      ? 'cursor-not-allowed opacity-60'
      : 'cursor-crosshair'}"
    style="height:{height}px;"
    on:pointerdown={start}
    on:pointermove={move}
    on:pointerup={end}
    on:pointerleave={end}
  ></canvas>
</div>
