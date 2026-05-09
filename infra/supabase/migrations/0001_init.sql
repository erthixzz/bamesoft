-- ============================================================================
-- Bamesoft · 0001_init.sql
-- Esquema inicial: enums, tablas, FKs e índices.
-- ============================================================================

create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- ---- ENUMS ------------------------------------------------------------------
do $$ begin
  create type user_role as enum ('admin','engineer','client','service','support');
exception when duplicate_object then null; end $$;

do $$ begin
  create type equipment_status as enum
    ('operational','out_of_service','under_maintenance','retired');
exception when duplicate_object then null; end $$;

do $$ begin
  create type risk_class as enum ('I','IIa','IIb','III');
exception when duplicate_object then null; end $$;

do $$ begin
  create type case_type as enum
    ('corrective','preventive','calibration','installation','inspection');
exception when duplicate_object then null; end $$;

do $$ begin
  create type case_status as enum
    ('open','assigned','in_progress','waiting_parts','waiting_client','closed','cancelled');
exception when duplicate_object then null; end $$;

do $$ begin
  create type case_priority as enum ('low','medium','high','critical');
exception when duplicate_object then null; end $$;

do $$ begin
  create type alert_type as enum
    ('preventive_due','calibration_due','warranty_expiring','case_sla','custom');
exception when duplicate_object then null; end $$;

do $$ begin
  create type alert_severity as enum ('info','warning','critical');
exception when duplicate_object then null; end $$;

do $$ begin
  create type document_type as enum
    ('manual','certificate','report','standard','invoice','other');
exception when duplicate_object then null; end $$;

-- ---- CLINICS / LOCATIONS ----------------------------------------------------
create table if not exists clinics (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  tax_id text unique,
  email text,
  phone text,
  address text,
  logo_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists locations (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references clinics(id) on delete cascade,
  code text not null,
  name text not null,
  building text,
  floor text,
  room text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (clinic_id, code)
);

-- ---- USERS (perfil; el id coincide con auth.users) --------------------------
create table if not exists users (
  id uuid primary key,
  email text unique not null,
  full_name text not null,
  role user_role not null default 'client',
  phone text,
  license_number text,
  avatar_url text,
  active boolean not null default true,
  clinic_id uuid references clinics(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists users_role_idx on users(role);

-- ---- EQUIPMENT --------------------------------------------------------------
create table if not exists equipment_categories (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null,
  description text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists equipment (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  qr_token text unique not null,
  name text not null,
  brand text,
  model text,
  serial_number text,
  manufacturer text,
  category_id uuid references equipment_categories(id) on delete set null,
  risk_class risk_class,
  status equipment_status not null default 'operational',
  clinic_id uuid not null references clinics(id) on delete cascade,
  location_id uuid references locations(id) on delete set null,
  acquisition_date date,
  warranty_until date,
  decommissioned_at date,
  image_url text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists equipment_clinic_idx on equipment(clinic_id);
create index if not exists equipment_status_idx on equipment(status);
create index if not exists equipment_serial_idx on equipment(serial_number);

-- ---- CASES + ACTIVITIES -----------------------------------------------------
create table if not exists cases (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  title text not null,
  description text,
  type case_type not null,
  status case_status not null default 'open',
  priority case_priority not null default 'medium',
  equipment_id uuid not null references equipment(id) on delete cascade,
  reported_by uuid references users(id) on delete set null,
  assigned_to uuid references users(id) on delete set null,
  opened_at timestamptz,
  closed_at timestamptz,
  sla_due_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists cases_status_idx on cases(status);
create index if not exists cases_assigned_idx on cases(assigned_to);
create index if not exists cases_equipment_idx on cases(equipment_id);

create table if not exists case_activities (
  id uuid primary key default gen_random_uuid(),
  case_id uuid not null references cases(id) on delete cascade,
  author_id uuid references users(id) on delete set null,
  action text not null,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists case_activities_case_idx on case_activities(case_id);

-- ---- MAINTENANCE / CALIBRATIONS --------------------------------------------
create table if not exists maintenance_schedules (
  id uuid primary key default gen_random_uuid(),
  equipment_id uuid not null references equipment(id) on delete cascade,
  name text not null,
  description text,
  frequency_days integer not null check (frequency_days > 0),
  last_done_at date,
  next_due_at date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists pm_due_idx on maintenance_schedules(next_due_at);

create table if not exists calibrations (
  id uuid primary key default gen_random_uuid(),
  equipment_id uuid not null references equipment(id) on delete cascade,
  performed_by uuid references users(id) on delete set null,
  performed_at date not null,
  expires_at date,
  passed boolean not null default true,
  standard text,
  certificate_path text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists cal_expires_idx on calibrations(expires_at);

-- ---- STANDARDS --------------------------------------------------------------
create table if not exists standards (
  id uuid primary key default gen_random_uuid(),
  code text unique not null,
  name text not null,
  issuer text,
  version text,
  description text,
  document_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists equipment_standards (
  id uuid primary key default gen_random_uuid(),
  equipment_id uuid not null references equipment(id) on delete cascade,
  standard_id uuid not null references standards(id) on delete cascade,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (equipment_id, standard_id)
);

-- ---- DOCUMENTS --------------------------------------------------------------
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  type document_type not null,
  storage_path text not null,
  mime_type text not null,
  size_bytes bigint not null default 0,
  clinic_id uuid references clinics(id) on delete cascade,
  equipment_id uuid references equipment(id) on delete cascade,
  case_id uuid references cases(id) on delete cascade,
  uploaded_by uuid references users(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- FK diferida: standards.document_id → documents.id
do $$ begin
  alter table standards
    add constraint standards_document_fk foreign key (document_id)
    references documents(id) on delete set null;
exception when duplicate_object then null; end $$;

-- ---- ALERTS -----------------------------------------------------------------
create table if not exists alerts (
  id uuid primary key default gen_random_uuid(),
  type alert_type not null,
  severity alert_severity not null default 'info',
  title text not null,
  message text not null,
  equipment_id uuid references equipment(id) on delete cascade,
  case_id uuid references cases(id) on delete cascade,
  due_at timestamptz,
  acknowledged_at timestamptz,
  resolved_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists alerts_open_idx on alerts(resolved_at) where resolved_at is null;

-- ---- updated_at automático --------------------------------------------------
create or replace function set_updated_at() returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;

do $$
declare t text;
begin
  for t in select unnest(array[
    'clinics','locations','users','equipment_categories','equipment','cases',
    'case_activities','maintenance_schedules','calibrations','standards',
    'equipment_standards','documents','alerts'
  ]) loop
    execute format(
      'drop trigger if exists trg_set_updated_at on %1$I;
       create trigger trg_set_updated_at before update on %1$I
       for each row execute function set_updated_at();', t);
  end loop;
end $$;
