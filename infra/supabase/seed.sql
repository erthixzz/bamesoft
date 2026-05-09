-- ============================================================================
-- Bamesoft · seed.sql · datos demo (idempotente)
-- ============================================================================

insert into clinics (id, name, tax_id, email, phone, address) values
  ('11111111-1111-1111-1111-111111111111',
   'Clínica Demo Bamesoft', 'NIT-900000000-0',
   'admin@demo.bamesoft.com', '+57 300 0000000', 'Bogotá')
on conflict (id) do nothing;

insert into locations (id, clinic_id, code, name, building, floor, room) values
  ('22222222-2222-2222-2222-222222222221',
   '11111111-1111-1111-1111-111111111111',
   'UCI-1', 'UCI Adultos · Sala 1', 'Torre A', '3', '305'),
  ('22222222-2222-2222-2222-222222222222',
   '11111111-1111-1111-1111-111111111111',
   'IMG-RX', 'Imagenología · Rayos X', 'Torre B', '1', '101')
on conflict (id) do nothing;

insert into equipment_categories (id, code, name, description) values
  ('33333333-3333-3333-3333-333333333331', 'VENT', 'Ventiladores',  'Soporte respiratorio'),
  ('33333333-3333-3333-3333-333333333332', 'MON',  'Monitores',     'Multiparamétricos'),
  ('33333333-3333-3333-3333-333333333333', 'IMG',  'Imagenología',  'RX, ECO, TAC, RMN'),
  ('33333333-3333-3333-3333-333333333334', 'LAB',  'Laboratorio',   'Equipos de diagnóstico in-vitro')
on conflict (id) do nothing;

insert into standards (id, code, name, issuer, version, description) values
  ('44444444-4444-4444-4444-444444444441',
   'ISO 13485', 'Sistemas de gestión de calidad para dispositivos médicos',
   'ISO', '2016', 'Norma de SGC aplicable a fabricantes y servicios.'),
  ('44444444-4444-4444-4444-444444444442',
   'IEC 60601-1', 'Equipos electromédicos · Requisitos generales de seguridad',
   'IEC', '3.2', 'Seguridad básica y rendimiento esencial.'),
  ('44444444-4444-4444-4444-444444444443',
   'INVIMA-RIPE', 'Registro de Importadores y Productores de Equipos',
   'INVIMA', '2024', 'Cumplimiento regulatorio Colombia.')
on conflict (id) do nothing;

insert into equipment (id, code, qr_token, name, brand, model, serial_number,
                        manufacturer, category_id, risk_class, status,
                        clinic_id, location_id)
values
  ('55555555-5555-5555-5555-555555555551',
   'EQ-0001', 'demo-token-0001', 'Ventilador Mecánico Adultos',
   'Hamilton', 'C3', 'SN-HAM-0001', 'Hamilton Medical',
   '33333333-3333-3333-3333-333333333331', 'IIb', 'operational',
   '11111111-1111-1111-1111-111111111111',
   '22222222-2222-2222-2222-222222222221'),
  ('55555555-5555-5555-5555-555555555552',
   'EQ-0002', 'demo-token-0002', 'Monitor Multiparámetro',
   'Mindray', 'uMEC12', 'SN-MIN-0002', 'Mindray',
   '33333333-3333-3333-3333-333333333332', 'IIa', 'operational',
   '11111111-1111-1111-1111-111111111111',
   '22222222-2222-2222-2222-222222222221')
on conflict (id) do nothing;

-- Plan preventivo cada 180 días
insert into maintenance_schedules (equipment_id, name, frequency_days, next_due_at)
select id, 'Mantenimiento semestral', 180, current_date + interval '60 days'
from equipment
where code in ('EQ-0001','EQ-0002')
on conflict do nothing;
