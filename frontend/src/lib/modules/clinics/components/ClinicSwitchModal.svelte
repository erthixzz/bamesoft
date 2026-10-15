<script lang="ts">
  /** Cambio de compañía para el super admin: al elegir una se actualiza su
   *  perfil (`clinic_id`) y las pantallas que dependen de la compañía activa
   *  (equipos, unidades de servicio…) se recargan filtradas por ella.
   *
   *  «Todas las compañías» deja `clinic_id` en null y devuelve la vista global.
   *  Ojo: esto es una comodidad de navegación, no una frontera de seguridad —
   *  el super admin sigue teniendo acceso a todo por API (`clinic_scope`
   *  devuelve `None` para su rol). */
  import Modal from '$lib/components/Modal.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import { usersApi } from '$lib/modules/users/api';
  import type { Clinic } from '$lib/modules/clinics/types';
  import { profile } from '$lib/stores/auth';
  import { toasts } from '$lib/stores/toasts';
  import { Building2, Check, Layers } from 'lucide-svelte';

  export let open = false;

  let clinics: Clinic[] = [];
  let loading = false;
  let loaded = false;
  let switchingId: string | null = null;
  /** Clave del pseudo-elemento «Todas las compañías» (no es un id real). */
  const ALL = '__all__';

  /** Sin compañía activa = vista global. */
  $: allCurrent = !$profile?.clinic_id;

  $: if (open && !loaded && !loading) {
    loading = true;
    clinicsApi
      .list()
      .then((c) => (clinics = c))
      .catch(() => (clinics = []))
      .finally(() => {
        loading = false;
        loaded = true;
      });
  }

  /** `null` = todas las compañías (vista global). */
  async function pick(id: string | null, name: string | null) {
    const me = $profile;
    if (!me || switchingId) return;
    if ((me.clinic_id ?? null) === id) {
      open = false;
      return;
    }
    switchingId = id ?? ALL;
    try {
      await usersApi.update(me.id, { clinic_id: id });
      profile.update((p) => (p ? { ...p, clinic_id: id, clinic_name: name } : p));
      toasts.success(name ? `Ahora estás en ${name}` : 'Viendo todas las compañías');
      open = false;
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo cambiar de compañía');
    } finally {
      switchingId = null;
    }
  }
</script>

<Modal bind:open title="Cambiar de compañía" size="sm">
  {#if loading && clinics.length === 0}
    <Spinner label="Cargando compañías…" />
  {:else if clinics.length === 0}
    <p class="py-4 text-center text-sm text-slate-400">No hay compañías registradas.</p>
  {:else}
    <ul class="space-y-1.5">
      <li>
        <button
          type="button"
          class="flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left transition
            {allCurrent ? 'border-brand-300 bg-brand-50' : 'border-slate-200 hover:border-brand-200 hover:bg-slate-50'}"
          on:click={() => pick(null, null)}
          disabled={!!switchingId}
        >
          <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-slate-600 to-slate-400 text-white">
            <Layers class="h-4 w-4" />
          </span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-sm font-semibold text-slate-800">Todas las compañías</span>
            <span class="block truncate text-xs text-slate-400">Vista global del super administrador</span>
          </span>
          {#if switchingId === ALL}
            <span class="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-brand-300 border-t-brand-600"></span>
          {:else if allCurrent}
            <Check class="h-4 w-4 shrink-0 text-brand-600" />
          {/if}
        </button>
      </li>
      {#each clinics as c (c.id)}
        {@const current = $profile?.clinic_id === c.id}
        <li>
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-xl border px-3 py-2.5 text-left transition
              {current ? 'border-brand-300 bg-brand-50' : 'border-slate-200 hover:border-brand-200 hover:bg-slate-50'}"
            on:click={() => pick(c.id, c.name)}
            disabled={!!switchingId}
          >
            <span class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 text-white">
              <Building2 class="h-4 w-4" />
            </span>
            <span class="min-w-0 flex-1">
              <span class="block truncate text-sm font-semibold text-slate-800">{c.name}</span>
              <span class="block truncate text-xs text-slate-400">{c.address ?? c.email ?? '—'}</span>
            </span>
            {#if switchingId === c.id}
              <span class="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-brand-300 border-t-brand-600"></span>
            {:else if current}
              <Check class="h-4 w-4 shrink-0 text-brand-600" />
            {/if}
          </button>
        </li>
      {/each}
    </ul>
    <p class="mt-3 text-xs text-slate-400">
      Equipos, unidades de servicio y altas nuevas se filtran por la compañía activa.
      Elige «Todas las compañías» para volver a la vista global.
    </p>
  {/if}
</Modal>
