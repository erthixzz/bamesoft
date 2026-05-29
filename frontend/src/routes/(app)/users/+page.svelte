<script lang="ts">
  import { onMount } from 'svelte';
  import Table from '$lib/components/Table.svelte';
  import Card from '$lib/components/Card.svelte';
  import Badge from '$lib/components/Badge.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import { usersApi } from '$lib/modules/users/api';
  import type { User } from '$lib/modules/users/types';
  import type { CtxItem } from '$lib/stores/contextMenu';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import type { UserRole } from '$lib/api/types';
  import { Users, Copy, UserX } from 'lucide-svelte';

  function roleLabel(r: string): string {
    return ROLE_LABELS[r as UserRole] ?? r;
  }

  let rows: User[] = [];
  let loading = true;
  const columns = [
    { key: 'full_name', label: 'Nombre' },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Rol' },
    { key: 'active', label: 'Estado' },
  ];

  async function load() {
    try {
      rows = await usersApi.list();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    setPageTitle('Usuarios');
    load();
  });

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
    { label: 'Copiar email', icon: Copy, onClick: () => copy(row.email, 'Email copiado') },
    ...(row.active
      ? [
          { divider: true } as CtxItem,
          { label: 'Desactivar', icon: UserX, danger: true, onClick: () => deactivate(row) } as CtxItem,
        ]
      : []),
  ];
</script>

<PageHeader title="Usuarios" subtitle="Administradores, ingenieros, servicio, soporte y clientes" icon={Users} gradient="brand" />

<Card>
  {#if loading}
    <Spinner label="Cargando usuarios…" />
  {:else if rows.length === 0}
    <EmptyState icon={Users} title="Sin usuarios registrados" />
  {:else}
    <Table {columns} {rows} {rowMenu}>
      <svelte:fragment slot="cell" let:row let:column>
        {#if column === 'role'}
          <Badge tone="blue">{roleLabel(row.role)}</Badge>
        {:else if column === 'active'}
          <Badge tone={row.active ? 'green' : 'gray'}>{row.active ? 'Activo' : 'Inactivo'}</Badge>
        {:else}
          {row[column] ?? '—'}
        {/if}
      </svelte:fragment>
    </Table>
  {/if}
</Card>
