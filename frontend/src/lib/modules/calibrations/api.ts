import { api } from '$lib/api/client';
import type { Calibration } from './types';

export const calibrationsApi = {
  forEquipment: (equipmentId: string) =>
    api.get<Calibration[]>(`/calibrations/equipment/${equipmentId}`),
  create: (payload: Omit<Calibration, 'id' | 'created_at'>) =>
    api.post<Calibration>('/calibrations', payload),
};
