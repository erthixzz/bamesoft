<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { get } from 'svelte/store';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Input from '$lib/components/Input.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import StatusBadge from '$lib/modules/equipment/components/StatusBadge.svelte';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import type { Sector } from '$lib/modules/sectors/types';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { Clinic } from '$lib/modules/clinics/types';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { profile, role } from '$lib/stores/auth';
  import { can } from '$lib/utils/permissions';
  import { Building2, PlusCircle, Boxes, Cpu } from 'lucide-svelte';

  let sectors: Sector[] = [];
  let equipment: Equipment[] = [];
  let clinics: Clinic[] = [];
  let loading = true;

  $: canManage = can.manageEquipment($role);
  $: bySector = (() => {
    const map: Record<string, Equipment[]> = {};
    for (const e of equipment) {
      const k = e.sector_id ?? '__none__';
      (map[k] ??= []).push(e);
    }
    return map;
  })();
  $: orphans = bySector['__none__'] ?? [];

  const ACCENTS = ['brand', 'cyan', 'emerald', 'amber', 'violet', 'rose'] as const;

  // ---- Modal: nueva unidad de servicio ----
  let newOpen = false;
  let saving = false;
  let form = { code: '', name: '', description: '' };
  let formErr: Record<string, string> = {};

  async function load() {
    loading = true;
    try {
      [sectors, equipment, clinics] = await Promise.all([
        sectorsApi.list(),
        equipmentApi.list({ limit: 500 }),
        clinicsApi.list().catch(() => []),
      ]);
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error cargando unidades');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Unidades de servicio');
    load();
  });

  function openNew() {
    form = { code: '', name: '', description: '' };
    formErr = {};
    newOpen = true;
  }

  async function saveSector() {
    const err: Record<string, string> = {};
    if (!form.code.trim()) err.code = 'Código requerido';
    if (!form.name.trim()) err.name = 'Nombre requerido';
    const clinic_id = get(profile)?.clinic_id ?? clinics[0]?.id;
    if (!clinic_id) err.name = 'No hay una clínica disponible';
    formErr = err;
    if (Object.keys(err).length) return;

    saving = true;
    try {
      await sectorsApi.create({
        clinic_id: clinic_id!,
        code: form.code.trim().toUpperCase(),
        name: form.name.trim(),
        description: form.description.trim() || null,
        default_engineer_id: null,
      });
      toasts.success(`Unidad ${form.name} creada`);
      newOpen = false;
      await load();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo crear la unidad');
    } finally {
      saving = false;
    }
  }
</script>

<PageHeader
  title="Unidades de servicio"
  subtitle="Áreas clínicas y el equipo médico asignado a cada una"
  icon={Building2}
  gradient="cyan"
>
  <svelte:fragment slot="actions">
    {#if canManage}
      <Button on:click={openNew}><PlusCircle class="h-4 w-4" /> Nueva unidad</Button>
    {/if}
  </svelte:fragment>
</PageHeader>

{#if loading}
  <Spinner label="Cargando unidades…" />
{:else if sectors.length === 0}
  <Card>
    <EmptyState
      icon={Building2}
      title="Sin unidades de servicio"
      description="Crea la primera unidad (UCI, Hospitalización, Rayos X…) para organizar el inventario por área."
    >
      <svelte:fragment slot="actions">
        {#if canManage}<Button on:click={openNew}>+ Nueva unidad</Button>{/if}
      </svelte:fragment>
    </EmptyState>
  </Card>
{:else}
  <div class="animate-fade-up grid gap-4 md:grid-cols-2 xl:grid-cols-3">
    {#each sectors as s, i (s.id)}
      {@const items = bySector[s.id] ?? []}
      <Card title={s.name} description={s.description ?? `Código ${s.code}`} icon={Building2} accent={ACCENTS[i % ACCENTS.length]}>
        <svelte:fragment slot="actions">
          <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold tabular-nums text-slate-600">
            <Cpu class="h-3.5 w-3.5" /> {items.length}
          </span>
        </svelte:fragment>

        {#if items.length}
          <ul class="space-y-1.5">
            {#each items as e (e.id)}
              <li>
                <a
                  href={`/equipment/${e.id}`}
                  class="flex items-center justify-between gap-2 rounded-lg border border-slate-100 px-3 py-2 transition hover:border-brand-200 hover:bg-brand-50/40"
                >
                  <span class="min-w-0">
                    <span class="font-mono text-[11px] text-slate-400">{e.code}</span>
                    <span class="block truncate text-sm font-medium text-slate-800">{e.name}</span>
                  </span>
                  <StatusBadge status={e.status} />
                </a>
              </li>
            {/each}
          </ul>
        {:else}
          <p class="value-pending">Aún no hay equipos en esta unidad.</p>
        {/if}

        {#if canManage}
          <div class="mt-3">
            <a class="btn-secondary w-full justify-center" href={`/equipment/new?sector_id=${s.id}`}>
              <PlusCircle class="h-4 w-4" /> Añadir equipo
            </a>
          </div>
        {/if}
      </Card>
    {/each}
  </div>

  {#if orphans.length}
    <div class="mt-4">
      <Card title="Sin unidad asignada" description="Equipos sin unidad de servicio; edítalos para asignarles una" icon={Boxes} accent="slate">
        <ul class="grid gap-1.5 sm:grid-cols-2">
          {#each orphans as e (e.id)}
            <li>
              <a href={`/equipment/${e.id}`} class="flex items-center justify-between gap-2 rounded-lg border border-slate-100 px-3 py-2 transition hover:bg-slate-50">
                <span class="min-w-0">
                  <span class="font-mono text-[11px] text-slate-400">{e.code}</span>
                  <span class="block truncate text-sm font-medium text-slate-800">{e.name}</span>
                </span>
                <StatusBadge status={e.status} />
              </a>
            </li>
          {/each}
        </ul>
      </Card>
    </div>
  {/if}
{/if}

<Modal bind:open={newOpen} title="Nueva unidad de servicio">
  <div class="grid gap-3 sm:grid-cols-2">
    <Input label="Código *" bind:value={form.code} placeholder="UCI" error={formErr.code} />
    <Input label="Nombre *" bind:value={form.name} placeholder="Unidad de Cuidados Intensivos" error={formErr.name} />
    <div class="sm:col-span-2">
      <Textarea label="Descripción" bind:value={form.description} rows={2} placeholder="Breve descripción del área…" />
    </div>
  </div>
  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2">
      <button class="btn-secondary" on:click={() => (newOpen = false)}>Cancelar</button>
      <Button on:click={saveSector} loading={saving}>Crear unidad</Button>
    </div>
  </svelte:fragment>
</Modal>
