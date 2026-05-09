import { api } from '$lib/api/client';
import type { Clinic, Location } from './types';

export const clinicsApi = {
  list: () => api.get<Clinic[]>('/clinics'),
  get: (id: string) => api.get<Clinic>(`/clinics/${id}`),
  locations: (clinicId: string) => api.get<Location[]>(`/clinics/${clinicId}/locations`),
};
