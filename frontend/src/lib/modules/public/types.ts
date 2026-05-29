export interface PublicCaseBrief {
  code: string;
  title: string;
  type: string;
  status: string;
  priority: string;
  opened_at: string | null;
  closed_at: string | null;
}

export interface PublicMaintenanceBrief {
  name: string;
  frequency_days: number;
  last_done_at: string | null;
  next_due_at: string | null;
}

export interface PublicCalibrationBrief {
  performed_at: string;
  expires_at: string | null;
  passed: boolean;
  standard: string | null;
}

export interface PublicEquipment {
  id: string;
  code: string;
  name: string;
  brand: string | null;
  model: string | null;
  serial_number: string | null;
  manufacturer: string | null;
  status: string;
  risk_class: string | null;
  category_name: string | null;
  clinic_name: string | null;
  location_name: string | null;
  acquisition_date: string | null;
  warranty_until: string | null;
  image_url: string | null;
  notes: string | null;
  cases_open: number;
  cases_total: number;
  cases: PublicCaseBrief[];
  maintenance: PublicMaintenanceBrief[];
  calibrations: PublicCalibrationBrief[];
}
