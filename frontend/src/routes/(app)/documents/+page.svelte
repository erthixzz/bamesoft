<script lang="ts">
  import { onMount } from 'svelte';
  import Card from '$lib/components/Card.svelte';
  import { setPageTitle } from '$lib/stores/page';

  onMount(() => setPageTitle('Documentos'));
</script>

<Card title="Biblioteca de documentos" description="Filtra por equipo o caso desde sus respectivas vistas.">
  <p class="text-sm text-slate-500">
    Desde la ficha de un equipo (o un caso) podrás subir manuales, certificados,
    reportes y normas. Los archivos se almacenan en Supabase Storage y se sirven con
    URLs firmadas temporales.
  </p>
</Card>
