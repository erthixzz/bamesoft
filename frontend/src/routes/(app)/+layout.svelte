<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import { isAuthenticated, profile, logout } from '$lib/stores/auth';
  import { authApi } from '$lib/modules/auth/api';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Header from '$lib/components/Header.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import AppBackdrop from '$lib/components/AppBackdrop.svelte';
  import ContextMenu from '$lib/components/ContextMenu.svelte';

  let bootError: string | null = null;
  let booting = true;

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
