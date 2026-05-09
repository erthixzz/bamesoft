import type { EquipmentStatus, RiskClass } from '$lib/api/types';

export interface Equipment {
  id: string;
  code: string;
  qr_token: string;
  name: string;
  brand?: string | null;
  model?: string | null;
  serial_number?: string | null;
  manufacturer?: string | null;
  category_id?: string | null;
  risk_class?: RiskClass | null;
  status: EquipmentStatus;
  clinic_id: string;
  location_id?: string | null;
  acquisition_date?: string | null;
  warranty_until?: string | null;
  decommissioned_at?: string | null;
  image_url?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EquipmentCreate {
  code: string;
  name: string;
  brand?: string;
  model?: string;
  serial_number?: string;
  manufacturer?: string;
  category_id?: string;
  risk_class?: RiskClass;
  status?: EquipmentStatus;
  clinic_id: string;
  location_id?: string;
  acquisition_date?: string;
  warranty_until?: string;
  notes?: string;
}

export type EquipmentUpdate = Partial<Omit<EquipmentCreate, 'code' | 'clinic_id'>>;

export interface EquipmentCategory {
  id: string;
  code: string;
  name: string;
  description?: string;
}
