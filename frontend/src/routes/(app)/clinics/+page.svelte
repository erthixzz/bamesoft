<script lang="ts">
  import { onMount } from 'svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Input from '$lib/components/Input.svelte';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import { usersApi } from '$lib/modules/users/api';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import type { Clinic } from '$lib/modules/clinics/types';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { role } from '$lib/stores/auth';
  import { can } from '$lib/utils/permissions';
  import { Building2, PlusCircle, Pencil, Mail, Phone, MapPin, Cpu, Users, ShieldAlert } from 'lucide-svelte';

  let clinics: Clinic[] = [];
  let equipCount: Record<string, number> = {};
  let userCount: Record<string, number> = {};
  let loading = true;

  $: allowed = can.manageClinics($role);
  const ACCENTS = ['brand', 'cyan', 'emerald', 'amber', 'violet', 'rose'] as const;

  let open = false;
  let saving = false;
  let editing: Clinic | null = null;
  let form = { name: '', tax_id: '', email: '', phone: '', address: '', logo_url: '' };
  let err: Record<string, string> = {};

  async function load() {
    loading = true;
    try {
      const [cs, us, eq] = await Promise.all([
        clinicsApi.list(),
        usersApi.list().catch(() => []),
        equipmentApi.list({ limit: 1000 }).catch(() => []),
      ]);
      clinics = cs;
      equipCount = {};
      for (const e of eq) equipCount[e.clinic_id] = (equipCount[e.clinic_id] ?? 0) + 1;
      userCount = {};
      for (const u of us) if (u.clinic_id) userCount[u.clinic_id] = (userCount[u.clinic_id] ?? 0) + 1;
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error cargando compañías');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Compañías');
    if (allowed) load();
    else loading = false;
  });

  function openNew() {
    editing = null;
    form = { name: '', tax_id: '', email: '', phone: '', address: '', logo_url: '' };
    err = {};
    open = true;
  }
  function openEdit(c: Clinic) {
    editing = c;
    form = {
      name: c.name,
      tax_id: c.tax_id ?? '',
      email: c.email ?? '',
      phone: c.phone ?? '',
      address: c.address ?? '',
      logo_url: c.logo_url ?? '',
    };
    err = {};
    open = true;
  }

  async function save() {
    err = {};
    if (!form.name.trim()) {
      err.name = 'Nombre requerido';
      return;
    }
    saving = true;
    try {
      if (editing) {
        await clinicsApi.update(editing.id, {
          name: form.name.trim(),
          email: form.email.trim() || null,
          phone: form.phone.trim() || null,
          address: form.address.trim() || null,
          logo_url: form.logo_url.trim() || null,
        });
        toasts.success('Compañía actualizada');
      } else {
        await clinicsApi.create({
          name: form.name.trim(),
          tax_id: form.tax_id.trim() || null,
          email: form.email.trim() || null,
          phone: form.phone.trim() || null,
          address: form.address.trim() || null,
          logo_url: form.logo_url.trim() || null,
        });
        toasts.success('Compañía creada');
      }
      open = false;
      await load();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar');
    } finally {
      saving = false;
    }
  }
</script>

<PageHeader title="Compañías" subtitle="Clínicas y hospitales gestionados en la plataforma" icon={Building2} gradient="brand">
  <svelte:fragment slot="actions">
    {#if allowed}
      <Button on:click={openNew}><PlusCircle class="h-4 w-4" /> Nueva compañía</Button>
    {/if}
  </svelte:fragment>
</PageHeader>

{#if !allowed}
  <Card>
    <EmptyState icon={ShieldAlert} title="Acceso restringido" description="Solo el super administrador puede gestionar las compañías." />
  </Card>
{:else if loading}
  <Spinner label="Cargando compañías…" />
{:else if clinics.length === 0}
  <Card>
    <EmptyState icon={Building2} title="Sin compañías" description="Crea la primera compañía (clínica u hospital).">
      <svelte:fragment slot="actions"><Button on:click={openNew}>+ Nueva compañía</Button></svelte:fragment>
    </EmptyState>
  </Card>
{:else}
  <div class="animate-fade-up grid gap-4 md:grid-cols-2 xl:grid-cols-3">
    {#each clinics as c, i (c.id)}
      <Card title={c.name} description={c.tax_id ?? 'Sin NIT'} icon={Building2} accent={ACCENTS[i % ACCENTS.length]} interactive>
        <svelte:fragment slot="actions">
          <button type="button" class="rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-brand-600" on:click={() => openEdit(c)} aria-label="Editar">
            <Pencil class="h-4 w-4" />
          </button>
        </svelte:fragment>

        <dl class="space-y-1.5 text-sm">
          <div class="flex items-center gap-2 text-slate-600"><Mail class="h-3.5 w-3.5 text-slate-400" />{c.email ?? '—'}</div>
          <div class="flex items-center gap-2 text-slate-600"><Phone class="h-3.5 w-3.5 text-slate-400" />{c.phone ?? '—'}</div>
          <div class="flex items-center gap-2 text-slate-600"><MapPin class="h-3.5 w-3.5 text-slate-400" />{c.address ?? '—'}</div>
        </dl>
        <div class="mt-3 flex gap-2 border-t border-slate-100 pt-3">
          <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
            <Cpu class="h-3.5 w-3.5" /> {equipCount[c.id] ?? 0} equipos
          </span>
          <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
            <Users class="h-3.5 w-3.5" /> {userCount[c.id] ?? 0} usuarios
          </span>
        </div>
      </Card>
    {/each}
  </div>
{/if}

<Modal bind:open title={editing ? `Editar ${editing.name}` : 'Nueva compañía'}>
  <div class="grid gap-3 sm:grid-cols-2">
    <div class="sm:col-span-2"><Input label="Nombre *" bind:value={form.name} error={err.name} placeholder="Clínica San Rafael" /></div>
    <Input label="NIT / Tax ID" bind:value={form.tax_id} placeholder="900.000.000-0" />
    <Input label="Email" type="email" bind:value={form.email} placeholder="contacto@clinica.com" />
    <Input label="Teléfono" bind:value={form.phone} placeholder="+57 300 000 0000" />
    <Input label="Dirección" bind:value={form.address} placeholder="Ciudad" />
    <div class="sm:col-span-2"><Input label="Logo (URL)" bind:value={form.logo_url} placeholder="https://…" /></div>
  </div>
  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2">
      <button class="btn-secondary" on:click={() => (open = false)}>Cancelar</button>
      <Button on:click={save} loading={saving}>{editing ? 'Guardar' : 'Crear'}</Button>
    </div>
  </svelte:fragment>
</Modal>
