-- 0010 · Auditoría (logs) + última conexión de usuarios
-- Registro inmutable de acciones (quién, qué, cuándo) y marca de última
-- actividad por usuario. La escritura de logs la hace el backend (middleware).

create table if not exists audit_logs (
  id          uuid primary key default gen_random_uuid(),
  actor_id    uuid references users(id)   on delete set null,
  actor_name  text,
  actor_role  text,
  clinic_id   uuid references clinics(id) on delete set null,
  method      text not null,
  action      text not null,
  entity      text,
  entity_id   text,
  path        text,
  status_code integer,
  created_at  timestamptz not null default now()
);

create index if not exists ix_audit_created on audit_logs (created_at desc);
create index if not exists ix_audit_actor   on audit_logs (actor_id);
create index if not exists ix_audit_clinic  on audit_logs (clinic_id);
create index if not exists ix_audit_entity  on audit_logs (entity);

-- Última vez que el usuario tocó la API (se refresca de forma "throttled").
alter table users add column if not exists last_seen_at timestamptz;

-- Capacidad nueva "audit" (ver bitácora) habilitada para admins.
insert into role_permissions (role, capability, enabled) values
  ('admin', 'audit', true),
  ('clinic_admin', 'audit', true)
on conflict (role, capability) do nothing;
