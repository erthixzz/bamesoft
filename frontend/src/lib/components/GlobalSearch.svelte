<script lang="ts">
  /** Buscador global · estilo Bamesoft.
   *  Busca equipos, casos, usuarios, unidades y compañías (scoped por rol y
   *  clínica en el backend) y navega al módulo correspondiente.
   *  Atajo: Ctrl/Cmd + K. En móvil se abre como panel superpuesto. */
  import { onMount, tick } from 'svelte';
  import { goto } from '$app/navigation';
  import GlobalSearchResults from '$lib/components/GlobalSearchResults.svelte';
  import { searchApi } from '$lib/modules/search/api';
  import type { SearchResult, SearchType } from '$lib/modules/search/types';
  import { Search, QrCode, Wrench, User, Building2, Landmark, X } from 'lucide-svelte';

  let q = '';
  let results: SearchResult[] = [];
  let open = false;
  let mobileOpen = false;
  let loading = false;
  let active = -1;
  let inputEl: HTMLInputElement;
  let mobileInputEl: HTMLInputElement;
  let timer: ReturnType<typeof setTimeout> | null = null;
  let seq = 0; // descarta respuestas fuera de orden

  const TYPE_META: Record<SearchType, { label: string; icon: typeof Search; tone: string }> = {
    equipment: { label: 'Equipos', icon: QrCode, tone: 'bg-brand-50 text-brand-600' },
    case: { label: 'Casos', icon: Wrench, tone: 'bg-amber-50 text-amber-600' },
    user: { label: 'Usuarios', icon: User, tone: 'bg-violet-50 text-violet-600' },
    sector: { label: 'Unidades de servicio', icon: Building2, tone: 'bg-cyan-50 text-cyan-600' },
    clinic: { label: 'Compañías', icon: Landmark, tone: 'bg-emerald-50 text-emerald-600' },
  };
  const TYPE_ORDER: SearchType[] = ['equipment', 'case', 'user', 'sector', 'clinic'];

  // Lista plana ordenada por tipo (para navegación con teclado) + grupos.
  $: ordered = TYPE_ORDER.flatMap((t) => results.filter((r) => r.type === t));
  $: groups = TYPE_ORDER.map((t) => ({
    type: t,
    ...TYPE_META[t],
    items: results.filter((r) => r.type === t),
  })).filter((g) => g.items.length > 0);

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

  // Caché en memoria por término: los repetidos (o al borrar letras) vuelven
  // instantáneos sin tocar la red.
  const CACHE_MAX = 80;
  const cache = new Map<string, SearchResult[]>();

  function cachePut(term: string, res: SearchResult[]) {
    if (cache.size >= CACHE_MAX) {
      const oldest = cache.keys().next().value;
      if (oldest !== undefined) cache.delete(oldest);
    }
    cache.set(term, res);
  }

  function onInput() {
    if (timer) clearTimeout(timer);
    const term = q.trim();
    if (term.length < 2) {
      results = [];
      open = false;
      loading = false;
      return;
    }

    // Acierto de caché: respuesta inmediata, sin red ni debounce.
    const hit = cache.get(term.toLowerCase());
    if (hit) {
      results = hit;
      open = true;
      active = -1;
      loading = false;
      return;
    }

    loading = true;
    timer = setTimeout(async () => {
      const mySeq = ++seq;
      try {
        const res = await searchApi.global(term);
        if (mySeq !== seq) return; // llegó tarde: ya hay otra búsqueda en curso
        cachePut(term.toLowerCase(), res.results);
        results = res.results;
        open = true;
        active = -1;
      } catch {
        if (mySeq === seq) results = [];
      } finally {
        if (mySeq === seq) loading = false;
      }
    }, 200);
  }

  function close() {
    open = false;
    mobileOpen = false;
    active = -1;
  }

  function pick(r: SearchResult) {
    close();
    q = '';
    results = [];
    goto(hrefFor(r));
  }

  function onKey(e: KeyboardEvent) {
    if (ordered.length === 0) {
      if (e.key === 'Escape') close();
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      active = Math.min(active + 1, ordered.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      active = Math.max(active - 1, 0);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      pick(ordered[Math.max(active, 0)]);
    } else if (e.key === 'Escape') {
      close();
    }
  }

  async function openMobile() {
    mobileOpen = true;
    await tick();
    mobileInputEl?.focus();
  }

  onMount(() => {
    const shortcut = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (window.innerWidth < 768) openMobile();
        else inputEl?.focus();
      }
    };
    window.addEventListener('keydown', shortcut);
    return () => window.removeEventListener('keydown', shortcut);
  });
</script>

<!-- Desktop: input inline -->
<div class="relative hidden w-full max-w-md md:block">
  <Search class="pointer-events-none absolute left-3 top-1/2 z-10 h-4 w-4 -translate-y-1/2 text-slate-400" />
  <input
    bind:this={inputEl}
    bind:value={q}
    on:input={onInput}
    on:keydown={onKey}
    on:focus={() => q.trim().length >= 2 && results.length && (open = true)}
    class="input pl-9 pr-16"
    placeholder="Buscar equipos, casos, usuarios…"
    aria-label="Búsqueda global"
  />
  <kbd class="pointer-events-none absolute right-3 top-1/2 hidden -translate-y-1/2 rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] font-semibold text-slate-400 lg:block">
    Ctrl K
  </kbd>

  {#if open}
    <button type="button" class="fixed inset-0 z-40 cursor-default" aria-label="Cerrar búsqueda" on:click={close}></button>
    <div class="absolute left-0 right-0 top-full z-50 mt-2 max-h-[70vh] overflow-y-auto rounded-xl border border-slate-200 bg-white pb-2 shadow-2xl shadow-slate-900/15">
      <GlobalSearchResults
        {groups}
        {ordered}
        {active}
        {loading}
        {q}
        on:pick={(e) => pick(e.detail)}
        on:hover={(e) => (active = e.detail)}
      />
    </div>
  {/if}
</div>

<!-- Móvil: botón + panel superpuesto -->
<button
  type="button"
  class="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 md:hidden"
  on:click={openMobile}
  aria-label="Buscar"
>
  <Search class="h-5 w-5" />
</button>

{#if mobileOpen}
  <div class="fixed inset-0 z-50 bg-slate-900/40 md:hidden" role="dialog" aria-modal="true">
    <div class="flex h-full flex-col bg-white">
      <div class="flex items-center gap-2 border-b border-slate-200 p-3">
        <Search class="h-4 w-4 shrink-0 text-slate-400" />
        <input
          bind:this={mobileInputEl}
          bind:value={q}
          on:input={onInput}
          on:keydown={onKey}
          class="min-w-0 flex-1 border-0 bg-transparent text-sm outline-none placeholder:text-slate-400"
          placeholder="Buscar en toda la app…"
          aria-label="Búsqueda global"
        />
        <button type="button" class="grid h-8 w-8 place-items-center rounded-lg text-slate-400 hover:bg-slate-100" on:click={close} aria-label="Cerrar">
          <X class="h-4 w-4" />
        </button>
      </div>
      <div class="flex-1 overflow-y-auto pb-4">
        {#if q.trim().length < 2}
          <p class="px-4 py-8 text-center text-sm text-slate-400">Escribe al menos 2 caracteres…</p>
        {:else}
          <GlobalSearchResults
            {groups}
            {ordered}
            {active}
            {loading}
            {q}
            on:pick={(e) => pick(e.detail)}
            on:hover={(e) => (active = e.detail)}
          />
        {/if}
      </div>
    </div>
  </div>
{/if}
