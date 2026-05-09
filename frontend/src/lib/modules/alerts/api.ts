import { api } from '$lib/api/client';
import type { Alert } from './types';

export const alertsApi = {
  list: (only_active = true, limit = 100) =>
    api.get<Alert[]>('/alerts', { only_active, limit }),
  ack: (id: string) => api.post<Alert>(`/alerts/${id}/ack`),
  resolve: (id: string) => api.post<Alert>(`/alerts/${id}/resolve`),
  sweep: () => api.post<{ preventive: number; calibrations: number }>('/alerts/sweep'),
};
