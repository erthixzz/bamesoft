import { api } from '$lib/api/client';
import type { User } from '$lib/modules/users/types';

import type {
  AccessRequest,
  ClinicFeaturesMatrix,
  Matrix,
  MyFeatures,
  RolesMatrix,
} from './types';

export const accessApi = {
  getRoles: () => api.get<RolesMatrix>('/access/roles'),
  saveRoles: (matrix: Matrix) => api.put<RolesMatrix>('/access/roles', { matrix }),
  getClinicFeatures: () => api.get<ClinicFeaturesMatrix>('/access/clinic-features'),
  saveClinicFeatures: (matrix: Matrix) =>
    api.put<ClinicFeaturesMatrix>('/access/clinic-features', { matrix }),
  myFeatures: () => api.get<MyFeatures>('/access/my-features'),

  /** Solicitudes de acceso. Solo el super admin las ve: una solicitud pendiente
   *  todavía no tiene clínica, y mostrarla a un admin de clínica revelaría
   *  correos de gente que intenta entrar a otra. */
  requests: (status: 'pending' | 'approved' | 'rejected' = 'pending') =>
    api.get<AccessRequest[]>('/access/requests', { status }),
  approveRequest: (userId: string, clinicId: string, role: string) =>
    api.post<User>(`/access/requests/${userId}/approve`, { clinic_id: clinicId, role }),
  rejectRequest: (userId: string, note?: string) =>
    api.post<AccessRequest>(`/access/requests/${userId}/reject`, { note: note ?? null }),
};
