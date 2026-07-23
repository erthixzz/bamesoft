-- ============================================================================
-- Bamesoft · 0012_satisfaction_cv_tecnovigilancia.sql
-- 1) Satisfacción del servicio en el caso: 3 caritas (bueno/regular/malo),
--    medible en reportes por ingeniero y visible en el PDF del caso.
-- 2) Hoja de vida (CV) del usuario: ruta de un archivo único reemplazable.
-- 3) Tecnovigilancia: nuevo tipo de documento para los equipos.
-- ============================================================================

-- ---- 1) Satisfacción del servicio ------------------------------------------
do $$ begin
  create type case_satisfaction as enum ('bueno', 'regular', 'malo');
exception when duplicate_object then null;
end $$;

alter table cases add column if not exists satisfaction case_satisfaction;

-- ---- 2) Hoja de vida (CV) del usuario --------------------------------------
alter table users add column if not exists cv_path varchar(1024);

-- ---- 3) Tecnovigilancia (tipo de documento; idempotente, PG12+) ------------
alter type document_type add value if not exists 'tecnovigilancia';
