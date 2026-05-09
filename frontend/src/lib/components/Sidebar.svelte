<script lang="ts">
  import { page } from '$app/stores';
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
</script>

<aside class="hidden w-64 shrink-0 border-r border-slate-200 bg-white md:block">
  <div class="flex h-16 items-center gap-2 px-5">
    <div class="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 font-bold text-white">B</div>
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
