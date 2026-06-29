<script lang="ts" context="module">
  export interface CaseReportRow {
    k: string;
    v: string;
  }
  export interface CaseReport {
    clinicName: string;
    clinicLogo?: string | null;
    code: string;
    statusLabel: string;
    typeLabel: string;
    priorityLabel: string;
    completionLabel: string;
    title: string;
    description: string;
    equipmentLabel: string;
    sectorLabel: string;
    reporterLabel: string;
    assigneeLabel: string;
    /** Filas de tiempos del flujo (clave/valor ya formateadas). */
    times: CaseReportRow[];
    operationLabel: string;
    workPerformed: string;
    partsCount: string;
    partsDetail: string;
    receiverName: string;
    receiverDoc: string;
    /** URLs (firmadas o dataURL) de las fotos de evidencia. */
    photos: string[];
    /** URL/dataURL de la firma de quien recibe. */
    signature?: string | null;
    generatedAt: string;
  }
</script>

<script lang="ts">
  /** Soporte de servicio imprimible (branded Bamesoft + clínica).
   *  Estilos inline con hex para captura fiel por html2canvas. Ancho A4 794px. */
  export let report: CaseReport;

  const txt = (v: string | null | undefined) => (v === null || v === undefined || v === '' ? '—' : v);
</script>

<div
  style="width:794px;box-sizing:border-box;background:#ffffff;color:#0f172a;font-family:Inter,Arial,sans-serif;font-size:11px;line-height:1.4;padding:24px;"
>
  <!-- Encabezado -->
  <div style="display:flex;justify-content:space-between;align-items:center;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;">
    <div style="display:flex;align-items:center;gap:10px;padding:10px 12px;">
      {#if report.clinicLogo}
        <img src={report.clinicLogo} alt="logo" style="height:38px;width:38px;object-fit:contain;" />
      {:else}
        <div style="height:38px;width:38px;border-radius:8px;background:linear-gradient(135deg,#1971f5,#06b6d4);color:#fff;font-weight:800;display:flex;align-items:center;justify-content:center;font-size:18px;">
          {report.clinicName?.[0] ?? 'B'}
        </div>
      {/if}
      <div>
        <div style="font-size:14px;font-weight:800;">{txt(report.clinicName)}</div>
        <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#1971f5;">
          Soporte de Servicio · Caso {report.code}
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
        <strong>Generado:</strong> {txt(report.generatedAt)}
      </div>
    </div>
  </div>

  <!-- Bloques clave/valor -->
  {#each [
      { t: 'Información del caso', rows: [
        ['Código', report.code],
        ['Estado', report.statusLabel],
        ['Tipo', report.typeLabel],
        ['Prioridad', report.priorityLabel],
        ['Equipo', report.equipmentLabel],
        ['Unidad de servicio', report.sectorLabel],
        ['Reportado por', report.reporterLabel],
        ['Atendido por', report.assigneeLabel],
      ], wide: [['Asunto', report.title], ['Descripción', report.description]] },
      { t: 'Tiempos del servicio', rows: [
        ...report.times.map((r) => [r.k, r.v]),
        ['Tiempo de operación', report.operationLabel],
      ] },
      { t: 'Actividad realizada', rows: [
        ['Estado final', report.completionLabel],
        ['Nº de repuestos', report.partsCount],
      ], wide: [
        ['¿Qué actividad se hizo?', report.workPerformed],
        ['Detalle de repuestos', report.partsDetail],
      ] },
    ] as section}
    <div style="margin-top:12px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;">
      <div style="background:#1971f5;color:#fff;font-weight:700;font-size:11px;padding:5px 10px;text-transform:uppercase;letter-spacing:.04em;">
        {section.t}
      </div>
      <div style="display:grid;grid-template-columns:repeat(2,1fr);">
        {#each section.rows as [k, v], i}
          <div style="display:flex;border-top:{i < 2 ? '0' : '1px'} solid #e2e8f0;{i % 2 === 0 ? 'border-right:1px solid #e2e8f0;' : ''}">
            <div style="width:42%;background:#f8fafc;color:#475569;font-weight:600;padding:5px 8px;">{k}</div>
            <div style="flex:1;padding:5px 8px;">{txt(v)}</div>
          </div>
        {/each}
      </div>
      {#if section.wide}
        <div>
          {#each section.wide as [k, v]}
            <div style="display:flex;border-top:1px solid #e2e8f0;">
              <div style="width:21%;background:#f8fafc;color:#475569;font-weight:600;padding:5px 8px;">{k}</div>
              <div style="flex:1;padding:5px 8px;white-space:pre-wrap;">{txt(v)}</div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/each}

  <!-- Evidencias fotográficas -->
  {#if report.photos.length}
    <div style="margin-top:12px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;">
      <div style="background:#1971f5;color:#fff;font-weight:700;font-size:11px;padding:5px 10px;text-transform:uppercase;letter-spacing:.04em;">
        Evidencias fotográficas
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:8px;">
        {#each report.photos as src}
          <img {src} alt="evidencia" style="width:100%;height:150px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0;" />
        {/each}
      </div>
    </div>
  {/if}

  <!-- Recibido por -->
  <div style="margin-top:12px;border:1px solid #cbd5e1;border-radius:8px;overflow:hidden;">
    <div style="background:#1971f5;color:#fff;font-weight:700;font-size:11px;padding:5px 10px;text-transform:uppercase;letter-spacing:.04em;">
      Recibido a satisfacción
    </div>
    <div style="display:flex;gap:12px;padding:12px;align-items:flex-end;">
      <div style="flex:1;">
        <div style="display:flex;border:1px solid #e2e8f0;border-radius:6px;overflow:hidden;margin-bottom:6px;">
          <div style="width:42%;background:#f8fafc;color:#475569;font-weight:600;padding:5px 8px;">Nombre</div>
          <div style="flex:1;padding:5px 8px;">{txt(report.receiverName)}</div>
        </div>
        <div style="display:flex;border:1px solid #e2e8f0;border-radius:6px;overflow:hidden;">
          <div style="width:42%;background:#f8fafc;color:#475569;font-weight:600;padding:5px 8px;">Documento</div>
          <div style="flex:1;padding:5px 8px;">{txt(report.receiverDoc)}</div>
        </div>
      </div>
      <div style="width:260px;text-align:center;">
        {#if report.signature}
          <img src={report.signature} alt="firma" style="width:100%;height:90px;object-fit:contain;" />
        {:else}
          <div style="height:90px;"></div>
        {/if}
        <div style="border-top:1px solid #0f172a;margin-top:2px;padding-top:4px;color:#475569;">Firma</div>
      </div>
    </div>
  </div>

  <div style="margin-top:14px;display:flex;align-items:center;justify-content:center;gap:10px;background:linear-gradient(135deg,#1971f5,#06b6d4);color:#ffffff;border-radius:10px;padding:11px 16px;">
    <div style="height:24px;width:24px;border-radius:6px;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:15px;">B</div>
    <span style="font-size:14px;font-weight:800;letter-spacing:.02em;">Generado con Bamesoft Solutions</span>
    <span style="font-size:11px;opacity:.9;">· Información protegida</span>
  </div>
</div>
