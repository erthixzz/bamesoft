import type { Handle } from '@sveltejs/kit';

/**
 * Hook server-side: deja un hook para inyectar sesión / cookies si más
 * adelante se mueve la lógica a SSR. Por ahora la sesión vive en el cliente.
 */
export const handle: Handle = async ({ event, resolve }) => {
  event.locals.session = null;
  event.locals.user = null;
  return resolve(event);
};
