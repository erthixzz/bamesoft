export interface DashboardKPIs {
  equipment_total: number;
  equipment_operational: number;
  equipment_out_of_service: number;
  cases_open: number;
  cases_in_progress: number;
  cases_closed_30d: number;
  preventive_due_30d: number;
  calibrations_due_30d: number;
  avg_close_time_hours: number | null;
  cases_by_status?: Record<string, number>;
}

export interface ComplianceItem {
  standard_code: string;
  standard_name: string;
  coverage_pct: number;
  equipment_with: number;
  equipment_total: number;
}

export interface ComplianceReport {
  items: ComplianceItem[];
  total: number;
}

export interface ProductivityRow {
  engineer_id: string | null;
  engineer_name: string;
  attended: number;
  completed: number;
  incomplete: number;
  closed: number;
  avg_response_hours: number | null;
  avg_to_start_hours: number | null;
  avg_work_hours: number | null;
  fcr_count: number;
  fcr_pct: number;
  /** Satisfacción Likert 1-7 (solo casos cerrados y calificados). */
  sat_count: number;
  sat_avg: number | null;
  sat_positive: number;
  sat_neutral: number;
  sat_negative: number;
}

export interface ProductivityReport {
  items: ProductivityRow[];
  attended: number;
  completed: number;
  incomplete: number;
  fcr_count: number;
  fcr_pct: number;
  sat_count: number;
  sat_avg: number | null;
  sat_positive: number;
  sat_neutral: number;
  sat_negative: number;
}

export interface DailyPoint {
  day: string;
  reported: number;
  closed: number;
}

export interface ReporterRow {
  user_id: string | null;
  name: string;
  count: number;
}

export interface OperationsReport {
  reported_total: number;
  closed_total: number;
  complete_total: number;
  incomplete_total: number;
  active_total: number;
  waiting_total: number;
  cancelled_total: number;
  waiting_now: number;
  daily: DailyPoint[];
  by_reporter: ReporterRow[];
}

export interface EquipmentReportRow {
  equipment_id: string;
  code: string;
  name: string;
  sector_name: string | null;
  cases_total: number;
  completed: number;
  incomplete: number;
  corrective: number;
  preventive: number;
  avg_work_hours: number | null;
  total_operation_minutes: number;
  last_service_at: string | null;
}

export interface EquipmentReport {
  items: EquipmentReportRow[];
  total: number;
}

export interface ServiceRow {
  case_id: string;
  code: string;
  title: string;
  equipment_label: string;
  engineer_name: string | null;
  type: string;
  status: string;
  completion: string | null;
  satisfaction_score?: number | null;
  is_tecnovigilancia: boolean;
  tecnovigilancia_stage?: string | null;
  work_performed: string | null;
  operation_minutes: number | null;
  opened_at: string | null;
  assigned_at: string | null;
  accepted_at: string | null;
  work_started_at: string | null;
  finished_at: string | null;
  closed_at: string | null;
}

export interface ServicesReport {
  items: ServiceRow[];
  total: number;
}

export interface NamedCount {
  label: string;
  value: number;
}

export interface BreakdownReport {
  by_status: NamedCount[];
  by_type: NamedCount[];
  by_priority: NamedCount[];
  by_sector: NamedCount[];
  monthly: NamedCount[];
  /** Satisfacción Likert: siempre los 7 puntos, label = '1'…'7'. */
  by_satisfaction: NamedCount[];
}

export interface TecnovigilanciaRow {
  case_id: string;
  code: string;
  title: string;
  equipment_label: string;
  sector_name: string | null;
  engineer_name: string | null;
  status: string;
  priority: string;
  stage: string | null;
  description: string | null;
  marked_at: string | null;
  opened_at: string | null;
  closed_at: string | null;
}

export interface TecnovigilanciaReport {
  items: TecnovigilanciaRow[];
  total: number;
  open_total: number;
  by_stage: NamedCount[];
  by_equipment: NamedCount[];
}
