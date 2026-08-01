<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import Table from '$lib/components/Table.svelte';
  import Card from '$lib/components/Card.svelte';
  import Badge from '$lib/components/Badge.svelte';
  import Input from '$lib/components/Input.svelte';
  import Button from '$lib/components/Button.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import AccessRequestsCard from '$lib/modules/access/components/AccessRequestsCard.svelte';
  import UserEditModal from '$lib/modules/users/components/UserEditModal.svelte';
  import UserCreateModal from '$lib/modules/users/components/UserCreateModal.svelte';
  import { usersApi } from '$lib/modules/users/api';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import type { User } from '$lib/modules/users/types';
  import type { Clinic } from '$lib/modules/clinics/types';
  import type { CtxItem } from '$lib/stores/contextMenu';
  import { ROLE_LABELS, CAPABILITIES, ALL_ROLES, permissions, hasCapIn } from '$lib/utils/permissions';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { timeFromNow, formatDateTime } from '$lib/utils/format';
  import type { UserRole } from '$lib/api/types';
  import { Users, Copy, UserX, Pencil, Check, ShieldCheck, PlusCircle, Search, Eye } from 'lucide-svelte';

  function roleLabel(r: string): string {
    return ROLE_LABELS[r as UserRole] ?? r;
  }

  let rows: User[] = [];
  let clinics: Clinic[] = [];
  let loading = true;
  let editOpen = false;
  let editing: User | null = null;
  let createOpen = false;
  let q = '';

  $: clinicName = Object.fromEntries(clinics.map((c) => [c.id, c.name]));

  // Filtro local: nombre, email, compañía o rol.
  $: filtered = q.trim()
    ? rows.filter((u) => {
        const hay = `${u.full_name} ${u.email} ${u.clinic_id ? (clinicName[u.clinic_id] ?? '') : ''} ${roleLabel(u.role)}`.toLowerCase();
        return hay.includes(q.trim().toLowerCase());
      })
    : rows;

  const columns = [
    { key: 'full_name', label: 'Nombre' },
    { key: 'email', label: 'Email' },
    { key: 'clinic_id', label: 'Compañía' },
    { key: 'role', label: 'Rol' },
    { key: 'last_seen_at', label: 'Última conexión' },
    { key: 'cv', label: 'Hoja de vida' },
    { key: 'active', label: 'Estado' },
  ];

  async function viewCv(id: string) {
    try {
      const { url } = await usersApi.cvUrl(id);
      window.open(url, '_blank');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo abrir la hoja de vida');
    }
  }

  async function load() {
    try {
      [rows, clinics] = await Promise.all([usersApi.list(), clinicsApi.list().catch(() => [])]);
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Usuarios');
    // Prefill desde el buscador global (/users?q=email).
    q = get(page).url.searchParams.get('q') ?? '';
    load();
  });

  function edit(row: User) {
    editing = row;
    editOpen = true;
  }

  function onSaved() {
    load();
  }

  async function copy(text: string, label = 'Copiado') {
    try {
      await navigator.clipboard.writeText(text);
      toasts.success(label);
    } catch {
      toasts.error('No se pudo copiar');
    }
  }

  async function deactivate(row: User) {
    if (!confirm(`¿Desactivar a ${row.full_name}? Perderá acceso a la plataforma.`)) return;
    try {
      await usersApi.deactivate(row.id);
      toasts.success(`${row.full_name} desactivado`);
      await load();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error al desactivar');
    }
  }

  const rowMenu = (row: User): CtxItem[] => [
    { label: 'Editar', icon: Pencil, onClick: () => edit(row) },
    { label: 'Copiar email', icon: Copy, onClick: () => copy(row.email, 'Email copiado') },
    ...(row.active
      ? [
          { divider: true } as CtxItem,
          { label: 'Desactivar', icon: UserX, danger: true, onClick: () => deactivate(row) } as CtxItem,
        ]
      : []),
  ];
</script>

<PageHeader title="Usuarios" subtitle="Gestiona roles, compañías y permisos" icon={Users} gradient="brand">
  <svelte:fragment slot="actions">
    <Button on:click={() => (createOpen = true)}><PlusCircle class="h-4 w-4" /> Nuevo usuario</Button>
  </svelte:fragment>
</PageHeader>

