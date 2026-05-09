export interface Calibration {
  id: string;
  equipment_id: string;
  performed_by?: string | null;
  performed_at: string;
  expires_at?: string | null;
  passed: boolean;
  standard?: string | null;
  certificate_path?: string | null;
  notes?: string | null;
  created_at: string;
}
