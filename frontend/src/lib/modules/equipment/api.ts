import { api } from '$lib/api/client';
import type { EquipmentStatus } from '$lib/api/types';
import type {
  Equipment,
  EquipmentCategory,
  EquipmentCreate,
  EquipmentUpdate,
} from './types';
import type { LifeSheet, LifeSheetUpdate } from './lifeSheet';

export interface ListParams {
  clinic_id?: string;
  sector_id?: string;
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
  getLifeSheet: (id: string) => api.get<LifeSheet>(`/equipment/${id}/life-sheet`),
  saveLifeSheet: (id: string, payload: LifeSheetUpdate) =>
    api.put<LifeSheet>(`/equipment/${id}/life-sheet`, payload),
};

/**
 * Parsea el contenido del QR y devuelve {code, token}.
 * Acepta el nuevo formato URL (`.../e/{code}?t={token}`) y el JSON antiguo.
 */
export function parseQrPayload(raw: string): { code: string; token: string } {
  const text = raw.trim();

  // Nuevo formato: URL
  if (text.startsWith('http://') || text.startsWith('https://')) {
    const url = new URL(text);
    const parts = url.pathname.split('/').filter(Boolean);
    const token = url.searchParams.get('t');
    const code =
      parts.length >= 2 && parts[parts.length - 2] === 'e' ? parts[parts.length - 1] : null;
    if (!code || !token) throw new Error('QR no reconocido');
    return { code: decodeURIComponent(code), token };
  }

  // Formato antiguo: JSON
  const data = JSON.parse(text) as { v?: number; code?: string; token?: string };
  if (data.v !== 1 || !data.code || !data.token) {
    throw new Error('QR no reconocido');
  }
  return { code: data.code, token: data.token };
}
