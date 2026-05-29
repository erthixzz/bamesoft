<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { fade } from 'svelte/transition';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { session } from '$lib/stores/auth';
  import AuthBackdrop from '$lib/components/AuthBackdrop.svelte';
  import {
    ArrowRight,
    Brain,
    Building2,
    Check,
    Cpu,
    FileCheck2,
    LineChart,
    Mail,
    Menu,
    ShieldCheck,
    Sparkles,
    Stethoscope,
    X,
    Zap,
  } from 'lucide-svelte';

  const navItems = [
    { h: '#inicio', l: 'Inicio' },
    { h: '#nosotros', l: 'Nosotros' },
    { h: '#precios', l: 'Precios' },
    { h: '#contacto', l: 'Contacto' },
  ] as const;

  let menuOpen = false;

  function closeMenu() {
    menuOpen = false;
  }

  /** Scroll suave desde el header (offset por barra fija). */
  function navToSection(e: MouseEvent, hash: string) {
    e.preventDefault();
    const id = hash.replace('#', '');
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.replaceState(null, '', hash);
    }
    menuOpen = false;
  }

  /** Entrada al hacer scroll */
  function scrollReveal(node: HTMLElement) {
    node.classList.add('sr-base');
    const obs = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            node.classList.add('sr-in');
            obs.unobserve(node);
          }
        }
      },
      { rootMargin: '0px 0px -10% 0px', threshold: 0.08 }
    );
    obs.observe(node);
    return { destroy() { obs.disconnect(); } };
  }

  type Stat = { target: number; suffix: string; label: string; Icon: typeof Building2; decimals?: number };
  const statDefs: Stat[] = [
    { target: 120, suffix: '+', label: 'clínicas y hospitales de confianza', Icon: Building2 },
    { target: 45000, suffix: '+', label: 'activos biomédicos bajo trazabilidad', Icon: Zap, decimals: 0 },
    { target: 99.9, suffix: '%', label: 'objetivo de disponibilidad cloud', Icon: ShieldCheck, decimals: 1 },
  ];

  let statDisplay: string[] = ['0', '0', '0'];
  let statsAnimated = false;

  function formatStat(n: number, decimals?: number): string {
    if (decimals === 1) return n.toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
    return Math.round(n).toLocaleString('es-ES');
  }

  onMount(() => {
    const unsub = session.subscribe((s) => {
      if (s?.access_token) goto('/dashboard');
    });

    const statRow = document.getElementById('stat-row');
    if (!statRow) return unsub;

    const obs = new IntersectionObserver(
      (entries) => {
        if (!entries[0]?.isIntersecting || statsAnimated) return;
        statsAnimated = true;
        const duration = 2200;
        const start = performance.now();

        const tickAnim = (now: number) => {
          const t = Math.min(1, (now - start) / duration);
          const ease = 1 - Math.pow(1 - t, 3);
          statDisplay = statDefs.map((s, i) => {
            const v = s.target * ease;
            return formatStat(v, s.decimals) + s.suffix;
          });
          if (t < 1) requestAnimationFrame(tickAnim);
          else statDisplay = statDefs.map((s) => formatStat(s.target, s.decimals) + s.suffix);
        };
        requestAnimationFrame(tickAnim);
        obs.disconnect();
      },
      { threshold: 0.25 }
    );
    obs.observe(statRow);

    return () => {
      unsub();
      obs.disconnect();
    };
  });

  function onDocKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') menuOpen = false;
  }

  $: if (browser) {
    document.body.style.overflow = menuOpen ? 'hidden' : '';
  }

  onDestroy(() => {
    if (browser) document.body.style.overflow = '';
  });
</script>

<svelte:window on:keydown={onDocKeydown} />

<svelte:head>
  <title>Bamesoft — Plataforma de ingeniería biomédica para clínicas</title>
  <meta
    name="description"
    content="Inventario, mantenimiento, calibraciones, IA y cumplimiento normativo. Una suite auditable para tu clínica."
  />
</svelte:head>

<!-- Fondo con más profundidad (menos “plano blanco”) -->
<div
  class="landing-root relative min-h-screen overflow-x-hidden bg-slate-950 text-slate-900 selection:bg-brand-500/30"
