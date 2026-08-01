<script lang="ts">
  /**
   * Pantalla para quien se autenticó correctamente pero todavía no tiene acceso.
   *
   * Es la contraparte visible del cierre del auto-alta en el backend: tener
   * credenciales válidas ya no basta para entrar, porque el perfil lo crea un
   * administrador. Sin esta página esa persona vería un 403 crudo y pensaría
   * que la aplicación está rota.
   *
   * En la práctica ocurre con cuentas creadas a mano en Supabase o con el
   * resto de un alta que falló a medias.
   */
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import BrandMark from '$lib/components/BrandMark.svelte';
  import Button from '$lib/components/Button.svelte';
  import { authApi } from '$lib/modules/auth/api';
  import { isAuthenticated, logout, profile, session } from '$lib/stores/auth';
  import { toasts } from '$lib/stores/toasts';
  import { Check, Copy, LogOut, RefreshCw, ShieldCheck } from 'lucide-svelte';

  let checking = false;
  let copied = false;

  $: email = $session?.user?.email ?? '';

  onMount(() => {
    // Sin sesión no hay nada que esperar: al login.
    if (!$isAuthenticated) goto('/login');
  });

  /** Reintenta: si un admin ya dio de alta la cuenta, entra directo. */
  async function recheck() {
    checking = true;
    try {
      const p = await authApi.whoami();
      profile.set(p);
      toasts.success(`¡Listo, ${p.full_name}! Ya tienes acceso.`);
      goto('/dashboard');
    } catch {
      toasts.info('Todavía no. Tu administrador aún no ha habilitado la cuenta.');
    } finally {
      checking = false;
    }
  }

  async function copyEmail() {
    try {
      await navigator.clipboard.writeText(email);
      copied = true;
      setTimeout(() => (copied = false), 2000);
    } catch {
      toasts.error('No se pudo copiar. Selecciónalo a mano.');
    }
  }
</script>

<svelte:head><title>Acceso pendiente · Bamesoft</title></svelte:head>

<section
  class="w-full max-w-lg"
  in:fly={{ y: 24, duration: 600, easing: cubicOut }}
>
  <div
    class="relative rounded-2xl border border-white/60 bg-white/70 p-8 text-center shadow-xl shadow-slate-900/5 backdrop-blur-xl"
  >
    <div
      class="pointer-events-none absolute -inset-px -z-10 rounded-2xl bg-gradient-to-br from-brand-500/30 via-cyan-400/20 to-emerald-400/20 opacity-50 blur-xl"
    ></div>

    <!-- Radar: identidad verificada, esperando autorización -->
    <div class="relative mx-auto mb-6 grid h-24 w-24 place-items-center">
      <span class="radar-ring"></span>
      <span class="radar-ring radar-ring--delayed"></span>
      <div class="relative z-10 rounded-2xl shadow-lg">
        <BrandMark size={52} />
      </div>
    </div>

    <p
      class="mx-auto mb-3 inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700"
    >
      <ShieldCheck class="h-3.5 w-3.5" />
      Identidad verificada
    </p>

    <h1 class="text-2xl font-bold tracking-tight text-slate-900">
      Tu cuenta aún no tiene acceso
    </h1>

    <p class="mx-auto mt-3 max-w-sm text-sm leading-relaxed text-slate-600">
      Tus credenciales son válidas, pero tu cuenta todavía no está asignada a
      ninguna clínica. En Bamesoft el acceso lo concede un administrador.
    </p>

    {#if email}
      <div class="mx-auto mt-6 max-w-sm">
        <p class="mb-1.5 text-xs font-medium uppercase tracking-wider text-slate-400">
          Pásale este correo a tu administrador
        </p>
        <button
          type="button"
          on:click={copyEmail}
          class="group flex w-full items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-left transition hover:border-brand-300 hover:bg-brand-50/50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
        >
          <span class="truncate font-mono text-sm text-slate-700">{email}</span>
          {#if copied}
            <Check class="h-4 w-4 shrink-0 text-emerald-600" />
          {:else}
            <Copy class="h-4 w-4 shrink-0 text-slate-400 transition group-hover:text-brand-600" />
          {/if}
        </button>
        <p class="mt-1.5 text-[11px] text-slate-400">
          {copied ? '¡Copiado!' : 'Toca para copiar'}
        </p>
      </div>
    {/if}

    <ol class="mx-auto mt-7 max-w-sm space-y-2.5 text-left text-sm text-slate-600">
      <li class="flex gap-3">
        <span class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-slate-100 text-[11px] font-bold text-slate-500">1</span>
        Tu administrador te da de alta en la clínica y te asigna un rol.
      </li>
      <li class="flex gap-3">
        <span class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-slate-100 text-[11px] font-bold text-slate-500">2</span>
        Vuelves aquí y pulsas <strong class="font-semibold text-slate-700">Comprobar de nuevo</strong>.
      </li>
      <li class="flex gap-3">
        <span class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-slate-100 text-[11px] font-bold text-slate-500">3</span>
        A partir de ahí entras con normalidad.
      </li>
    </ol>

    <div class="mt-8 flex flex-col gap-2.5 sm:flex-row sm:justify-center">
      <Button loading={checking} on:click={recheck}>
        <span class="flex items-center gap-2">
          <RefreshCw class="h-4 w-4 {checking ? 'animate-spin' : ''}" />
          Comprobar de nuevo
        </span>
      </Button>
      <button
        type="button"
        on:click={logout}
        class="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500"
      >
        <LogOut class="h-4 w-4" />
        Cerrar sesión
      </button>
    </div>
  </div>
</section>

<style>
  /* Ondas de radar: comunican "esperando" sin una barra de progreso falsa,
     porque no hay progreso real que mostrar — depende de una persona. */
  .radar-ring {
    position: absolute;
    inset: 0;
    border-radius: 1rem;
    border: 2px solid theme('colors.brand.400');
    opacity: 0;
    animation: radar 3s cubic-bezier(0.22, 0.61, 0.36, 1) infinite;
  }

  .radar-ring--delayed {
    animation-delay: 1.5s;
  }

  @keyframes radar {
    0%   { transform: scale(0.55); opacity: 0.75; }
    70%  { opacity: 0.06; }
    100% { transform: scale(1.35); opacity: 0; }
  }

  @media (prefers-reduced-motion: reduce) {
    .radar-ring {
      animation: none;
      opacity: 0.25;
      transform: scale(1);
    }
  }
</style>
