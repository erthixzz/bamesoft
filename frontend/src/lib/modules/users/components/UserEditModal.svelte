<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Button from '$lib/components/Button.svelte';
  import { usersApi } from '$lib/modules/users/api';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import type { User, UserUpdate } from '$lib/modules/users/types';
  import type { Clinic } from '$lib/modules/clinics/types';
  import type { UserRole } from '$lib/api/types';
  import { ROLE_LABELS, ALL_ROLES } from '$lib/utils/permissions';
  import { toasts } from '$lib/stores/toasts';

  export let open = false;
  export let user: User;

  const dispatch = createEventDispatcher<{ saved: User }>();

  let clinics: Clinic[] = [];
  let saving = false;

  let form = {
    full_name: '',
    role: 'client' as UserRole,
    phone: '',
    license_number: '',
    clinic_id: '',
    active: 'true',
  };

  $: form = {
    full_name: user.full_name,
    role: user.role,
    phone: user.phone ?? '',
    license_number: user.license_number ?? '',
    clinic_id: user.clinic_id ?? '',
    active: user.active ? 'true' : 'false',
  };

  $: if (open && clinics.length === 0) {
    clinicsApi
      .list()
      .then((c) => (clinics = c))
      .catch(() => (clinics = []));
  }

  const roleOptions = ALL_ROLES.map((r) => ({ value: r, label: ROLE_LABELS[r] }));

  async function save() {
    saving = true;
    try {
      const payload: UserUpdate = {
        full_name: form.full_name,
        role: form.role,
        phone: form.phone || null,
        license_number: form.license_number || null,
        clinic_id: form.clinic_id || null,
        active: form.active === 'true',
      };
      const updated = await usersApi.update(user.id, payload);
      toasts.success('Usuario actualizado');
      dispatch('saved', updated);
      open = false;
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error al guardar');
    } finally {
      saving = false;
    }
  }
</script>

<Modal bind:open title={`Editar ${user.full_name}`}>
  <div class="grid gap-4 sm:grid-cols-2">
    <div class="sm:col-span-2"><Input label="Nombre completo" bind:value={form.full_name} /></div>
    <Select label="Rol" bind:value={form.role} options={roleOptions} />
    <Select
      label="Compañía / clínica"
      bind:value={form.clinic_id}
      options={clinics.map((c) => ({ value: c.id, label: c.name }))}
      placeholder="— Sin compañía —"
    />
    <Input label="Teléfono" bind:value={form.phone} />
    <Input label="Licencia / matrícula" bind:value={form.license_number} />
    <Select
      label="Estado"
      bind:value={form.active}
      options={[
        { value: 'true', label: 'Activo' },
        { value: 'false', label: 'Inactivo' },
      ]}
    />
    <div class="sm:col-span-2 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500">
      <span class="font-medium text-slate-600">Email:</span> {user.email}
      <span class="ml-2 text-slate-400">(no editable)</span>
    </div>
  </div>
  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2">
      <button class="btn-secondary" on:click={() => (open = false)}>Cancelar</button>
      <Button on:click={save} loading={saving}>Guardar</Button>
    </div>
  </svelte:fragment>
</Modal>
