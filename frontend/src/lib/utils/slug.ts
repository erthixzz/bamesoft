const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** ¿El parámetro de ruta es un UUID (id) o un código legible (slug)? */
export function isUuid(value: string): boolean {
  return UUID_RE.test(value);
}
