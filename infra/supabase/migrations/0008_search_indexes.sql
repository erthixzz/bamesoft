-- ============================================================================
-- Bamesoft · 0008_search_indexes.sql
-- Índices GIN pg_trgm para la búsqueda global (/search).
-- Las expresiones indexadas coinciden EXACTAMENTE con las del UNION ALL de
-- `app/modules/search/routes.py`: así un ILIKE '%término%' usa índice
-- (búsqueda por trigramas, sublineal) en vez de escanear la tabla completa.
-- ============================================================================

create extension if not exists pg_trgm;

create index if not exists equipment_search_trgm on equipment
  using gin ((coalesce(code,'') || ' ' || coalesce(name,'') || ' ' ||
              coalesce(serial_number,'') || ' ' || coalesce(brand,'') || ' ' ||
              coalesce(model,'')) gin_trgm_ops);

create index if not exists cases_search_trgm on cases
  using gin ((coalesce(code,'') || ' ' || coalesce(title,'')) gin_trgm_ops);

create index if not exists sectors_search_trgm on sectors
  using gin ((coalesce(code,'') || ' ' || coalesce(name,'')) gin_trgm_ops);

create index if not exists users_search_trgm on users
  using gin ((coalesce(full_name,'') || ' ' || coalesce(email,'')) gin_trgm_ops);

create index if not exists clinics_search_trgm on clinics
  using gin ((coalesce(name,'')) gin_trgm_ops);
