<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import Table from '$lib/components/Table.svelte';
  import { standardsApi } from '$lib/modules/standards/api';
  import type { Standard } from '$lib/modules/standards/types';
  import { setPageTitle } from '$lib/stores/page';

  let rows: Standard[] = [];
  const columns = [
    { key: 'code', label: 'Código' },
    { key: 'name', label: 'Nombre' },
    { key: 'issuer', label: 'Emisor' },
    { key: 'version', label: 'Versión' },
  ];

  onMount(async () => {
    setPageTitle('Normas');
    rows = await standardsApi.list();
  });
</script>

<Card>
  <Table {columns} {rows} />
</Card>
