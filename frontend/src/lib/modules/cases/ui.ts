/** Metadatos visuales y utilidades compartidas de casos.
 *  Centraliza colores de "semáforo", opciones de selects y cálculos de
 *  edad / SLA para que dashboard, lista y detalle se vean coherentes.
 */
import type {
  CaseCompletion,
  CasePriority,
  CaseStatus,
  CaseType,
  SatisfactionScore,
  TecnovigilanciaStage,
} from '$lib/api/types';
import type { Case } from './types';

export interface PriorityMeta {
  label: string;
  color: string; // hex del punto/semáforo
  glow: string; // rgba para el resplandor (--glow)
  pulse: boolean; // ¿debe titilar?
  rank: number; // para ordenar (mayor = más urgente)
}

export const PRIORITY_META: Record<CasePriority, PriorityMeta> = {
  low: { label: 'Baja', color: '#64748b', glow: 'rgba(100,116,139,.5)', pulse: false, rank: 0 },
  medium: { label: 'Media', color: '#f59e0b', glow: 'rgba(245,158,11,.55)', pulse: false, rank: 1 },
  high: { label: 'Alta', color: '#f97316', glow: 'rgba(249,115,22,.6)', pulse: true, rank: 2 },
  critical: { label: 'Crítica', color: '#ef4444', glow: 'rgba(239,68,68,.7)', pulse: true, rank: 3 },
};

export interface StatusMeta {
  label: string;
  color: string; // hex del acento del estado
  tint: string; // fondo suave (tailwind class)
  text: string; // texto (tailwind class)
}

export const STATUS_META: Record<CaseStatus, StatusMeta> = {
  open: { label: 'Abierto', color: '#1971f5', tint: 'bg-brand-50', text: 'text-brand-700' },
  assigned: { label: 'Asignado', color: '#8b5cf6', tint: 'bg-violet-50', text: 'text-violet-700' },
  in_progress: { label: 'En progreso', color: '#f59e0b', tint: 'bg-amber-50', text: 'text-amber-700' },
  waiting_parts: { label: 'Esp. repuestos', color: '#fb923c', tint: 'bg-orange-50', text: 'text-orange-700' },
  waiting_client: { label: 'Esp. cliente', color: '#a855f7', tint: 'bg-purple-50', text: 'text-purple-700' },
  closed: { label: 'Cerrado', color: '#10b981', tint: 'bg-emerald-50', text: 'text-emerald-700' },
  cancelled: { label: 'Cancelado', color: '#94a3b8', tint: 'bg-slate-100', text: 'text-slate-600' },
};

export const TYPE_LABEL: Record<CaseType, string> = {
  corrective: 'Correctivo',
  preventive: 'Preventivo',
  calibration: 'Calibración',
  installation: 'Instalación',
  inspection: 'Inspección',
  mishandling: 'Daño por mal manejo',
};

export const STATUS_OPTIONS = (Object.keys(STATUS_META) as CaseStatus[]).map((value) => ({
  value,
  label: STATUS_META[value].label,
}));

export const PRIORITY_OPTIONS = (Object.keys(PRIORITY_META) as CasePriority[]).map((value) => ({
  value,
  label: PRIORITY_META[value].label,
}));

export const TYPE_OPTIONS = (Object.keys(TYPE_LABEL) as CaseType[]).map((value) => ({
  value,
  label: TYPE_LABEL[value],
}));

export const COMPLETION_LABEL: Record<CaseCompletion, string> = {
  complete: 'Completo',
  incomplete: 'Incompleto',
};

export const COMPLETION_OPTIONS = (Object.keys(COMPLETION_LABEL) as CaseCompletion[]).map(
  (value) => ({ value, label: COMPLETION_LABEL[value] }),
);

// ---- Satisfacción del servicio · Likert de 7 puntos ------------------------
// «¿Qué tan satisfecho(a) está con el servicio?» — 1 Muy insatisfecho …
// 7 Muy satisfecho. Sustituye a las 3 caritas (bueno/regular/malo).

export type SatisfactionGroup = 'negative' | 'neutral' | 'positive';

