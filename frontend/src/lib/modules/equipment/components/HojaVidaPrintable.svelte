<script lang="ts">
  /** Representación imprimible (branded Bamesoft + clínica) de la hoja de vida.
   *  Usa estilos inline con colores hex para que html2canvas la capture fiel.
   *  Ancho fijo A4 @96dpi (794px). */
  import type { LifeSheet } from '$lib/modules/equipment/lifeSheet';
  import { formatDate } from '$lib/utils/format';

  export let sheet: LifeSheet;

  const LABELS: Record<string, string> = {
    operational: 'Operativo',
    under_maintenance: 'En mantenimiento',
    out_of_service: 'Fuera de servicio',
    retired: 'Retirado',
    movil: 'Móvil',
    fijo: 'Fijo',
    compra: 'Compra',
    comodato: 'Comodato',
    donacion: 'Donación',
    alquiler: 'Alquiler',
    orden_compra: 'Orden de compra',
    factura: 'Factura',
    contrato: 'Contrato',
    mensual: 'Mensual',
    bimensual: 'Bimensual',
    trimestral: 'Trimestral',
    cuatrimestral: 'Cuatrimestral',
    semestral: 'Semestral',
    anual: 'Anual',
    bianual: 'Bianual',
    electrico: 'Eléctrico',
    electronico: 'Electrónico',
    mecanico: 'Mecánico',
    electromecanico: 'Electromecánico',
    hidraulico: 'Hidráulico',
    neumatico: 'Neumático',
    agua: 'Agua',
    gas: 'Gas',
    aire: 'Aire',
    vapor: 'Vapor',
    electricidad: 'Electricidad',
    vacio: 'Vacío',
    otro: 'Otro',
    operacion: 'Operación',
    mtto: 'Mantenimiento',
    partes: 'Partes',
    diagnostico: 'Diagnóstico',
    prevencion: 'Prevención',
    rehabilitacion: 'Rehabilitación',
    analisis_lab: 'Análisis de laboratorio',
    tto_mto_vida: 'Tto y Mto de la vida',
    c_ambientales: 'Condiciones ambientales',
    RS: 'RS',
    PC: 'PC',
    NR: 'NR',
  };

  const lbl = (v: string | null | undefined) => (v ? (LABELS[v] ?? v) : '—');
  const txt = (v: string | number | null | undefined) =>
    v === null || v === undefined || v === '' ? '—' : String(v);
  const list = (arr: string[]) => (arr && arr.length ? arr.map((v) => LABELS[v] ?? v).join(', ') : '—');
  const dt = (v: string | null | undefined) => (v ? formatDate(v) : '—');

  $: d = sheet.data;
  $: s = sheet.shared;
</script>

<div
  style="width:794px;box-sizing:border-box;background:#ffffff;color:#0f172a;font-family:Inter,Arial,sans-serif;font-size:11px;line-height:1.35;padding:24px;"
