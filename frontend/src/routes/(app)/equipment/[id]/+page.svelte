<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import StatusBadge from '$lib/modules/equipment/components/StatusBadge.svelte';
  import CaseStatusBadge from '$lib/modules/cases/components/CaseStatusBadge.svelte';
  import EquipmentEditModal from '$lib/modules/equipment/components/EquipmentEditModal.svelte';
  import { Pencil, FileUp, Copy, ExternalLink, Download, FileText } from 'lucide-svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import { publicQrPngUrl } from '$lib/modules/public/api';
  import { toasts } from '$lib/stores/toasts';
  import { casesApi } from '$lib/modules/cases/api';
  import { calibrationsApi } from '$lib/modules/calibrations/api';
  import { maintenanceApi } from '$lib/modules/maintenance/api';
  import { documentsApi } from '$lib/modules/documents/api';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { Case } from '$lib/modules/cases/types';
  import type { Calibration } from '$lib/modules/calibrations/types';
  import type { MaintenanceSchedule } from '$lib/modules/maintenance/types';
  import type { Doc } from '$lib/modules/documents/types';
  import { formatDate } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';

  let id = '';
  let eq: Equipment | null = null;
  let cases: Case[] = [];
  let cals: Calibration[] = [];
  let pms: MaintenanceSchedule[] = [];
  let docs: Doc[] = [];
  let sectorLabel = '—';
  let loading = true;
  let error: string | null = null;
  let editOpen = false;
  let uploading = false;

  $: id = $page.params.id ?? '';
  $: setPageTitle(eq ? `${eq.code} · ${eq.name}` : 'Equipo');

  onMount(async () => {
    try {
      eq = await equipmentApi.get(id);
      // Abre el modal de edición si se llegó con ?edit=1 (desde el menú contextual).
      if ($page.url.searchParams.get('edit') === '1') editOpen = true;
      [cases, cals, pms, docs] = await Promise.all([
        casesApi.list({ equipment_id: id }),
        calibrationsApi.forEquipment(id),
        maintenanceApi.forEquipment(id),
        documentsApi.forEquipment(id),
      ]);
      if (eq.sector_id) {
        sectorLabel = (await sectorsApi.get(eq.sector_id).catch(() => null))?.name ?? '—';
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Error';
    } finally {
      loading = false;
    }
  });

  function onSaved(e: CustomEvent<Equipment>) {
    eq = e.detail;
  }

  // Enlace público que codifica el QR (mismo origen que esta app).
  $: publicUrl =
    eq && browser
      ? `${window.location.origin}/e/${encodeURIComponent(eq.code)}?t=${encodeURIComponent(eq.qr_token)}`
      : '';

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(publicUrl);
      toasts.success('Enlace público copiado');
    } catch {
      toasts.error('No se pudo copiar');
    }
  }

  async function onFile(e: Event) {
    const input = e.currentTarget as HTMLInputElement;
    const file = input.files?.[0];
    if (!file || !eq) return;
    uploading = true;
    try {
      await documentsApi.upload(file, {
        title: file.name,
        type: 'manual',
        equipment_id: eq.id,
      });
      docs = await documentsApi.forEquipment(eq.id);
    } finally {
      uploading = false;
      input.value = '';
    }
  }
</script>

