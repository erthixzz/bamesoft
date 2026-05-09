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
