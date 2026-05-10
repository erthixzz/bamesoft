-- ============================================================================
-- Bamesoft · 0003_sectors.sql
-- Sectores de la clínica (cirugía, UCI, urgencias…) con ingeniero por defecto.
-- Añade `sector_id` a `cases` y unas RLS básicas.
-- ============================================================================

create table if not exists sectors (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references clinics(id) on delete cascade,
  code text not null,
  name text not null,
  description text,
  default_engineer_id uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (clinic_id, code)
);
create index if not exists sectors_clinic_idx on sectors(clinic_id);

drop trigger if exists trg_set_updated_at on sectors;
create trigger trg_set_updated_at before update on sectors
for each row execute function set_updated_at();

-- ---- cases.sector_id (nullable) --------------------------------------------
alter table cases add column if not exists sector_id uuid references sectors(id) on delete set null;
create index if not exists cases_sector_idx on cases(sector_id);

-- ---- RLS para sectors -------------------------------------------------------
alter table sectors enable row level security;

drop policy if exists sectors_select on sectors;
create policy sectors_select on sectors for select using (
  current_app_role() = 'admin' or clinic_id = current_clinic_id()
);

drop policy if exists sectors_admin on sectors;
create policy sectors_admin on sectors for all using (
  current_app_role() in ('admin','engineer')
) with check (
  current_app_role() in ('admin','engineer')
);

-- ---- Seed de sectores típicos ----------------------------------------------
insert into sectors (clinic_id, code, name, description) values
  ('11111111-1111-1111-1111-111111111111', 'UCI',  'UCI Adultos',     'Unidad de Cuidados Intensivos'),
  ('11111111-1111-1111-1111-111111111111', 'CIR',  'Cirugía',         'Salas quirúrgicas'),
  ('11111111-1111-1111-1111-111111111111', 'URG',  'Urgencias',       'Atención de urgencias'),
  ('11111111-1111-1111-1111-111111111111', 'IMG',  'Imagenología',    'RX, ECO, TAC, RMN'),
  ('11111111-1111-1111-1111-111111111111', 'LAB',  'Laboratorio',     'Laboratorio clínico'),
  ('11111111-1111-1111-1111-111111111111', 'GEN',  'General',         'Hospitalización general')
on conflict (clinic_id, code) do nothing;
