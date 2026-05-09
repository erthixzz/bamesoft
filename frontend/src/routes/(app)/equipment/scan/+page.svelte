<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import QRScanner from '$lib/components/QRScanner.svelte';
  import Card from '$lib/components/Card.svelte';
  import { equipmentApi, parseQrPayload } from '$lib/modules/equipment/api';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';

  let lastError: string | null = null;

  onMount(() => setPageTitle('Escanear QR'));

  async function onScan(e: CustomEvent<{ raw: string }>) {
    lastError = null;
    try {
      const { code, token } = parseQrPayload(e.detail.raw);
      const eq = await equipmentApi.scan(code, token);
      toasts.success(`Equipo ${eq.code} reconocido`);
      goto(`/equipment/${eq.id}`);
    } catch (err) {
      lastError = err instanceof Error ? err.message : 'No se pudo identificar el QR';
    }
  }
</script>

<Card title="Apunta la cámara al QR del equipo" description="Otorga permiso de cámara cuando el navegador lo pida.">
  <QRScanner on:scan={onScan} />
  {#if lastError}
    <p class="mt-3 text-sm text-danger-600">{lastError}</p>
  {/if}
</Card>
