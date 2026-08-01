import { api } from '$lib/api/client';
import type {
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
};
