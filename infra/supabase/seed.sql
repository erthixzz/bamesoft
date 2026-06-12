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

-- ---- HOJAS DE VIDA de prueba (EQ-0001 y EQ-0002) ---------------------------
-- Fechas de compra/garantía viven en `equipment` (campos compartidos).
update equipment set acquisition_date = '2021-03-10', warranty_until = '2024-03-10'
where code = 'EQ-0001';
update equipment set acquisition_date = '2022-06-20', warranty_until = '2025-06-20'
where code = 'EQ-0002';

insert into equipment_life_sheets (equipment_id, formato_codigo, formato_fecha, data)
values
  ('55555555-5555-5555-5555-555555555551', 'MNT-FR-023', '3/Abril/2018',
   $json${
     "identificacion": {
       "activo_fijo": "AF-VENT-001", "registro_tipo": "RS",
       "registro_numero": "INVIMA 2018EBC-0012345", "codigo_prestador": "7600101125-01",
       "sede": "CNSR", "distintivo": "VENT-UCI-03",
       "descripcion": "Ventilador mecanico para soporte respiratorio invasivo y no invasivo en pacientes adultos en unidad de cuidados intensivos."
     },
     "equipo": {
       "tipo": "Ventilador mecanico de adultos", "referencia_lote": "C3-AD",
       "servicio": "UCI Adultos", "ubicacion_texto": "Cama 3 - UCI", "movilidad": "movil"
     },
     "registro_historico": {
       "forma_adquisicion": "compra", "documento_adquisicion": "factura",
       "acta_recibo": "2021-03-10", "fecha_instalacion": "2021-03-12",
       "inicio_operacion": "2021-03-15", "fecha_fabricacion": "2020-11-01",
       "tec_predominante": ["electronico", "neumatico"],
       "costo": 85000000, "moneda": "COP", "vida_util_anios": 10,
       "proveedor": {"nombre": "Hamilton Medical LATAM", "telefono": "018000-112233", "correo": "ventas@hamilton-medical.com", "pais": ""},
       "representante": {"nombre": "BioAndes S.A.S.", "telefono": "301-4455667", "correo": "soporte@bioandes.co", "pais": ""},
       "fabricante": {"nombre": "Hamilton Medical AG", "telefono": "+41 58 610 10 20", "correo": "", "pais": "Suiza"}
     },
     "tecnico": {
       "fuente_alimentacion": ["electricidad", "aire", "vacio"],
       "voltaje_max": "240 V", "voltaje_min": "100 V", "corriente_max": "2 A", "corriente_min": "1 A",
       "potencia": "150 VA", "frecuencia": "50-60 Hz", "presion": "4.1 bar", "velocidad": "",
       "peso": "12.5 Kg", "temperatura": "10-40 C", "otros": "35 x 38 x 56 cm",
       "rangos": {"voltaje": "100-240 V", "corriente": "1-2 A", "potencia": "150 VA", "humedad": "15-95%", "temperatura": "10-40 C", "frecuencia": "50-60 Hz", "presion": "2.8-6 bar", "velocidad": ""},
       "accesorios": "Circuito paciente reutilizable, sensor de flujo, brazo soporte, bateria interna, filtro HEPA.",
       "recomendaciones": "Verificar sensor de flujo antes de cada uso. Calibracion de O2 mensual."
     },
     "apoyo_tecnico": {
       "manuales": ["operacion", "mtto"], "planos": ["electronico", "neumatico"],
       "clas_biomedica": ["tto_mto_vida"]
     },
     "componentes": [
       {"nombre": "Sensor de flujo", "marca": "Hamilton", "modelo": "281637", "serie": "FS-0091"},
       {"nombre": "Bateria interna", "marca": "Hamilton", "modelo": "369976", "serie": "BAT-0455"}
     ],
     "mantenimiento": {"frec_mantenimiento": "semestral", "requiere_calibracion": true, "frec_calibracion": "anual"}
   }$json$::jsonb),

  ('55555555-5555-5555-5555-555555555552', 'MNT-FR-023', '3/Abril/2018',
   $json${
     "identificacion": {
       "activo_fijo": "AF-MON-002", "registro_tipo": "RS",
       "registro_numero": "INVIMA 2019EBC-0067890", "codigo_prestador": "7600101125-01",
       "sede": "CNSR", "distintivo": "MON-URG-07",
       "descripcion": "Monitor multiparametrico para vigilancia continua de signos vitales (ECG, SpO2, NIBP, temperatura, respiracion)."
     },
     "equipo": {
       "tipo": "Monitor de signos vitales", "referencia_lote": "uMEC12",
       "servicio": "Urgencias", "ubicacion_texto": "Box 7 - Urgencias", "movilidad": "movil"
     },
     "registro_historico": {
       "forma_adquisicion": "compra", "documento_adquisicion": "orden_compra",
       "acta_recibo": "2022-06-20", "fecha_instalacion": "2022-06-22",
       "inicio_operacion": "2022-06-25", "fecha_fabricacion": "2022-03-01",
       "tec_predominante": ["electronico"],
       "costo": 18500000, "moneda": "COP", "vida_util_anios": 8,
       "proveedor": {"nombre": "Mindray Colombia", "telefono": "018000-998877", "correo": "info@mindray.com.co", "pais": ""},
       "representante": {"nombre": "Medequipos S.A.S.", "telefono": "310-7788990", "correo": "servicio@medequipos.co", "pais": ""},
       "fabricante": {"nombre": "Shenzhen Mindray Bio-Medical", "telefono": "+86 755 8188 8998", "correo": "", "pais": "China"}
     },
     "tecnico": {
       "fuente_alimentacion": ["electricidad"],
       "voltaje_max": "240 V", "voltaje_min": "100 V", "corriente_max": "1.2 A", "corriente_min": "0.6 A",
       "potencia": "80 VA", "frecuencia": "50-60 Hz", "presion": "", "velocidad": "",
       "peso": "4.8 Kg", "temperatura": "0-40 C", "otros": "30 x 24 x 14 cm",
       "rangos": {"voltaje": "100-240 V", "corriente": "0.6-1.2 A", "potencia": "80 VA", "humedad": "10-90%", "temperatura": "0-40 C", "frecuencia": "50-60 Hz", "presion": "", "velocidad": ""},
       "accesorios": "Brazalete NIBP adulto, sensor SpO2, cable ECG 5 derivaciones, sonda de temperatura.",
       "recomendaciones": "Verificar exactitud de NIBP anualmente con simulador."
     },
     "apoyo_tecnico": {
       "manuales": ["operacion", "mtto", "partes"], "planos": ["electronico", "electrico"],
       "clas_biomedica": ["diagnostico"]
     },
     "componentes": [
       {"nombre": "Sensor SpO2", "marca": "Mindray", "modelo": "512F-30", "serie": "SPO-2213"},
       {"nombre": "Brazalete NIBP", "marca": "Mindray", "modelo": "CM1203", "serie": "NIB-7781"}
     ],
     "mantenimiento": {"frec_mantenimiento": "trimestral", "requiere_calibracion": true, "frec_calibracion": "semestral"}
   }$json$::jsonb)
on conflict (equipment_id) do nothing;
