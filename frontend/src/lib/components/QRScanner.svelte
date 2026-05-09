<script lang="ts">
  import { onDestroy, onMount, createEventDispatcher } from 'svelte';
  import jsQR from 'jsqr';

  const dispatch = createEventDispatcher<{ scan: { raw: string } }>();

  let video: HTMLVideoElement;
  let canvas: HTMLCanvasElement;
  let stream: MediaStream | null = null;
  let raf: number | null = null;
  let running = false;
  let error: string | null = null;

  async function start() {
    error = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      });
      video.srcObject = stream;
      await video.play();
      running = true;
      tick();
    } catch (e) {
      error = e instanceof Error ? e.message : 'No se pudo acceder a la cámara';
    }
  }

  function stop() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = null;
    stream?.getTracks().forEach((t) => t.stop());
    stream = null;
  }

  function tick() {
    if (!running) return;
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (ctx) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const img = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(img.data, img.width, img.height, { inversionAttempts: 'dontInvert' });
        if (code?.data) {
          dispatch('scan', { raw: code.data });
          stop();
          return;
        }
      }
    }
    raf = requestAnimationFrame(tick);
  }

  onMount(start);
  onDestroy(stop);
</script>

<div class="space-y-3">
  <div class="overflow-hidden rounded-xl border border-slate-200 bg-black">
    <video bind:this={video} class="aspect-video w-full" muted playsinline></video>
  </div>
  <canvas bind:this={canvas} hidden></canvas>
  {#if error}
    <p class="text-sm text-danger-600">{error}</p>
    <button class="btn-secondary" on:click={start}>Reintentar</button>
  {/if}
</div>
