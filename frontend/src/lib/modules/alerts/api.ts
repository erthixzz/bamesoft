import { api } from '$lib/api/client';
import type { AlertSeverity, AlertType } from '$lib/api/types';
import type { Alert } from './types';

export interface AlertCreate {
  type: AlertType;
  severity: AlertSeverity;
  title: string;
  message: string;
  equipment_id?: string;
  case_id?: string;
  due_at?: string;
}

export const alertsApi = {
  list: (only_active = true, limit = 100) =>
    api.get<Alert[]>('/alerts', { only_active, limit }),
  create: (payload: AlertCreate) => api.post<Alert>('/alerts', payload),
  ack: (id: string) => api.post<Alert>(`/alerts/${id}/ack`),
  resolve: (id: string) => api.post<Alert>(`/alerts/${id}/resolve`),
  sweep: () => api.post<{ preventive: number; calibrations: number }>('/alerts/sweep'),
};
