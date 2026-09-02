import type {
  CaseCompletion,
  CasePriority,
  CaseStatus,
  CaseType,
  SatisfactionScore,
  TecnovigilanciaStage,
} from '$lib/api/types';

/** Campos del soporte/cierre del servicio (compartidos entre Case y CaseUpdate). */
export interface CaseResolution {
  operation_minutes?: number | null;
  work_performed?: string | null;
  parts_count?: number | null;
  parts_detail?: string | null;
  completion?: CaseCompletion | null;
  /** Satisfacción del servicio en escala Likert de 7 puntos. */
  satisfaction_score?: SatisfactionScore | null;
  receiver_name?: string | null;
  receiver_doc?: string | null;
  signature_path?: string | null;
}

export interface Case extends CaseResolution {
  id: string;
  code: string;
  title: string;
  description?: string | null;
  type: CaseType;
  status: CaseStatus;
  priority: CasePriority;
  equipment_id: string;
  sector_id?: string | null;
  reported_by?: string | null;
  assigned_to?: string | null;
  opened_at?: string | null;
  closed_at?: string | null;
  sla_due_at?: string | null;
  assigned_at?: string | null;
  accepted_at?: string | null;
  work_started_at?: string | null;
  finished_at?: string | null;
  /** Tecnovigilancia: el caso es un evento adverso / incidente con el equipo. */
  is_tecnovigilancia: boolean;
  tecnovigilancia_stage?: TecnovigilanciaStage | null;
  tecnovigilancia_description?: string | null;
  tecnovigilancia_at?: string | null;
  created_at: string;
  updated_at: string;
}

/** Payload de `PATCH /cases/{id}/tecnovigilancia`. */
export interface CaseTecnovigilancia {
  is_tecnovigilancia: boolean;
  stage?: TecnovigilanciaStage | null;
  description?: string | null;
}

export interface CaseCreate {
  title: string;
  description?: string;
  type: CaseType;
  priority?: CasePriority;
  equipment_id: string;
  sector_id?: string;
  assigned_to?: string;
  sla_due_at?: string;
}

export interface CaseUpdate extends CaseResolution {
  title?: string;
  description?: string;
  type?: CaseType;
  priority?: CasePriority;
  status?: CaseStatus;
  sector_id?: string;
  assigned_to?: string;
  sla_due_at?: string;
}

export interface CaseActivity {
  id: string;
  case_id: string;
  author_id: string | null;
  action: string;
  notes: string | null;
  created_at: string;
}
