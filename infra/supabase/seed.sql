-- ============================================================================
-- Bamesoft · seed.sql · datos demo (idempotente)
-- Escenario de prueba: 3 unidades de servicio (UCI, Hospitalización, Rayos X),
-- cada una con 3 equipos: Máquina de anestesia, Desfibrilador y Equipo de Rayos X.
-- ============================================================================

insert into clinics (id, name, tax_id, email, phone, address) values
  ('11111111-1111-1111-1111-111111111111',
   'Clínica Demo Bamesoft', 'NIT-900000000-0',
   'admin@demo.bamesoft.com', '+57 300 0000000', 'Bogotá')
on conflict (id) do nothing;

-- ---- Unidades de servicio (sectores): solo dejamos las 3 del escenario ------
insert into sectors (clinic_id, code, name, description) values
  ('11111111-1111-1111-1111-111111111111', 'UCI',  'UCI',             'Unidad de Cuidados Intensivos'),
  ('11111111-1111-1111-1111-111111111111', 'HOSP', 'Hospitalización', 'Áreas de hospitalización general'),
  ('11111111-1111-1111-1111-111111111111', 'RX',   'Rayos X',         'Imagenología y radiología')
on conflict (clinic_id, code) do update set name = excluded.name, description = excluded.description;

-- Quitar los sectores demo que no pertenecen al escenario (cases.sector_id => SET NULL).
delete from sectors
where clinic_id = '11111111-1111-1111-1111-111111111111'
  and code in ('CIR', 'URG', 'IMG', 'LAB', 'GEN');

-- ---- Ubicaciones físicas (una por unidad de servicio) ----------------------
insert into locations (id, clinic_id, code, name, building, floor, room) values
  ('22222222-2222-2222-2222-222222222221',
   '11111111-1111-1111-1111-111111111111',
   'UCI-1',  'UCI · Sala 1',          'Torre A', '3', '305'),
  ('22222222-2222-2222-2222-222222222222',
   '11111111-1111-1111-1111-111111111111',
   'HOSP-1', 'Hospitalización · Ala B','Torre A', '2', '210'),
  ('22222222-2222-2222-2222-222222222223',
   '11111111-1111-1111-1111-111111111111',
   'RX-1',   'Rayos X · Sala 1',       'Torre B', '1', '101')
on conflict (id) do nothing;

-- ---- Categorías de equipo ---------------------------------------------------
insert into equipment_categories (id, code, name, description) values
  ('33333333-3333-3333-3333-333333333333', 'IMG',  'Imagenología',   'RX, ECO, TAC, RMN'),
  ('33333333-3333-3333-3333-333333333335', 'ANES', 'Anestesia',      'Máquinas de anestesia y soporte'),
  ('33333333-3333-3333-3333-333333333336', 'DESF', 'Desfibrilación', 'Desfibriladores y cardioversión')
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

-- ---- Limpiar equipos demo antiguos (sus hojas de vida/casos caen en cascada) -
delete from equipment where code in ('EQ-0001', 'EQ-0002');

-- ---- 9 equipos: 3 por unidad de servicio ------------------------------------
insert into equipment (id, code, qr_token, name, brand, model, serial_number,
                        manufacturer, category_id, risk_class, status,
                        clinic_id, location_id)
values
  -- UCI
  ('55555555-5555-5555-5555-5555555550a1', 'ANE-UCI-01', 'demo-token-ane-uci', 'Máquina de Anestesia', 'Dräger', 'Fabius GS', 'SN-ANE-UCI-01', 'Dräger', '33333333-3333-3333-3333-333333333335', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222221'),
  ('55555555-5555-5555-5555-5555555550a2', 'DES-UCI-01', 'demo-token-des-uci', 'Desfibrilador',        'Philips','HeartStart','SN-DES-UCI-01', 'Philips','33333333-3333-3333-3333-333333333336', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222221'),
  ('55555555-5555-5555-5555-5555555550a3', 'RX-UCI-01',  'demo-token-rx-uci',  'Equipo de Rayos X',    'Siemens','Mobilett','SN-RX-UCI-01',  'Siemens','33333333-3333-3333-3333-333333333333', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222221'),
  -- Hospitalización
  ('55555555-5555-5555-5555-5555555550b1', 'ANE-HOS-01', 'demo-token-ane-hos', 'Máquina de Anestesia', 'Dräger', 'Fabius GS', 'SN-ANE-HOS-01', 'Dräger', '33333333-3333-3333-3333-333333333335', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'),
  ('55555555-5555-5555-5555-5555555550b2', 'DES-HOS-01', 'demo-token-des-hos', 'Desfibrilador',        'Philips','HeartStart','SN-DES-HOS-01', 'Philips','33333333-3333-3333-3333-333333333336', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'),
  ('55555555-5555-5555-5555-5555555550b3', 'RX-HOS-01',  'demo-token-rx-hos',  'Equipo de Rayos X',    'Siemens','Mobilett','SN-RX-HOS-01',  'Siemens','33333333-3333-3333-3333-333333333333', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222222'),
  -- Rayos X
  ('55555555-5555-5555-5555-5555555550c1', 'ANE-RAD-01', 'demo-token-ane-rad', 'Máquina de Anestesia', 'Dräger', 'Fabius GS', 'SN-ANE-RAD-01', 'Dräger', '33333333-3333-3333-3333-333333333335', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222223'),
  ('55555555-5555-5555-5555-5555555550c2', 'DES-RAD-01', 'demo-token-des-rad', 'Desfibrilador',        'Philips','HeartStart','SN-DES-RAD-01', 'Philips','33333333-3333-3333-3333-333333333336', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222223'),
  ('55555555-5555-5555-5555-5555555550c3', 'RX-RAD-01',  'demo-token-rx-rad',  'Equipo de Rayos X',    'Siemens','Mobilett','SN-RX-RAD-01',  'Siemens','33333333-3333-3333-3333-333333333333', 'IIb', 'operational', '11111111-1111-1111-1111-111111111111', '22222222-2222-2222-2222-222222222223')
on conflict (id) do nothing;

-- Asignar la unidad de servicio (sector) por área, según la ubicación.
update equipment set sector_id = (select id from sectors where clinic_id = equipment.clinic_id and code = 'UCI')
where code in ('ANE-UCI-01', 'DES-UCI-01', 'RX-UCI-01');
update equipment set sector_id = (select id from sectors where clinic_id = equipment.clinic_id and code = 'HOSP')
where code in ('ANE-HOS-01', 'DES-HOS-01', 'RX-HOS-01');
update equipment set sector_id = (select id from sectors where clinic_id = equipment.clinic_id and code = 'RX')
where code in ('ANE-RAD-01', 'DES-RAD-01', 'RX-RAD-01');

-- Plan preventivo cada 180 días para los 9 equipos.
insert into maintenance_schedules (equipment_id, name, frequency_days, next_due_at)
select id, 'Mantenimiento semestral', 180, current_date + interval '60 days'
from equipment
where clinic_id = '11111111-1111-1111-1111-111111111111'
on conflict do nothing;
