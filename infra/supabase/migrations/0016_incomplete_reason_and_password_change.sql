-- ============================================================================
-- Bamesoft · 0016_incomplete_reason_and_password_change.sql
-- 1) Razón del estado final del caso: cuando el servicio queda INCOMPLETO hay
--    que dejar por escrito por qué (repuesto no disponible, equipo en uso,
--    falta autorización…). Sin esto el soporte firmado no explica nada.
-- 2) Cambio de contraseña obligatorio en el primer acceso: las cuentas nuevas
--    se crean con una contraseña por defecto que el usuario debe reemplazar
--    antes de poder usar la aplicación.
-- ============================================================================

-- ---- 1) Razón del cierre incompleto ----------------------------------------
alter table cases add column if not exists incomplete_reason text;

-- Coherencia: la razón solo tiene sentido si el estado final es `incomplete`.
-- Si el caso se reabre o se marca como completo, la razón no puede quedar
-- arrastrada de un cierre anterior.
-- `coalesce(...)` y no `completion = 'incomplete'` a secas: con `completion`
-- nulo la comparación da NULL, y un CHECK que devuelve NULL se considera
-- satisfecho — el motivo se colaría en casos sin estado final.
alter table cases drop constraint if exists cases_incomplete_reason_coherent;
alter table cases add constraint cases_incomplete_reason_coherent check (
  coalesce(completion = 'incomplete', false) or incomplete_reason is null
);

comment on column cases.incomplete_reason is
  'Motivo por el que el servicio quedó incompleto. Obligatorio si completion = incomplete; null en cualquier otro caso.';

-- ---- 2) Cambio de contraseña en el primer acceso ---------------------------
alter table users add column if not exists must_change_password boolean not null default false;

comment on column users.must_change_password is
  'La cuenta se creó con una contraseña por defecto: la app obliga a cambiarla antes de dejar entrar.';

-- Las cuentas que ya existen no se ven afectadas: sus dueños eligieron su
-- propia contraseña al ser dadas de alta.
