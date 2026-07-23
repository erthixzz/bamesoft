<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { browser } from '$app/environment';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import Select from '$lib/components/Select.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import StatusBadge from '$lib/modules/equipment/components/StatusBadge.svelte';
  import CaseStatusBadge from '$lib/modules/cases/components/CaseStatusBadge.svelte';
  import EquipmentEditModal from '$lib/modules/equipment/components/EquipmentEditModal.svelte';
  import {
    Pencil,
    FileUp,
    Copy,
    ExternalLink,
    Download,
    FileText,
    Building2,
    Barcode,
    ShieldAlert,
    CalendarClock,
    Stethoscope,
    QrCode,
    StickyNote,
    Wrench,
    Gauge,
    FolderOpen,
  } from 'lucide-svelte';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import { publicQrPngUrl } from '$lib/modules/public/api';
  import { toasts } from '$lib/stores/toasts';
  import { casesApi } from '$lib/modules/cases/api';
  import { calibrationsApi } from '$lib/modules/calibrations/api';
  import { maintenanceApi } from '$lib/modules/maintenance/api';
  import { documentsApi } from '$lib/modules/documents/api';
  import {
    DOC_TYPE_ORDER,
    DOC_TYPE_LABEL,
    EQUIPMENT_DOC_TYPE_OPTIONS,
  } from '$lib/modules/documents/ui';
  import type { DocumentType } from '$lib/api/types';
  import type { Equipment } from '$lib/modules/equipment/types';
  import type { Case } from '$lib/modules/cases/types';
  import type { Calibration } from '$lib/modules/calibrations/types';
  import type { MaintenanceSchedule } from '$lib/modules/maintenance/types';
  import type { Doc } from '$lib/modules/documents/types';
  import { formatDate } from '$lib/utils/format';
  import { isUuid } from '$lib/utils/slug';
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
  let uploadType = 'manual';

  // Documentos agrupados por tipo (carpetas), en el orden definido.
  $: docFolders = DOC_TYPE_ORDER.map((type) => ({
    type,
    label: DOC_TYPE_LABEL[type],
    items: docs.filter((d) => d.type === type),
  })).filter((f) => f.items.length > 0);

  $: id = $page.params.id ?? '';
  $: setPageTitle(eq ? `${eq.code} · ${eq.name}` : 'Equipo');

  onMount(async () => {
    try {
      // La URL puede traer el código legible (ANE-UCI-01) o un UUID.
      eq = isUuid(id) ? await equipmentApi.get(id) : await equipmentApi.byCode(id);
      const eqId = eq.id;
      // Abre el modal de edición si se llegó con ?edit=1 (desde el menú contextual).
      if ($page.url.searchParams.get('edit') === '1') editOpen = true;
      [cases, cals, pms, docs] = await Promise.all([
        casesApi.list({ equipment_id: eqId }),
        calibrationsApi.forEquipment(eqId),
        maintenanceApi.forEquipment(eqId),
        documentsApi.forEquipment(eqId),
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
        type: uploadType as DocumentType,
        equipment_id: eq.id,
      });
      docs = await documentsApi.forEquipment(eq.id);
      toasts.success('Documento subido');
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'No se pudo subir el documento');
    } finally {
      uploading = false;
      input.value = '';
    }
  }

  async function openDoc(id: string) {
    try {
      const { url } = await documentsApi.signedUrl(id);
      window.open(url, '_blank');
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'No se pudo abrir el documento');
    }
  }
</script>

