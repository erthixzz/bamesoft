import { env } from '$env/dynamic/public';

const BASE_URL = env.PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

/** Versión del diseño del QR: subir este número invalida la caché del navegador
 *  cuando cambia el arte del logo incrustado (mismo URL, imagen distinta). */
const QR_ART_VERSION = 3;

/** URL del PNG del QR (para mostrar/descargar/imprimir). El QR codifica la URL
 *  del portón `/e/{code}`, que exige login antes de mostrar cualquier dato. */
export function publicQrPngUrl(code: string, token: string): string {
  return `${BASE_URL}/public/equipment/${encodeURIComponent(code)}/qr.png?token=${encodeURIComponent(token)}&v=${QR_ART_VERSION}`;
}
