<script lang="ts">
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { fly, fade } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import Button from '$lib/components/Button.svelte';
  import Input from '$lib/components/Input.svelte';
  import BrandMark from '$lib/components/BrandMark.svelte';
  import { login } from '$lib/stores/auth';
  import { toasts } from '$lib/stores/toasts';
  import { ArrowLeft, ArrowRight, ShieldCheck } from 'lucide-svelte';

  let email = '';
  let password = '';
  let loading = false;
  let error: string | null = null;

  /** Solo se permite redirigir a rutas internas (evita open-redirect). */
  function safeNext(): string {
    const next = $page.url.searchParams.get('next') ?? '';
    return next.startsWith('/') && !next.startsWith('//') ? next : '/dashboard';
  }

  async function onSubmit(e: SubmitEvent) {
    e.preventDefault();
    loading = true;
    error = null;
    try {
      await login(email, password);
      toasts.success('¡Bienvenido!');
      goto(safeNext());
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error al iniciar sesión';
    } finally {
      loading = false;
    }
  }
</script>

<div class="grid w-full max-w-5xl items-center gap-10 lg:grid-cols-[1.2fr_1fr]">
  <!-- HERO: título gigante con degradado + tagline -->
  <section
    class="text-center lg:text-left"
    in:fly={{ y: 24, duration: 600, delay: 80, easing: cubicOut }}
  >
    <!-- Volver a la landing -->
    <a
      href="/"
      class="group mb-5 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/70 px-3.5 py-1.5 text-xs font-semibold text-slate-600 shadow-sm backdrop-blur transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700"
    >
      <ArrowLeft class="h-3.5 w-3.5 transition group-hover:-translate-x-0.5" />
      Volver al inicio
    </a>

    <p class="mb-3 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/70 px-3 py-1 text-xs font-medium uppercase tracking-wider text-slate-600 shadow-sm backdrop-blur lg:flex lg:w-fit">
      <span class="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_8px_2px_rgba(16,185,129,0.6)]"></span>
      Bienvenido a
    </p>

    <a href="/" class="block" aria-label="Volver al inicio de Bamesoft">
      <h1 class="bm-title text-[3.5rem] font-extrabold leading-[1.05] tracking-tight transition-transform hover:scale-[1.01] sm:text-7xl lg:text-[5.5rem]">
        Bamesoft
      </h1>
    </a>

    <p class="mt-4 max-w-xl text-lg font-medium text-slate-700 sm:text-xl">
      Ingeniería biomédica
      <span class="text-brand-600">·</span>
      Inteligencia artificial
      <span class="text-cyan-600">·</span>
      Cumplimiento clínico
    </p>

    <p class="mt-3 max-w-xl text-sm text-slate-500">
      Inventario, mantenimientos, calibraciones y normas de tu clínica
      en una sola plataforma. Simple, potente y siempre auditable.
    </p>

    <!-- Pildora de seguridad -->
    <div class="mt-6 flex flex-wrap items-center justify-center gap-2 text-xs text-slate-500 lg:justify-start">
      <span class="inline-flex items-center gap-1.5 rounded-full bg-white/70 px-3 py-1 ring-1 ring-slate-200 backdrop-blur">
        <ShieldCheck class="h-3.5 w-3.5 text-emerald-600" />
        Datos protegidos por Supabase Auth
      </span>
      <span class="inline-flex items-center gap-1.5 rounded-full bg-white/70 px-3 py-1 ring-1 ring-slate-200 backdrop-blur">
        ISO 13485 · IEC 60601 · INVIMA
      </span>
    </div>
  </section>

  <!-- LOGIN CARD glassmorphism -->
  <section in:fly={{ y: 24, duration: 600, delay: 180, easing: cubicOut }}>
    <form
      on:submit={onSubmit}
      class="relative rounded-2xl border border-white/60 bg-white/70 p-6 shadow-xl shadow-slate-900/5 backdrop-blur-xl"
    >
      <!-- Halo del card -->
      <div class="pointer-events-none absolute -inset-px -z-10 rounded-2xl bg-gradient-to-br from-brand-500/30 via-cyan-400/20 to-emerald-400/20 opacity-50 blur-xl"></div>

      <header class="mb-5 flex items-center gap-3">
        <a
          href="/"
          class="shrink-0 rounded-xl shadow-md transition hover:brightness-110 active:scale-95"
          aria-label="Volver al inicio"
        >
          <BrandMark size={40} />
        </a>
        <div>
          <h2 class="text-base font-semibold text-slate-900">Iniciar sesión</h2>
          <p class="text-xs text-slate-500">Accede a tu suite biomédica</p>
        </div>
      </header>

      <div class="space-y-3">
        <Input label="Email" type="email" bind:value={email} required placeholder="tu@clinica.com" />
        <Input label="Contraseña" type="password" bind:value={password} required placeholder="••••••••" />
      </div>

      {#if error}
        <p class="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-danger-700">{error}</p>
      {/if}

      <div class="mt-6">
        <Button type="submit" {loading}>
          <span class="flex items-center gap-2">
            Entrar
            <ArrowRight class="h-4 w-4" />
          </span>
        </Button>
      </div>

      <p class="mt-4 text-center text-xs text-slate-500">
        ¿Necesitas una cuenta? Habla con tu administrador.
      </p>
    </form>
  </section>
</div>

<style>
  /* Título con degradado animado */
  .bm-title {
    background: linear-gradient(
      120deg,
      #1971f5 0%,
      #06b6d4 35%,
      #10b981 70%,
      #1971f5 100%
    );
    background-size: 200% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
    animation: shimmer 9s ease-in-out infinite;
    text-shadow: 0 4px 24px rgba(25, 113, 245, 0.15);
  }
  @keyframes shimmer {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
</style>
