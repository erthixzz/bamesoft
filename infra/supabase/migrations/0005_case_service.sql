-- ============================================================================
-- Bamesoft · 0005_case_service.sql
-- Soporte de servicio del caso: tiempos de flujo (asignado/aceptado/inicio/fin)
-- y campos de resolución (tiempo de operación, actividad realizada, repuestos,
-- estado final completo/incompleto, receptor y firma). Añade los tipos de
-- documento `photo` y `signature` para las evidencias del caso.
-- ============================================================================

-- ---- Enum de estado final del servicio -------------------------------------
do $$ begin
  create type case_completion as enum ('complete', 'incomplete');
exception when duplicate_object then null;
end $$;

-- ---- Tiempos de flujo (alimentan métricas de productividad) ----------------
alter table cases add column if not exists assigned_at      timestamptz;
alter table cases add column if not exists accepted_at      timestamptz;
alter table cases add column if not exists work_started_at  timestamptz;
alter table cases add column if not exists finished_at      timestamptz;

-- ---- Resolución / soporte de servicio --------------------------------------
alter table cases add column if not exists operation_minutes integer;
alter table cases add column if not exists work_performed    text;
alter table cases add column if not exists parts_count       integer;
alter table cases add column if not exists parts_detail      text;
alter table cases add column if not exists completion        case_completion;
alter table cases add column if not exists receiver_name     varchar(255);
alter table cases add column if not exists receiver_doc      varchar(64);
alter table cases add column if not exists signature_path    varchar(1024);

-- ---- Tipos de documento para evidencias del caso (idempotente; PG12+) ------
alter type document_type add value if not exists 'photo';
alter type document_type add value if not exists 'signature';
