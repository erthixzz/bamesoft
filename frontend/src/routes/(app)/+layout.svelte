<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { isAuthenticated, profile, logout, role } from '$lib/stores/auth';
  import { authApi } from '$lib/modules/auth/api';
  import { accessApi } from '$lib/modules/access/api';
  import {
    setPermissions,
    setMyFeatures,
    permissions,
    hasCapIn,
    featureOn,
    myFeatures,
    type Capability,
  } from '$lib/utils/permissions';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Header from '$lib/components/Header.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import AppBackdrop from '$lib/components/AppBackdrop.svelte';
  import ContextMenu from '$lib/components/ContextMenu.svelte';
  import Assistant from '$lib/components/Assistant.svelte';
  import { ShieldAlert } from 'lucide-svelte';

  let bootError: string | null = null;
  let booting = true;

  // Guardia de rutas por capacidad de rol + módulo de compañía. Bloquea el
  // acceso directo por URL a módulos no permitidos (no solo oculta el menú).
  const ROUTE_RULES: { prefix: string; cap?: Capability; feature?: string }[] = [
    { prefix: '/dashboard', cap: 'dashboard', feature: 'dashboard' },
    { prefix: '/equipment', cap: 'equipment', feature: 'equipment' },
    { prefix: '/sectors', cap: 'sectors', feature: 'sectors' },
    { prefix: '/cases', cap: 'report', feature: 'cases' },
    { prefix: '/alerts', cap: 'work', feature: 'alerts' },
    { prefix: '/documents', cap: 'docs', feature: 'documents' },
    { prefix: '/standards', cap: 'standards', feature: 'standards' },
    { prefix: '/reports', cap: 'reports', feature: 'reports' },
    { prefix: '/clinics', cap: 'clinics' },
    { prefix: '/users', cap: 'users' },
    { prefix: '/roles', cap: 'access' },
    { prefix: '/permissions', cap: 'access' },
  ];

  $: rule = ROUTE_RULES.find((r) => $page.url.pathname.startsWith(r.prefix));
  $: accessDenied =
    !booting &&
    !bootError &&
    !!rule &&
    ((rule.cap && !hasCapIn($permissions, $role, rule.cap)) ||
      (rule.feature && !featureOn($myFeatures, rule.feature)));

  // Primera ruta a la que el usuario SÍ tiene acceso (según rol + módulos de la
  // compañía). Sirve como destino seguro cuando cae en un módulo no permitido.
  function firstAllowedRoute(): string {
    for (const r of ROUTE_RULES) {
      const capOk = !r.cap || hasCapIn($permissions, $role, r.cap);
      const featOk = !r.feature || featureOn($myFeatures, r.feature);
      if (capOk && featOk) return r.prefix;
    }
    return '/settings';
  }

  // Si aterriza (o navega por URL) en un módulo prohibido, lo reubicamos en su
  // primera ruta permitida en vez de dejarlo en un muro sin salida.
  $: if (accessDenied) {
    const dest = firstAllowedRoute();
    if (!$page.url.pathname.startsWith(dest)) goto(dest);
  }

  onMount(async () => {
    if (!get(isAuthenticated)) {
      goto('/login');
      return;
    }
    if (!get(profile)) {
      try {
        const p = await authApi.whoami();
        profile.set(p);
      } catch (e) {
        // No redirigir: muestra el error para depurar (CORS, 401, etc.)
        bootError = e instanceof Error ? e.message : 'Error desconocido';
      }
    }
    // Cargar control de acceso (roles + módulos de la compañía). Si falla,
    // se conservan los valores por defecto ya inicializados en el store.
    try {
      const [roles, mine] = await Promise.all([accessApi.getRoles(), accessApi.myFeatures()]);
      setPermissions(roles.matrix);
      setMyFeatures(mine.features);
    } catch {
      /* defaults */
    }
    booting = false;
  });
</script>

<AppBackdrop />
<ContextMenu />

<div class="relative flex min-h-screen">
  <Sidebar />
  <div class="flex w-full min-w-0 flex-col">
    <Header />
    <main class="min-w-0 flex-1 overflow-x-hidden p-3 sm:p-4 lg:p-6">
      {#if booting}
        <Spinner label="Cargando perfil…" />
      {:else if accessDenied}
        <div class="mx-auto mt-10 max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <div class="mx-auto mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-amber-50 text-amber-600">
            <ShieldAlert class="h-7 w-7" />
          </div>
          <h2 class="text-lg font-bold text-slate-900">Acceso restringido</h2>
          <p class="mt-2 text-sm text-slate-600">Tu rol no tiene permiso para ver esta sección.</p>
          <a class="btn-primary mt-5 inline-flex" href="/settings">Ir a mi cuenta</a>
        </div>
      {:else if bootError}
        <div class="mx-auto max-w-2xl rounded-xl border border-danger-500 bg-red-50 p-6">
          <h2 class="mb-2 text-lg font-semibold text-danger-600">No se pudo cargar el perfil</h2>
          <p class="mb-3 text-sm text-slate-700"><strong>Error:</strong> {bootError}</p>
          <p class="text-sm text-slate-700">
            Posibles causas:
          </p>
          <ul class="ml-5 list-disc text-sm text-slate-700">
            <li>El backend no está corriendo en <code>http://localhost:8000</code></li>
            <li>El navegador está en <code>127.0.0.1:5173</code> pero CORS solo permite <code>localhost:5173</code> (o viceversa)</li>
            <li>El JWT no es válido o expiró</li>
          </ul>
          <div class="mt-4 flex flex-wrap gap-2">
            <button class="btn-secondary" on:click={() => location.reload()}>Reintentar</button>
            <button class="btn-danger" on:click={() => logout().then(() => goto('/login'))}>
              Cerrar sesión
            </button>
          </div>
        </div>
      {:else}
        <slot />
      {/if}
    </main>
  </div>
</div>

{#if !booting && !bootError}
  <Assistant />
{/if}
