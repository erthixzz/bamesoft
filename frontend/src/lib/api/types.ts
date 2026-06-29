/**
 * Tipos compartidos con el backend (mantener sincronizado con
 * `backend/app/db/enums.py` y los `schemas.py` de cada módulo).
 */

export type UserRole = 'admin' | 'engineer' | 'client' | 'service' | 'support';

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
  | 'inspection';

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
  | 'other';

export interface Paginated<T> {
  items: T[];
  total: number;
}