export interface SatisfactionMeta {
  score: SatisfactionScore;
  label: string; // «Algo satisfecho»
  color: string; // hex del acento (también para el PDF y las gráficas)
  tint: string; // fondo suave (tailwind) del punto seleccionado
  text: string; // color del texto (tailwind)
  group: SatisfactionGroup;
}

export const SATISFACTION_SCALE: SatisfactionMeta[] = [
  { score: 1, label: 'Muy insatisfecho', color: '#b91c1c', tint: 'bg-danger-100', text: 'text-danger-800', group: 'negative' },
  { score: 2, label: 'Insatisfecho', color: '#ef4444', tint: 'bg-danger-50', text: 'text-danger-700', group: 'negative' },
  { score: 3, label: 'Algo insatisfecho', color: '#f97316', tint: 'bg-orange-50', text: 'text-orange-700', group: 'negative' },
  { score: 4, label: 'Neutral', color: '#94a3b8', tint: 'bg-slate-100', text: 'text-slate-600', group: 'neutral' },
  { score: 5, label: 'Algo satisfecho', color: '#84cc16', tint: 'bg-lime-50', text: 'text-lime-700', group: 'positive' },
  { score: 6, label: 'Satisfecho', color: '#22c55e', tint: 'bg-green-50', text: 'text-green-700', group: 'positive' },
  { score: 7, label: 'Muy satisfecho', color: '#059669', tint: 'bg-emerald-50', text: 'text-emerald-700', group: 'positive' },
];

export const SATISFACTION_BY_SCORE: Record<number, SatisfactionMeta> = Object.fromEntries(
  SATISFACTION_SCALE.map((s) => [s.score, s]),
);

export const SATISFACTION_QUESTION = '¿Qué tan satisfecho(a) está con el servicio?';

/** «Algo satisfecho» — solo la etiqueta; '—' si aún sin calificar. */
export function satisfactionLabel(score: number | null | undefined): string {
  return score ? (SATISFACTION_BY_SCORE[score]?.label ?? String(score)) : '—';
}

/** «5 — Algo satisfecho» (formato completo, para PDF y bitácora). */
export function satisfactionFull(score: number | null | undefined): string {
  return score && SATISFACTION_BY_SCORE[score]
    ? `${score} — ${SATISFACTION_BY_SCORE[score].label}`
    : '—';
}

export function satisfactionColor(score: number | null | undefined): string {
  return (score && SATISFACTION_BY_SCORE[score]?.color) || '#cbd5e1';
}

export const SATISFACTION_OPTIONS = SATISFACTION_SCALE.map((s) => ({
  value: String(s.score),
  label: `${s.score} — ${s.label}`,
}));

/** Agrupación para KPIs: 5-7 satisfechos · 4 neutral · 1-3 insatisfechos. */
export const SATISFACTION_GROUP_META: Record<
  SatisfactionGroup,
  { label: string; hint: string; scores: SatisfactionScore[]; color: string; text: string }
> = {
  positive: {
    label: 'Satisfechos',
    hint: 'Calificaciones 5 a 7 (algo satisfecho, satisfecho, muy satisfecho).',
    scores: [5, 6, 7],
    color: '#22c55e',
    text: 'text-emerald-700',
  },
  neutral: {
    label: 'Neutrales',
    hint: 'Calificación 4 (ni satisfecho ni insatisfecho).',
    scores: [4],
    color: '#94a3b8',
    text: 'text-slate-600',
  },
  negative: {
    label: 'Insatisfechos',
    hint: 'Calificaciones 1 a 3 (algo insatisfecho, insatisfecho, muy insatisfecho).',
    scores: [1, 2, 3],
    color: '#ef4444',
    text: 'text-danger-700',
  },
};

export function satisfactionGroup(score: number | null | undefined): SatisfactionGroup | null {
  return score ? (SATISFACTION_BY_SCORE[score]?.group ?? null) : null;
}

// ---- Tecnovigilancia -------------------------------------------------------
// Un caso de tecnovigilancia es un evento adverso o incidente en el que el
// dispositivo causó (o pudo causar) daño al paciente o al operador. El proceso
// tiene etapas: se detecta, se reporta, se investiga, se corrige, se hace
// seguimiento y se cierra.

