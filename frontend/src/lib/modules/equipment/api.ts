import { api } from '$lib/api/client';
import type { EquipmentStatus } from '$lib/api/types';
import type {
  Equipment,
  EquipmentCategory,
  EquipmentCreate,
  EquipmentUpdate,
} from './types';

export interface ListParams {
  clinic_id?: string;
  status?: EquipmentStatus;
  q?: string;
  limit?: number;
  offset?: number;
}

export const equipmentApi = {
  list: (params: ListParams = {}) => api.get<Equipment[]>('/equipment', params),
  get: (id: string) => api.get<Equipment>(`/equipment/${id}`),
  byCode: (code: string) => api.get<Equipment>(`/equipment/by-code/${code}`),
  scan: (code: string, token: string) =>
    api.get<Equipment>('/equipment/scan', { code, token }),
  create: (payload: EquipmentCreate) => api.post<Equipment>('/equipment', payload),
  update: (id: string, payload: EquipmentUpdate) =>
    api.patch<Equipment>(`/equipment/${id}`, payload),
  regenerateQr: (id: string) => api.post<Equipment>(`/equipment/${id}/regenerate-qr`),
  qrPngUrl: (id: string) => `/api/v1/equipment/${id}/qr.png`,
  categories: () => api.get<EquipmentCategory[]>('/equipment/categories'),
};

/** Parsea el payload escaneado y devuelve {code, token}. */
export function parseQrPayload(raw: string): { code: string; token: string } {
  const data = JSON.parse(raw) as { v?: number; code?: string; token?: string };
  if (data.v !== 1 || !data.code || !data.token) {
    throw new Error('QR no reconocido');
  }
  return { code: data.code, token: data.token };
}
