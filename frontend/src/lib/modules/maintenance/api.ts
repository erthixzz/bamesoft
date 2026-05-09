import { api } from '$lib/api/client';
import type { MaintenanceSchedule } from './types';

export const maintenanceApi = {
  due: (on?: string) => api.get<MaintenanceSchedule[]>('/maintenance/due', { on }),
  forEquipment: (equipmentId: string) =>
    api.get<MaintenanceSchedule[]>(`/maintenance/equipment/${equipmentId}`),
  markDone: (id: string, on?: string) =>
    api.post<MaintenanceSchedule>(`/maintenance/${id}/mark-done`, { on }),
};
