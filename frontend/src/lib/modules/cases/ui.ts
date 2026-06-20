/** Metadatos visuales y utilidades compartidas de casos.
 *  Centraliza colores de "semáforo", opciones de selects y cálculos de
 *  edad / SLA para que dashboard, lista y detalle se vean coherentes.
 */
import type { CasePriority, CaseStatus, CaseType } from '$lib/api/types';
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

/** ¿Lleva demasiado tiempo abierto? (umbral por prioridad, en horas) */
export function isAging(c: Case): boolean {
  if (!isActive(c)) return false;
  const age = caseAgeHours(c);
  const threshold =
    c.priority === 'critical' ? 8 : c.priority === 'high' ? 24 : c.priority === 'medium' ? 72 : 168;
  return age > threshold;
}
