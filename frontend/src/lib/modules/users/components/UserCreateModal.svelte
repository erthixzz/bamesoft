<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import Modal from '$lib/components/Modal.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Button from '$lib/components/Button.svelte';
  import { usersApi } from '$lib/modules/users/api';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import type { User } from '$lib/modules/users/types';
  import type { Clinic } from '$lib/modules/clinics/types';
  import type { UserRole } from '$lib/api/types';
  import { ROLE_LABELS, ALL_ROLES } from '$lib/utils/permissions';
  import { toasts } from '$lib/stores/toasts';
  import { role } from '$lib/stores/auth';

  export let open = false;

  const dispatch = createEventDispatcher<{ created: User }>();

  let clinics: Clinic[] = [];
  let saving = false;
  let errors: Record<string, string> = {};

  let form = {
    full_name: '',
    email: '',
    password: '',
    role: 'client' as UserRole,
    clinic_id: '',
    phone: '',
    license_number: '',
  };

  // Solo el super admin puede crear otros super admins y elegir compañía;
  // el admin de clínica crea usuarios dentro de la suya (backend lo fuerza).
  $: isSuper = $role === 'admin';
  $: roleOptions = ALL_ROLES.filter((r) => isSuper || r !== 'admin').map((r) => ({
    value: r,
    label: ROLE_LABELS[r],
  }));

  $: if (open && isSuper && clinics.length === 0) {
    clinicsApi
      .list()
      .then((c) => (clinics = c))
      .catch(() => (clinics = []));
  }

  function reset() {
    form = { full_name: '', email: '', password: '', role: 'client', clinic_id: '', phone: '', license_number: '' };
    errors = {};
  }

  $: if (open === false) reset();

  async function save() {
    const e: Record<string, string> = {};
    if (form.full_name.trim().length < 2) e.full_name = 'Nombre requerido';
    if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) e.email = 'Email inválido';
    if (form.password.length < 8) e.password = 'Mínimo 8 caracteres';
    errors = e;
    if (Object.keys(e).length) return;

    saving = true;
    try {
      const created = await usersApi.invite({
        full_name: form.full_name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        role: form.role,
        clinic_id: form.clinic_id || null,
        phone: form.phone.trim() || null,
        license_number: form.license_number.trim() || null,
      });
      toasts.success(`${created.full_name} creado — ya puede iniciar sesión`);
      dispatch('created', created);
      open = false;
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'No se pudo crear el usuario');
    } finally {
      saving = false;
    }
  }
</script>

<Modal bind:open title="Nuevo usuario">
  <div class="grid gap-4 sm:grid-cols-2">
    <div class="sm:col-span-2">
      <Input label="Nombre completo *" bind:value={form.full_name} error={errors.full_name} placeholder="Nombre y apellidos" />
    </div>
    <Input label="Email *" type="email" bind:value={form.email} error={errors.email} placeholder="usuario@clinica.com" />
    <Input label="Contraseña *" type="password" bind:value={form.password} error={errors.password} placeholder="Mínimo 8 caracteres" />
    <Select label="Rol" bind:value={form.role} options={roleOptions} />
    {#if isSuper}
      <Select
        label="Compañía / clínica"
        bind:value={form.clinic_id}
        options={clinics.map((c) => ({ value: c.id, label: c.name }))}
        placeholder="— Sin compañía —"
      />
    {/if}
    <Input label="Teléfono" bind:value={form.phone} />
    <Input label="Licencia / matrícula" bind:value={form.license_number} />
  </div>
  <p class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500">
    El usuario podrá entrar de inmediato con su email y contraseña. Pídele que la cambie en su primer acceso.
  </p>
  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2">
      <button class="btn-secondary" on:click={() => (open = false)}>Cancelar</button>
      <Button on:click={save} loading={saving}>Crear usuario</Button>
    </div>
  </svelte:fragment>
</Modal>