export interface TecnovigilanciaStageMeta {
  label: string;
  /** Qué significa la etapa (se muestra dentro del modal, junto a cada opción). */
  description: string;
  color: string; // hex del acento
  tint: string; // fondo suave (tailwind)
  text: string; // texto (tailwind)
}

export const TECNOVIGILANCIA_STAGE_ORDER: TecnovigilanciaStage[] = [
  'detection',
  'report',
  'investigation',
  'corrective_action',
  'follow_up',
  'closed',
];

export const TECNOVIGILANCIA_STAGE_META: Record<TecnovigilanciaStage, TecnovigilanciaStageMeta> = {
  detection: {
    label: 'Detección',
    description: 'Se identificó el evento adverso o incidente con el equipo.',
    color: '#f97316',
    tint: 'bg-orange-50',
    text: 'text-orange-700',
  },
  report: {
    label: 'Reporte',
    description: 'Notificado al comité de tecnovigilancia y/o al INVIMA.',
    color: '#ef4444',
    tint: 'bg-danger-50',
    text: 'text-danger-700',
  },
  investigation: {
    label: 'Investigación',
    description: 'Análisis de causa raíz: qué falló y por qué.',
    color: '#8b5cf6',
    tint: 'bg-violet-50',
    text: 'text-violet-700',
  },
  corrective_action: {
    label: 'Acción correctiva',
    description: 'Se ejecutan las acciones correctivas o preventivas definidas.',
    color: '#1971f5',
    tint: 'bg-brand-50',
    text: 'text-brand-700',
  },
  follow_up: {
    label: 'Seguimiento',
    description: 'Verificación de que las acciones tomadas fueron eficaces.',
    color: '#06b6d4',
    tint: 'bg-cyan-50',
    text: 'text-cyan-700',
  },
  closed: {
    label: 'Cerrado',
    description: 'El proceso de tecnovigilancia terminó y quedó documentado.',
    color: '#10b981',
    tint: 'bg-emerald-50',
    text: 'text-emerald-700',
  },
};

export const TECNOVIGILANCIA_STAGE_OPTIONS = TECNOVIGILANCIA_STAGE_ORDER.map((value) => ({
  value,
  label: TECNOVIGILANCIA_STAGE_META[value].label,
}));

/** Metadatos de la etapa a partir de un string suelto (API, filtros); `null` si
 *  no corresponde a ninguna etapa conocida. */
export function tecnovigilanciaStageMeta(
  stage: string | null | undefined,
): TecnovigilanciaStageMeta | null {
  return stage ? (TECNOVIGILANCIA_STAGE_META[stage as TecnovigilanciaStage] ?? null) : null;
}

export function tecnovigilanciaStageLabel(stage: string | null | undefined): string {
  return tecnovigilanciaStageMeta(stage)?.label ?? (stage || '—');
}

/** Descripción corta de cada estado (para la leyenda "?"). */
export const STATUS_DESCRIPTIONS: Record<CaseStatus, string> = {
  open: 'Reportado, aún sin ingeniero asignado.',
  assigned: 'Asignado a un ingeniero; pendiente de iniciar.',
  in_progress: 'El ingeniero está trabajando en el caso.',
  waiting_parts: 'En pausa esperando repuestos o insumos.',
  waiting_client: 'En pausa esperando respuesta o acción del cliente.',
  closed: 'Resuelto y cerrado.',
  cancelled: 'Anulado; no se le dará seguimiento.',
};

/** Descripción corta de cada prioridad (para la leyenda "?"). */
export const PRIORITY_DESCRIPTIONS: Record<CasePriority, string> = {
  low: 'Sin urgencia; puede atenderse cuando haya disponibilidad.',
  medium: 'Atención normal dentro del flujo habitual.',
  high: 'Requiere atención pronta (el indicador titila).',
  critical: 'Máxima urgencia; impacta la operación (el indicador titila).',
};

/** Agrupación de estados para la gráfica/filtro del dashboard.
 *  "En espera" combina esperando repuestos + esperando cliente. */
