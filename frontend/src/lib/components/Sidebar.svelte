<script lang="ts">
  import { page } from '$app/stores';
  import { afterNavigate } from '$app/navigation';
  import { sidebarOpen, closeSidebar } from '$lib/stores/sidebar';
  import { fly, fade } from 'svelte/transition';
  import { tooltip } from '$lib/actions/tooltip';
  import CaseLegendModal from '$lib/modules/cases/components/CaseLegendModal.svelte';
  import { role } from '$lib/stores/auth';
  import { isOneOf } from '$lib/utils/permissions';
  import type { UserRole } from '$lib/api/types';
  import {
    LayoutDashboard,
    Wrench,
    QrCode,
    AlertTriangle,
    FileText,
    BookOpen,
    BarChart3,
    Users,
    Settings,
    HelpCircle,
    X,
  } from 'lucide-svelte';

  let legendOpen = false;

  // `roles` ausente = visible para todos. El operario (service) y el cliente
  // ven solo lo necesario para reportar y consultar.
  const items: { href: string; label: string; icon: typeof Wrench; roles?: UserRole[] }[] = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, roles: ['admin', 'engineer', 'support'] },
    { href: '/equipment', label: 'Equipos', icon: QrCode },
    { href: '/cases', label: 'Casos', icon: Wrench },
    { href: '/alerts', label: 'Alertas', icon: AlertTriangle },
    { href: '/documents', label: 'Documentos', icon: FileText },
    { href: '/standards', label: 'Normas', icon: BookOpen, roles: ['admin', 'engineer'] },
    { href: '/reports', label: 'Reportes', icon: BarChart3, roles: ['admin', 'engineer', 'support'] },
    { href: '/users', label: 'Usuarios', icon: Users, roles: ['admin'] },
    { href: '/settings', label: 'Ajustes', icon: Settings },
  ];

  $: visibleItems = items.filter((i) => !i.roles || isOneOf($role, i.roles));
  $: current = $page.url.pathname;

  // Cerrar el drawer al navegar (móvil)
  afterNavigate(() => closeSidebar());
</script>

<!-- Sidebar fijo en desktop (md+): pegado a la pantalla al hacer scroll -->
<aside class="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
  <div class="flex h-16 shrink-0 items-center gap-2 px-5">
    <div class="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 font-bold text-white">B</div>
    <div>
      <p class="text-sm font-semibold leading-tight">Bamesoft</p>
      <p class="text-xs text-slate-500">Biomedical Suite</p>
    </div>
  </div>
  <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-2">
    {#each visibleItems as item}
      {@const active = current === item.href || current.startsWith(item.href + '/')}
      <a
        href={item.href}
        class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition
               {active ? 'bg-brand-50 text-brand-700' : 'text-slate-700 hover:bg-slate-100'}"
      >
        <svelte:component this={item.icon} class="h-4 w-4" />
        {item.label}
      </a>
    {/each}
  </nav>

  <!-- Footer: branding + ayuda -->
  <div class="shrink-0 border-t border-slate-100 p-3">
    <div class="flex items-center gap-2.5 rounded-xl bg-slate-50 p-2.5">
      <div class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 text-sm font-bold text-white shadow-sm">B</div>
      <div class="min-w-0 flex-1">
        <p class="truncate text-xs font-semibold text-slate-700">Bamesoft Solutions</p>
        <p class="truncate text-[10px] text-slate-400">Ingeniería biomédica</p>
      </div>
      <button
        type="button"
        class="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-600"
        on:click={() => (legendOpen = true)}
        use:tooltip={{ text: 'Guía: estados y prioridades', placement: 'top' }}
        aria-label="Ayuda: estados y prioridades de casos"
      >
        <HelpCircle class="h-5 w-5" />
      </button>
    </div>
  </div>
</aside>

<!-- Drawer móvil (md:hidden) -->
{#if $sidebarOpen}
  <div
    class="fixed inset-0 z-40 bg-slate-900/40 md:hidden"
    transition:fade={{ duration: 150 }}
    on:click={closeSidebar}
    on:keydown={(e) => e.key === 'Escape' && closeSidebar()}
    role="button"
    tabindex="-1"
    aria-label="Cerrar menú"
  ></div>

  <aside
    class="fixed left-0 top-0 z-50 flex h-screen w-72 max-w-[80vw] flex-col border-r border-slate-200 bg-white shadow-2xl md:hidden"
    transition:fly={{ x: -288, duration: 220 }}
  >
    <div class="flex h-16 shrink-0 items-center justify-between gap-2 px-5">
      <div class="flex items-center gap-2">
        <div class="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 font-bold text-white">B</div>
        <div>
          <p class="text-sm font-semibold leading-tight">Bamesoft</p>
          <p class="text-xs text-slate-500">Biomedical Suite</p>
        </div>
      </div>
      <button class="text-slate-400 hover:text-slate-700" on:click={closeSidebar} aria-label="Cerrar">
        <X class="h-5 w-5" />
      </button>
    </div>
    <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-2">
      {#each items as item}
        {@const active = current === item.href || current.startsWith(item.href + '/')}
        <a
          href={item.href}
          class="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition
                 {active ? 'bg-brand-50 text-brand-700' : 'text-slate-700 hover:bg-slate-100'}"
        >
          <svelte:component this={item.icon} class="h-4 w-4" />
          {item.label}
        </a>
      {/each}
    </nav>

    <!-- Footer: branding + ayuda -->
    <div class="shrink-0 border-t border-slate-100 p-3">
      <div class="flex items-center gap-2.5 rounded-xl bg-slate-50 p-2.5">
        <div class="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 text-sm font-bold text-white shadow-sm">B</div>
        <div class="min-w-0 flex-1">
          <p class="truncate text-xs font-semibold text-slate-700">Bamesoft Solutions</p>
          <p class="truncate text-[10px] text-slate-400">Ingeniería biomédica</p>
        </div>
        <button
          type="button"
          class="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-slate-400 transition hover:bg-brand-50 hover:text-brand-600"
          on:click={() => (legendOpen = true)}
          aria-label="Ayuda: estados y prioridades de casos"
        >
          <HelpCircle class="h-5 w-5" />
        </button>
      </div>
    </div>
  </aside>
{/if}

<CaseLegendModal bind:open={legendOpen} />
