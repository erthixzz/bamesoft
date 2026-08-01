import type { Handle } from '@sveltejs/kit';
import { dev } from '$app/environment';

/**
 * Cabeceras de seguridad de la app web.
 *
 * Son una superficie distinta a la de la API (que pone las suyas en
 * `backend/app/core/security_headers.py`): aquí protegemos el navegador del
 * usuario, allí la API.
 *
 * La CSP NO se define aquí sino en `svelte.config.js` (`kit.csp`), porque
 * SvelteKit necesita generar nonces/hashes para sus propios scripts inline.
 */
const SECURITY_HEADERS: Record<string, string> = {
  // No adivinar el tipo de contenido (un archivo subido no debe volverse HTML).
  'X-Content-Type-Options': 'nosniff',
  // La app no debe embeberse en un iframe ajeno (clickjacking).
  'X-Frame-Options': 'DENY',
  // No filtrar la URL completa (lleva ids de casos y equipos) a terceros.
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  // La app no usa estas capacidades del navegador.
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=()',
};

export const handle: Handle = async ({ event, resolve }) => {
  // Hook para inyectar sesión / cookies si más adelante se mueve a SSR.
  // Por ahora la sesión vive en el cliente.
  event.locals.session = null;
  event.locals.user = null;

  const response = await resolve(event);

  for (const [header, value] of Object.entries(SECURITY_HEADERS)) {
    response.headers.set(header, value);
  }

  // HSTS solo en producción: en local forzaría https://localhost.
  if (!dev) {
    response.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  }

  return response;
};
