<script lang="ts">
  import { onMount } from 'svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import { accessApi } from '$lib/modules/access/api';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import type { Clinic } from '$lib/modules/clinics/types';
  import type { Matrix } from '$lib/modules/access/types';
  import { FEATURES, can } from '$lib/utils/permissions';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { role } from '$lib/stores/auth';
  import { KeyRound, Save, Check, ShieldAlert } from 'lucide-svelte';

  let clinics: Clinic[] = [];
  let local: Matrix = {};
  let loading = true;
  let saving = false;

  $: allowed = can.manageAccess($role);

  async function load() {
    loading = true;
    try {
      const [cs, feats] = await Promise.all([clinicsApi.list(), accessApi.getClinicFeatures()]);
      clinics = cs;
      // Ausente en BD = habilitado por defecto.
      local = Object.fromEntries(
        cs.map((c) => [
          c.id,
          Object.fromEntries(FEATURES.map((f) => [f.key, feats.matrix?.[c.id]?.[f.key] !== false])),
        ]),
      );
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error cargando permisos');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Permisos');
    if (allowed) load();
    else loading = false;
  });

  async function save() {
    saving = true;
    try {
      await accessApi.saveClinicFeatures(local);
      toasts.success('Permisos actualizados');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar');
    } finally {
      saving = false;
    }
  }
</script>

<PageHeader title="Permisos" subtitle="Qué módulos puede ver cada compañía" icon={KeyRound} gradient="cyan">
  <svelte:fragment slot="actions">
    {#if allowed && clinics.length}<Button on:click={save} loading={saving}><Save class="h-4 w-4" /> Guardar</Button>{/if}
  </svelte:fragment>
</PageHeader>

{#if !allowed}
  <Card><EmptyState icon={ShieldAlert} title="Acceso restringido" description="Solo el super administrador puede gestionar los permisos por compañía." /></Card>
{:else if loading}
  <Spinner label="Cargando permisos…" />
{:else if clinics.length === 0}
  <Card><EmptyState icon={KeyRound} title="Sin compañías" description="Crea una compañía en la sección Compañías para asignarle módulos." /></Card>
{:else}
  <Card title="Módulos habilitados por compañía" description="Desmarca un módulo para ocultarlo del menú de esa compañía." icon={KeyRound} accent="cyan">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-left">
            <th class="py-2 pr-3 font-semibold text-slate-600">Compañía</th>
            {#each FEATURES as f}
              <th class="px-3 text-center font-semibold text-slate-600">{f.label}</th>
            {/each}
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          {#each clinics as c (c.id)}
            <tr>
              <td class="py-2.5 pr-3 font-medium text-slate-800">{c.name}</td>
              {#each FEATURES as f}
                <td class="px-3 text-center">
                  <label class="inline-flex cursor-pointer items-center justify-center">
                    <input type="checkbox" class="sr-only" bind:checked={local[c.id][f.key]} />
                    <span
                      class="grid h-5 w-5 place-items-center rounded-md border transition
                        {local[c.id][f.key] ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-300 bg-white text-transparent'} hover:border-brand-400"
                    >
                      <Check class="h-3.5 w-3.5" />
                    </span>
                  </label>
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </Card>
{/if}
