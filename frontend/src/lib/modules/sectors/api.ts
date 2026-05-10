import { api } from '$lib/api/client';
import type { Sector } from './types';

export const sectorsApi = {
  list: (clinic_id?: string) => api.get<Sector[]>('/sectors', { clinic_id }),
  get: (id: string) => api.get<Sector>(`/sectors/${id}`),
  create: (payload: Omit<Sector, 'id' | 'created_at' | 'updated_at'>) =>
    api.post<Sector>('/sectors', payload),
  update: (id: string, payload: Partial<Sector>) => api.patch<Sector>(`/sectors/${id}`, payload),
};
