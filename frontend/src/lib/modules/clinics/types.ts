export interface Clinic {
  id: string;
  name: string;
  tax_id?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  logo_url?: string | null;
  created_at: string;
}

export interface Location {
  id: string;
  clinic_id: string;
  code: string;
  name: string;
  building?: string | null;
  floor?: string | null;
  room?: string | null;
}
