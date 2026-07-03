import { api } from '$lib/api/client';
import type { Clinic, ClinicCreate, ClinicUpdate, Location } from './types';

export const clinicsApi = {
  list: () => api.get<Clinic[]>('/clinics'),
  get: (id: string) => api.get<Clinic>(`/clinics/${id}`),
  create: (payload: ClinicCreate) => api.post<Clinic>('/clinics', payload),
  update: (id: string, payload: ClinicUpdate) => api.patch<Clinic>(`/clinics/${id}`, payload),
  locations: (clinicId: string) => api.get<Location[]>(`/clinics/${clinicId}/locations`),
};
