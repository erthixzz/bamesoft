-- ============================================================================
-- Bamesoft · 0004_life_sheets.sql
-- Hoja de Vida de Equipo Biomédico (formato clínico tipo MNT-FR-023).
-- Relación 1:1 con `equipment`; el cuerpo del formato vive en JSONB y los
-- campos compartidos (código, marca, serial, clínica, garantía…) se reutilizan
-- desde la fila de `equipment`.
-- ============================================================================

create table if not exists equipment_life_sheets (
  id uuid primary key default gen_random_uuid(),
  equipment_id uuid not null unique references equipment(id) on delete cascade,
  formato_codigo text not null default 'MNT-FR-023',
  formato_fecha text,
  data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists els_equipment_idx on equipment_life_sheets(equipment_id);

-- Clasificar el PDF generado de la hoja de vida (idempotente; PG12+).
alter type document_type add value if not exists 'life_sheet';

-- ---- RLS: misma lógica que `equipment`, atada a la clínica del equipo --------
alter table equipment_life_sheets enable row level security;

drop policy if exists els_select on equipment_life_sheets;
create policy els_select on equipment_life_sheets for select using (
  current_app_role() = 'admin'
  or exists (
    select 1 from equipment e
    where e.id = equipment_life_sheets.equipment_id
      and e.clinic_id = current_clinic_id()
  )
);

drop policy if exists els_write on equipment_life_sheets;
create policy els_write on equipment_life_sheets for all using (
  current_app_role() in ('admin', 'engineer')
) with check (
  current_app_role() in ('admin', 'engineer')
);
