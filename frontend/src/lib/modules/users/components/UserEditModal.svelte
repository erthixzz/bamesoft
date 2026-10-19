<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { FileText, KeyRound, Trash2, TriangleAlert, Upload } from 'lucide-svelte';
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
  import { DEFAULT_PASSWORD, MIN_PASSWORD_LENGTH } from '$lib/modules/users/constants';
  import { toasts } from '$lib/stores/toasts';
  import { role } from '$lib/stores/auth';

  export let open = false;
  export let user: User;

  const dispatch = createEventDispatcher<{ saved: User; deleted: string }>();

  let clinics: Clinic[] = [];
  let saving = false;
  let uploadingCv = false;
  let hasCv = false;

  $: hasCv = !!user.cv_path;

  async function onCvFile(e: Event) {
    const input = e.currentTarget as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    uploadingCv = true;
    try {
      const updated = await usersApi.uploadCv(user.id, file);
      user = updated;
      dispatch('saved', updated);
      toasts.success('Hoja de vida actualizada');
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'No se pudo subir la hoja de vida');
    } finally {
      uploadingCv = false;
      input.value = '';
    }
  }

  async function viewCv() {
    try {
      const { url } = await usersApi.cvUrl(user.id);
      window.open(url, '_blank');
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'No se pudo abrir la hoja de vida');
    }
  }

  let form = {
    email: '',
    full_name: '',
    role: 'client' as UserRole,
    phone: '',
    license_number: '',
    clinic_id: '',
    active: 'true',
  };
  let errors: Record<string, string> = {};

  // Contraseña: campo aparte del formulario. Se envía solo si se escribe algo,
  // porque es una operación distinta (toca Supabase Auth, no el perfil).
  let newPassword = '';
  let resettingPwd = false;
  let deleting = false;
  let confirmDelete = false;

  function hydrate() {
    form = {
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      phone: user.phone ?? '',
      license_number: user.license_number ?? '',
      clinic_id: user.clinic_id ?? '',
      active: user.active ? 'true' : 'false',
    };
    errors = {};
    newPassword = '';
    confirmDelete = false;
  }

  /** Un no-admin sin compañía entra pero no ve ni equipos ni unidades. */
  $: sinCompania = form.role !== 'admin' && !form.clinic_id;

  async function resetPassword() {
    if (newPassword.length < MIN_PASSWORD_LENGTH) {
      errors = { ...errors, newPassword: `Mínimo ${MIN_PASSWORD_LENGTH} caracteres` };
      return;
    }
    resettingPwd = true;
    try {
      const updated = await usersApi.resetPassword(user.id, newPassword);
      user = updated;
      dispatch('saved', updated);
      toasts.success(
        newPassword === DEFAULT_PASSWORD
          ? `Contraseña restablecida a la provisional. ${updated.full_name} deberá cambiarla al entrar.`
          : 'Contraseña actualizada',
      );
      newPassword = '';
      errors = { ...errors, newPassword: '' };
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo cambiar la contraseña');
    } finally {
      resettingPwd = false;
    }
  }

  async function removeUser() {
    deleting = true;
    try {
      await usersApi.remove(user.id);
      toasts.success(`${user.full_name} eliminado`);
      dispatch('deleted', user.id);
      open = false;
    } catch (e) {
      // El backend responde 409 con el motivo cuando hay historial que preservar.
      toasts.error(e instanceof Error ? e.message : 'No se pudo eliminar el usuario');
      confirmDelete = false;
    } finally {
      deleting = false;
    }
  }

  // Hidratar SOLO al abrir el modal. Un `$: form = {...user}` reactivo se
  // re-ejecuta con cada re-render del padre (las props objeto siempre se
  // consideran "cambiadas") y pisa lo que el usuario está editando.
  let prevOpen = false;
  $: if (open && !prevOpen) {
    hydrate();
    prevOpen = true;
  }
  $: if (!open && prevOpen) {
    prevOpen = false;
  }

  $: if (open && clinics.length === 0) {
    clinicsApi
      .list()
      .then((c) => (clinics = c))
      .catch(() => (clinics = []));
  }

  // Solo el super admin puede asignar el rol de super admin.
  $: isSuper = $role === 'admin';
  $: roleOptions = ALL_ROLES.filter((r) => isSuper || r !== 'admin').map((r) => ({
    value: r,
    label: ROLE_LABELS[r],
  }));

  async function save() {
    const e: Record<string, string> = {};
    if (form.full_name.trim().length < 2) e.full_name = 'Nombre requerido';
    if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) e.email = 'Email inválido';
    errors = e;
    if (Object.keys(e).length) return;

    saving = true;
    try {
      const payload: UserUpdate = {
        email: form.email.trim().toLowerCase(),
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
    <div class="sm:col-span-2"><Input label="Nombre completo" bind:value={form.full_name} error={errors.full_name} /></div>
    <div class="sm:col-span-2">
      <Input label="Email (acceso)" type="email" bind:value={form.email} error={errors.email} />
      <p class="mt-1 text-xs text-slate-400">
        Es la credencial con la que entra: al cambiarlo, entrará con el nuevo.
      </p>
    </div>
    <Select label="Rol" bind:value={form.role} options={roleOptions} />
    {#if isSuper}
      <Select
        label="Compañía / clínica"
        bind:value={form.clinic_id}
        options={clinics.map((c) => ({ value: c.id, label: c.name }))}
        placeholder="— Sin compañía —"
      />
    {/if}
    {#if sinCompania}
      <p class="sm:col-span-2 flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-relaxed text-amber-800">
        <TriangleAlert class="mt-0.5 h-4 w-4 shrink-0" />
        <span>
          Sin compañía asignada puede iniciar sesión, pero no verá ningún equipo
          ni unidad de servicio y no podrá crear casos. Asígnale una compañía.
        </span>
      </p>
    {/if}
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
    <div class="sm:col-span-2">
      <span class="mb-1.5 block text-sm font-medium text-slate-600">Hoja de vida (CV)</span>
      <div class="flex flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
        <FileText class="h-5 w-5 shrink-0 {hasCv ? 'text-brand-600' : 'text-slate-400'}" />
        {#if hasCv}
          <button type="button" class="text-sm font-medium text-brand-600 hover:underline" on:click={viewCv}>
            Ver hoja de vida actual
          </button>
        {:else}
          <span class="text-sm text-slate-500">Sin hoja de vida adjunta</span>
        {/if}
        <label class="btn-secondary ml-auto inline-flex cursor-pointer items-center gap-2 text-sm {uploadingCv ? 'pointer-events-none opacity-60' : ''}">
          <Upload class="h-4 w-4" />
          {uploadingCv ? 'Subiendo…' : hasCv ? 'Reemplazar' : 'Adjuntar'}
          <input
            type="file"
            class="hidden"
            accept=".pdf,.doc,.docx,image/*"
            on:change={onCvFile}
            disabled={uploadingCv}
          />
        </label>
      </div>
    </div>

    <!-- Contraseña: operación aparte, se aplica al instante y no espera a Guardar. -->
    <div class="sm:col-span-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-3">
      <span class="mb-1.5 block text-sm font-medium text-slate-600">Contraseña</span>
      <div class="flex flex-col gap-2 sm:flex-row sm:items-start">
        <div class="flex-1">
          <Input
            bind:value={newPassword}
            error={errors.newPassword}
            placeholder={`Nueva contraseña (mínimo ${MIN_PASSWORD_LENGTH})`}
          />
        </div>
        <Button variant="secondary" on:click={resetPassword} loading={resettingPwd}>
          <KeyRound class="h-4 w-4" /> Cambiar
        </Button>
      </div>
      <button
        type="button"
        class="mt-2 text-xs font-medium text-brand-600 hover:underline"
        on:click={() => (newPassword = DEFAULT_PASSWORD)}
      >
        Usar la provisional ({DEFAULT_PASSWORD}) y pedir que la cambie al entrar
      </button>
    </div>

    <!-- Eliminar: destructivo, con confirmación en dos pasos. -->
    <div class="sm:col-span-2 rounded-lg border border-danger-200 bg-danger-50/50 px-3 py-3">
      <span class="mb-1 block text-sm font-medium text-danger-700">Eliminar usuario</span>
      {#if confirmDelete}
        <p class="mb-2 text-xs leading-relaxed text-danger-700">
          Se borrarán su perfil, su acceso y su hoja de vida. No se puede deshacer.
          Si tiene casos o documentos a su nombre, se cancelará y te lo diré.
        </p>
        <div class="flex flex-wrap gap-2">
          <Button variant="danger" on:click={removeUser} loading={deleting}>
            <Trash2 class="h-4 w-4" /> Sí, eliminar definitivamente
          </Button>
          <button class="btn-secondary" type="button" on:click={() => (confirmDelete = false)}>
            Cancelar
          </button>
        </div>
      {:else}
        <p class="mb-2 text-xs leading-relaxed text-slate-500">
          Para quitarle el acceso conservando su historial, ponlo <strong>Inactivo</strong> arriba.
          Eliminar solo es posible si nunca registró nada.
        </p>
        <button
          type="button"
          class="text-xs font-semibold text-danger-600 hover:underline"
          on:click={() => (confirmDelete = true)}
        >
          Eliminar definitivamente…
        </button>
      {/if}
    </div>
  </div>
  <svelte:fragment slot="footer">
    <div class="flex justify-end gap-2">
      <button class="btn-secondary" type="button" on:click={() => (open = false)}>Cancelar</button>
      <Button on:click={save} loading={saving}>Guardar</Button>
    </div>
  </svelte:fragment>
</Modal>
