-- ============================================================================
-- Bamesoft · 0006_equipment_sector.sql
-- Vincula cada equipo a una unidad de servicio (sector): UCI, Hospitalización,
-- Rayos X, etc. Permite listar/agrupar el inventario por unidad de servicio.
-- ============================================================================

alter table equipment
  add column if not exists sector_id uuid references sectors(id) on delete set null;

create index if not exists equipment_sector_idx on equipment(sector_id);
