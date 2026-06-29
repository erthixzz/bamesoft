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
}

export interface ProductivityReport {
  items: ProductivityRow[];
  attended: number;
  completed: number;
  incomplete: number;
  fcr_count: number;
  fcr_pct: number;
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
  waiting_now: number;
  daily: DailyPoint[];
  by_reporter: ReporterRow[];
}
