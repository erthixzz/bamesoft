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
        <svg width="40" height="40" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
          <defs><linearGradient id="hvG" gradientUnits="userSpaceOnUse" x1="4" y1="2" x2="44" y2="46"><stop offset="0" stop-color="#1e3a8a"/><stop offset="0.5" stop-color="#1971f5"/><stop offset="1" stop-color="#06b6d4"/></linearGradient></defs>
          <rect x="1" y="1" width="46" height="46" rx="13" fill="url(#hvG)"/>
          <g stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"><path d="M1 17 H47 M1 31 H47 M17 1 V47 M31 1 V47"/></g>
          <g stroke="#7dd3fc" stroke-width="1.4" fill="none" stroke-linecap="round"><path d="M32.5 16 h6"/><path d="M34.5 32 h5"/></g>
          <g fill="#7dd3fc"><circle cx="39.2" cy="16" r="1.9"/><circle cx="40" cy="32" r="1.7"/></g>
          <g fill="#ffffff"><rect x="12" y="10" width="7.6" height="28" rx="2.6"/><path d="M13 10 h13 a7 7 0 0 1 0 14 H13 Z"/><path d="M13 23 h14 a7.6 7.6 0 0 1 0 15.2 H13 Z"/></g>
          <g fill="url(#hvG)"><path d="M19.6 14.3 h5.6 a3.85 3.85 0 0 1 0 7.7 H19.6 Z"/><path d="M19.6 26.7 h6.1 a4.15 4.15 0 0 1 0 8.3 H19.6 Z"/></g>
          <g fill="#34d399"><rect x="21.3" y="15.7" width="2" height="5.6" rx="0.9"/><rect x="19.5" y="17.5" width="5.6" height="2" rx="0.9"/></g>
        </svg>
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

  <div style="margin-top:18px;border-top:2px solid #1971f5;padding-top:12px;display:flex;align-items:center;justify-content:space-between;gap:12px;">
    <div style="display:flex;align-items:center;gap:9px;">
      <svg width="30" height="30" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
        <defs><linearGradient id="hvGf" gradientUnits="userSpaceOnUse" x1="4" y1="2" x2="44" y2="46"><stop offset="0" stop-color="#1e3a8a"/><stop offset="0.5" stop-color="#1971f5"/><stop offset="1" stop-color="#06b6d4"/></linearGradient></defs>
        <rect x="1" y="1" width="46" height="46" rx="13" fill="url(#hvGf)"/>
        <g fill="#ffffff"><rect x="12" y="10" width="7.6" height="28" rx="2.6"/><path d="M13 10 h13 a7 7 0 0 1 0 14 H13 Z"/><path d="M13 23 h14 a7.6 7.6 0 0 1 0 15.2 H13 Z"/></g>
        <g fill="url(#hvGf)"><path d="M19.6 14.3 h5.6 a3.85 3.85 0 0 1 0 7.7 H19.6 Z"/><path d="M19.6 26.7 h6.1 a4.15 4.15 0 0 1 0 8.3 H19.6 Z"/></g>
        <g fill="#34d399"><rect x="21.3" y="15.7" width="2" height="5.6" rx="0.9"/><rect x="19.5" y="17.5" width="5.6" height="2" rx="0.9"/></g>
      </svg>
      <div style="line-height:1.2;">
        <div style="font-size:12.5px;font-weight:800;color:#0f172a;">Bamesoft <span style="color:#1971f5;">Biomedical Suite</span></div>
        <div style="font-size:8px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#64748b;">IA · Ingeniería clínica · Cumplimiento</div>
      </div>
    </div>
    <div style="text-align:right;line-height:1.5;">
      <div style="font-size:9px;font-weight:700;color:#475569;">Documento generado con Bamesoft</div>
      <div style="font-size:8.5px;color:#94a3b8;">Información confidencial · No divulgar sin autorización</div>
    </div>
  </div>
</div>