export interface StatusGroup {
  key: string;
  label: string;
  color: string;
  statuses: CaseStatus[];
}

export const STATUS_GROUPS: StatusGroup[] = [
  { key: 'open', label: 'Abierto', color: STATUS_META.open.color, statuses: ['open'] },
  { key: 'assigned', label: 'Asignado', color: STATUS_META.assigned.color, statuses: ['assigned'] },
  { key: 'in_progress', label: 'En progreso', color: STATUS_META.in_progress.color, statuses: ['in_progress'] },
  { key: 'waiting', label: 'En espera', color: STATUS_META.waiting_parts.color, statuses: ['waiting_parts', 'waiting_client'] },
  { key: 'closed', label: 'Cerrado', color: STATUS_META.closed.color, statuses: ['closed'] },
  { key: 'cancelled', label: 'Cancelado', color: STATUS_META.cancelled.color, statuses: ['cancelled'] },
];

export const STATUS_GROUP_OPTIONS = STATUS_GROUPS.map((g) => ({ value: g.key, label: g.label }));

/** Descripción corta de cada grupo de estado resumido (para la leyenda "?"). */
export const STATUS_GROUP_DESCRIPTIONS: Record<string, string> = {
  open: 'Reportado, aún sin ingeniero asignado.',
  assigned: 'Asignado a un ingeniero; pendiente de iniciar.',
  in_progress: 'El ingeniero está trabajando en el caso.',
  waiting: 'En pausa esperando repuestos, insumos o respuesta del cliente.',
  closed: 'Resuelto y cerrado.',
  cancelled: 'Anulado; no se le dará seguimiento.',
};

/** Clave del grupo resumido al que pertenece un estado concreto. */
export function statusGroupKey(status: CaseStatus): string {
  return STATUS_GROUPS.find((g) => g.statuses.includes(status))?.key ?? status;
}

/** Traduce la clave de un grupo resumido al estado concreto que se guardará.
 *  Si el caso ya está dentro del grupo, conserva su subestado actual
 *  (p. ej. no convierte "Esp. cliente" en "Esp. repuestos" sin necesidad). */
export function groupToStatus(key: string, current: CaseStatus): CaseStatus {
  const group = STATUS_GROUPS.find((g) => g.key === key);
  if (!group) return current;
  if (group.statuses.includes(current)) return current;
  return group.statuses[0];
}

/** Estados que cuentan como "activos" (no cerrados/cancelados). */
export const ACTIVE_STATUSES: CaseStatus[] = [
  'open',
  'assigned',
  'in_progress',
  'waiting_parts',
  'waiting_client',
];

export function isActive(c: Case): boolean {
  return ACTIVE_STATUSES.includes(c.status);
}

/** Horas transcurridas desde la apertura (o creación) hasta el cierre o ahora. */
export function caseAgeHours(c: Case): number {
  const start = c.opened_at ?? c.created_at;
  if (!start) return 0;
  const end = c.closed_at ? new Date(c.closed_at) : new Date();
  const ms = end.getTime() - new Date(start).getTime();
  return Math.max(0, ms / 3_600_000);
}

/** "2d 4h", "5h", "45m" — compacto. */
export function formatAge(hours: number): string {
  if (hours < 1) return `${Math.max(1, Math.round(hours * 60))}m`;
  if (hours < 24) return `${Math.round(hours)}h`;
  const d = Math.floor(hours / 24);
  const h = Math.round(hours % 24);
  return h ? `${d}d ${h}h` : `${d}d`;
}

export type SlaState = 'none' | 'ok' | 'soon' | 'overdue';

export interface SlaInfo {
  state: SlaState;
  label: string;
  hoursLeft: number | null;
}

/** Estado del SLA. "soon" si vence en <24h; "overdue" si ya venció (y sigue activo). */
export function slaInfo(c: Case): SlaInfo {
  if (!c.sla_due_at) return { state: 'none', label: 'Sin SLA', hoursLeft: null };
  const due = new Date(c.sla_due_at).getTime();
  const hoursLeft = (due - Date.now()) / 3_600_000;
  const closed = c.status === 'closed' || c.status === 'cancelled';
  if (closed) return { state: 'ok', label: 'SLA cumplido', hoursLeft };
  if (hoursLeft < 0) return { state: 'overdue', label: `Vencido ${formatAge(-hoursLeft)}`, hoursLeft };
  if (hoursLeft < 24) return { state: 'soon', label: `Vence en ${formatAge(hoursLeft)}`, hoursLeft };
  return { state: 'ok', label: `${formatAge(hoursLeft)} restantes`, hoursLeft };
}