>
  <!-- Encabezado -->
  <div style="display:flex;justify-content:space-between;align-items:center;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;">
    <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;">
      {#if sheet.clinic?.logo_url}
        <img src={sheet.clinic.logo_url} alt="logo" style="height:38px;width:38px;object-fit:contain;" />
      {:else}
        <div style="height:38px;width:38px;border-radius:8px;background:linear-gradient(135deg,#1971f5,#06b6d4);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:18px;">
          {sheet.clinic?.name?.[0] ?? 'B'}
        </div>
      {/if}
      <div>
        <div style="font-size:14px;font-weight:800;">{sheet.clinic?.name ?? 'Clínica'}</div>
        <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#1971f5;">
          Hoja de Vida · Equipo Biomédico
        </div>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;padding:10px 12px;border-left:1px solid #cbd5e1;min-width:210px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="height:36px;width:36px;border-radius:9px;background:linear-gradient(135deg,#1971f5,#06b6d4);color:#fff;font-weight:900;display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 1px 4px rgba(15,23,42,.2);">B</div>
        <div style="line-height:1.05;text-align:left;">
          <div style="font-size:20px;font-weight:900;letter-spacing:-.02em;color:#0f172a;">Bamesoft</div>
          <div style="font-size:8px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#1971f5;">Biomedical Software</div>
        </div>
      </div>
      <div style="font-size:10px;color:#475569;text-align:right;">
        <strong>Código:</strong> {txt(sheet.formato_codigo)} · <strong>Fecha:</strong> {txt(sheet.formato_fecha)}
      </div>
    </div>
  </div>

  {#each [{ t: 'Identificación', rows: [
        ['Código del equipo', txt(sheet.code)],
        ['Activo fijo', txt(d.identificacion.activo_fijo)],
        ['Registro', `${lbl(d.identificacion.registro_tipo)} ${txt(d.identificacion.registro_numero)}`],
        ['Código del prestador', txt(d.identificacion.codigo_prestador)],
        ['Sede', txt(d.identificacion.sede)],
        ['Distintivo', txt(d.identificacion.distintivo)],
        ['Serie', txt(s.serial_number)],
        ['Estado', lbl(s.status)],
      ], wide: [['Descripción', txt(d.identificacion.descripcion)]] },
      { t: 'Equipo', rows: [
        ['Nombre', txt(s.name)],
        ['Tipo', txt(d.equipo.tipo)],
        ['Marca', txt(s.brand)],
        ['Modelo', txt(s.model)],
        ['Referencia / Lote', txt(d.equipo.referencia_lote)],
        ['Servicio', txt(d.equipo.servicio)],
        ['Ubicación', txt(d.equipo.ubicacion_texto)],
        ['Movilidad', lbl(d.equipo.movilidad)],
        ['Clase de riesgo', txt(s.risk_class)],
      ] },
      { t: 'Registro histórico', rows: [
        ['Forma de adquisición', lbl(d.registro_historico.forma_adquisicion)],
        ['Documento', lbl(d.registro_historico.documento_adquisicion)],
        ['Fecha de compra', dt(s.acquisition_date)],
        ['Acta de recibo', dt(d.registro_historico.acta_recibo)],
        ['Fecha de instalación', dt(d.registro_historico.fecha_instalacion)],
        ['Inicio de operación', dt(d.registro_historico.inicio_operacion)],
        ['Venc. garantía', dt(s.warranty_until)],
        ['Fecha de fabricación', dt(d.registro_historico.fecha_fabricacion)],
        ['Costo', d.registro_historico.costo != null ? `${d.registro_historico.costo} ${d.registro_historico.moneda ?? ''}` : '—'],
        ['Vida útil', d.registro_historico.vida_util_anios != null ? `${d.registro_historico.vida_util_anios} años` : '—'],
      ], wide: [
        ['Tecnología predominante', list(d.registro_historico.tec_predominante)],
        ['Proveedor', `${txt(d.registro_historico.proveedor.nombre)} · ${txt(d.registro_historico.proveedor.telefono)} · ${txt(d.registro_historico.proveedor.correo)}`],
        ['Representante', `${txt(d.registro_historico.representante.nombre)} · ${txt(d.registro_historico.representante.telefono)} · ${txt(d.registro_historico.representante.correo)}`],
        ['Fabricante', `${txt(d.registro_historico.fabricante.nombre)} · ${txt(d.registro_historico.fabricante.telefono)} · ${txt(d.registro_historico.fabricante.pais)}`],
      ] },
      { t: 'Registro técnico de funcionamiento', rows: [
        ['Voltaje máx.', txt(d.tecnico.voltaje_max)],
        ['Voltaje mín.', txt(d.tecnico.voltaje_min)],
        ['Corriente máx.', txt(d.tecnico.corriente_max)],
        ['Corriente mín.', txt(d.tecnico.corriente_min)],
        ['Potencia', txt(d.tecnico.potencia)],
        ['Frecuencia', txt(d.tecnico.frecuencia)],
        ['Presión', txt(d.tecnico.presion)],
        ['Velocidad', txt(d.tecnico.velocidad)],
        ['Peso', txt(d.tecnico.peso)],
        ['Temperatura', txt(d.tecnico.temperatura)],
        ['Rango voltaje', txt(d.tecnico.rangos.voltaje)],
        ['Rango corriente', txt(d.tecnico.rangos.corriente)],
        ['Rango temperatura', txt(d.tecnico.rangos.temperatura)],
        ['Rango frecuencia', txt(d.tecnico.rangos.frecuencia)],
      ], wide: [
        ['Fuente de alimentación', list(d.tecnico.fuente_alimentacion)],
        ['Otros', txt(d.tecnico.otros)],
        ['Accesorios', txt(d.tecnico.accesorios)],
        ['Recomendaciones', txt(d.tecnico.recomendaciones)],
      ] },
      { t: 'Apoyo técnico y mantenimiento', rows: [
        ['Frecuencia mantenimiento', lbl(d.mantenimiento.frec_mantenimiento)],
        ['Requiere calibración', d.mantenimiento.requiere_calibracion === true ? 'Sí' : d.mantenimiento.requiere_calibracion === false ? 'No' : '—'],
        ['Frecuencia calibración', lbl(d.mantenimiento.frec_calibracion)],
      ], wide: [
        ['Manuales', list(d.apoyo_tecnico.manuales)],
        ['Planos', list(d.apoyo_tecnico.planos)],
        ['Clasificación biomédica', list(d.apoyo_tecnico.clas_biomedica)],
      ] }] as section}
    <div style="margin-top:12px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;">
      <div style="background:#1971f5;color:#fff;font-weight:700;font-size:11px;padding:5px 10px;text-transform:uppercase;letter-spacing:.04em;">
        {section.t}
      </div>
      <div style="display:grid;grid-template-columns:repeat(2,1fr);">
        {#each section.rows as [k, v], i}
          <div style="display:flex;border-top:{i < 2 ? '0' : '1px'} solid #e2e8f0;{i % 2 === 0 ? 'border-right:1px solid #e2e8f0;' : ''}">
            <div style="width:42%;background:#f8fafc;color:#475569;font-weight:600;padding:5px 8px;">{k}</div>
            <div style="flex:1;padding:5px 8px;">{v}</div>
          </div>
        {/each}
      </div>
      {#if section.wide}
        <div>
          {#each section.wide as [k, v]}
            <div style="display:flex;border-top:1px solid #e2e8f0;">
              <div style="width:21%;background:#f8fafc;color:#475569;font-weight:600;padding:5px 8px;">{k}</div>
              <div style="flex:1;padding:5px 8px;white-space:pre-wrap;">{v}</div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/each}

  <!-- Componentes -->
  <div style="margin-top:12px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;">
    <div style="background:#1971f5;color:#fff;font-weight:700;font-size:11px;padding:5px 10px;text-transform:uppercase;letter-spacing:.04em;">
      Componentes
    </div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);background:#f8fafc;color:#475569;font-weight:600;">
      <div style="padding:5px 8px;">Nombre</div>
      <div style="padding:5px 8px;">Marca</div>
      <div style="padding:5px 8px;">Modelo</div>
      <div style="padding:5px 8px;">Serie</div>
    </div>
    {#if d.componentes.length === 0}
      <div style="padding:6px 8px;color:#94a3b8;border-top:1px solid #e2e8f0;">Sin componentes registrados.</div>
    {:else}
      {#each d.componentes as c}
        <div style="display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #e2e8f0;">
          <div style="padding:5px 8px;">{txt(c.nombre)}</div>
          <div style="padding:5px 8px;">{txt(c.marca)}</div>
          <div style="padding:5px 8px;">{txt(c.modelo)}</div>
          <div style="padding:5px 8px;">{txt(c.serie)}</div>
        </div>
      {/each}
    {/if}
  </div>

  <div style="margin-top:14px;display:flex;align-items:center;justify-content:center;gap:10px;background:linear-gradient(135deg,#1971f5,#06b6d4);color:#ffffff;border-radius:10px;padding:11px 16px;">
    <div style="height:24px;width:24px;border-radius:6px;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:15px;">B</div>
    <span style="font-size:14px;font-weight:800;letter-spacing:.02em;">Generado con Bamesoft Solutions</span>
    <span style="font-size:11px;opacity:.9;">· Información protegida</span>
  </div>
</div>
