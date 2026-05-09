<script lang="ts">
  import { onMount } from 'svelte';
  import Table from '$lib/components/Table.svelte';
  import Badge from '$lib/components/Badge.svelte';
  import { usersApi } from '$lib/modules/users/api';
  import type { User } from '$lib/modules/users/types';
  import { ROLE_LABELS } from '$lib/utils/permissions';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import type { UserRole } from '$lib/api/types';

  function roleLabel(r: string): string {
    return ROLE_LABELS[r as UserRole] ?? r;
  }

  let rows: User[] = [];
  const columns = [
    { key: 'full_name', label: 'Nombre' },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Rol' },
    { key: 'active', label: 'Estado' },
  ];

  onMount(async () => {
    setPageTitle('Usuarios');
    try {
      rows = await usersApi.list();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error');
    }
  });
</script>

<Table {columns} {rows}>
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
