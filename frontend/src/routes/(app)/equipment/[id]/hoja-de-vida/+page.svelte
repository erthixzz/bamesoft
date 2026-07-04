<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { page } from '$app/stores';
  import { FileText, Save, FileDown, Paperclip, ArrowLeft } from 'lucide-svelte';

  import PageHeader from '$lib/components/PageHeader.svelte';
  import Card from '$lib/components/Card.svelte';
  import Button from '$lib/components/Button.svelte';
  import Spinner from '$lib/components/Spinner.svelte';
  import Input from '$lib/components/Input.svelte';
  import Select from '$lib/components/Select.svelte';
  import Textarea from '$lib/components/Textarea.svelte';
  import DatePicker from '$lib/components/DatePicker.svelte';
  import CheckChips from '$lib/modules/equipment/components/CheckChips.svelte';
  import HojaVidaPrintable from '$lib/modules/equipment/components/HojaVidaPrintable.svelte';

  import { equipmentApi } from '$lib/modules/equipment/api';
  import { documentsApi } from '$lib/modules/documents/api';
  import { exportLifeSheetPdf } from '$lib/modules/equipment/pdf';
  import {
    emptyLifeSheetData,
    type LifeSheet,
    type LifeSheetData,
    type SharedFields,
  } from '$lib/modules/equipment/lifeSheet';
  import { toasts } from '$lib/stores/toasts';
  import { setPageTitle } from '$lib/stores/page';
  import { isUuid } from '$lib/utils/slug';

  let id = '';
  let eqId = ''; // UUID real del equipo (la URL puede traer el código)
  let sheet: LifeSheet | null = null;
  let loading = true;
  let error: string | null = null;
  let saving = false;
  let exporting = false;
  let savingPdf = false;
  let printEl: HTMLElement;

  // Proxies de string para campos no-texto (los componentes de input emiten string).
  let reqCal = '';
  let costoStr = '';
  let vidaStr = '';

  $: id = $page.params.id ?? '';
  $: setPageTitle(sheet ? `Hoja de vida · ${sheet.code}` : 'Hoja de vida');

  type ContactKey = 'proveedor' | 'representante' | 'fabricante';
  const CONTACTS: { key: ContactKey; title: string }[] = [
    { key: 'proveedor', title: 'Proveedor' },
    { key: 'representante', title: 'Representante' },
    { key: 'fabricante', title: 'Fabricante' },
  ];

  /** Rellena nulls/ausentes del backend con los valores de una plantilla. */
  function normalize(tmpl: unknown, inc: unknown): unknown {
    if (inc === null || inc === undefined) return tmpl;
    if (Array.isArray(tmpl)) return Array.isArray(inc) ? inc : tmpl;
    if (tmpl && typeof tmpl === 'object') {
      const out: Record<string, unknown> = {};
      for (const k of Object.keys(tmpl as Record<string, unknown>)) {
        out[k] = normalize((tmpl as Record<string, unknown>)[k], (inc as Record<string, unknown>)?.[k]);
      }
      return out;
    }
    return inc;
  }

  const SHARED_TMPL: SharedFields = {
    name: '',
    brand: '',
    model: '',
    serial_number: '',
    manufacturer: '',
    risk_class: '',
    status: 'operational',
    location_id: '',
    acquisition_date: '',
    warranty_until: '',
    image_url: '',
    notes: '',
  };

  function hydrate(s: LifeSheet) {
    // Normalizar contra plantillas: nulls → '' para un binding consistente.
    s.data = normalize(emptyLifeSheetData(), s.data) as LifeSheetData;
    s.data.componentes = (s.data.componentes ?? []).map((c) => ({
      nombre: c?.nombre ?? '',
      marca: c?.marca ?? '',
      modelo: c?.modelo ?? '',
      serie: c?.serie ?? '',
    }));
    s.shared = normalize(SHARED_TMPL, s.shared) as SharedFields;
    s.formato_codigo = s.formato_codigo || 'MNT-FR-023';
    s.formato_fecha = s.formato_fecha || '';
    reqCal =
      s.data.mantenimiento.requiere_calibracion === true
        ? 'si'
        : s.data.mantenimiento.requiere_calibracion === false
          ? 'no'
          : '';
    costoStr = s.data.registro_historico.costo != null ? String(s.data.registro_historico.costo) : '';
    vidaStr =
      s.data.registro_historico.vida_util_anios != null
        ? String(s.data.registro_historico.vida_util_anios)
        : '';
    return s;
  }

  onMount(async () => {
    try {
      // La URL puede traer el código legible o un UUID; resolvemos el UUID.
      eqId = isUuid(id) ? id : (await equipmentApi.byCode(id)).id;
      sheet = hydrate(await equipmentApi.getLifeSheet(eqId));
    } catch (e) {
      error = e instanceof Error ? e.message : 'No se pudo cargar la hoja de vida.';
    } finally {
      loading = false;
    }
  });

  /** Convierte recursivamente cadenas vacías en null (las fechas/números vacíos
   *  rompen la validación de Pydantic; todos los campos del formato son opcionales). */
  function nullifyEmpty<T>(v: T): T {
    if (v === '') return null as unknown as T;
    if (Array.isArray(v)) return v.map((x) => nullifyEmpty(x)) as unknown as T;
    if (v && typeof v === 'object') {
      const o: Record<string, unknown> = {};
      for (const [k, val] of Object.entries(v as Record<string, unknown>)) o[k] = nullifyEmpty(val);
      return o as unknown as T;
    }
    return v;
  }

  function buildPayload() {
    if (!sheet) return null;
    const data = nullifyEmpty(structuredClone(sheet.data));
    data.mantenimiento.requiere_calibracion = reqCal === 'si' ? true : reqCal === 'no' ? false : null;
    data.registro_historico.costo = costoStr.trim() ? Number(costoStr) : null;
    data.registro_historico.vida_util_anios = vidaStr.trim() ? parseInt(vidaStr, 10) : null;
    return {
      data,
      formato_codigo: sheet.formato_codigo || null,
      formato_fecha: sheet.formato_fecha || null,
      shared: nullifyEmpty(structuredClone(sheet.shared)),
    };
  }

  async function save() {
    const payload = buildPayload();
    if (!payload) return;
    saving = true;
    try {
      sheet = hydrate(await equipmentApi.saveLifeSheet(eqId, payload));
      toasts.success('Hoja de vida guardada');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar');
    } finally {
      saving = false;
    }
  }

  async function generatePdf(): Promise<Blob | null> {
    if (!sheet) return null;
    await tick(); // asegurar que el nodo imprimible refleje el estado actual
    return exportLifeSheetPdf(printEl);
  }

  async function exportPdf() {
    exporting = true;
    try {
      const blob = await generatePdf();
      if (!blob || !sheet) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `hoja-de-vida-${sheet.code}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo exportar el PDF');
    } finally {
      exporting = false;
    }
  }

  async function savePdfToEquipment() {
    savingPdf = true;
    try {
      const blob = await generatePdf();
      if (!blob || !sheet) return;
      const file = new File([blob], `hoja-de-vida-${sheet.code}.pdf`, { type: 'application/pdf' });
      await documentsApi.upload(file, {
        title: `Hoja de Vida ${sheet.code}`,
        type: 'life_sheet',
        equipment_id: sheet.equipment_id,
      });
      toasts.success('PDF guardado en los documentos del equipo');
    } catch (e) {
      toasts.error(e instanceof Error ? e.message : 'No se pudo guardar el PDF');
    } finally {
      savingPdf = false;
    }
  }

  // ---- Catálogos de opciones ----
  const STATUS_OPTS = [
    { value: 'operational', label: 'Operativo' },
    { value: 'under_maintenance', label: 'En mantenimiento' },
    { value: 'out_of_service', label: 'Fuera de servicio' },
    { value: 'retired', label: 'Retirado' },
  ];
  const RISK_OPTS = [
    { value: 'I', label: 'I' },
    { value: 'IIa', label: 'IIa' },
    { value: 'IIb', label: 'IIb' },
    { value: 'III', label: 'III' },
  ];
  const REG_TIPO_OPTS = [
    { value: 'RS', label: 'RS (Registro Sanitario)' },
    { value: 'PC', label: 'PC (Permiso de Comercialización)' },
    { value: 'NR', label: 'NR (No Requiere)' },
  ];
  const MOVILIDAD_OPTS = [
    { value: 'movil', label: 'Móvil' },
    { value: 'fijo', label: 'Fijo' },
  ];
  const FORMA_ADQ_OPTS = [
    { value: 'compra', label: 'Compra' },
    { value: 'comodato', label: 'Comodato' },
    { value: 'donacion', label: 'Donación' },
    { value: 'alquiler', label: 'Alquiler' },
  ];
  const DOC_ADQ_OPTS = [
    { value: 'orden_compra', label: 'Orden de compra' },
    { value: 'factura', label: 'Factura' },
    { value: 'contrato', label: 'Contrato' },
  ];
  const FREC_MNT_OPTS = [
    { value: 'mensual', label: 'Mensual' },
    { value: 'bimensual', label: 'Bimensual' },
    { value: 'trimestral', label: 'Trimestral' },
    { value: 'cuatrimestral', label: 'Cuatrimestral' },
    { value: 'semestral', label: 'Semestral' },
    { value: 'anual', label: 'Anual' },
  ];
  const FREC_CAL_OPTS = [
    { value: 'semestral', label: 'Semestral' },
    { value: 'anual', label: 'Anual' },
    { value: 'bianual', label: 'Bianual' },
  ];
  const REQ_CAL_OPTS = [
    { value: 'si', label: 'Sí' },
    { value: 'no', label: 'No' },
  ];
  const TEC_PRED_OPTS = [
    { value: 'electrico', label: 'Eléctrico' },
    { value: 'electronico', label: 'Electrónico' },
    { value: 'mecanico', label: 'Mecánico' },
    { value: 'electromecanico', label: 'Electromecánico' },
    { value: 'hidraulico', label: 'Hidráulico' },
    { value: 'neumatico', label: 'Neumático' },
  ];
  const FUENTE_OPTS = [
    { value: 'agua', label: 'Agua' },
    { value: 'gas', label: 'Gas' },
    { value: 'aire', label: 'Aire' },
    { value: 'vapor', label: 'Vapor' },
    { value: 'electricidad', label: 'Electricidad' },
    { value: 'vacio', label: 'Vacío' },
    { value: 'otro', label: 'Otro' },
  ];
  const MANUALES_OPTS = [
    { value: 'operacion', label: 'Operación' },
    { value: 'mtto', label: 'Mantenimiento' },
    { value: 'partes', label: 'Partes' },
  ];
  const PLANOS_OPTS = [
    { value: 'electronico', label: 'Electrónico' },
    { value: 'electrico', label: 'Eléctrico' },
    { value: 'neumatico', label: 'Neumático' },
    { value: 'mecanico', label: 'Mecánico' },
  ];
  const CLAS_BIO_OPTS = [
    { value: 'diagnostico', label: 'Diagnóstico' },
    { value: 'prevencion', label: 'Prevención' },
    { value: 'rehabilitacion', label: 'Rehabilitación' },
    { value: 'analisis_lab', label: 'Análisis de laboratorio' },
    { value: 'tto_mto_vida', label: 'Tto y Mto de la vida' },
    { value: 'c_ambientales', label: 'Condiciones ambientales' },
  ];

  function addComponente() {
    if (!sheet) return;
    sheet.data.componentes = [
      ...sheet.data.componentes,
      { nombre: '', marca: '', modelo: '', serie: '' },
    ];
  }
  function removeComponente(i: number) {
    if (!sheet) return;
    sheet.data.componentes = sheet.data.componentes.filter((_, idx) => idx !== i);
  }
</script>

<PageHeader title="Hoja de vida" subtitle={sheet ? `${sheet.code}` : ''} icon={FileText}>
  <svelte:fragment slot="actions">
    <a class="btn-secondary" href={`/equipment/${sheet?.code ?? id}`}>
      <ArrowLeft class="h-4 w-4" /> Volver al equipo
    </a>
    <Button variant="secondary" on:click={exportPdf} loading={exporting} disabled={!sheet}>
      <FileDown class="h-4 w-4" /> Exportar PDF
    </Button>
    <Button variant="secondary" on:click={savePdfToEquipment} loading={savingPdf} disabled={!sheet}>
      <Paperclip class="h-4 w-4" /> Guardar PDF en el equipo
    </Button>
    <Button on:click={save} loading={saving} disabled={!sheet}>
      <Save class="h-4 w-4" /> Guardar
    </Button>
  </svelte:fragment>
</PageHeader>

{#if loading}
  <Spinner />
{:else if error || !sheet}
  <p class="text-danger-600">{error ?? 'No se encontró'}</p>
{:else}
  <!-- Encabezado branded: clínica + Bamesoft + datos del formato -->
  <div class="mb-4 flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between">
    <div class="flex items-center gap-3">
      {#if sheet.clinic?.logo_url}
        <img src={sheet.clinic.logo_url} alt={sheet.clinic.name} class="h-12 w-12 rounded-lg object-contain ring-1 ring-slate-200" />
      {:else}
        <span class="grid h-12 w-12 place-items-center rounded-lg bg-gradient-to-br from-brand-600 to-cyan-500 text-lg font-black text-white">
          {sheet.clinic?.name?.[0] ?? 'B'}
        </span>
      {/if}
      <div>
        <p class="text-base font-bold text-slate-900">{sheet.clinic?.name ?? 'Clínica'}</p>
        <p class="text-xs font-semibold uppercase tracking-wide text-brand-700">Hoja de Vida Equipo Biomédico</p>
      </div>
    </div>
    <div class="grid grid-cols-2 gap-2 sm:max-w-xs">
      <Input label="Código del formato" bind:value={sheet.formato_codigo} />
      <Input label="Fecha del formato" bind:value={sheet.formato_fecha} placeholder="3/Abril/2018" />
    </div>
  </div>

  <div class="space-y-4">
    <!-- IDENTIFICACIÓN -->
    <Card title="Identificación">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Input label="Código del equipo" bind:value={sheet.code} />
        <Input label="Activo fijo" bind:value={sheet.data.identificacion.activo_fijo} />
        <Select label="Registro (RS/PC/NR)" options={REG_TIPO_OPTS} bind:value={sheet.data.identificacion.registro_tipo} />
        <Input label="Número de registro" bind:value={sheet.data.identificacion.registro_numero} />
        <Input label="Código del prestador" bind:value={sheet.data.identificacion.codigo_prestador} />
        <Input label="Sede" bind:value={sheet.data.identificacion.sede} />
        <Input label="Distintivo" bind:value={sheet.data.identificacion.distintivo} />
        <Input label="Serie" bind:value={sheet.shared.serial_number} />
        <Select label="Estado" options={STATUS_OPTS} bind:value={sheet.shared.status} />
      </div>
      <div class="mt-4">
        <Textarea label="Descripción" rows={3} bind:value={sheet.data.identificacion.descripcion} />
      </div>
    </Card>

    <!-- EQUIPO -->
    <Card title="Equipo">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Input label="Nombre del equipo" bind:value={sheet.shared.name} />
        <Input label="Tipo / descripción corta" bind:value={sheet.data.equipo.tipo} />
        <Input label="Marca" bind:value={sheet.shared.brand} />
        <Input label="Modelo" bind:value={sheet.shared.model} />
        <Input label="Referencia / Lote" bind:value={sheet.data.equipo.referencia_lote} />
        <Input label="Servicio" bind:value={sheet.data.equipo.servicio} />
        <Input label="Ubicación" bind:value={sheet.data.equipo.ubicacion_texto} />
        <Select label="Movilidad" options={MOVILIDAD_OPTS} bind:value={sheet.data.equipo.movilidad} />
        <Select label="Clasificación por riesgo" options={RISK_OPTS} bind:value={sheet.shared.risk_class} />
      </div>
    </Card>

    <!-- REGISTRO HISTÓRICO -->
    <Card title="Registro histórico">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Select label="Forma de adquisición" options={FORMA_ADQ_OPTS} bind:value={sheet.data.registro_historico.forma_adquisicion} />
        <Select label="Documento de adquisición" options={DOC_ADQ_OPTS} bind:value={sheet.data.registro_historico.documento_adquisicion} />
        <DatePicker label="Fecha de compra" bind:value={sheet.shared.acquisition_date} />
        <DatePicker label="Acta de recibo" bind:value={sheet.data.registro_historico.acta_recibo} />
        <DatePicker label="Fecha de instalación" bind:value={sheet.data.registro_historico.fecha_instalacion} />
        <DatePicker label="Inicio de operación" bind:value={sheet.data.registro_historico.inicio_operacion} />
        <DatePicker label="Venc. garantía" bind:value={sheet.shared.warranty_until} />
        <DatePicker label="Fecha de fabricación" bind:value={sheet.data.registro_historico.fecha_fabricacion} />
        <Input label="Costo" type="number" bind:value={costoStr} />
        <Input label="Moneda" bind:value={sheet.data.registro_historico.moneda} />
        <Input label="Vida útil (años)" type="number" bind:value={vidaStr} />
      </div>
      <div class="mt-4">
        <CheckChips label="Tecnología predominante" options={TEC_PRED_OPTS} bind:value={sheet.data.registro_historico.tec_predominante} />
      </div>

      <div class="mt-5 grid gap-4 lg:grid-cols-3">
        {#each CONTACTS as c (c.key)}
          <div class="rounded-lg border border-slate-100 bg-slate-50/60 p-3">
            <p class="mb-2 text-sm font-semibold text-slate-700">{c.title}</p>
            <div class="space-y-2">
              <Input label="Nombre" bind:value={sheet.data.registro_historico[c.key].nombre} />
              <Input label="Teléfono" bind:value={sheet.data.registro_historico[c.key].telefono} />
              {#if c.key === 'fabricante'}
                <Input label="País" bind:value={sheet.data.registro_historico[c.key].pais} />
              {:else}
                <Input label="Correo" bind:value={sheet.data.registro_historico[c.key].correo} />
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </Card>

    <!-- REGISTRO TÉCNICO DE INSTALACIÓN -->
    <Card title="Registro técnico de instalación">
      <CheckChips label="Fuente de alimentación" options={FUENTE_OPTS} bind:value={sheet.data.tecnico.fuente_alimentacion} />
    </Card>

    <!-- REGISTRO TÉCNICO DE FUNCIONAMIENTO -->
    <Card title="Registro técnico de funcionamiento">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Input label="Voltaje máx." bind:value={sheet.data.tecnico.voltaje_max} />
        <Input label="Voltaje mín." bind:value={sheet.data.tecnico.voltaje_min} />
        <Input label="Corriente máx." bind:value={sheet.data.tecnico.corriente_max} />
        <Input label="Corriente mín." bind:value={sheet.data.tecnico.corriente_min} />
        <Input label="Potencia" bind:value={sheet.data.tecnico.potencia} />
        <Input label="Frecuencia" bind:value={sheet.data.tecnico.frecuencia} />
        <Input label="Presión" bind:value={sheet.data.tecnico.presion} />
        <Input label="Velocidad" bind:value={sheet.data.tecnico.velocidad} />
        <Input label="Peso" bind:value={sheet.data.tecnico.peso} />
        <Input label="Temperatura" bind:value={sheet.data.tecnico.temperatura} />
        <Input label="Otros (dimensiones…)" bind:value={sheet.data.tecnico.otros} />
      </div>

      <p class="mb-2 mt-5 text-sm font-semibold text-slate-700">Rangos de operación</p>
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Input label="Rango voltaje" bind:value={sheet.data.tecnico.rangos.voltaje} />
        <Input label="Rango corriente" bind:value={sheet.data.tecnico.rangos.corriente} />
        <Input label="Rango potencia" bind:value={sheet.data.tecnico.rangos.potencia} />
        <Input label="Rango humedad" bind:value={sheet.data.tecnico.rangos.humedad} />
        <Input label="Rango temperatura" bind:value={sheet.data.tecnico.rangos.temperatura} />
        <Input label="Rango frecuencia" bind:value={sheet.data.tecnico.rangos.frecuencia} />
        <Input label="Rango presión" bind:value={sheet.data.tecnico.rangos.presion} />
        <Input label="Rango velocidad" bind:value={sheet.data.tecnico.rangos.velocidad} />
      </div>

      <div class="mt-4 grid gap-4 lg:grid-cols-2">
        <Textarea label="Accesorios incluidos" rows={3} bind:value={sheet.data.tecnico.accesorios} />
        <Textarea label="Otras recomendaciones del fabricante" rows={3} bind:value={sheet.data.tecnico.recomendaciones} />
      </div>
    </Card>

    <!-- REGISTRO DE APOYO TÉCNICO -->
    <Card title="Registro de apoyo técnico">
      <div class="space-y-4">
        <CheckChips label="Manuales" options={MANUALES_OPTS} bind:value={sheet.data.apoyo_tecnico.manuales} />
        <CheckChips label="Planos" options={PLANOS_OPTS} bind:value={sheet.data.apoyo_tecnico.planos} />
        <CheckChips label="Clasificación biomédica" options={CLAS_BIO_OPTS} bind:value={sheet.data.apoyo_tecnico.clas_biomedica} />
      </div>
    </Card>

    <!-- COMPONENTES -->
    <Card title={`Componentes (${sheet.data.componentes.length})`}>
      <div slot="actions">
        <button type="button" class="btn-secondary" on:click={addComponente}>+ Agregar</button>
      </div>
      {#if sheet.data.componentes.length === 0}
        <p class="text-sm text-slate-400">Sin componentes. Usa “Agregar” para registrar nombre, marca, modelo y serie.</p>
      {:else}
        <div class="space-y-3">
          {#each sheet.data.componentes as comp, i (i)}
            <div class="grid gap-3 rounded-lg border border-slate-100 bg-slate-50/60 p-3 sm:grid-cols-4">
              <Input label="Nombre" bind:value={comp.nombre} />
              <Input label="Marca" bind:value={comp.marca} />
              <Input label="Modelo" bind:value={comp.modelo} />
              <div class="flex items-end gap-2">
                <div class="flex-1"><Input label="Serie" bind:value={comp.serie} /></div>
                <button type="button" class="btn-secondary mb-0.5 !px-3 text-danger-600" on:click={() => removeComponente(i)} aria-label="Quitar componente">✕</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </Card>

    <!-- MANTENIMIENTO -->
    <Card title="Mantenimiento">
      <div class="grid gap-4 sm:grid-cols-3">
        <Select label="Frecuencia de mantenimiento" options={FREC_MNT_OPTS} bind:value={sheet.data.mantenimiento.frec_mantenimiento} />
        <Select label="¿Requiere calibración?" options={REQ_CAL_OPTS} bind:value={reqCal} />
        <Select label="Frecuencia de calibración" options={FREC_CAL_OPTS} bind:value={sheet.data.mantenimiento.frec_calibracion} />
      </div>
    </Card>

    <!-- NOTAS (sincronizado con el equipo) -->
    <Card title="Notas">
      <Textarea rows={3} bind:value={sheet.shared.notes} placeholder="Notas generales del equipo…" />
    </Card>
  </div>

  <!-- Nodo imprimible (fuera de pantalla) para generar el PDF branded -->
  <div class="pointer-events-none fixed -left-[9999px] top-0" aria-hidden="true">
    <div bind:this={printEl}>
      <HojaVidaPrintable {sheet} />
    </div>
  </div>
{/if}