>
  <!-- Capas decorativas -->
  <div class="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(25,113,245,0.35),transparent_55%)]"></div>
  <div
    class="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_85%_20%,rgba(6,182,212,0.12),transparent_40%)]"
  ></div>
  <div
    class="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_10%_60%,rgba(16,185,129,0.08),transparent_45%)]"
  ></div>
  <div
    class="pointer-events-none fixed inset-0 z-0 opacity-[0.35] mix-blend-overlay"
    style="background-image:url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22n%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23n)%22 opacity=%220.04%22/%3E%3C/svg%3E')"
  ></div>

  <div class="relative z-[1] bg-gradient-to-b from-slate-50 via-white to-slate-100/95">
    <AuthBackdrop />

    <div class="relative z-10" in:fade={{ duration: 450 }}>
      <!-- Header: logo | (nav escritorio + hamburguesa móvil + Entrar) -->
      <header
        class="landing-header sticky top-0 z-30 border-b border-slate-200 bg-white shadow-[0_4px_20px_rgba(15,23,42,0.07)] md:border-brand-200/40 md:bg-white/95 md:shadow-[0_8px_32px_-12px_rgba(25,113,245,0.18)] md:backdrop-blur-xl"
      >
        <div
          class="pointer-events-none absolute inset-x-0 bottom-0 hidden h-px bg-gradient-to-r from-transparent via-brand-400/50 to-transparent md:block"
        ></div>
        <div
          class="mx-auto flex w-full max-w-6xl items-center justify-between gap-3 px-3 py-2.5 md:gap-4 md:px-6 md:py-3 lg:px-10"
        >
          <!-- Logo amplio (marca + nombre) -->
          <a href="/" class="group flex min-w-0 shrink-0 items-center gap-2.5 sm:gap-3" on:click={closeMenu}>
            <span
              class="logo-mark relative grid h-12 w-12 shrink-0 place-items-center overflow-hidden rounded-2xl text-base font-black text-white shadow-lg shadow-brand-600/35 ring-2 ring-brand-100 sm:h-14 sm:w-14 sm:text-lg md:h-[3.75rem] md:w-[3.75rem]"
            >
              <span class="relative z-10">B</span>
            </span>
            <span class="hidden min-[360px]:flex min-w-0 flex-col leading-tight">
              <span class="logo-wordmark text-base font-black tracking-tight sm:text-lg md:text-xl"
                >Bamesoft</span
              >
              <span
                class="text-[9px] font-bold uppercase tracking-[0.16em] text-brand-700 sm:text-[10px] sm:tracking-[0.2em]"
                >Biomedical Suite</span
              >
            </span>
          </a>

          <div class="flex shrink-0 items-center gap-2 md:gap-3 lg:gap-4">
            <!-- Navegación escritorio -->
            <nav class="hidden items-center gap-1 md:flex lg:gap-2" aria-label="Principal">
              {#each navItems as item}
                <a
                  href={item.h}
                  class="nav-pill-desk relative rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:text-brand-700"
                  on:click={(e) => navToSection(e, item.h)}
                >
                  {item.l}
                </a>
              {/each}
            </nav>

            <!-- Hamburguesa solo móvil / tablet estrecha -->
            <button
              type="button"
              class="flex h-11 w-11 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-slate-800 shadow-sm transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-800 md:hidden"
              aria-expanded={menuOpen}
              aria-controls="drawer-nav"
              aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
              on:click={() => (menuOpen = !menuOpen)}
            >
              {#if menuOpen}
                <X class="h-5 w-5" stroke-width={2.25} />
              {:else}
                <Menu class="h-5 w-5" stroke-width={2.25} />
              {/if}
            </button>

            <a
              href="/login"
              class="inline-flex min-h-[44px] min-w-[4.5rem] items-center justify-center gap-1.5 rounded-xl bg-gradient-to-r from-brand-600 to-brand-500 px-4 py-2.5 text-sm font-bold text-white shadow-md shadow-brand-600/30 transition hover:brightness-105 active:scale-[0.98] md:min-h-0 md:rounded-2xl md:px-5 md:py-2.5"
            >
              <span class="md:hidden">Entrar</span>
              <span class="hidden md:inline">Iniciar sesión</span>
              <ArrowRight class="h-4 w-4 md:h-4" />
            </a>
          </div>
        </div>
      </header>

      <!-- Drawer móvil -->
      {#if menuOpen}
        <div
          class="fixed inset-0 z-40 flex md:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Menú de navegación"
        >
          <button
            type="button"
            class="absolute inset-0 bg-slate-900/55 backdrop-blur-[2px]"
            aria-label="Cerrar menú"
            on:click={closeMenu}
          ></button>
          <nav
            id="drawer-nav"
            class="relative ml-auto flex h-full w-[min(20rem,88vw)] flex-col border-l border-slate-200 bg-white shadow-2xl"
          >
            <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
              <span class="text-sm font-bold text-slate-800">Menú</span>
              <button
                type="button"
                class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800"
                aria-label="Cerrar"
                on:click={closeMenu}
              >
                <X class="h-5 w-5" />
              </button>
            </div>
            <div class="flex flex-1 flex-col gap-1 p-3">
              {#each navItems as item}
                <a
                  href={item.h}
                  class="rounded-xl px-4 py-3.5 text-base font-semibold text-slate-800 transition hover:bg-brand-50 hover:text-brand-800"
                  on:click={(e) => navToSection(e, item.h)}
                >
                  {item.l}
                </a>
              {/each}
            </div>
            <div class="border-t border-slate-100 p-4">
              <a
                href="/login"
                class="flex w-full items-center justify-center gap-2 rounded-xl bg-brand-600 py-3.5 text-sm font-bold text-white shadow-md"
                on:click={closeMenu}
              >
                Iniciar sesión
                <ArrowRight class="h-4 w-4" />
              </a>
            </div>
          </nav>
        </div>
      {/if}

      <main>
        <!-- Hero -->
        <section
          id="inicio"
          class="relative mx-auto max-w-6xl scroll-mt-20 px-3 pb-16 pt-12 text-center sm:scroll-mt-28 sm:px-6 sm:pb-24 sm:pt-16 lg:scroll-mt-32 lg:px-10 lg:pt-24"
        >
          <div class="pointer-events-none absolute left-1/2 top-0 h-48 w-[110%] -translate-x-1/2 bg-gradient-to-b from-brand-100/80 to-transparent blur-3xl sm:h-64 sm:w-[120%]"></div>

          <div use:scrollReveal class="relative">
            <p
              class="mb-4 inline-flex max-w-[95vw] flex-wrap items-center justify-center gap-2 rounded-full border border-brand-300/50 bg-gradient-to-r from-brand-50 to-cyan-50 px-4 py-2 text-[10px] font-bold uppercase leading-tight tracking-wider text-brand-900 shadow-sm shadow-brand-500/10 sm:mb-5 sm:px-5 sm:text-xs sm:tracking-[0.2em]"
            >
              <Sparkles class="h-3.5 w-3.5 shrink-0 text-brand-600 sm:h-4 sm:w-4" />
              <span>IA · Ingeniería clínica · Cumplimiento</span>
            </p>

            <h1
              class="bm-hero-title text-4xl font-black leading-[0.95] tracking-tight sm:text-6xl lg:text-[5.25rem]"
            >
              Bamesoft
            </h1>

            <p
              class="mx-auto mt-5 max-w-2xl text-base font-medium leading-relaxed text-slate-600 sm:mt-6 sm:text-lg lg:text-xl"
            >
              La suite que une <span class="font-semibold text-slate-800">ingeniería biomédica</span>,
              <span class="bg-gradient-to-r from-brand-600 to-cyan-600 bg-clip-text font-bold text-transparent"
                >inteligencia artificial</span
              >
              y
              <span class="font-semibold text-slate-800">cumplimiento normativo</span>
              en una sola experiencia — auditable, escalable y lista para auditoría.
            </p>

            <div class="mt-10 flex max-w-md flex-col items-stretch justify-center gap-3 sm:mx-auto sm:mt-12 sm:max-w-none sm:flex-row sm:items-center sm:justify-center sm:gap-4">
              <a
                href="/login"
                class="group relative inline-flex min-h-[48px] w-full items-center justify-center gap-2 overflow-hidden rounded-2xl bg-gradient-to-r from-brand-600 via-brand-500 to-brand-600 bg-[length:200%_100%] px-8 py-3.5 text-sm font-bold text-white shadow-2xl shadow-brand-600/35 transition hover:shadow-brand-500/45 sm:w-auto sm:min-w-[220px] sm:px-10 sm:py-4 sm:text-base animate-cta-shine"
              >
                <span class="relative z-10 flex items-center gap-2">
                  Iniciar sesión
                  <ArrowRight class="h-5 w-5 transition group-hover:translate-x-1" />
                </span>
              </a>
              <a
                href="#precios"
                class="inline-flex min-h-[48px] w-full items-center justify-center rounded-2xl border-2 border-slate-200 bg-white px-8 py-3.5 text-sm font-bold text-slate-800 shadow-md shadow-slate-900/5 transition hover:border-brand-300 hover:bg-brand-50/90 sm:w-auto sm:min-w-[220px] sm:px-10 sm:py-4 sm:text-base"
                on:click={(e) => navToSection(e, '#precios')}
              >
                Ver planes
              </a>
            </div>
          </div>

          <!-- Stats: tarjetas con vidrio, brillo y contador -->
          <div
            id="stat-row"
            class="relative mx-auto mt-14 grid max-w-5xl gap-3 sm:mt-20 sm:grid-cols-3 sm:gap-5"
            aria-label="Indicadores orientativos"
          >
            {#each statDefs as s, i}
              <div
                use:scrollReveal
                class="stat-card group relative overflow-hidden rounded-2xl border border-slate-200/90 bg-gradient-to-br from-white via-brand-50/50 to-white p-5 text-left shadow-lg shadow-slate-900/6 sm:rounded-3xl sm:border-white/80 sm:p-8 sm:shadow-[0_20px_50px_-24px_rgba(25,113,245,0.35)]"
                style="transition-delay: {i * 90}ms"
              >
                <div
                  class="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full bg-brand-400/15 blur-2xl transition group-hover:bg-brand-400/25 sm:-right-8 sm:-top-8 sm:h-32 sm:w-32 sm:blur-2xl"
                ></div>
                <svelte:component
                  this={s.Icon}
                  class="relative mb-3 h-7 w-7 text-brand-600 drop-shadow-sm sm:mb-4 sm:h-8 sm:w-8"
                  stroke-width={1.75}
                />
                <p
                  class="stat-num relative font-mono text-3xl font-black tabular-nums tracking-tight text-slate-900 drop-shadow-sm sm:text-4xl lg:text-5xl"
                >
                  <span class="bg-gradient-to-br from-brand-700 via-brand-600 to-cyan-600 bg-clip-text text-transparent">
                    {statDisplay[i]}
                  </span>
                </p>
                <p class="relative mt-1.5 text-xs font-semibold leading-snug text-slate-600 sm:mt-2 sm:text-sm">
                  {s.label}
                </p>
              </div>
            {/each}
          </div>
          <p class="mt-3 max-w-[90vw] px-1 text-[11px] font-medium leading-snug text-slate-400 sm:mt-4 sm:text-xs">
            Cifras orientativas de referencia de mercado · resultados según despliegue
          </p>
        </section>

        <!-- ¿Por qué? — bento / más densidad visual -->
        <section
          id="nosotros"
          class="relative scroll-mt-20 border-y border-slate-200/90 bg-gradient-to-b from-slate-100/90 via-white to-slate-50 py-16 sm:scroll-mt-28 sm:py-24 lg:scroll-mt-32"
        >
          <div
            class="pointer-events-none absolute inset-0 bg-[linear-gradient(105deg,transparent_40%,rgba(25,113,245,0.04)_50%,transparent_60%)]"
          ></div>
          <div class="relative mx-auto max-w-6xl px-3 sm:px-6 lg:px-10">
            <div use:scrollReveal class="mx-auto max-w-3xl text-center">
              <p class="text-xs font-bold uppercase tracking-widest text-brand-600 sm:text-sm">Diferencial</p>
              <h2 class="mt-2 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
                ¿Por qué Bamesoft?
              </h2>
              <p class="mt-3 text-base leading-relaxed text-slate-600 sm:mt-4 sm:text-lg">
                Porque no es “otro CMMS”: es una <strong>capa operativa y de gobierno</strong> pensada para
                ingeniería clínica, con trazabilidad real, documentación alineada a norma y reporting que
                entiende dirección médica y calidad.
              </p>
            </div>

            <div class="mt-10 grid items-start gap-3 sm:mt-16 sm:grid-cols-6 sm:gap-4 lg:grid-cols-12 lg:gap-5">
              <!-- Tarjeta ancha oscura -->
              <div
                use:scrollReveal
                class="relative overflow-hidden rounded-2xl border border-slate-800/80 bg-gradient-to-br from-slate-900 via-brand-950 to-slate-900 p-5 text-white shadow-xl shadow-brand-900/30 sm:rounded-3xl sm:p-8 sm:shadow-2xl sm:shadow-brand-900/40 sm:col-span-6 lg:col-span-7 lg:row-span-2 lg:p-10"
              >
                <div
                  class="pointer-events-none absolute -right-16 top-0 h-56 w-56 rounded-full bg-brand-500/25 blur-3xl sm:-right-20 sm:h-80 sm:w-80"
                ></div>
                <Brain class="relative mb-4 h-10 w-10 text-cyan-300 sm:mb-5 sm:h-12 sm:w-12" stroke-width={1.25} />
                <h3 class="relative text-xl font-bold leading-tight sm:text-2xl lg:text-3xl">
                  IA que reduce carga cognitiva del biomédico
                </h3>
                <p class="relative mt-3 max-w-xl text-sm leading-relaxed text-slate-300 sm:mt-4 sm:text-base">
                  Priorización de casos, lectura asistida de evidencias y alertas anticipadas sobre
                  calibraciones y mantenimiento — sin sustituir el criterio clínico, potenciándolo.
                </p>
                <ul class="relative mt-6 grid gap-2.5 sm:mt-8 sm:grid-cols-2 sm:gap-3">
                  {#each ['Modelos de riesgo por equipo', 'Sugerencias de repuestos y SLA', 'Resúmenes para comité', 'Correlación norma ↔ activo'] as line}
                    <li class="flex items-start gap-2 text-xs font-medium text-slate-200 sm:text-sm">
                      <span class="grid h-6 w-6 place-items-center rounded-lg bg-white/10">
                        <Check class="h-3.5 w-3.5 text-emerald-400" stroke-width={3} />
                      </span>
                      {line}
                    </li>
                  {/each}
                </ul>
              </div>

              <!-- Tarjetas compactas -->
              <div
                use:scrollReveal
                class="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-md shadow-slate-900/5 sm:col-span-3 sm:rounded-3xl sm:p-6 lg:col-span-5"
              >
                <Stethoscope class="mb-3 h-8 w-8 text-brand-600 sm:mb-4 sm:h-9 sm:w-9" stroke-width={1.5} />
                <h3 class="text-lg font-bold text-slate-900">Flujo clínico real</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-600">
                  Casos correctivos/preventivos, calibración e instalación en un solo hilo con bitácora y
                  responsables.
                </p>
              </div>

              <div
                use:scrollReveal
                class="rounded-2xl border border-slate-200/90 bg-gradient-to-br from-brand-50 to-white p-5 shadow-md shadow-brand-500/10 sm:col-span-3 sm:rounded-3xl sm:p-6 lg:col-span-5"
              >
                <ShieldCheck class="mb-3 h-8 w-8 text-brand-700 sm:mb-4 sm:h-9 sm:w-9" stroke-width={1.5} />
                <h3 class="text-lg font-bold text-slate-900">Defensa en profundidad</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-600">
                  Roles en API + políticas RLS en base de datos. Menos superficie de error en auditorías.
                </p>
              </div>

              <div
                use:scrollReveal
                class="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-md sm:col-span-3 sm:rounded-3xl sm:p-6 lg:col-span-4"
              >
                <Cpu class="mb-3 h-8 w-8 text-cyan-600 sm:mb-4 sm:h-9 sm:w-9" stroke-width={1.5} />
                <h3 class="text-lg font-bold text-slate-900">Inventario con QR</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-600">
                  Identificación opaca, regenerable y trazable por equipo y sede.
                </p>
              </div>

              <div
                use:scrollReveal
                class="rounded-2xl border border-slate-200/90 bg-white p-5 shadow-md sm:col-span-3 sm:rounded-3xl sm:p-6 lg:col-span-4"
              >
                <FileCheck2 class="mb-3 h-8 w-8 text-emerald-600 sm:mb-4 sm:h-9 sm:w-9" stroke-width={1.5} />
                <h3 class="text-lg font-bold text-slate-900">Normativa integrada</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-600">
                  ISO 13485, IEC 60601, INVIMA — documentos y requisitos enlazados al activo.
                </p>
              </div>

              <div
                use:scrollReveal
                class="rounded-2xl border border-slate-200/90 bg-gradient-to-br from-slate-900 to-brand-900 p-5 text-white shadow-lg sm:col-span-6 sm:rounded-3xl sm:p-6 sm:shadow-xl lg:col-span-4"
              >
                <LineChart class="mb-3 h-8 w-8 text-brand-200 sm:mb-4 sm:h-9 sm:w-9" stroke-width={1.5} />
                <h3 class="text-lg font-bold">Reporting ejecutivo</h3>
                <p class="mt-2 text-sm leading-relaxed text-brand-100/90">
                  KPIs listos para acreditación, mesas de riesgo y proveedores — exportables y comparables
                  en el tiempo.
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- Precios -->
        <section
          id="precios"
          class="relative mx-auto max-w-6xl scroll-mt-20 px-3 py-16 sm:scroll-mt-28 sm:px-6 sm:py-24 lg:scroll-mt-32 lg:px-10"
        >
          <div use:scrollReveal class="text-center">
            <p class="text-xs font-bold uppercase tracking-widest text-brand-600 sm:text-sm">Inversión</p>
            <h2 class="mt-2 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
              Planes para escalar con control
            </h2>
            <p class="mx-auto mt-3 max-w-2xl px-1 text-base text-slate-600 sm:mt-4 sm:text-lg">
              Transparencia en alcance. Onboarding guiado. Opciones Enterprise para redes y compliance
              estricto.
            </p>
          </div>

          <div class="mt-10 grid items-start gap-4 sm:mt-16 sm:gap-6 lg:grid-cols-3">
            {#each [
              {
                name: 'Esencial',
                price: 'Desde USD 199',
                period: '/ mes',
                desc: 'Clínicas que centralizan inventario, mantenimiento y documentación.',
                feats: ['Hasta 500 activos', '5 usuarios incluidos', 'Soporte email'],
                highlight: false,
              },
              {
                name: 'Profesional',
                price: 'Desde USD 449',
                period: '/ mes',
                desc: 'Multi-sede, auditorías frecuentes y equipos de ingeniería más exigentes.',
                feats: ['Activos ilimitados', 'Roles avanzados + API', 'Soporte prioritario'],
                highlight: true,
              },
              {
                name: 'Enterprise',
                price: 'A medida',
                period: '',
                desc: 'HIS/LIS, instancia dedicada, SLA contractual y customer success.',
                feats: ['Integraciones a medida', 'Ambientes segregados', 'Éxito del cliente dedicado'],
                highlight: false,
              },
            ] as p, i}
              <div
                use:scrollReveal
                class="relative flex flex-col overflow-hidden rounded-2xl border p-5 shadow-lg transition sm:rounded-3xl sm:p-8 sm:shadow-xl sm:hover:-translate-y-1 sm:hover:shadow-2xl {p.highlight
                  ? 'border-brand-400/80 bg-gradient-to-b from-brand-50 via-white to-white ring-2 ring-brand-500/30'
                  : 'border-slate-200/90 bg-white/95 hover:border-brand-200'}"
                style="transition-delay: {i * 80}ms"
              >
                {#if p.highlight}
                  <div
                    class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-brand-500 via-cyan-400 to-emerald-400"
                  ></div>
                  <span
                    class="absolute right-3 top-3 max-w-[42%] truncate rounded-full bg-gradient-to-r from-brand-600 to-cyan-500 px-2.5 py-1 text-[10px] font-bold text-white shadow-md sm:right-4 sm:top-4 sm:max-w-none sm:px-3 sm:text-xs"
                    >Recomendado</span
                  >
                {/if}
                <h3 class="text-lg font-black text-slate-900 sm:text-xl">{p.name}</h3>
                <p class="mt-2 text-sm leading-relaxed text-slate-600">{p.desc}</p>
                <p class="mt-8">
                  <span class="bg-gradient-to-r from-brand-800 to-brand-600 bg-clip-text text-2xl font-black text-transparent sm:text-3xl lg:text-4xl">{p.price}</span>
                  <span class="text-slate-500">{p.period}</span>
                </p>
                <ul class="mt-6 flex-1 space-y-2.5 text-sm font-medium text-slate-700 sm:mt-8 sm:space-y-3">
                  {#each p.feats as f}
                    <li class="flex gap-2">
                      <Check class="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" stroke-width={2.5} />
                      {f}
                    </li>
                  {/each}
                </ul>
                <a
                  href="#contacto"
                  class="mt-8 block min-h-[48px] w-full rounded-xl py-3 text-center text-sm font-bold transition sm:mt-10 sm:rounded-2xl sm:py-3.5 {p.highlight
                    ? 'bg-gradient-to-r from-brand-600 to-brand-500 text-white shadow-lg shadow-brand-600/30 hover:brightness-110'
                    : 'border-2 border-slate-200 bg-slate-50 text-slate-800 hover:border-brand-300 hover:bg-brand-50'}"
                  on:click={(e) => navToSection(e, '#contacto')}
                >
                  Solicitar información
                </a>
              </div>
            {/each}
          </div>
        </section>

        <!-- Contacto premium + mailto -->
        <section
          id="contacto"
          class="relative scroll-mt-20 overflow-hidden border-t border-slate-800/50 bg-slate-950 py-16 text-white sm:scroll-mt-28 sm:py-24 lg:scroll-mt-32"
        >
          <div
            class="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_120%,rgba(25,113,245,0.45),transparent_55%)]"
          ></div>
          <div
            class="pointer-events-none absolute left-0 top-0 h-full w-1/2 bg-gradient-to-r from-brand-600/10 to-transparent"
          ></div>

          <div class="relative mx-auto max-w-6xl px-3 sm:px-6 lg:px-10">
            <div use:scrollReveal class="grid gap-10 sm:gap-12 lg:grid-cols-2 lg:items-center">
              <div>
                <p class="text-xs font-bold uppercase tracking-widest text-cyan-300/90 sm:text-sm">Contacto</p>
                <h2 class="mt-2 text-3xl font-black leading-tight tracking-tight sm:mt-3 sm:text-4xl lg:text-5xl">
                  Solicita una demo o propuesta
                </h2>
                <p class="mt-4 max-w-lg text-base leading-relaxed text-slate-300 sm:mt-5 sm:text-lg">
                  Cuéntanos tu tipo de centro, número aproximado de activos y si operas en una o varias
                  sedes. Respondemos en <strong class="text-white">menos de 24 h hábiles</strong>.
                </p>
              </div>

              <div class="relative">
                <div
                  class="absolute -inset-px rounded-2xl bg-gradient-to-br from-brand-400 via-cyan-400 to-emerald-400 opacity-70 blur-sm sm:rounded-3xl"
                ></div>
                <div
                  class="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-900/90 p-0.5 shadow-2xl sm:rounded-3xl"
                >
                  <div class="rounded-[18px] bg-gradient-to-b from-slate-800/90 to-slate-950 p-5 sm:rounded-[22px] sm:p-8 lg:p-10">
                    <div class="flex flex-col items-center gap-5 text-center sm:flex-row sm:items-start sm:text-left">
                      <div
                        class="grid h-14 w-14 shrink-0 place-items-center rounded-2xl bg-gradient-to-br from-brand-500 to-cyan-500 shadow-lg shadow-brand-500/40 sm:h-16 sm:w-16"
                      >
                        <Mail class="h-7 w-7 text-white sm:h-8 sm:w-8" stroke-width={1.5} />
                      </div>
                      <div class="min-w-0 flex-1">
                        <p class="text-[10px] font-bold uppercase tracking-widest text-brand-200 sm:text-xs">
                          Email comercial
                        </p>
                        <a
                          class="mt-1 block break-all text-lg font-bold text-white transition hover:text-cyan-200 sm:text-xl lg:text-2xl"
                          href="mailto:contacto@bamesoft.app?subject=Solicitud%20de%20contacto%20%E2%80%94%20Bamesoft&body=Hola%20equipo%20Bamesoft%2C%0D%0A%0D%0ANombre%20y%20cargo%3A%0D%0A%0D%0ACentro%20%2F%20cl%C3%ADnica%3A%0D%0A%0D%0AActivos%20aproximados%3A%0D%0A%0D%0ANecesidad%20principal%3A%0D%0A"
                          >contacto@bamesoft.app</a
                        >
                        <p class="mt-3 text-xs leading-relaxed text-slate-400 sm:text-sm">
                          Se abrirá tu correo con un borrador listo. También puedes copiar la dirección.
                        </p>
                      </div>
                    </div>

                    <div class="mt-6 flex flex-col gap-3 sm:mt-8 sm:flex-row">
                      <a
                        href="mailto:contacto@bamesoft.app?subject=Solicitud%20de%20contacto%20%E2%80%94%20Bamesoft&body=Hola%20equipo%20Bamesoft%2C%0D%0A%0D%0ANombre%20y%20cargo%3A%0D%0A%0D%0ACentro%20%2F%20cl%C3%ADnica%3A%0D%0A%0D%0AActivos%20aproximados%3A%0D%0A%0D%0ANecesidad%20principal%3A%0D%0A"
                        class="inline-flex min-h-[48px] flex-1 items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-brand-500 to-cyan-500 px-5 py-3.5 text-center text-sm font-bold text-white shadow-lg transition active:scale-[0.99] sm:px-6 sm:py-4 hover:brightness-110"
                      >
                        <Mail class="h-4 w-4 shrink-0" />
                        <span class="leading-tight">Solicitar contacto por email</span>
                      </a>
                      <a
                        href="/login"
                        class="inline-flex min-h-[48px] flex-1 items-center justify-center gap-2 rounded-2xl border border-white/25 bg-white/10 px-5 py-3.5 text-sm font-bold text-white backdrop-blur transition hover:bg-white/15 sm:px-6 sm:py-4"
                      >
                        Ya soy cliente
                        <ArrowRight class="h-4 w-4 shrink-0" />
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer
        class="border-t border-slate-200 bg-slate-100/90 px-3 py-8 text-center text-[11px] font-medium leading-relaxed text-slate-500 sm:py-10 sm:text-xs"
      >
        <span class="font-bold text-slate-800">Bamesoft Solutions</span>
        · ISO 13485 · IEC 60601 · INVIMA
        <span class="mx-2">·</span>
        <a class="text-slate-600 underline-offset-2 hover:text-brand-700 hover:underline" href="/terminos"
          >Términos</a
        >
        ·
        <a
          class="text-slate-600 underline-offset-2 hover:text-brand-700 hover:underline"
          href="/privacidad">Privacidad</a
        >
      </footer>
    </div>
  </div>
</div>

<style>
  .landing-root :global(section[id]) {
    scroll-margin-top: 5.25rem;
  }
  @media (min-width: 640px) {
    .landing-root :global(section[id]) {
      scroll-margin-top: 5.75rem;
    }
  }
  @media (min-width: 1024px) {
    .landing-root :global(section[id]) {
      scroll-margin-top: 6rem;
    }
  }

  /* Subrayado enlaces header escritorio */
  @media (min-width: 768px) {
    .nav-pill-desk::after {
      content: '';
      position: absolute;
      left: 50%;
      bottom: 4px;
      width: 0;
      height: 2px;
      border-radius: 2px;
      background: linear-gradient(90deg, #1971f5, #06b6d4);
      transform: translateX(-50%);
      transition: width 0.35s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .nav-pill-desk:hover::after {
      width: 55%;
    }
  }

  .logo-mark {
    background: linear-gradient(135deg, #2f8eff 0%, #1971f5 35%, #06b6d4 70%, #10b981 100%);
    background-size: 200% 200%;
    animation: logo-gradient 8s ease infinite;
  }
  @keyframes logo-gradient {
    0%,
    100% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
  }

  .logo-wordmark {
    background: linear-gradient(90deg, #0f172a 0%, #1971f5 45%, #0891b2 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }

  .bm-hero-title {
    background: linear-gradient(120deg, #0f172a 0%, #1971f5 30%, #2f8eff 50%, #06b6d4 75%, #0f172a 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    -webkit-text-fill-color: transparent;
    animation: hero-shimmer 12s ease-in-out infinite;
  }
  @keyframes hero-shimmer {
    0% {
      background-position: 0% 50%;
    }
    50% {
      background-position: 100% 50%;
    }
    100% {
      background-position: 0% 50%;
    }
  }

  @keyframes cta-shine {
    0% {
      background-position: 0% 50%;
    }
    100% {
      background-position: 200% 50%;
    }
  }
  .animate-cta-shine {
    background-size: 200% 100%;
    animation: cta-shine 4s ease infinite;
  }

  /* Scroll reveal */
  :global(.sr-base) {
    opacity: 0;
    transform: translateY(40px) scale(0.98);
    filter: blur(4px);
    transition:
      opacity 0.85s cubic-bezier(0.22, 1, 0.36, 1),
      transform 0.9s cubic-bezier(0.22, 1, 0.36, 1),
      filter 0.7s ease;
  }
  :global(.sr-base.sr-in) {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }

  .stat-card {
    transition:
      transform 0.5s cubic-bezier(0.22, 1, 0.36, 1),
      box-shadow 0.5s ease;
  }
  @media (hover: hover) and (pointer: fine) {
    .stat-card:hover {
      transform: translateY(-4px);
    }
  }
</style>
