-- ============================================================================
-- Bamesoft · 0015_tecnovigilancia_cases_and_likert.sql
-- 1) Tecnovigilancia en el CASO: bandera, etapa del proceso (INVIMA) y una
--    descripción breve del evento adverso / incidente con el equipo.
--    (Antes solo existía como tipo de documento del equipo; el evento se
--     reporta y se sigue sobre el caso, que es donde está la trazabilidad.)
-- 2) Satisfacción del servicio: escala Likert de 7 puntos, en reemplazo de las
--    3 caritas (bueno/regular/malo).
-- ============================================================================

-- ---- 1) Tecnovigilancia del caso -------------------------------------------
do $$ begin
  create type tecnovigilancia_stage as enum (
    'detection',          -- Detección / identificación del evento
    'report',             -- Reporte / notificación (INVIMA, comité)
    'investigation',      -- Investigación y análisis de causa
    'corrective_action',  -- Acción correctiva / preventiva
    'follow_up',          -- Seguimiento y verificación de eficacia
    'closed'              -- Cerrado
  );
exception when duplicate_object then null;
end $$;

alter table cases add column if not exists is_tecnovigilancia      boolean not null default false;
alter table cases add column if not exists tecnovigilancia_stage   tecnovigilancia_stage;
alter table cases add column if not exists tecnovigilancia_description text;
alter table cases add column if not exists tecnovigilancia_at      timestamptz;

-- Los reportes filtran casi siempre por "solo casos de tecnovigilancia":
-- índice parcial para no pagar por el 99 % de casos que no lo son.
create index if not exists cases_tecnovigilancia_idx
  on cases (tecnovigilancia_stage)
  where is_tecnovigilancia;

-- Coherencia: si el caso no es de tecnovigilancia no puede arrastrar etapa ni
-- descripción de un marcado anterior.
alter table cases drop constraint if exists cases_tecnovigilancia_coherent;
alter table cases add constraint cases_tecnovigilancia_coherent check (
  is_tecnovigilancia
  or (tecnovigilancia_stage is null and tecnovigilancia_description is null)
);

comment on column cases.is_tecnovigilancia is
  'El caso corresponde a un evento adverso / incidente con el dispositivo (tecnovigilancia).';
comment on column cases.tecnovigilancia_stage is
  'Etapa del proceso de tecnovigilancia: detección, reporte, investigación, acción correctiva, seguimiento, cierre.';

-- ---- 2) Satisfacción: escala Likert de 7 puntos ----------------------------
alter table cases add column if not exists satisfaction_score smallint;

alter table cases drop constraint if exists cases_satisfaction_score_range;
alter table cases add constraint cases_satisfaction_score_range check (
  satisfaction_score is null or satisfaction_score between 1 and 7
);

-- Backfill desde las 3 caritas (columna heredada `satisfaction`):
--   malo → 2 (Insatisfecho) · regular → 4 (Neutral) · bueno → 6 (Satisfecho)
update cases
   set satisfaction_score = case satisfaction
         when 'bueno'   then 6
         when 'regular' then 4
         when 'malo'    then 2
       end
 where satisfaction is not null
   and satisfaction_score is null;

-- La columna `satisfaction` (enum de 3 caritas) queda OBSOLETA: se conserva
-- únicamente como respaldo histórico del backfill. La aplicación ya no la lee
-- ni la escribe.
comment on column cases.satisfaction is
  'OBSOLETO (0015): reemplazado por cases.satisfaction_score (Likert 1-7).';
comment on column cases.satisfaction_score is
  'Satisfacción del servicio, Likert de 7 puntos: 1=Muy insatisfecho … 4=Neutral … 7=Muy satisfecho.';