// ---- Bitácora: traducción de acciones y notas a lenguaje legible ----------

/** Etiqueta en español para cada acción de la bitácora. */
export const ACTION_LABEL: Record<string, string> = {
  created: 'Caso creado',
  updated: 'Actualización del caso',
  accepted: 'Tomado por el ingeniero',
  note: 'Nota',
  tecnovigilancia: 'Marcado como tecnovigilancia',
};

export function actionLabel(action: string): string {
  return ACTION_LABEL[action] ?? action;
}

const FIELD_LABEL: Record<string, string> = {
  status: 'Estado',
  priority: 'Prioridad',
  type: 'Tipo',
  completion: 'Estado final',
  satisfaction_score: 'Satisfacción',
  tecnovigilancia: 'Tecnovigilancia',
  tecnovigilancia_stage: 'Etapa de tecnovigilancia',
  operation_minutes: 'Tiempo de operación',
  work_performed: 'Actividad realizada',
  parts_count: 'N.º de repuestos',
  parts_detail: 'Detalle de repuestos',
  receiver_name: 'Recibe',
  receiver_doc: 'Documento',
  title: 'Título',
  description: 'Descripción',
};

// Campos técnicos/ids que no aportan a un humano leyendo la bitácora.
const FIELD_HIDDEN = new Set([
  'signature_path',
  'assigned_to',
  'sector_id',
  'sla_due_at',
  'equipment_id',
]);

function humanValue(key: string, raw: string): string {
  const v = raw.trim();
  if (key === 'status') return STATUS_META[v as CaseStatus]?.label ?? v;
  if (key === 'completion') return COMPLETION_LABEL[v as CaseCompletion] ?? v;
  if (key === 'satisfaction_score') return satisfactionFull(Number(v));
  if (key === 'tecnovigilancia_stage') return tecnovigilanciaStageLabel(v);
  if (key === 'type') return TYPE_LABEL[v as CaseType] ?? v;
  if (key === 'priority') return PRIORITY_META[v as CasePriority]?.label ?? v;
  if (key === 'operation_minutes') return `${v} min`;
  return v.length > 80 ? `${v.slice(0, 80)}…` : v;
}

export interface NotePair {
  label: string;
  value: string;
}

/** Convierte una nota cruda ("k=v, k=v") en pares legibles en español.
 *  Devuelve `null` si la nota no tiene ese formato (texto libre / nota manual). */
export function parseActivityNote(notes: string | null): NotePair[] | null {
  if (!notes) return null;
  if (!/\w+=/.test(notes)) return null; // texto libre (nota, "Caso creado", …)
  const pairs: NotePair[] = [];
  const re = /(\w+)=(.*?)(?=,\s\w+=|$)/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(notes)) !== null) {
    const key = m[1];
    if (FIELD_HIDDEN.has(key)) continue;
    pairs.push({ label: FIELD_LABEL[key] ?? key, value: humanValue(key, m[2]) });
  }
  return pairs;
}

/** Diferencia humana entre dos instantes ISO; "—" si falta alguno. */
export function elapsedBetween(
  from: string | null | undefined,
  to: string | null | undefined,
): string {
  if (!from || !to) return '—';
  const ms = new Date(to).getTime() - new Date(from).getTime();
  if (ms < 0) return '—';
  return formatAge(ms / 3_600_000);
}

/** ¿Lleva demasiado tiempo abierto? (umbral por prioridad, en horas) */
export function isAging(c: Case): boolean {
  if (!isActive(c)) return false;
  const age = caseAgeHours(c);
  const threshold =
    c.priority === 'critical' ? 8 : c.priority === 'high' ? 24 : c.priority === 'medium' ? 72 : 168;
  return age > threshold;
}
