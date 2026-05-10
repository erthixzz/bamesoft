<script lang="ts">
  import { page } from '$app/stores';
  import { afterNavigate } from '$app/navigation';
  import { sidebarOpen, closeSidebar } from '$lib/stores/sidebar';
  import { fly, fade } from 'svelte/transition';
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
    X,
  } from 'lucide-svelte';

  const items = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/equipment', label: 'Equipos', icon: QrCode },
    { href: '/cases', label: 'Casos', icon: Wrench },
    { href: '/alerts', label: 'Alertas', icon: AlertTriangle },
    { href: '/documents', label: 'Documentos', icon: FileText },
    { href: '/standards', label: 'Normas', icon: BookOpen },
    { href: '/reports', label: 'Reportes', icon: BarChart3 },
    { href: '/users', label: 'Usuarios', icon: Users },
    { href: '/settings', label: 'Ajustes', icon: Settings },
  ];

  $: current = $page.url.pathname;

  // Cerrar el drawer al navegar (móvil)
  afterNavigate(() => closeSidebar());
</script>

<!-- Sidebar fijo en desktop (md+) -->
<aside class="hidden w-64 shrink-0 border-r border-slate-200 bg-white md:block">
  <div class="flex h-16 items-center gap-2 px-5">
    <div class="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 font-bold text-white">B</div>
    <div>
      <p class="text-sm font-semibold leading-tight">Bamesoft</p>
      <p class="text-xs text-slate-500">Biomedical Suite</p>
    </div>
  </div>
  <nav class="space-y-1 px-3 py-2">
    {#each items as item}
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
    class="fixed left-0 top-0 z-50 h-screen w-72 max-w-[80vw] border-r border-slate-200 bg-white shadow-2xl md:hidden"
    transition:fly={{ x: -288, duration: 220 }}
  >
    <div class="flex h-16 items-center justify-between gap-2 px-5">
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
    <nav class="space-y-1 px-3 py-2">
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
  </aside>
{/if}
