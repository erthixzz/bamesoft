<script lang="ts" context="module">
  /** Carga del script de Cloudflare, una sola vez para toda la app. */
  let loader: Promise<void> | null = null;

  const SCRIPT_SRC = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';

  function loadTurnstile(): Promise<void> {
    if (loader) return loader;
    loader = new Promise((resolve, reject) => {
      if (typeof window === 'undefined') return reject(new Error('SSR'));
      if (window.turnstile) return resolve();

      const script = document.createElement('script');
      script.src = SCRIPT_SRC;
      script.async = true;
      script.defer = true;
      script.onload = () => resolve();
      script.onerror = () => {
        loader = null; // permite reintentar si fue un fallo de red puntual
        reject(new Error('No se pudo cargar el verificador de Cloudflare'));
      };
      document.head.appendChild(script);
    });
    return loader;
  }
</script>

<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { env } from '$env/dynamic/public';
  import { ShieldCheck, TriangleAlert } from 'lucide-svelte';

  /**
   * Verificación anti-bot de Cloudflare Turnstile.
   *
   * Supabase exige un `captchaToken` en el login cuando la protección CAPTCHA
   * está activa (Settings → Authentication → Bot and Abuse Protection). Este
   * componente resuelve el reto y devuelve ese token por `bind:token`.
   *
   * Si `PUBLIC_TURNSTILE_SITE_KEY` no está definida, el componente no se
   * muestra y `token` queda en `null`: así el desarrollo local sigue
   * funcionando cuando la protección está apagada en el proyecto de Supabase.
   *
   * El token es de un solo uso y caduca a los ~5 minutos. Tras un intento
   * fallido de login hay que llamar a `reset()`.
   */
  export let token: string | null = null;

  const siteKey = env.PUBLIC_TURNSTILE_SITE_KEY ?? '';

  /** `true` si hay sitekey configurada y, por tanto, el reto es obligatorio. */
  export const required = !!siteKey;

  let container: HTMLDivElement;
  let widgetId: string | undefined;
  let status: 'idle' | 'loading' | 'ready' | 'error' = 'idle';
  let errorMsg = '';

  /** Limpia el token y pide un reto nuevo. Úsalo tras un login fallido. */
  export function reset(): void {
    token = null;
    if (widgetId !== undefined) window.turnstile?.reset(widgetId);
  }

  onMount(async () => {
    if (!siteKey) return;
    status = 'loading';
    try {
      await loadTurnstile();
      widgetId = window.turnstile?.render(container, {
        sitekey: siteKey,
        theme: 'light',
        size: 'flexible',
        language: 'es',
        callback: (t: string) => {
          token = t;
          status = 'ready';
        },
        'expired-callback': () => {
          token = null;
        },
        'error-callback': () => {
          token = null;
          status = 'error';
          errorMsg = 'No se pudo verificar. Revisa tu conexión e inténtalo de nuevo.';
        },
      });
      if (status === 'loading') status = 'ready';
    } catch (e) {
      status = 'error';
      errorMsg = e instanceof Error ? e.message : 'Error al cargar la verificación';
    }
  });

  onDestroy(() => {
    if (widgetId !== undefined) window.turnstile?.remove(widgetId);
  });
</script>

{#if siteKey}
  <div class="mt-4">
    <div bind:this={container} class="flex min-h-[65px] justify-center"></div>

    {#if status === 'loading'}
      <p class="mt-1 text-center text-xs text-slate-400">Verificando que no eres un robot…</p>
    {:else if status === 'error'}
      <p
        class="mt-1 flex items-center justify-center gap-1.5 text-center text-xs text-danger-700"
        role="alert"
      >
        <TriangleAlert class="h-3.5 w-3.5 shrink-0" />
        {errorMsg}
      </p>
    {:else if token}
      <p class="mt-1 flex items-center justify-center gap-1.5 text-center text-xs text-emerald-600">
        <ShieldCheck class="h-3.5 w-3.5 shrink-0" />
        Verificado
      </p>
    {/if}
  </div>
{/if}
