import { api } from '$lib/api/client';
import type { Standard } from './types';

export const standardsApi = {
  list: () => api.get<Standard[]>('/standards'),
  forEquipment: (equipmentId: string) =>
    api.get<Standard[]>(`/standards/equipment/${equipmentId}`),
  link: (equipment_id: string, standard_id: string) =>
    api.post('/standards/link', { equipment_id, standard_id }),
};
