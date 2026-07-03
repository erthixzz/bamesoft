import { writable, get } from 'svelte/store';
import type { UserRole } from '$lib/api/types';

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Super administrador',
  clinic_admin: 'Admin de clínica',
  engineer: 'Ingeniero biomédico',
  service: 'Operario',
  support: 'Soporte',
  client: 'Cliente',
};

export const ALL_ROLES: UserRole[] = [
  'admin',
  'clinic_admin',
  'engineer',
  'service',
  'support',
  'client',
];

const RANK: Record<UserRole, number> = {
  admin: 100,
  clinic_admin: 90,
  engineer: 80,
  service: 60,
  support: 50,
  client: 10,
};

export function canAtLeast(role: UserRole | null | undefined, min: UserRole): boolean {
  if (!role) return false;
  return RANK[role] >= RANK[min];
}

export function isOneOf(role: UserRole | null | undefined, roles: UserRole[]): boolean {
  return !!role && roles.includes(role);
}

// ---- Capacidades (acciones) que puede tener un rol -------------------------
export type Capability =
  | 'report'
  | 'work'
  | 'close'
  | 'equipment'
  | 'sectors'
  | 'docs'
  | 'standards'
  | 'reports'
  | 'users'
  | 'clinics'
  | 'access'
  | 'dashboard';

export interface CapabilityDef {
  key: Capability;
  label: string;
}

export const CAPABILITIES: CapabilityDef[] = [
  { key: 'dashboard', label: 'Ver dashboard' },
  { key: 'report', label: 'Reportar casos' },
  { key: 'work', label: 'Tomar y trabajar casos' },
  { key: 'close', label: 'Cerrar / soporte de servicio' },
  { key: 'equipment', label: 'Gestionar equipos' },
  { key: 'sectors', label: 'Gestionar unidades de servicio' },
  { key: 'docs', label: 'Subir documentos / fotos' },
  { key: 'standards', label: 'Gestionar normas' },
  { key: 'reports', label: 'Ver reportes / KPIs' },
  { key: 'users', label: 'Gestionar usuarios' },
  { key: 'clinics', label: 'Gestionar compañías' },
  { key: 'access', label: 'Gestionar roles y permisos' },
];

// ---- Módulos que una compañía puede ver (features) -------------------------
export interface FeatureDef {
  key: string;
  label: string;
}

export const FEATURES: FeatureDef[] = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'equipment', label: 'Equipos' },
  { key: 'sectors', label: 'Unidades de servicio' },
  { key: 'cases', label: 'Casos' },
  { key: 'alerts', label: 'Alertas' },
  { key: 'documents', label: 'Documentos' },
  { key: 'standards', label: 'Normas' },
  { key: 'reports', label: 'Reportes' },
];

export type PermMatrix = Record<string, Record<string, boolean>>; // rol -> cap -> bool

// Defaults (deben reflejar el seed del backend); se usan antes de cargar de BD.
const DEFAULTS: Record<UserRole, Capability[]> = {
  admin: ['report', 'work', 'close', 'equipment', 'sectors', 'docs', 'standards', 'reports', 'users', 'clinics', 'access', 'dashboard'],
  clinic_admin: ['report', 'work', 'close', 'equipment', 'sectors', 'docs', 'standards', 'reports', 'users', 'dashboard'],
  engineer: ['report', 'work', 'close', 'equipment', 'sectors', 'docs', 'standards', 'reports', 'dashboard'],
  support: ['report', 'docs', 'reports', 'dashboard'],
  service: ['report', 'docs'],
  client: ['report'],
};

export const DEFAULT_MATRIX: PermMatrix = Object.fromEntries(
  ALL_ROLES.map((r) => [r, Object.fromEntries(DEFAULTS[r].map((c) => [c, true]))]),
);

/** Matriz rol→capacidad (cargada de BD en el arranque; init con defaults). */
export const permissions = writable<PermMatrix>(DEFAULT_MATRIX);
/** Features de la compañía del usuario actual (cargadas de BD; init: todo true). */
export const myFeatures = writable<Record<string, boolean>>(
  Object.fromEntries(FEATURES.map((f) => [f.key, true])),
);

export function setPermissions(m: PermMatrix): void {
  if (m && Object.keys(m).length) permissions.set(m);
}
export function setMyFeatures(f: Record<string, boolean>): void {
  if (f && Object.keys(f).length) myFeatures.set(f);
}

export function hasCapIn(m: PermMatrix, role: UserRole | null | undefined, cap: Capability): boolean {
  if (!role) return false;
  return !!m?.[role]?.[cap];
}
export function hasCap(role: UserRole | null | undefined, cap: Capability): boolean {
  return hasCapIn(get(permissions), role, cap);
}
export function featureOn(features: Record<string, boolean>, key: string): boolean {
  return features?.[key] !== false; // ausente = habilitado
}

export const can = {
  reportCase: (r: UserRole | null | undefined) => hasCap(r, 'report'),
  workCase: (r: UserRole | null | undefined) => hasCap(r, 'work'),
  closeCase: (r: UserRole | null | undefined) => hasCap(r, 'close'),
  manageEquipment: (r: UserRole | null | undefined) => hasCap(r, 'equipment'),
  manageSectors: (r: UserRole | null | undefined) => hasCap(r, 'sectors'),
  uploadDocs: (r: UserRole | null | undefined) => hasCap(r, 'docs'),
  manageStandards: (r: UserRole | null | undefined) => hasCap(r, 'standards'),
  viewReports: (r: UserRole | null | undefined) => hasCap(r, 'reports'),
  viewDashboard: (r: UserRole | null | undefined) => hasCap(r, 'dashboard'),
  manageUsers: (r: UserRole | null | undefined) => hasCap(r, 'users'),
  manageClinics: (r: UserRole | null | undefined) => hasCap(r, 'clinics'),
  manageAccess: (r: UserRole | null | undefined) => hasCap(r, 'access'),
};
