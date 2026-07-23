-- ============================================================================
-- Bamesoft · 0013_case_type_mishandling.sql
-- Nuevo tipo de actividad/caso: "Daño por mal manejo" (mishandling), para
-- clasificar daños causados por uso o manejo incorrecto del equipo.
-- ============================================================================

alter type case_type add value if not exists 'mishandling';
