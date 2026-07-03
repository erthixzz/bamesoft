<script lang="ts">
  import { onMount } from 'svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import { accessApi } from '$lib/modules/access/api';
  import {
    CAPABILITIES,
    ALL_ROLES,
    ROLE_LABELS,
    DEFAULT_MATRIX,
    setPermissions,
    can,
    type PermMatrix,
  } from '$lib/utils/permissions';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { role } from '$lib/stores/auth';
  import { ShieldCheck, Save, Check, ShieldAlert } from 'lucide-svelte';

  let local: PermMatrix = {};
  let loading = true;
  let saving = false;

  $: allowed = can.manageAccess($role);

  function hydrate(matrix: PermMatrix) {
    const base = matrix && Object.keys(matrix).length ? matrix : DEFAULT_MATRIX;
    local = Object.fromEntries(
      ALL_ROLES.map((r) => [
        r,
        Object.fromEntries(CAPABILITIES.map((c) => [c.key, !!base?.[r]?.[c.key]])),
      ]),
    );
  }

  async function load() {
    loading = true;
    try {
      hydrate((await accessApi.getRoles()).matrix);
    } catch {
      hydrate(DEFAULT_MATRIX);
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Roles');
    if (allowed) load();
    else loading = false;
  });

  async function save() {
    saving = true;
    try {
      const res = await accessApi.saveRoles(local);
      setPermissions(res.matrix); // aplicar en vivo
      toasts.success('Roles actualizados');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar');
    } finally {
      saving = false;
    }
  }
</script>

<PageHeader title="Roles" subtitle="Qué puede hacer cada rol en la plataforma" icon={ShieldCheck} gradient="brand">
  <svelte:fragment slot="actions">
    {#if allowed}<Button on:click={save} loading={saving}><Save class="h-4 w-4" /> Guardar</Button>{/if}
  </svelte:fragment>
</PageHeader>

{#if !allowed}
  <Card><EmptyState icon={ShieldAlert} title="Acceso restringido" description="Solo el super administrador puede gestionar los roles." /></Card>
{:else if loading}
  <Spinner label="Cargando roles…" />
{:else}
  <Card title="Matriz de acciones por rol" description="Marca lo que cada rol puede hacer. Se aplica de inmediato al guardar." icon={ShieldCheck} accent="brand">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-200 text-left">
            <th class="py-2 pr-3 font-semibold text-slate-600">Acción</th>
            {#each ALL_ROLES as r}
              <th class="px-3 text-center font-semibold text-slate-600">{ROLE_LABELS[r]}</th>
            {/each}
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          {#each CAPABILITIES as cap}
            <tr>
              <td class="py-2.5 pr-3 text-slate-700">{cap.label}</td>
              {#each ALL_ROLES as r}
                <td class="px-3 text-center">
                  <label class="inline-flex cursor-pointer items-center justify-center">
                    <input
                      type="checkbox"
                      class="peer sr-only"
                      bind:checked={local[r][cap.key]}
                      disabled={r === 'admin'}
                    />
                    <span
                      class="grid h-5 w-5 place-items-center rounded-md border transition
                        {local[r][cap.key] ? 'border-brand-600 bg-brand-600 text-white' : 'border-slate-300 bg-white text-transparent'}
                        {r === 'admin' ? 'opacity-60' : 'hover:border-brand-400'}"
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
    <p class="mt-3 text-xs text-slate-400">
      El <strong class="text-slate-500">Super administrador</strong> siempre tiene acceso total (no editable).
    </p>
  </Card>
{/if}
