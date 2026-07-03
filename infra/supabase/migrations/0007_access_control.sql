-- ============================================================================
-- Bamesoft · 0007_access_control.sql
-- 1) Rol `clinic_admin` (admin de una clínica; `admin` = super admin global).
-- 2) Roles: matriz rol → capacidad (qué puede HACER cada rol).
-- 3) Permisos: matriz compañía → módulo (qué puede VER cada compañía).
-- Tablas de configuración global: sin RLS (solo las gestiona el backend con
-- require_admin). El aislamiento por clínica se aplica en la capa de servicio.
-- ============================================================================

-- Rol nuevo (idempotente; PG12+). Va solo, sin usarse en la misma transacción.
alter type user_role add value if not exists 'clinic_admin';

-- ---- Roles: acciones por rol -----------------------------------------------
create table if not exists role_permissions (
  role text not null,
  capability text not null,
  enabled boolean not null default false,
  primary key (role, capability)
);

insert into role_permissions (role, capability, enabled)
select r.role, c.cap, true
from (values
  ('admin',        array['report','work','close','equipment','sectors','docs','standards','reports','users','clinics','access','dashboard']),
  ('clinic_admin', array['report','work','close','equipment','sectors','docs','standards','reports','users','dashboard']),
  ('engineer',     array['report','work','close','equipment','sectors','docs','standards','reports','dashboard']),
  ('support',      array['report','docs','reports','dashboard']),
  ('service',      array['report','docs']),
  ('client',       array['report'])
) as r(role, caps)
cross join lateral unnest(r.caps) as c(cap)
on conflict (role, capability) do nothing;

-- ---- Permisos: módulos visibles por compañía -------------------------------
create table if not exists clinic_features (
  clinic_id uuid not null references clinics(id) on delete cascade,
  feature text not null,
  enabled boolean not null default true,
  primary key (clinic_id, feature)
);

insert into clinic_features (clinic_id, feature, enabled)
select cl.id, f.feature, true
from clinics cl
cross join unnest(array['dashboard','equipment','sectors','cases','alerts','documents','standards','reports']) as f(feature)
on conflict (clinic_id, feature) do nothing;
