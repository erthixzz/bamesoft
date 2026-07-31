-- ============================================================================
-- Bamesoft · check_rls.sql — auditoría de exposición vía PostgREST
--
-- Complementa el gate estático (`backend/tests/test_rls_coverage.py`), que solo
-- ve lo declarado en las migraciones. Esta query interroga la BD real y detecta
-- deriva: tablas creadas a mano en Studio que nunca pasaron por una migración.
--
-- Uso: pégala en el SQL Editor de Supabase (o `psql "$DATABASE_URL" -f`).
-- Resultado esperado: CERO filas. Cada fila es una tabla alcanzable desde
-- internet con la anon key del frontend.
-- ============================================================================

select
  c.relname                                              as tabla,
  c.relrowsecurity                                       as rls_activada,
  c.relforcerowsecurity                                  as rls_forzada,
  coalesce(
    (select string_agg(distinct g.grantee || ':' || g.privilege_type, ', ' order by
                       g.grantee || ':' || g.privilege_type)
       from information_schema.role_table_grants g
      where g.table_schema = 'public'
        and g.table_name = c.relname
        and g.grantee in ('anon', 'authenticated')),
    '(sin grants)'
  )                                                      as expuesta_a,
  case
    when not c.relrowsecurity then 'FALTA: alter table ' || c.relname
                                   || ' enable row level security;'
    when c.relforcerowsecurity then 'FORCE activo: el backend (owner) perdio acceso'
  end                                                    as accion
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relkind = 'r'                    -- solo tablas ordinarias
  and not c.relispartition
  and (
        not c.relrowsecurity             -- sin RLS  -> hueco abierto
     or c.relforcerowsecurity            -- con FORCE -> rompe el backend
  )
order by c.relname;
