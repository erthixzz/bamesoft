<script lang="ts">
  /** Asistente IA de Bamesoft — mini pop-up de chat futurista.
   *  FAB flotante con el monograma SVG y estrellas orbitando (tipo aurora
   *  boreal). Al abrir, un chat para preguntar por equipos, casos, usuarios…
   *  (usa el buscador global, scoped por rol/clínica en el backend) y navega
   *  al módulo correspondiente. */
  import { tick } from 'svelte';
  import type { ComponentType } from 'svelte';
  import { goto } from '$app/navigation';
  import { searchApi } from '$lib/modules/search/api';
  import type { SearchResult, SearchType } from '$lib/modules/search/types';
  import { role } from '$lib/stores/auth';
  import { permissions, myFeatures, hasCapIn, featureOn, type Capability } from '$lib/utils/permissions';
  import BrandMark from '$lib/components/BrandMark.svelte';
  import {
    Sparkles,
    Send,
    X,
    QrCode,
    Wrench,
    User,
    Building2,
    Landmark,
    BarChart3,
    CornerDownLeft,
  } from 'lucide-svelte';

  type Msg = { role: 'bot' | 'user'; text?: string; results?: SearchResult[] };

  let open = false;
  let loading = false;
  let input = '';
  let inputEl: HTMLInputElement;
  let scrollEl: HTMLDivElement;

  const GREETING: Msg = {
    role: 'bot',
    text: '¡Hola! Soy tu asistente Bamesoft. Pregúntame por un equipo, caso, usuario o unidad y te llevo directo. ✨',
  };
  let messages: Msg[] = [GREETING];

  const TYPE_META: Record<SearchType, { icon: ComponentType; tone: string }> = {
    equipment: { icon: QrCode, tone: 'bg-brand-50 text-brand-600' },
    case: { icon: Wrench, tone: 'bg-amber-50 text-amber-600' },
    user: { icon: User, tone: 'bg-violet-50 text-violet-600' },
    sector: { icon: Building2, tone: 'bg-cyan-50 text-cyan-600' },
    clinic: { icon: Landmark, tone: 'bg-emerald-50 text-emerald-600' },
  };

  // Accesos rápidos, filtrados por rol (cap) y módulos de la compañía (feature).
  const QUICK: { label: string; href: string; icon: ComponentType; cap?: Capability; feature?: string }[] = [
    { label: 'Equipos', href: '/equipment', icon: QrCode, cap: 'equipment', feature: 'equipment' },
    { label: 'Casos', href: '/cases', icon: Wrench, cap: 'report', feature: 'cases' },
    { label: 'Reportes', href: '/reports', icon: BarChart3, cap: 'reports', feature: 'reports' },
  ];
  $: quick = QUICK.filter(
    (q) =>
      (!q.cap || hasCapIn($permissions, $role, q.cap)) && (!q.feature || featureOn($myFeatures, q.feature)),
  );

  function hrefFor(r: SearchResult): string {
    switch (r.type) {
      case 'equipment':
        return `/equipment/${r.slug ?? r.id}`;
      case 'case':
        return `/cases/${r.slug ?? r.id}`;
      case 'user':
        return `/users?q=${encodeURIComponent(r.subtitle ?? r.title)}`;
      case 'sector':
        return '/sectors';
      case 'clinic':
        return '/clinics';
    }
  }

  async function scrollDown() {
    await tick();
    scrollEl?.scrollTo({ top: scrollEl.scrollHeight, behavior: 'smooth' });
  }

  async function toggle() {
    open = !open;
    if (open) {
      await tick();
      inputEl?.focus();
      scrollDown();
    }
  }

  function pick(r: SearchResult) {
    open = false;
    goto(hrefFor(r));
  }

  function goQuick(href: string) {
    open = false;
    goto(href);
  }

  async function send() {
    const q = input.trim();
    if (!q || loading) return;
    messages = [...messages, { role: 'user', text: q }];
    input = '';
    loading = true;
    scrollDown();
    try {
      const res = await searchApi.global(q);
      if (res.results.length) {
        messages = [
          ...messages,
          {
            role: 'bot',
            text: `Encontré ${res.total} resultado${res.total === 1 ? '' : 's'} para «${q}». Toca para abrir:`,
            results: res.results.slice(0, 8),
          },
        ];
      } else {
        messages = [
          ...messages,
          {
            role: 'bot',
            text: `No encontré nada para «${q}». Prueba con el código del equipo, el nombre de un caso o un usuario.`,
          },
        ];
      }
    } catch {
      messages = [
        ...messages,
        { role: 'bot', text: 'Ups, no pude consultar ahora mismo. Inténtalo de nuevo en un momento.' },
      ];
    } finally {
      loading = false;
      scrollDown();
    }
  }

  function onKey(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    } else if (e.key === 'Escape') {
      open = false;
    }
  }
