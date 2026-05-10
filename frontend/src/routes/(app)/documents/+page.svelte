<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import PageHeader from '$lib/components/PageHeader.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import { setPageTitle } from '$lib/stores/page';
  import { FileText, FolderOpen } from 'lucide-svelte';

  onMount(() => setPageTitle('Documentos'));
</script>

<PageHeader title="Documentos" subtitle="Manuales, certificados, hojas de vida y normas" icon={FileText} gradient="cyan" />

<Card>
  <EmptyState
    icon={FolderOpen}
    title="Biblioteca centralizada"
    description="Sube manuales, certificados de calibración, reportes técnicos y normas desde la ficha de cada equipo o caso. Los archivos se guardan cifrados en Supabase Storage."
  >
    <svelte:fragment slot="actions">
      <a class="btn-secondary" href="/equipment">Ir a equipos</a>
      <a class="btn-primary" href="/cases">Ir a casos</a>
    </svelte:fragment>
  </EmptyState>
</Card>
