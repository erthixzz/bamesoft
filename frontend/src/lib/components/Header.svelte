<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { profile, logout } from '$lib/stores/auth';
  import { pageTitle } from '$lib/stores/page';
  import { toggleSidebar } from '$lib/stores/sidebar';
  import GlobalSearch from '$lib/components/GlobalSearch.svelte';
  import ClinicSwitchModal from '$lib/modules/clinics/components/ClinicSwitchModal.svelte';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { tooltip } from '$lib/actions/tooltip';
  import { Building2, LogOut, Menu, ArrowLeft, ChevronRight, ChevronDown } from 'lucide-svelte';

  let clinicSwitchOpen = false;

  // Etiquetas legibles por segmento de ruta para el breadcrumb.
  const LABELS: Record<string, string> = {
    dashboard: 'Dashboard',
    equipment: 'Equipos',
    cases: 'Casos',
    alerts: 'Alertas',
    documents: 'Documentos',
    standards: 'Normas',
    reports: 'Reportes',
    users: 'Usuarios',
    settings: 'Ajustes',
    new: 'Nuevo',
    scan: 'Escanear QR',
    'hoja-de-vida': 'Hoja de vida',
  };

  const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

  function pretty(seg: string): string {
    if (UUID_RE.test(seg)) return 'Detalle';
    return seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' ');
  }

  // Breadcrumb: el último segmento usa el título de página (más descriptivo).
  $: crumbs = (() => {
    const segs = $page.url.pathname.split('/').filter(Boolean);
    let path = '';
    return segs.map((seg, i) => {
      path += '/' + seg;
      const isLast = i === segs.length - 1;
      const label = isLast ? ($pageTitle || LABELS[seg] || pretty(seg)) : LABELS[seg] || pretty(seg);
      return { path, label };
    });
  })();

  $: parentPath = crumbs.length > 1 ? crumbs[crumbs.length - 2].path : null;

  function goBack() {
    if (parentPath) goto(parentPath);
  }
</script>

<header class="flex h-16 items-center justify-between gap-2 border-b border-slate-200 bg-white px-3 sm:px-6">
  <div class="flex min-w-0 items-center gap-2 sm:gap-3">
    <button
      class="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-slate-500 hover:bg-slate-100 md:hidden"
      on:click={toggleSidebar}
      use:tooltip={{ text: 'Menú', placement: 'bottom' }}
      aria-label="Abrir menú"
    >
      <Menu class="h-5 w-5" />
    </button>

    {#if parentPath}
      <button
        class="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-slate-200 text-slate-600 transition hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700"
        on:click={goBack}
        use:tooltip={{ text: 'Volver', placement: 'bottom' }}
        aria-label="Volver"
      >
        <ArrowLeft class="h-4 w-4" />
      </button>
    {/if}

    <!-- Breadcrumb (desktop) -->
    <nav class="hidden min-w-0 items-center gap-1.5 sm:flex" aria-label="Ruta de navegación">
      {#each crumbs as c, i}
        {#if i > 0}
          <ChevronRight class="h-3.5 w-3.5 shrink-0 text-slate-300" />
        {/if}
        {#if i < crumbs.length - 1}
          <a href={c.path} class="shrink-0 text-sm text-slate-500 transition hover:text-brand-700">{c.label}</a>
        {:else}
          <span class="min-w-0 truncate text-sm font-semibold text-slate-900">{c.label}</span>
        {/if}
      {/each}
    </nav>

    <!-- Título (móvil) -->
    <h1 class="truncate text-sm font-semibold text-slate-900 sm:hidden">{$pageTitle}</h1>
  </div>

  <!-- Buscador global (centro en desktop, icono en móvil) -->
  <div class="flex flex-1 items-center justify-end px-1 md:justify-center md:px-3">
    <GlobalSearch />
  </div>

  <div class="flex shrink-0 items-center gap-2 sm:gap-3">
    {#if $profile?.role === 'admin'}
      <!-- Super admin: clic para cambiar de compañía activa -->
      <button
        type="button"
        class="hidden items-center gap-2 rounded-full border border-brand-200/80 bg-gradient-to-r from-brand-50 to-cyan-50 py-1 pl-1.5 pr-2.5 shadow-sm transition hover:border-brand-400 hover:shadow md:flex"
        on:click={() => (clinicSwitchOpen = true)}
        use:tooltip={{ text: 'Cambiar de compañía', placement: 'bottom' }}
      >
        <span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-600 to-cyan-500 text-white shadow-sm">
          <Building2 class="h-3.5 w-3.5" />
        </span>
        <span class="max-w-[180px] truncate text-sm font-semibold text-brand-800">
          {$profile.clinic_name ?? 'Elegir compañía'}
        </span>
        <ChevronDown class="h-3.5 w-3.5 shrink-0 text-brand-400" />
      </button>
    {:else if $profile?.clinic_name}
      <div
        class="hidden items-center gap-2 rounded-full border border-brand-200/80 bg-gradient-to-r from-brand-50 to-cyan-50 py-1 pl-1.5 pr-3 shadow-sm md:flex"
      >
        <span class="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-600 to-cyan-500 text-white shadow-sm">
          <Building2 class="h-3.5 w-3.5" />
        </span>
        <span class="max-w-[180px] truncate text-sm font-semibold text-brand-800">{$profile.clinic_name}</span>
      </div>
    {/if}
    {#if $profile}
      <div class="hidden text-right sm:block">
        <p class="max-w-[160px] truncate text-sm font-semibold leading-tight text-slate-900">{$profile.full_name}</p>
        <p class="text-xs text-slate-500">{ROLE_LABELS[$profile.role]}</p>
      </div>
      <div
        class="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand-600 to-cyan-500 font-semibold text-white"
        use:tooltip={{ text: `${$profile.full_name}${$profile.clinic_name ? ' · ' + $profile.clinic_name : ''}`, placement: 'bottom' }}
      >
        {$profile.full_name.charAt(0).toUpperCase()}
      </div>
      <button
        class="grid h-9 w-9 place-items-center rounded-lg text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
        use:tooltip={{ text: 'Cerrar sesión', placement: 'bottom' }}
        aria-label="Cerrar sesión"
        on:click={() => logout()}
      >
        <LogOut class="h-5 w-5" />
      </button>
    {/if}
  </div>
</header>

<ClinicSwitchModal bind:open={clinicSwitchOpen} />