{#if loading}
  <Spinner />
{:else if error || !eq}
  <p class="text-danger-600">{error ?? 'No se encontró'}</p>
{:else}
  <!-- Hero del equipo -->
  <div class="animate-fade-up mb-4 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-200/50">
    <div class="bg-grid bg-gradient-to-br from-slate-50 to-white p-4">
      <div class="flex flex-wrap items-start justify-between gap-2">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-md bg-slate-900 px-2 py-0.5 font-mono text-[11px] font-semibold tracking-wide text-white">
            {eq.code}
          </span>
          <h1 class="mt-1.5 text-lg font-bold leading-tight text-slate-900 sm:text-xl">{eq.name}</h1>
          <p class="mt-0.5 text-sm text-slate-500">{eq.brand ?? 'Sin marca'} · {eq.model ?? 'Sin modelo'}</p>
        </div>
        <StatusBadge status={eq.status} />
      </div>

      <div class="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {#each [{ icon: Building2, label: 'Unidad', value: sectorLabel }, { icon: Barcode, label: 'Serial', value: eq.serial_number || 'Sin serial' }, { icon: ShieldAlert, label: 'Riesgo', value: eq.risk_class || 'Sin clasificar' }, { icon: CalendarClock, label: 'Garantía', value: formatDate(eq.warranty_until) }] as f}
          <div class="rounded-lg border border-slate-100 bg-white/70 px-3 py-2 backdrop-blur">
            <div class="section-label flex items-center gap-1.5">
              <svelte:component this={f.icon} class="h-3.5 w-3.5" />{f.label}
            </div>
            <p class="mt-0.5 truncate text-sm font-medium text-slate-800" title={f.value}>{f.value}</p>
          </div>
        {/each}
      </div>

      <div class="mt-3 flex flex-wrap gap-2">
        <Button on:click={() => (editOpen = true)}><Pencil class="h-4 w-4" /> Editar</Button>
        <a class="btn-secondary" href={`/equipment/${eq.code}/hoja-de-vida`}><FileText class="h-4 w-4" /> Hoja de vida</a>
        <a class="btn-secondary" href={`/cases/new?equipment_id=${eq.id}`}><Wrench class="h-4 w-4" /> Caso para este equipo</a>
      </div>
    </div>
  </div>

  <div class="grid gap-4 lg:grid-cols-3">
    <Card title="Información general" icon={Stethoscope} accent="brand">
      <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <dt class="text-slate-500">Código</dt><dd class="font-medium">{eq.code}</dd>
        <dt class="text-slate-500">Marca</dt>
        <dd>{#if eq.brand}{eq.brand}{:else}<span class="value-pending">Sin marca</span>{/if}</dd>
        <dt class="text-slate-500">Modelo</dt>
        <dd>{#if eq.model}{eq.model}{:else}<span class="value-pending">Sin modelo</span>{/if}</dd>
        <dt class="text-slate-500">Fabricante</dt>
        <dd>{#if eq.manufacturer}{eq.manufacturer}{:else}<span class="value-pending">Sin registrar</span>{/if}</dd>
        <dt class="text-slate-500">Unidad de servicio</dt><dd>{sectorLabel}</dd>
        <dt class="text-slate-500">Riesgo</dt>
        <dd>{#if eq.risk_class}{eq.risk_class}{:else}<span class="value-pending">Sin clasificar</span>{/if}</dd>
        <dt class="text-slate-500">Adquirido</dt>
        <dd>{#if eq.acquisition_date}{formatDate(eq.acquisition_date)}{:else}<span class="value-pending">Sin fecha</span>{/if}</dd>
        <dt class="text-slate-500">Garantía</dt>
        <dd>{#if eq.warranty_until}{formatDate(eq.warranty_until)}{:else}<span class="value-pending">Sin fecha</span>{/if}</dd>
      </dl>
    </Card>

    <Card title="QR público" icon={QrCode} accent="cyan">
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

    <Card title="Notas" icon={StickyNote} accent="slate">
      {#if eq.notes}
        <p class="whitespace-pre-wrap text-sm text-slate-700">{eq.notes}</p>
      {:else}
        <p class="value-pending">Sin notas registradas.</p>
      {/if}
    </Card>
  </div>

  <div class="mt-6 grid gap-4 lg:grid-cols-2">
    <Card title={`Casos (${cases.length})`} icon={Wrench} accent="amber">
      <ul class="space-y-2">
        {#each cases as c}
          <li class="flex items-center justify-between border-b border-slate-100 py-2 last:border-0">
            <a class="text-sm font-medium text-brand-700 hover:underline" href={`/cases/${c.code}`}>
              {c.code} · {c.title}
            </a>
            <CaseStatusBadge status={c.status} />
          </li>
        {:else}
          <li class="value-pending">Sin casos asociados.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Mantenimientos preventivos (${pms.length})`} icon={CalendarClock} accent="emerald">
      <ul class="space-y-2 text-sm">
        {#each pms as p}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{p.name} · cada {p.frequency_days}d</span>
            <span class="text-slate-500">próximo: {formatDate(p.next_due_at)}</span>
          </li>
        {:else}
          <li class="value-pending">Sin programación.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Calibraciones (${cals.length})`} icon={Gauge} accent="violet">
      <ul class="space-y-2 text-sm">
        {#each cals as c}
          <li class="flex justify-between border-b border-slate-100 py-2 last:border-0">
            <span>{formatDate(c.performed_at)} · {c.standard ?? '—'}</span>
            <span class={c.passed ? 'text-emerald-600' : 'text-danger-600'}>
              {c.passed ? 'Pasó' : 'Falló'}
            </span>
          </li>
        {:else}
          <li class="value-pending">Sin registros.</li>
        {/each}
      </ul>
    </Card>

    <Card title={`Documentos (${docs.length})`} icon={FolderOpen} accent="cyan">
      <svelte:fragment slot="actions">
        <div class="flex items-center gap-2">
          <div class="w-40">
            <Select bind:value={uploadType} options={EQUIPMENT_DOC_TYPE_OPTIONS} />
          </div>
          <label class="btn-secondary inline-flex cursor-pointer items-center gap-2 {uploading ? 'pointer-events-none opacity-60' : ''}">
            <FileUp class="h-4 w-4" />
            {uploading ? 'Subiendo…' : 'Subir'}
            <input type="file" class="hidden" on:change={onFile} disabled={uploading} />
          </label>
        </div>
      </svelte:fragment>

      {#if docFolders.length === 0}
        <p class="value-pending">Sin documentos.</p>
      {:else}
        <div class="space-y-4">
          {#each docFolders as folder (folder.type)}
            <div>
              <h4 class="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
                <FolderOpen class="h-3.5 w-3.5" />
                {folder.label}
                <span class="font-normal text-slate-400">({folder.items.length})</span>
              </h4>
              <ul class="space-y-1 text-sm">
                {#each folder.items as d (d.id)}
                  <li class="flex items-center justify-between gap-2 border-b border-slate-100 py-2 last:border-0">
                    <button
                      type="button"
                      class="flex min-w-0 items-center gap-2 text-left text-slate-700 hover:text-brand-600"
                      on:click={() => openDoc(d.id)}
                    >
                      <FileText class="h-4 w-4 shrink-0 text-slate-400" />
                      <span class="truncate">{d.title}</span>
                    </button>
                    <span class="shrink-0 text-xs text-slate-500">{formatDate(d.created_at)}</span>
                  </li>
                {/each}
              </ul>
            </div>
          {/each}
        </div>
      {/if}
    </Card>
  </div>

  <EquipmentEditModal bind:open={editOpen} equipment={eq} on:saved={onSaved} />
{/if}
