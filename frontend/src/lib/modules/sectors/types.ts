export interface Sector {
  id: string;
  clinic_id: string;
  code: string;
  name: string;
  description?: string | null;
  default_engineer_id?: string | null;
  created_at: string;
  updated_at: string;
}
