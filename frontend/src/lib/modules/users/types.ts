import type { UserRole } from '$lib/api/types';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  phone?: string | null;
  license_number?: string | null;
  avatar_url?: string | null;
  cv_path?: string | null;
  active: boolean;
  /** La cuenta nació con la contraseña por defecto y aún no la ha cambiado. */
  must_change_password?: boolean;
  clinic_id?: string | null;
  clinic_name?: string | null;
  last_seen_at?: string | null;
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

/** `email` incluido: al cambiarlo, el backend mueve también la credencial en Supabase Auth. */
export type UserUpdate = Partial<Omit<UserCreate, 'id'>> & { active?: boolean };

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
