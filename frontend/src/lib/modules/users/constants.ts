/**
 * Contraseña con la que nace una cuenta nueva cuando quien la da de alta no
 * escribe otra. Es provisional: el backend marca `must_change_password` y la
 * app obliga a cambiarla en el primer acceso.
 *
 * Debe coincidir con `DEFAULT_USER_PASSWORD` del backend
 * (`backend/app/core/config.py`). Supabase Auth no acepta menos de 6
 * caracteres, así que el mínimo del proyecto tiene que estar en 6.
 */
export const DEFAULT_PASSWORD = '123456';

/** Longitud mínima que acepta Supabase Auth (GoTrue). */
export const MIN_PASSWORD_LENGTH = 6;
