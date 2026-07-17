-- 0011 · Detalle legible de la acción en la bitácora
-- Guarda qué cambió exactamente (p. ej. "CASO-012 · estado → En progreso ·
-- asignado a Juan Hurtado"). `action` sigue siendo genérico para agrupar.
alter table audit_logs add column if not exists detail text;