<!-- Va arriba y solo aparece si hay algo pendiente: es lo que requiere acción. -->
<div class="mb-4">
  <AccessRequestsCard {clinics} on:approved={load} />
</div>

<Card>
  <div class="mb-4 max-w-md">
    <Input placeholder="Buscar por nombre, email, compañía o rol…" bind:value={q} />
  </div>

  {#if loading}
    <Spinner label="Cargando usuarios…" />
  {:else if rows.length === 0}
    <EmptyState icon={Users} title="Sin usuarios registrados" description="Crea el primero con el botón «Nuevo usuario».">
      <svelte:fragment slot="actions">
        <Button on:click={() => (createOpen = true)}>+ Nuevo usuario</Button>
      </svelte:fragment>
    </EmptyState>
  {:else if filtered.length === 0}
    <EmptyState icon={Search} title="Sin resultados" description={`Ningún usuario coincide con «${q.trim()}».`} />
  {:else}
    <Table {columns} rows={filtered} {rowMenu}>
      <svelte:fragment slot="cell" let:row let:column>
        {#if column === 'full_name'}
          <button type="button" class="inline-flex items-center gap-1.5 font-medium text-brand-700 hover:underline" on:click={() => edit(row)}>
            <Pencil class="h-3.5 w-3.5 opacity-60" />
            {row.full_name}
          </button>
        {:else if column === 'clinic_id'}
          {row.clinic_id ? (clinicName[row.clinic_id] ?? '—') : '—'}
        {:else if column === 'role'}
          <Badge tone="blue">{roleLabel(row.role)}</Badge>
        {:else if column === 'last_seen_at'}
          {#if row.last_seen_at}
            {@const online = Date.now() - new Date(row.last_seen_at).getTime() < 5 * 60000}
            <span class="inline-flex items-center gap-1.5 text-sm text-slate-600" title={formatDateTime(row.last_seen_at)}>
              <span class="h-1.5 w-1.5 rounded-full {online ? 'bg-emerald-500 shadow-[0_0_6px_1px_rgba(16,185,129,0.6)]' : 'bg-slate-300'}"></span>
              {online ? 'En línea' : timeFromNow(row.last_seen_at)}
            </span>
          {:else}
            <span class="value-pending">Nunca</span>
          {/if}
        {:else if column === 'cv'}
          {#if row.cv_path}
            <button
              type="button"
              class="inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:underline"
              title="Ver hoja de vida"
              on:click={() => viewCv(row.id)}
            >
              <Eye class="h-4 w-4" /> Ver
            </button>
          {:else}
            <span class="value-pending">—</span>
          {/if}
        {:else if column === 'active'}
          <Badge tone={row.active ? 'green' : 'gray'}>{row.active ? 'Activo' : 'Inactivo'}</Badge>
        {:else}
          {row[column] ?? '—'}
        {/if}
      </svelte:fragment>
    </Table>
  {/if}
</Card>

<!-- Matriz de permisos por rol -->
<div class="mt-4">
  <Card title="Permisos por rol" description="Vista de solo lectura; se edita en la sección Roles." icon={ShieldCheck} accent="violet">
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="text-left text-xs uppercase text-slate-500">
          <tr class="border-b border-slate-200">
            <th class="py-2 pr-3">Capacidad</th>
            {#each ALL_ROLES as r}
              <th class="px-2 text-center">{roleLabel(r)}</th>
            {/each}
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          {#each CAPABILITIES as cap}
            <tr>
              <td class="py-2.5 pr-3 text-slate-700">{cap.label}</td>
              {#each ALL_ROLES as r}
                <td class="px-2 text-center">
                  {#if hasCapIn($permissions, r, cap.key)}
                    <Check class="mx-auto h-4 w-4 text-emerald-600" />
                  {:else}
                    <span class="text-slate-300">—</span>
                  {/if}
                </td>
              {/each}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
    <p class="mt-3 flex items-center gap-1.5 text-xs text-slate-400">
      <ShieldCheck class="h-3.5 w-3.5" />
      El <strong class="text-slate-500">Operario</strong> solo reporta casos; el cierre y el soporte de servicio los realiza el ingeniero.
    </p>
  </Card>
</div>

{#if editing}
  <UserEditModal bind:open={editOpen} user={editing} on:saved={onSaved} />
{/if}

<UserCreateModal bind:open={createOpen} on:created={onSaved} />