{#if loading}
  <Spinner />
{:else if error || !eq}
  <p class="text-danger-600">{error ?? 'No se encontró'}</p>
{:else}
  <div class="mb-4 flex flex-col gap-2 sm:flex-row sm:justify-end">
    <a class="btn-secondary text-center" href={`/equipment/${eq.id}/hoja-de-vida`}>
      <FileText class="h-4 w-4" /> Hoja de vida
    </a>
    <a class="btn-secondary text-center" href={`/cases/new?equipment_id=${eq.id}`}>+ Caso para este equipo</a>
    <Button on:click={() => (editOpen = true)}>
      <Pencil class="h-4 w-4" /> Editar
    </Button>
  </div>

  <div class="grid gap-4 lg:grid-cols-3">
    <Card title="Información general">
      <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <dt class="text-slate-500">Código</dt><dd class="font-medium">{eq.code}</dd>
        <dt class="text-slate-500">Estado</dt><dd><StatusBadge status={eq.status} /></dd>
        <dt class="text-slate-500">Marca</dt><dd>{eq.brand ?? '—'}</dd>
        <dt class="text-slate-500">Modelo</dt><dd>{eq.model ?? '—'}</dd>
        <dt class="text-slate-500">Serial</dt><dd>{eq.serial_number ?? '—'}</dd>
        <dt class="text-slate-500">Unidad de servicio</dt><dd>{sectorLabel}</dd>
        <dt class="text-slate-500">Riesgo</dt><dd>{eq.risk_class ?? '—'}</dd>
        <dt class="text-slate-500">Adquirido</dt><dd>{formatDate(eq.acquisition_date)}</dd>
        <dt class="text-slate-500">Garantía</dt><dd>{formatDate(eq.warranty_until)}</dd>
      </dl>
    </Card>

    <Card title="QR público">
      <img
        alt={`QR de ${eq.code}`}
        src={publicQrPngUrl(eq.code, eq.qr_token)}
        class="mx-auto h-44 w-44 rounded-lg border border-slate-100"
      />
      <p class="mt-3 text-center text-xs text-slate-500">
        Escanéalo con la cámara del teléfono para ver la ficha pública del equipo.
      </p>
      <div class="mt-3 flex flex-wrap justify-center gap-2">
        <button class="btn-secondary" on:click={copyLink}>
          <Copy class="h-4 w-4" /> Copiar enlace
        </button>
        <a class="btn-secondary" href={publicUrl} target="_blank" rel="noopener">
          <ExternalLink class="h-4 w-4" /> Abrir
        </a>
        <a
          class="btn-secondary"
          href={publicQrPngUrl(eq.code, eq.qr_token)}
          target="_blank"
          rel="noopener"
          download={`qr-${eq.code}.png`}
        >
          <Download class="h-4 w-4" /> Descargar
        </a>
      </div>
    </Card>

    <Card title="Notas">
      <p class="whitespace-pre-wrap text-sm text-slate-700">{eq.notes ?? 'Sin notas.'}</p>
    </Card>
  </div>

  <div class="mt-6 grid gap-4 lg:grid-cols-2">
    <Card title={`Casos (${cases.length})`}>
      <ul class="space-y-2">
        {#each cases as c}
          <li class="flex items-center justify-between border-b border-slate-100 py-2 last:border-0">
            <a class="text-sm font-medium text-brand-700 hover:underline" href={`/cases/${c.id}`}>
              {c.code} · {c.title}
            </a>
            <CaseStatusBadge status={c.status} />
          </li>
        {:else}
          <li class="text-sm text-slate-400">Sin casos.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Mantenimientos preventivos (${pms.length})`}>
      <ul class="space-y-2 text-sm">
        {#each pms as p}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{p.name} · cada {p.frequency_days}d</span>
            <span class="text-slate-500">próximo: {formatDate(p.next_due_at)}</span>
          </li>
        {:else}
          <li class="text-slate-400">Sin programación.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Calibraciones (${cals.length})`}>
      <ul class="space-y-2 text-sm">
        {#each cals as c}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{formatDate(c.performed_at)} · {c.standard ?? '—'}</span>
            <span class={c.passed ? 'text-emerald-600' : 'text-danger-600'}>
              {c.passed ? 'Pasó' : 'Falló'}
            </span>
          </li>
        {:else}
          <li class="text-slate-400">Sin registros.</li>
        {/each}
      </ul>
    </Card>

    <Card>
      <div slot="actions">
        <label class="btn-secondary inline-flex cursor-pointer items-center gap-2">
          <FileUp class="h-4 w-4" />
          {uploading ? 'Subiendo…' : 'Subir documento'}
          <input type="file" class="hidden" on:change={onFile} disabled={uploading} />
        </label>
      </div>
      <h3 class="text-base font-semibold">Documentos ({docs.length})</h3>
      <ul class="mt-3 space-y-2 text-sm">
        {#each docs as d}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{d.title} <span class="text-xs text-slate-400">({d.type})</span></span>
            <span class="text-slate-500">{formatDate(d.created_at)}</span>
          </li>
        {:else}
          <li class="text-slate-400">Sin documentos.</li>
        {/each}
      </ul>
    </Card>
  </div>

  <EquipmentEditModal bind:open={editOpen} equipment={eq} on:saved={onSaved} />
{/if}
