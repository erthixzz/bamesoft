export type Matrix = Record<string, Record<string, boolean>>;

export interface RolesMatrix {
  matrix: Matrix; // rol -> capacidad -> bool
}

export interface ClinicFeaturesMatrix {
  matrix: Matrix; // clinic_id -> feature -> bool
}

export interface MyFeatures {
  features: Record<string, boolean>;
}

/** Alguien se autenticó (normalmente con Google) y aún no tiene acceso. */
export interface AccessRequest {
  user_id: string;
  email: string;
  full_name?: string | null;
  avatar_url?: string | null;
  provider?: string | null;
  status: 'pending' | 'approved' | 'rejected';
  attempts: number;
  first_seen_at: string;
  last_seen_at: string;
  resolved_at?: string | null;
  note?: string | null;
}
