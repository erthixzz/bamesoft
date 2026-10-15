<script lang="ts">
  /** Pad de firma · estilo Bamesoft.
   *  Canvas táctil/mouse responsive. Expone `clear()`, `isEmpty()`,
   *  `toDataURL()` y `toBlob()` (PNG) vía `bind:this`. Soporta alta densidad (DPR). */
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

  // Ancho máximo del PNG exportado. En un móvil con DPR 3 el lienzo real supera
  // los 3000 px: más resolución de la que necesita una firma y un archivo
  // innecesariamente pesado de subir.
  const MAX_EXPORT_WIDTH = 1200;

  /** Copia del trazo sobre fondo blanco (para que se vea bien en PDF/impresión). */
  function composite(): HTMLCanvasElement | null {
    if (!ctx || !dirty) return null;
    const scale = Math.min(1, MAX_EXPORT_WIDTH / canvas.width);
    const out = document.createElement('canvas');
    out.width = Math.max(1, Math.round(canvas.width * scale));
    out.height = Math.max(1, Math.round(canvas.height * scale));
    const octx = out.getContext('2d');
    if (!octx) return null;
    octx.fillStyle = '#ffffff';
    octx.fillRect(0, 0, out.width, out.height);
    octx.drawImage(canvas, 0, 0, out.width, out.height);
    return out;
  }

  /** PNG como data URL (para incrustar en la vista imprimible). */
  export function toDataURL(): string | null {
    return composite()?.toDataURL('image/png') ?? null;
  }

  /**
   * PNG como `Blob`, listo para subir.
   *
   * Se usa `canvas.toBlob()` en vez de `fetch(toDataURL())`: la CSP de la app
   * acota `connect-src` a la API y a Supabase, así que pedir un `data:` URL con
   * `fetch` lo bloquea el navegador y falla con un opaco "Failed to fetch".
   */
  export function toBlob(): Promise<Blob | null> {
    const out = composite();
    if (!out) return Promise.resolve(null);
    return new Promise((resolve) => out.toBlob((b) => resolve(b), 'image/png'));
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
