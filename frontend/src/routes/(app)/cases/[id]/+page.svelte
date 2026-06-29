<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { page } from '$app/stores';
  import {
    Play,
    HandMetal,
    CheckCircle2,
    FileDown,
    Save,
    Paperclip,
    Camera,
    FileText,
    Download,
    Clock,
    History,
    ClipboardCheck,
    Images,
    MessageSquarePlus,
    Building2,
    User,
    UserCog,
    Wrench,
    ShieldAlert,
    PlusCircle,
    PencilLine,
    MessageSquare,
    Activity,
  } from 'lucide-svelte';

  import Card from '$lib/components/Card.svelte';
  import Input from '$lib/components/Input.svelte';
  import Button from '$lib/components/Button.svelte';
  import Select from '$lib/components/Select.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import SignaturePad from '$lib/components/SignaturePad.svelte';
  import CaseStatusBadge from '$lib/modules/cases/components/CaseStatusBadge.svelte';
  import PriorityBadge from '$lib/modules/cases/components/PriorityBadge.svelte';
  import CaseReportPrintable, {
    type CaseReport,
  } from '$lib/modules/cases/components/CaseReportPrintable.svelte';

  import { casesApi } from '$lib/modules/cases/api';
  import { documentsApi } from '$lib/modules/documents/api';
  import { equipmentApi } from '$lib/modules/equipment/api';
  import { clinicsApi } from '$lib/modules/clinics/api';
  import { usersApi } from '$lib/modules/users/api';
  import { sectorsApi } from '$lib/modules/sectors/api';
  import { exportNodeToPdf } from '$lib/modules/cases/pdf';
  import type { Case, CaseActivity } from '$lib/modules/cases/types';
  import type { Doc } from '$lib/modules/documents/types';
  import {
    TYPE_LABEL,
    TYPE_OPTIONS,
    COMPLETION_LABEL,
    COMPLETION_OPTIONS,
    STATUS_META,
    PRIORITY_META,
    elapsedBetween,
    actionLabel,
    parseActivityNote,
  } from '$lib/modules/cases/ui';
  import { formatDateTime, formatBytes } from '$lib/utils/format';
  import { setPageTitle } from '$lib/stores/page';
  import { toasts } from '$lib/stores/toasts';
  import { role } from '$lib/stores/auth';
  import { can, isOneOf } from '$lib/utils/permissions';

  let id = '';
  let c: Case | null = null;
  let activities: CaseActivity[] = [];
  let docs: Doc[] = [];
  let urlMap: Record<string, string> = {};
  let newNote = '';
  let loading = true;

  // Contexto resuelto para el soporte.
  let equipmentLabel = '—';
  let clinicName = 'Clínica';
  let clinicLogo: string | null = null;
  let sectorName = '—';
  let reporterName = '—';
  let assigneeName = '—';

  // Formulario de cierre / soporte (proxies de string para inputs numéricos).
  let fType = '';
  let fOperation = '';
  let fWork = '';
  let fPartsCount = '';
  let fPartsDetail = '';
  let fCompletion = '';
  let fReceiverName = '';
  let fReceiverDoc = '';

  let sigPad: SignaturePad;
  let sigDrawn = false;
  let errors: Record<string, string> = {};
  let savingClose = false;
  let accepting = false;
  let starting = false;
  let uploadingPhoto = false;
  let exporting = false;
  let savingPdf = false;
  let printEl: HTMLElement;

  $: id = $page.params.id ?? '';
  $: setPageTitle(c ? `Caso ${c.code}` : 'Caso');
  $: isEngineer = isOneOf($role, ['admin', 'engineer']);
  $: canUpload = can.uploadDocs($role);
  $: photoDocs = docs.filter((d) => d.type === 'photo');
  $: reportDocs = docs.filter((d) => d.type === 'report');
  $: latestSignature = docs.filter((d) => d.type === 'signature').at(-1) ?? null;
  $: hasSignature = sigDrawn || !!latestSignature;

  // Línea de tiempo del flujo de servicio (estado "Pendiente" si aún sin sellar).
  $: steps = c
    ? [
        { label: 'Reportado', at: c.opened_at },
        { label: 'Asignado', at: c.assigned_at },
        { label: 'Tomado por el ingeniero', at: c.accepted_at },
        { label: 'En trabajo', at: c.work_started_at },
        { label: 'Finalizado', at: c.finished_at },
        { label: 'Cerrado', at: c.closed_at },
      ]
    : [];

  const ACTION_ICON: Record<string, typeof Activity> = {
    created: PlusCircle,
    updated: PencilLine,
    accepted: HandMetal,
    note: MessageSquare,
  };
  const ACTION_TONE: Record<string, string> = {
    created: 'bg-brand-50 text-brand-600',
    updated: 'bg-amber-50 text-amber-600',
    accepted: 'bg-violet-50 text-violet-600',
    note: 'bg-slate-100 text-slate-500',
  };

  async function safe<T>(p: Promise<T>): Promise<T | null> {
    try {
      return await p;
    } catch {
      return null;
    }
  }

  function hydrateForm(x: Case) {
    fType = x.type ?? '';
    fOperation = x.operation_minutes != null ? String(x.operation_minutes) : '';
    fWork = x.work_performed ?? '';
    fPartsCount = x.parts_count != null ? String(x.parts_count) : '';
    fPartsDetail = x.parts_detail ?? '';
    fCompletion = x.completion ?? '';
    fReceiverName = x.receiver_name ?? '';
    fReceiverDoc = x.receiver_doc ?? '';
  }

  async function loadDocs() {
    docs = (await safe(documentsApi.forCase(id))) ?? [];
    // URLs firmadas para imágenes (fotos + firma) que necesitan visualizarse.
    const imgs = docs.filter((d) => d.type === 'photo' || d.type === 'signature');
    const entries = await Promise.all(
      imgs.map(async (d) => {
        const s = await safe(documentsApi.signedUrl(d.id));
        return [d.id, s?.url ?? ''] as const;
      }),
    );
    urlMap = Object.fromEntries(entries);
  }

  async function reload() {
    loading = true;
    try {
      [c, activities] = await Promise.all([casesApi.get(id), casesApi.activities(id)]);
      hydrateForm(c);
      await loadDocs();

      // Contexto del soporte (defensivo: errores no rompen la página).
      const eq = await safe(equipmentApi.get(c.equipment_id));
      if (eq) {
        equipmentLabel = `${eq.name} (${eq.code})`;
        if (eq.clinic_id) {
          const cl = await safe(clinicsApi.get(eq.clinic_id));
          if (cl) {
            clinicName = cl.name;
            clinicLogo = cl.logo_url ?? null;
          }
        }
      }
      sectorName = c.sector_id ? ((await safe(sectorsApi.get(c.sector_id)))?.name ?? '—') : '—';
      reporterName = c.reported_by
        ? ((await safe(usersApi.get(c.reported_by)))?.full_name ?? '—')
        : '—';
      assigneeName = c.assigned_to
        ? ((await safe(usersApi.get(c.assigned_to)))?.full_name ?? '—')
        : 'Sin asignar';
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo cargar el caso');
    } finally {
      loading = false;
    }
  }

  onMount(reload);

  async function addNote() {
    if (!newNote.trim()) return;
    try {
      await casesApi.addActivity(id, 'note', newNote);
      newNote = '';
      await reload();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'Error');
    }
  }

  async function takeCase() {
    accepting = true;
    try {
      c = await casesApi.accept(id);
      toasts.success('Caso tomado');
      await reload();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo tomar el caso');
    } finally {
      accepting = false;
    }
  }

  async function startWork() {
    starting = true;
    try {
      c = await casesApi.update(id, { status: 'in_progress' });
      toasts.success('Trabajo iniciado');
      await reload();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo iniciar el trabajo');
    } finally {
      starting = false;
    }
  }

  /** Sube la firma del pad (si hay trazo) y devuelve su storage_path. */
  async function uploadSignatureIfDrawn(): Promise<string | null> {
    if (!sigPad || sigPad.isEmpty() || !c) return c?.signature_path ?? null;
    const dataUrl = sigPad.toDataURL();
    if (!dataUrl) return c.signature_path ?? null;
    const blob = await (await fetch(dataUrl)).blob();
    const file = new File([blob], `firma-${c.code}.png`, { type: 'image/png' });
    const doc = await documentsApi.upload(file, {
      title: `Firma ${c.code}`,
      type: 'signature',
      case_id: c.id,
    });
    return doc.storage_path;
  }

  /** Valida el soporte. `close=true` exige además receptor + firma. */
  function validate(close: boolean): boolean {
    const e: Record<string, string> = {};
    if (!fType) e.fType = 'Selecciona el tipo de actividad';
    if (!fOperation.trim() || isNaN(Number(fOperation)))
      e.fOperation = 'Indica el tiempo de operación';
    if (!fWork.trim()) e.fWork = 'Describe la actividad realizada';
    if (!fCompletion) e.fCompletion = 'Indica el estado final (completo/incompleto)';
    if (close) {
      if (!fReceiverName.trim()) e.fReceiverName = 'Nombre de quien recibe';
      if (!fReceiverDoc.trim()) e.fReceiverDoc = 'Documento de quien recibe';
      if (!hasSignature) e.signature = 'Captura la firma de quien recibe';
    }
    errors = e;
    return Object.keys(e).length === 0;
  }

  async function saveClosure(close: boolean) {
    if (!c) return;
    if (!validate(close)) {
      toasts.error('Completa los campos obligatorios del soporte de servicio.');
      return;
    }
    savingClose = true;
    try {
      const signature_path = await uploadSignatureIfDrawn();
      c = await casesApi.update(id, {
        type: (fType || c.type) as Case['type'],
        operation_minutes: fOperation.trim() ? Number(fOperation) : null,
        work_performed: fWork.trim() || null,
        parts_count: fPartsCount.trim() ? Number(fPartsCount) : null,
        parts_detail: fPartsDetail.trim() || null,
        completion: (fCompletion || null) as Case['completion'],
        receiver_name: fReceiverName.trim() || null,
        receiver_doc: fReceiverDoc.trim() || null,
        signature_path,
        ...(close ? { status: 'closed' as const } : {}),
      });
      toasts.success(close ? 'Caso finalizado y cerrado' : 'Soporte guardado');
      await reload();
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar el soporte');
    } finally {
      savingClose = false;
    }
  }

  async function onPhoto(e: Event) {
    const input = e.currentTarget as HTMLInputElement;
    const files = Array.from(input.files ?? []);
    if (!files.length || !c) return;
    uploadingPhoto = true;
    try {
      for (const file of files) {
        await documentsApi.upload(file, {
          title: file.name,
          type: 'photo',
          case_id: c.id,
        });
      }
      await loadDocs();
      toasts.success(files.length > 1 ? `${files.length} fotos subidas` : 'Foto subida');
    } catch (err) {
      toasts.error(err instanceof Error ? err.message : 'No se pudo subir la foto');
    } finally {
      uploadingPhoto = false;
      input.value = '';
    }
  }

  async function openDoc(d: Doc) {
    try {
      const { url } = await documentsApi.signedUrl(d.id);
      window.open(url, '_blank');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo abrir el documento');
    }
  }

  function buildReport(): CaseReport | null {
    if (!c) return null;
    const num = (v: number | null | undefined) => (v != null ? String(v) : '—');
    return {
      clinicName,
      clinicLogo,
      code: c.code,
      statusLabel: STATUS_META[c.status].label,
      typeLabel: TYPE_LABEL[c.type],
      priorityLabel: PRIORITY_META[c.priority].label,
      completionLabel: c.completion ? COMPLETION_LABEL[c.completion] : '—',
      title: c.title,
      description: c.description ?? '—',
      equipmentLabel,
      sectorLabel: sectorName,
      reporterLabel: reporterName,
      assigneeLabel: assigneeName,
      times: [
        { k: 'Abierto', v: formatDateTime(c.opened_at) },
        { k: 'Asignado', v: formatDateTime(c.assigned_at) },
        { k: 'Tomado por el ingeniero', v: formatDateTime(c.accepted_at) },
        { k: 'Inicio de trabajo', v: formatDateTime(c.work_started_at) },
        { k: 'Finalizado', v: formatDateTime(c.finished_at) },
        { k: 'Cerrado', v: formatDateTime(c.closed_at) },
      ],
      operationLabel: c.operation_minutes != null ? `${c.operation_minutes} min` : '—',
      workPerformed: c.work_performed ?? '—',
      partsCount: num(c.parts_count),
      partsDetail: c.parts_detail ?? '—',
      receiverName: c.receiver_name ?? '—',
      receiverDoc: c.receiver_doc ?? '—',
      photos: photoDocs.map((d) => urlMap[d.id]).filter(Boolean),
      signature: latestSignature ? urlMap[latestSignature.id] : sigPad?.toDataURL() ?? null,
      generatedAt: formatDateTime(new Date()),
    };
  }

  let report: CaseReport | null = null;

  async function generatePdf(): Promise<Blob | null> {
    report = buildReport();
    if (!report) return null;
    await tick();
    return exportNodeToPdf(printEl);
  }

  async function exportPdf() {
    exporting = true;
    try {
      const blob = await generatePdf();
      if (!blob || !c) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `soporte-${c.code}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo exportar el PDF');
    } finally {
      exporting = false;
    }
  }

  async function savePdfToCase() {
    savingPdf = true;
    try {
      const blob = await generatePdf();
      if (!blob || !c) return;
      const file = new File([blob], `soporte-${c.code}.pdf`, { type: 'application/pdf' });
      await documentsApi.upload(file, {
        title: `Soporte de servicio ${c.code}`,
        type: 'report',
        case_id: c.id,
      });
      await loadDocs();
      toasts.success('Soporte guardado en la carpeta del caso');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar el soporte');
    } finally {
      savingPdf = false;
    }
  }
</script>

{#if loading}
  <Spinner label="Cargando caso…" />
{:else if c}
  <!-- Hero del caso -->
  <div class="animate-fade-up mb-4 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm shadow-slate-200/50">
    <div class="bg-grid bg-gradient-to-br from-slate-50 to-white p-4">
      <div class="flex flex-wrap items-start justify-between gap-2">
        <div class="min-w-0">
          <span class="inline-flex items-center rounded-md bg-slate-900 px-2 py-0.5 font-mono text-[11px] font-semibold tracking-wide text-white">
            {c.code}
          </span>
          <h1 class="mt-1.5 text-lg font-bold leading-tight text-slate-900 sm:text-xl">{c.title}</h1>
          {#if c.description}
            <p class="mt-0.5 max-w-2xl text-sm text-slate-500">{c.description}</p>
          {/if}
        </div>
        <div class="flex flex-wrap gap-1.5">
          <CaseStatusBadge status={c.status} />
          <PriorityBadge priority={c.priority} />
          <span class="badge bg-slate-100 text-slate-700">{TYPE_LABEL[c.type]}</span>
          {#if c.completion}
            <span class="badge {c.completion === 'complete' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}">
              {COMPLETION_LABEL[c.completion]}
            </span>
          {/if}
        </div>
      </div>

      <div class="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
        {#each [{ icon: Wrench, label: 'Equipo', value: equipmentLabel }, { icon: Building2, label: 'Unidad', value: sectorName }, { icon: User, label: 'Reportó', value: reporterName }, { icon: UserCog, label: 'Atiende', value: assigneeName }] as f}
          <div class="rounded-lg border border-slate-100 bg-white/70 px-3 py-2 backdrop-blur">
            <div class="section-label flex items-center gap-1.5">
              <svelte:component this={f.icon} class="h-3.5 w-3.5" />{f.label}
            </div>
            <p class="mt-0.5 truncate text-sm font-medium text-slate-800" title={f.value}>{f.value}</p>
          </div>
        {/each}
      </div>

      {#if isEngineer && c.status !== 'closed' && c.status !== 'cancelled'}
        <div class="mt-3 flex flex-wrap gap-2">
          {#if !c.accepted_at}
            <Button on:click={takeCase} loading={accepting}><HandMetal class="h-4 w-4" /> Tomar caso</Button>
          {/if}
          {#if c.status !== 'in_progress'}
            <Button variant="secondary" on:click={startWork} loading={starting}><Play class="h-4 w-4" /> Iniciar trabajo</Button>
          {/if}
        </div>
      {/if}
    </div>
  </div>

  <div class="grid gap-4 lg:grid-cols-3">
    <!-- Columna principal -->
    <div class="space-y-4 lg:col-span-2">
      <!-- Línea de tiempo del servicio -->
      <Card title="Tiempos del servicio" description="Trazabilidad del flujo de atención" icon={Clock} accent="cyan">
        <div>
          {#each steps as s, i}
            <div class="flex gap-3">
              <div class="flex flex-col items-center">
                <span class="grid h-4 w-4 shrink-0 place-items-center rounded-full {s.at ? 'bg-brand-600' : 'border border-dashed border-slate-300 bg-white'}">
                  {#if s.at}<span class="h-1.5 w-1.5 rounded-full bg-white"></span>{/if}
                </span>
                {#if i < steps.length - 1}
                  <span class="w-px flex-1 {s.at ? 'bg-brand-200' : 'bg-slate-200'}"></span>
                {/if}
              </div>
              <div class="{i < steps.length - 1 ? 'pb-4' : ''} min-w-0">
                <p class="text-sm font-medium {s.at ? 'text-slate-800' : 'text-slate-400'}">{s.label}</p>
                {#if s.at}
                  <p class="text-xs text-slate-500">{formatDateTime(s.at)}</p>
                {:else}
                  <p class="value-pending text-xs">No registrado aún</p>
                {/if}
              </div>
            </div>
          {/each}
        </div>

        <div class="mt-1 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-3 text-xs">
          <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">
            <ShieldAlert class="h-3.5 w-3.5" /> SLA: {c.sla_due_at ? formatDateTime(c.sla_due_at) : 'Sin definir'}
          </span>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">Respuesta: {elapsedBetween(c.assigned_at, c.accepted_at)}</span>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">A inicio: {elapsedBetween(c.accepted_at, c.work_started_at)}</span>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">Duración: {elapsedBetween(c.work_started_at, c.finished_at)}</span>
        </div>
      </Card>

      <!-- Soporte de servicio / cierre -->
      {#if isEngineer}
        <Card
          title="Soporte de servicio"
          description="Registra la actividad realizada y el cierre del caso"
          icon={ClipboardCheck}
          accent="emerald"
        >
          <div class="mb-4 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-500">
            Los campos con <span class="font-semibold text-danger-500">*</span> son obligatorios. Para
            <strong class="text-slate-600"> finalizar y cerrar</strong> también se requieren los datos de quien recibe y su firma.
          </div>
          <div class="grid gap-3 sm:grid-cols-2">
            <Select label="Tipo de actividad / mantenimiento *" bind:value={fType} options={TYPE_OPTIONS} error={errors.fType} />
            <Input label="Tiempo de operación (min) *" type="number" bind:value={fOperation} placeholder="Ej. 45" error={errors.fOperation} />
          </div>
          <div class="mt-3">
            <Textarea label="¿Qué actividad se hizo? *" bind:value={fWork} rows={3} placeholder="Describe el trabajo realizado…" required error={errors.fWork} />
          </div>
          <div class="mt-3 grid gap-3 sm:grid-cols-2">
            <Input label="Nº de repuestos" type="number" bind:value={fPartsCount} placeholder="0" />
            <Select label="Estado final *" bind:value={fCompletion} options={COMPLETION_OPTIONS} placeholder="— Selecciona —" error={errors.fCompletion} />
          </div>
          <div class="mt-3">
            <Textarea label="Detalle de repuestos" bind:value={fPartsDetail} rows={2} placeholder="Lista de repuestos usados…" />
          </div>

          <h4 class="section-label mt-6 mb-2">Recibido a satisfacción</h4>
          <div class="grid gap-3 sm:grid-cols-2">
            <Input label="Nombre de quien recibe" bind:value={fReceiverName} placeholder="Nombre completo" error={errors.fReceiverName} />
            <Input label="Documento / cédula" bind:value={fReceiverDoc} placeholder="C.C." error={errors.fReceiverDoc} />
          </div>
          <div class="mt-3">
            <SignaturePad bind:this={sigPad} label="Firma de quien recibe" on:change={(e) => (sigDrawn = e.detail)} />
            {#if errors.signature}
              <p class="mt-1 text-xs text-danger-600">{errors.signature}</p>
            {:else if latestSignature && urlMap[latestSignature.id]}
              <p class="mt-1 text-xs text-slate-400">Hay una firma guardada; dibuja una nueva para reemplazarla.</p>
            {/if}
          </div>

          <div class="mt-5 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
            <Button on:click={() => saveClosure(false)} loading={savingClose}>
              <Save class="h-4 w-4" /> Guardar soporte
            </Button>
            {#if c.status !== 'closed'}
              <Button variant="secondary" on:click={() => saveClosure(true)} loading={savingClose}>
                <CheckCircle2 class="h-4 w-4" /> Finalizar y cerrar
              </Button>
            {/if}
          </div>
        </Card>
      {/if}

      <!-- Evidencias y soportes -->
      <Card title="Evidencias y soportes" description="Fotos, firmas y reportes guardados del caso" icon={Images} accent="violet">
        <div class="mb-3 flex flex-wrap gap-2">
          {#if canUpload}
            <label class="btn-secondary inline-flex cursor-pointer items-center gap-2">
              <Camera class="h-4 w-4" />
              {uploadingPhoto ? 'Subiendo…' : 'Subir fotos'}
              <input type="file" accept="image/*" multiple class="hidden" on:change={onPhoto} disabled={uploadingPhoto} />
            </label>
          {/if}
          <Button variant="secondary" on:click={exportPdf} loading={exporting}>
            <FileDown class="h-4 w-4" /> Exportar soporte (PDF)
          </Button>
          {#if isEngineer}
            <Button variant="secondary" on:click={savePdfToCase} loading={savingPdf}>
              <Save class="h-4 w-4" /> Guardar soporte
            </Button>
          {/if}
        </div>

        {#if photoDocs.length}
          <div class="mb-4 grid grid-cols-3 gap-2 sm:grid-cols-4">
            {#each photoDocs as p (p.id)}
              <button type="button" class="block overflow-hidden rounded-lg border border-slate-200" on:click={() => openDoc(p)}>
                {#if urlMap[p.id]}
                  <img src={urlMap[p.id]} alt={p.title} class="h-24 w-full object-cover transition hover:opacity-80" />
                {:else}
                  <div class="grid h-24 w-full place-items-center bg-slate-50 text-slate-300"><Camera class="h-6 w-6" /></div>
                {/if}
              </button>
            {/each}
          </div>
        {/if}

        {#if reportDocs.length}
          <ul class="divide-y divide-slate-100">
            {#each reportDocs as d (d.id)}
              <li class="flex items-center justify-between gap-3 py-2">
                <div class="flex min-w-0 items-center gap-2">
                  <FileText class="h-4 w-4 shrink-0 text-brand-600" />
                  <div class="min-w-0">
                    <p class="truncate text-sm font-medium text-slate-700">{d.title}</p>
                    <p class="text-xs text-slate-400">{formatDateTime(d.created_at)} · {formatBytes(d.size_bytes)}</p>
                  </div>
                </div>
                <button type="button" class="btn-secondary" on:click={() => openDoc(d)}>
                  <Download class="h-4 w-4" />
                </button>
              </li>
            {/each}
          </ul>
        {:else if !photoDocs.length}
          <EmptyState icon={Paperclip} title="Sin soportes aún" description="Sube fotos o genera el soporte de servicio en PDF." />
        {/if}
      </Card>
    </div>

    <!-- Columna lateral: bitácora + nota -->
    <div class="space-y-4">
      <Card title="Bitácora" description="Histórico de actividades del caso" icon={History} accent="slate">
        <ol class="space-y-1">
          {#each activities as a, i (a.id)}
            {@const pairs = parseActivityNote(a.notes)}
            <li class="flex gap-3">
              <div class="flex flex-col items-center">
                <span class="grid h-7 w-7 shrink-0 place-items-center rounded-full {ACTION_TONE[a.action] ?? 'bg-slate-100 text-slate-500'}">
                  <svelte:component this={ACTION_ICON[a.action] ?? Activity} class="h-3.5 w-3.5" />
                </span>
                {#if i < activities.length - 1}
                  <span class="my-1 w-px flex-1 bg-slate-200"></span>
                {/if}
              </div>
              <div class="min-w-0 pb-3">
                <div class="flex flex-wrap items-center justify-between gap-x-2">
                  <span class="text-sm font-semibold text-slate-800">{actionLabel(a.action)}</span>
                  <span class="shrink-0 text-[11px] text-slate-400">{formatDateTime(a.created_at)}</span>
                </div>
                {#if pairs && pairs.length}
                  <ul class="mt-1.5 flex flex-wrap gap-1.5">
                    {#each pairs as p}
                      <li class="inline-flex items-center gap-1 rounded-md bg-slate-50 px-2 py-0.5 text-xs ring-1 ring-slate-100">
                        <span class="text-slate-400">{p.label}:</span>
                        <span class="font-medium text-slate-700">{p.value}</span>
                      </li>
                    {/each}
                  </ul>
                {:else if a.action === 'note' && a.notes}
                  <p class="mt-0.5 text-sm text-slate-600">{a.notes}</p>
                {/if}
              </div>
            </li>
          {:else}
            <li class="value-pending">Aún no hay actividad registrada.</li>
          {/each}
        </ol>
      </Card>

      <Card title="Añadir nota" icon={MessageSquarePlus} accent="brand">
        <Input bind:value={newNote} placeholder="Escribe una nota…" />
        <div class="mt-3"><Button on:click={addNote}>Añadir</Button></div>
      </Card>
    </div>
  </div>

  <!-- Nodo imprimible (fuera de pantalla) para generar el PDF branded -->
  <div class="pointer-events-none fixed -left-[9999px] top-0" aria-hidden="true">
    <div bind:this={printEl}>
      {#if report}
        <CaseReportPrintable {report} />
      {/if}
    </div>
  </div>
{/if}
