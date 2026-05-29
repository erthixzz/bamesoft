import { env } from '$env/dynamic/public';
import type { PublicEquipment } from './types';

const BASE_URL = env.PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

/** Ficha pública del equipo (sin autenticación). El token viene del QR. */
export async function fetchPublicEquipment(code: string, token: string): Promise<PublicEquipment> {
  const url = `${BASE_URL}/public/equipment/${encodeURIComponent(code)}?token=${encodeURIComponent(token)}`;
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  if (!res.ok) {
    if (res.status === 404) throw new Error('QR no válido o equipo no encontrado.');
    throw new Error(`No se pudo cargar la información (${res.status}).`);
  }
  return (await res.json()) as PublicEquipment;
}

/** URL del PNG del QR público (para mostrar/descargar/imprimir). */
export function publicQrPngUrl(code: string, token: string): string {
  return `${BASE_URL}/public/equipment/${encodeURIComponent(code)}/qr.png?token=${encodeURIComponent(token)}`;
}
