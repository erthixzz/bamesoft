-- ============================================================================
-- Bamesoft · 0014_rls_config_tables.sql
-- Cierra el hueco detectado por el linter de Supabase: `audit_logs`,
-- `role_permissions` y `clinic_features` quedaron sin RLS.
--
-- El comentario de 0007 ("las gestiona el backend con require_admin") solo
-- cubre la puerta del API. La otra puerta es PostgREST: expone el esquema
-- `public` con la anon key, que viaja en el bundle del frontend. Sin RLS,
-- cualquiera puede leer la bitácora o escribir en la matriz de capacidades
-- (escalada de privilegios) sin tocar FastAPI.
--
-- RLS activada SIN políticas = deny-all para PostgREST. El backend no se ve
-- afectado: se conecta como owner de las tablas y en Postgres el owner omite
-- RLS (por eso NO usamos `force row level security` aquí — rompería la app).
--
-- Idempotente: `enable row level security` y `revoke` no fallan si ya se
-- aplicaron.
-- ============================================================================

alter table audit_logs       enable row level security;
alter table role_permissions enable row level security;
alter table clinic_features  enable row level security;

-- Cinturón y tirantes: Supabase concede grants por defecto a anon/authenticated
-- en las tablas nuevas de `public`. Sin grants, ni siquiera se llega a evaluar
-- RLS. `service_role` conserva el acceso (y de todos modos bypassea RLS).
revoke all on table audit_logs       from anon, authenticated;
revoke all on table role_permissions from anon, authenticated;
revoke all on table clinic_features  from anon, authenticated;
