import type { UserRole } from '$lib/api/types';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string | null;
  license_number?: string | null;
  avatar_url?: string | null;
  active: boolean;
  clinic_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string | null;
  license_number?: string | null;
  clinic_id?: string | null;
}

export type UserUpdate = Partial<Omit<UserCreate, 'id' | 'email'>> & { active?: boolean };

/** Alta completa desde la UI (crea cuenta de acceso + perfil). */
export interface UserInvite {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
  phone?: string | null;
  license_number?: string | null;
  clinic_id?: string | null;
}
