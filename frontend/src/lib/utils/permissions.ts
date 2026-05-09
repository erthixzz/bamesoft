import type { UserRole } from '$lib/api/types';

export const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Administrador',
  engineer: 'Ingeniero biomédico',
  client: 'Cliente',
  service: 'Servicio',
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
  closeCase: (r: UserRole | null | undefined) =>
    isOneOf(r, ['admin', 'engineer', 'service']),
  uploadDocs: (r: UserRole | null | undefined) =>
    isOneOf(r, ['admin', 'engineer', 'service', 'support']),
  viewReports: (r: UserRole | null | undefined) =>
    isOneOf(r, ['admin', 'engineer', 'support']),
};
