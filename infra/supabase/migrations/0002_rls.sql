-- ============================================================================
-- Bamesoft · 0002_rls.sql
-- Row-Level Security: cada usuario sólo ve los datos de su clínica
-- (excepto admin que ve todo).
-- ============================================================================

-- Helper: rol y clínica del JWT actual
create or replace function current_app_role() returns user_role
  language sql stable as $$
  select coalesce(
    (select role from users where id = auth.uid()),
    'client'::user_role
  );
$$;

create or replace function current_clinic_id() returns uuid
  language sql stable as $$
  select clinic_id from users where id = auth.uid();
$$;

-- Habilitar RLS en todas las tablas operativas
alter table clinics enable row level security;
alter table locations enable row level security;
alter table users enable row level security;
alter table equipment enable row level security;
alter table equipment_categories enable row level security;
alter table cases enable row level security;
alter table case_activities enable row level security;
alter table maintenance_schedules enable row level security;
alter table calibrations enable row level security;
alter table standards enable row level security;
alter table equipment_standards enable row level security;
alter table documents enable row level security;
alter table alerts enable row level security;

-- ----------------------------------------------------------------------------
-- USERS: cada uno ve su propio perfil; admin ve todo
-- ----------------------------------------------------------------------------
drop policy if exists users_select on users;
create policy users_select on users for select using (
  id = auth.uid() or current_app_role() = 'admin'
);

drop policy if exists users_update_self on users;
create policy users_update_self on users for update using (
  id = auth.uid() or current_app_role() = 'admin'
);

-- ----------------------------------------------------------------------------
-- CLINICS / LOCATIONS: el usuario ve su clínica; admin ve todas
-- ----------------------------------------------------------------------------
drop policy if exists clinics_select on clinics;
create policy clinics_select on clinics for select using (
  current_app_role() = 'admin' or id = current_clinic_id()
);

drop policy if exists clinics_admin on clinics;
create policy clinics_admin on clinics for all using (current_app_role() = 'admin')
  with check (current_app_role() = 'admin');

drop policy if exists locations_select on locations;
create policy locations_select on locations for select using (
  current_app_role() = 'admin' or clinic_id = current_clinic_id()
);

drop policy if exists locations_admin on locations;
create policy locations_admin on locations for all using (current_app_role() = 'admin')
  with check (current_app_role() = 'admin');

-- ----------------------------------------------------------------------------
-- EQUIPMENT (incl. categorías globales)
-- ----------------------------------------------------------------------------
drop policy if exists equipment_select on equipment;
create policy equipment_select on equipment for select using (
  current_app_role() = 'admin' or clinic_id = current_clinic_id()
);

drop policy if exists equipment_write on equipment;
create policy equipment_write on equipment for all using (
  current_app_role() in ('admin','engineer')
) with check (current_app_role() in ('admin','engineer'));

drop policy if exists equipment_categories_read on equipment_categories;
create policy equipment_categories_read on equipment_categories for select using (true);

drop policy if exists equipment_categories_admin on equipment_categories;
create policy equipment_categories_admin on equipment_categories for all
  using (current_app_role() = 'admin') with check (current_app_role() = 'admin');

-- ----------------------------------------------------------------------------
-- CASES / ACTIVITIES
-- ----------------------------------------------------------------------------
drop policy if exists cases_select on cases;
create policy cases_select on cases for select using (
  current_app_role() = 'admin'
  or exists (
    select 1 from equipment e
    where e.id = cases.equipment_id
      and e.clinic_id = current_clinic_id()
  )
);

drop policy if exists cases_write on cases;
create policy cases_write on cases for all using (
  current_app_role() in ('admin','engineer','service','support')
) with check (
  current_app_role() in ('admin','engineer','service','support')
);

drop policy if exists case_activities_select on case_activities;
create policy case_activities_select on case_activities for select using (
  exists (select 1 from cases c where c.id = case_activities.case_id)
);

drop policy if exists case_activities_insert on case_activities;
create policy case_activities_insert on case_activities for insert with check (
  current_app_role() in ('admin','engineer','service','support','client')
);

-- ----------------------------------------------------------------------------
-- MAINTENANCE / CALIBRATIONS
-- ----------------------------------------------------------------------------
drop policy if exists pm_select on maintenance_schedules;
create policy pm_select on maintenance_schedules for select using (
  exists (select 1 from equipment e where e.id = maintenance_schedules.equipment_id)
);

drop policy if exists pm_write on maintenance_schedules;
create policy pm_write on maintenance_schedules for all using (
  current_app_role() in ('admin','engineer')
) with check (current_app_role() in ('admin','engineer'));

drop policy if exists cal_select on calibrations;
create policy cal_select on calibrations for select using (
  exists (select 1 from equipment e where e.id = calibrations.equipment_id)
);

drop policy if exists cal_write on calibrations;
create policy cal_write on calibrations for all using (
  current_app_role() in ('admin','engineer','service')
) with check (current_app_role() in ('admin','engineer','service'));

-- ----------------------------------------------------------------------------
-- DOCUMENTS / STANDARDS
-- ----------------------------------------------------------------------------
drop policy if exists documents_select on documents;
create policy documents_select on documents for select using (
  current_app_role() = 'admin'
  or clinic_id = current_clinic_id()
  or exists (select 1 from equipment e
             where e.id = documents.equipment_id and e.clinic_id = current_clinic_id())
);

drop policy if exists documents_write on documents;
create policy documents_write on documents for all using (
  current_app_role() in ('admin','engineer','service','support')
) with check (current_app_role() in ('admin','engineer','service','support'));

drop policy if exists standards_read on standards;
create policy standards_read on standards for select using (true);

drop policy if exists standards_admin on standards;
create policy standards_admin on standards for all
  using (current_app_role() = 'admin') with check (current_app_role() = 'admin');

drop policy if exists eq_std_read on equipment_standards;
create policy eq_std_read on equipment_standards for select using (true);

drop policy if exists eq_std_admin on equipment_standards;
create policy eq_std_admin on equipment_standards for all
  using (current_app_role() in ('admin','engineer'))
  with check (current_app_role() in ('admin','engineer'));

-- ----------------------------------------------------------------------------
-- ALERTS
-- ----------------------------------------------------------------------------
drop policy if exists alerts_select on alerts;
create policy alerts_select on alerts for select using (
  current_app_role() = 'admin'
  or exists (select 1 from equipment e
             where e.id = alerts.equipment_id and e.clinic_id = current_clinic_id())
);

drop policy if exists alerts_write on alerts;
create policy alerts_write on alerts for all using (
  current_app_role() in ('admin','engineer','service','support')
) with check (current_app_role() in ('admin','engineer','service','support'));
