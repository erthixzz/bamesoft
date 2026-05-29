<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Table from '$lib/components/Table.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import { standardsApi } from '$lib/modules/standards/api';
  import type { Standard } from '$lib/modules/standards/types';
  import type { CtxItem } from '$lib/stores/contextMenu';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { BookOpen, Copy, Type } from 'lucide-svelte';

  let rows: Standard[] = [];
  let loading = true;
  const columns = [
    { key: 'code', label: 'Código' },
    { key: 'name', label: 'Nombre' },
    { key: 'issuer', label: 'Emisor' },
    { key: 'version', label: 'Versión' },
  ];

  onMount(async () => {
    setPageTitle('Normas');
    try {
      rows = await standardsApi.list();
    } finally {
      loading = false;
    }
  });

  async function copy(text: string, label = 'Copiado') {
    try {
      await navigator.clipboard.writeText(text);
      toasts.success(label);
    } catch {
      toasts.error('No se pudo copiar');
    }
  }

  const rowMenu = (row: Standard): CtxItem[] => [
    { label: 'Copiar código', icon: Copy, onClick: () => copy(row.code, 'Código copiado') },
    { label: 'Copiar nombre', icon: Type, onClick: () => copy(row.name, 'Nombre copiado') },
  ];
</script>

<PageHeader title="Normas" subtitle="Estándares aplicables a la operación clínica" icon={BookOpen} gradient="cyan" />

<Card>
  {#if loading}
    <Spinner label="Cargando normas…" />
  {:else if rows.length === 0}
    <EmptyState icon={BookOpen} title="Sin normas registradas" description="Agrega ISO 13485, IEC 60601, INVIMA, NTC u otras según apliquen." />
  {:else}
    <Table {columns} {rows} {rowMenu} />
  {/if}
</Card>
