/**
 * Tipos compartidos con el backend (mantener sincronizado con
 * `backend/app/db/enums.py` y los `schemas.py` de cada módulo).
 */

export type UserRole =
  | 'admin'
  | 'clinic_admin'
  | 'engineer'
  | 'client'
  | 'service'
  | 'support';

export type EquipmentStatus =
  | 'operational'
  | 'out_of_service'
  | 'under_maintenance'
  | 'retired';

export type RiskClass = 'I' | 'IIa' | 'IIb' | 'III';

export type CaseType =
  | 'corrective'
  | 'preventive'
  | 'calibration'
  | 'installation'
  | 'inspection'
  | 'mishandling';

export type CaseStatus =
  | 'open'
  | 'assigned'
  | 'in_progress'
  | 'waiting_parts'
  | 'waiting_client'
  | 'closed'
  | 'cancelled';

export type CasePriority = 'low' | 'medium' | 'high' | 'critical';

export type CaseCompletion = 'complete' | 'incomplete';

/** Satisfacción del servicio: escala Likert de 7 puntos (1 = Muy insatisfecho
 *  … 7 = Muy satisfecho). Sustituye a las 3 caritas (migración 0015). */
export type SatisfactionScore = 1 | 2 | 3 | 4 | 5 | 6 | 7;

/** Etapa del proceso de tecnovigilancia de un caso. */
export type TecnovigilanciaStage =
  | 'detection'
  | 'report'
  | 'investigation'
  | 'corrective_action'
  | 'follow_up'
  | 'closed';

export type AlertType =
  | 'preventive_due'
  | 'calibration_due'
  | 'warranty_expiring'
  | 'case_sla'
  | 'custom';

export type AlertSeverity = 'info' | 'warning' | 'critical';

export type DocumentType =
  | 'manual'
  | 'certificate'
  | 'report'
  | 'standard'
  | 'invoice'
  | 'life_sheet'
  | 'photo'
  | 'signature'
  | 'tecnovigilancia'
  | 'other';

export interface Paginated<T> {
  items: T[];
  total: number;
}