</script>

<!-- Panel de chat -->
{#if open}
  <button
    type="button"
    class="fixed inset-0 z-40 cursor-default bg-slate-900/20 backdrop-blur-[1px] sm:bg-transparent sm:backdrop-blur-0"
    aria-label="Cerrar asistente"
    on:click={() => (open = false)}
  ></button>

  <div
    class="animate-fade-up fixed inset-x-3 bottom-3 top-20 z-50 flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl shadow-slate-900/20 sm:inset-auto sm:bottom-24 sm:right-6 sm:top-auto sm:h-[560px] sm:w-[380px]"
    role="dialog"
    aria-modal="true"
    aria-label="Asistente Bamesoft"
  >
    <!-- Cabecera con logo + estrellas orbitando -->
    <div class="relative overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-cyan-600 px-4 py-3.5 text-white">
      <div class="bg-grid pointer-events-none absolute inset-0 opacity-20"></div>
      <div class="relative flex items-center gap-3">
        <div class="relative grid h-11 w-11 shrink-0 place-items-center">
          <span aria-hidden="true" class="absolute -inset-1 animate-orbit">
            <span class="absolute left-1/2 top-0 h-1.5 w-1.5 -translate-x-1/2 rounded-full bg-cyan-200 shadow-[0_0_8px_2px_rgba(165,243,252,0.9)]"></span>
            <span class="absolute bottom-0 right-1 h-1 w-1 rounded-full bg-emerald-200 shadow-[0_0_7px_2px_rgba(167,243,208,0.9)]"></span>
          </span>
          <span aria-hidden="true" class="absolute -inset-0.5 animate-orbit-rev">
            <span class="absolute right-0 top-1/2 h-1 w-1 -translate-y-1/2 rounded-full bg-violet-200 shadow-[0_0_7px_2px_rgba(221,214,254,0.9)]"></span>
          </span>
          <span class="relative grid h-9 w-9 place-items-center rounded-xl bg-white/95 shadow-inner">
            <BrandMark size={26} />
          </span>
        </div>
        <div class="min-w-0 flex-1">
          <p class="flex items-center gap-1.5 text-sm font-bold leading-tight">
            Asistente IA
            <Sparkles class="h-3.5 w-3.5 text-cyan-200" />
          </p>
          <p class="truncate text-[11px] text-white/70">Bamesoft · biomédico inteligente</p>
        </div>
        <button
          type="button"
          class="grid h-8 w-8 place-items-center rounded-lg text-white/80 transition hover:bg-white/15 hover:text-white"
          on:click={() => (open = false)}
          aria-label="Cerrar"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Mensajes -->
    <div bind:this={scrollEl} class="flex-1 space-y-3 overflow-y-auto bg-slate-50/60 p-3">
      {#each messages as m}
        {#if m.role === 'user'}
          <div class="flex justify-end">
            <p class="max-w-[85%] rounded-2xl rounded-br-md bg-gradient-to-br from-brand-600 to-brand-500 px-3.5 py-2 text-sm text-white shadow-sm">
              {m.text}
            </p>
          </div>
        {:else}
          <div class="flex flex-col gap-2">
            {#if m.text}
              <div class="flex items-end gap-2">
                <span class="grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-white shadow-sm ring-1 ring-slate-200">
                  <BrandMark size={16} />
                </span>
                <p class="max-w-[85%] rounded-2xl rounded-bl-md border border-slate-200 bg-white px-3.5 py-2 text-sm text-slate-700 shadow-sm">
                  {m.text}
                </p>
              </div>
            {/if}
            {#if m.results && m.results.length}
              <div class="ml-8 space-y-1.5">
                {#each m.results as r (r.type + r.id)}
                  <button
                    type="button"
                    class="flex w-full items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-2.5 py-2 text-left shadow-sm transition hover:border-brand-300 hover:bg-brand-50/50"
                    on:click={() => pick(r)}
                  >
                    <span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg {TYPE_META[r.type].tone}">
                      <svelte:component this={TYPE_META[r.type].icon} class="h-4 w-4" />
                    </span>
                    <span class="min-w-0 flex-1">
                      <span class="block truncate text-sm font-medium text-slate-800">{r.title}</span>
                      {#if r.subtitle}
                        <span class="block truncate text-xs text-slate-400">{r.subtitle}</span>
                      {/if}
                    </span>
                    <CornerDownLeft class="h-3.5 w-3.5 shrink-0 text-slate-300" />
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      {/each}

      {#if loading}
        <div class="flex items-end gap-2">
          <span class="grid h-6 w-6 shrink-0 place-items-center rounded-lg bg-white shadow-sm ring-1 ring-slate-200">
            <BrandMark size={16} />
          </span>
          <p class="rounded-2xl rounded-bl-md border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-400 shadow-sm">
            <span class="inline-flex gap-1">
              <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300" style="animation-delay:0ms"></span>
              <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300" style="animation-delay:120ms"></span>
              <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-300" style="animation-delay:240ms"></span>
            </span>
          </p>
        </div>
      {/if}

      <!-- Accesos rápidos (solo tras el saludo inicial) -->
      {#if messages.length === 1 && quick.length}
        <div class="ml-8 flex flex-wrap gap-1.5 pt-1">
          {#each quick as q}
            <button
              type="button"
              class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 shadow-sm transition hover:border-brand-300 hover:text-brand-700"
              on:click={() => goQuick(q.href)}
            >
              <svelte:component this={q.icon} class="h-3.5 w-3.5" />
              {q.label}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Entrada -->
    <div class="border-t border-slate-200 bg-white p-2.5">
      <div class="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-3 py-1.5 transition focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/30">
        <input
          bind:this={inputEl}
          bind:value={input}
          on:keydown={onKey}
          class="min-w-0 flex-1 border-0 bg-transparent py-1 text-sm text-slate-800 outline-none placeholder:text-slate-400"
          placeholder="Pregunta por un equipo, caso…"
          aria-label="Escribe tu pregunta"
        />
        <button
          type="button"
          class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-brand-500 text-white shadow-sm transition hover:from-brand-700 hover:to-brand-600 disabled:opacity-40"
          on:click={send}
          disabled={!input.trim() || loading}
          aria-label="Enviar"
        >
          <Send class="h-4 w-4" />
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- FAB con logo + estrellas orbitando (aurora) -->
{#if !open}
  <button
    type="button"
    class="group fixed bottom-5 right-5 z-40 grid h-16 w-16 place-items-center sm:bottom-6 sm:right-6"
    on:click={toggle}
    aria-label="Abrir asistente IA"
  >
    <!-- Halo aurora -->
    <span
      aria-hidden="true"
      class="animate-gradient absolute -inset-2 rounded-full bg-gradient-to-tr from-brand-500/50 via-cyan-400/50 to-emerald-400/50 blur-lg"
    ></span>
    <!-- Estrellas orbitando -->
    <span aria-hidden="true" class="absolute -inset-1.5 animate-orbit">
      <span class="absolute left-1/2 top-0 h-2 w-2 -translate-x-1/2 rounded-full bg-cyan-300 shadow-[0_0_10px_3px_rgba(103,232,249,0.85)]"></span>
      <span class="absolute bottom-1 right-0 h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_9px_2px_rgba(110,231,183,0.85)]"></span>
    </span>
    <span aria-hidden="true" class="absolute -inset-2 animate-orbit-rev">
      <span class="absolute right-0 top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-violet-300 shadow-[0_0_9px_2px_rgba(196,181,253,0.85)]"></span>
      <span class="absolute bottom-0 left-1/4 h-1 w-1 rounded-full bg-sky-200 shadow-[0_0_8px_2px_rgba(186,230,253,0.85)]"></span>
    </span>
    <!-- Núcleo con el monograma -->
    <span
      class="relative grid h-14 w-14 place-items-center rounded-full bg-white shadow-lg shadow-brand-900/20 ring-1 ring-slate-900/5 transition duration-200 group-hover:scale-105 group-active:scale-95"
    >
      <BrandMark size={34} />
    </span>
  </button>
{/if}
