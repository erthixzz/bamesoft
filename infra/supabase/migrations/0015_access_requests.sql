-- ============================================================================
-- Bamesoft · 0015_access_requests.sql
-- Bandeja de solicitudes de acceso.
--
-- Con el inicio de sesión por Google, cualquiera puede autenticarse pero nadie
-- entra sin que un administrador lo dé de alta (ver `NoProfile` en el backend).
-- Antes esas personas quedaban en el limbo: tenían que escribirle al admin por
-- fuera y no quedaba rastro. Aquí se registran para que el admin las apruebe o
-- descarte desde la aplicación.
--
-- Una fila por usuario de Supabase Auth: los reintentos actualizan la misma
-- fila en vez de llenar la tabla.
-- ============================================================================

create table if not exists access_requests (
  -- Es el `auth.users.id` de Supabase: al aprobar, se convierte en el id del
  -- perfil, de modo que la sesión que ya tiene la persona pasa a ser válida.
  user_id      uuid primary key,
  email        text not null,
  full_name    text,
  avatar_url   text,
  provider     text,
  status       text not null default 'pending'
               check (status in ('pending', 'approved', 'rejected')),
  attempts     integer not null default 1,
  first_seen_at timestamptz not null default now(),
  last_seen_at  timestamptz not null default now(),
  -- Quién resolvió la solicitud y cuándo (queda como evidencia).
  resolved_at  timestamptz,
  resolved_by  uuid references users(id) on delete set null,
  note         text
);

create index if not exists ix_access_requests_status
  on access_requests (status, last_seen_at desc);

-- RLS obligatoria (ver la regla en infra/supabase/README.md). Sin políticas =
-- deny-all para PostgREST; el backend entra como owner y la omite.
alter table access_requests enable row level security;
revoke all on table access_requests from anon, authenticated;
