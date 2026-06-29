import type { UserRole } from '$lib/api/types';

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrador',
  engineer: 'Ingeniero biomédico',
  client: 'Cliente',
  service: 'Operario',
  support: 'Soporte',
};

const RANK: Record<UserRole, number> = {
  admin: 100,
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

export const can = {
  manageUsers: (r: UserRole | null | undefined) => isOneOf(r, ['admin']),
  manageEquipment: (r: UserRole | null | undefined) => isOneOf(r, ['admin', 'engineer']),
  // El operario (service) solo reporta: no cierra ni gestiona casos.
  workCase: (r: UserRole | null | undefined) => isOneOf(r, ['admin', 'engineer']),
  closeCase: (r: UserRole | null | undefined) => isOneOf(r, ['admin', 'engineer']),
  uploadDocs: (r: UserRole | null | undefined) =>
    isOneOf(r, ['admin', 'engineer', 'service', 'support']),
  viewReports: (r: UserRole | null | undefined) =>
    isOneOf(r, ['admin', 'engineer', 'support']),
  viewDashboard: (r: UserRole | null | undefined) =>
    isOneOf(r, ['admin', 'engineer', 'support']),
  manageStandards: (r: UserRole | null | undefined) => isOneOf(r, ['admin', 'engineer']),
};

/** Capacidades por rol (para la matriz de permisos de la vista de usuarios). */
export interface Capability {
  key: string;
  label: string;
  roles: UserRole[];
}

export const ROLE_CAPABILITIES: Capability[] = [
  { key: 'report', label: 'Reportar casos', roles: ['admin', 'engineer', 'service', 'support', 'client'] },
  { key: 'work', label: 'Tomar y trabajar casos', roles: ['admin', 'engineer'] },
  { key: 'close', label: 'Cerrar / soporte de servicio', roles: ['admin', 'engineer'] },
  { key: 'equipment', label: 'Gestionar equipos', roles: ['admin', 'engineer'] },
  { key: 'docs', label: 'Subir documentos / fotos', roles: ['admin', 'engineer', 'service', 'support'] },
  { key: 'reports', label: 'Ver reportes / KPIs', roles: ['admin', 'engineer', 'support'] },
  { key: 'users', label: 'Gestionar usuarios', roles: ['admin'] },
];

export const ALL_ROLES: UserRole[] = ['admin', 'engineer', 'service', 'support', 'client'];
