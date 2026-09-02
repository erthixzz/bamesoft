# Modelo de datos

```
clinics ──< locations
   │
   └──< users (role, clinic_id)
         │
         └──< cases ──< case_activities
               │
               └──> equipment ──< maintenance_schedules
                       │       ──< calibrations
                       │       ──< documents
                       └──< equipment_standards >── standards
alerts (referencias polimórficas a equipment / case)
```

## Entidades

### `clinics`
Centro médico. Una instalación de Bamesoft puede gestionar varias clínicas
(multi-tenant), aunque en producción es típica 1.

### `locations`
Ubicación física dentro de una clínica (UCI sala 3, sala de RX, etc.).

### `users`
Perfil sincronizado con `auth.users` (Supabase). Su `id` es el `auth.uid()`.
Roles: `admin`, `engineer`, `client`, `service`, `support`.

### `equipment_categories`
Catálogo global de tipos: ventiladores, monitores, imagenología, laboratorio…

### `equipment`
Activo médico individual. Campos relevantes:
- `code` (interno) y `qr_token` (opaco, regenerable).
- `risk_class` (I, IIa, IIb, III).
- `status`: `operational | out_of_service | under_maintenance | retired`.

### `cases`
Ticket sobre un equipo. Tipos: `corrective | preventive | calibration |
installation | inspection | mishandling`. Lleva su propio `code`
(`BMS-YYYYMM-XXXX`), `opened_at`, `sla_due_at`, `closed_at`.

- **Satisfacción**: `satisfaction_score` (smallint 1-7, escala Likert —
  1 Muy insatisfecho … 4 Neutral … 7 Muy satisfecho). La columna `satisfaction`
  (enum de 3 caritas) quedó obsoleta en la migración 0015; se conserva solo
  como respaldo del backfill y la aplicación no la usa.
- **Tecnovigilancia**: `is_tecnovigilancia` marca los casos en los que el equipo
  causó —o pudo causar— daño al paciente o al operador.
  `tecnovigilancia_stage` es la etapa del proceso (`detection | report |
  investigation | corrective_action | follow_up | closed`),
  `tecnovigilancia_description` el relato breve del evento y
  `tecnovigilancia_at` cuándo se marcó. Un check garantiza que un caso sin la
  marca no arrastre etapa ni descripción.

### `case_activities`
Bitácora inmutable: cada acción (asignación, cambio de estado, nota técnica)
queda registrada con autor y timestamp.

### `maintenance_schedules`
Plan preventivo por equipo (cada N días). Calcula `next_due_at`.

### `calibrations`
Resultado puntual con `performed_at`, `expires_at`, certificado adjunto.

### `documents`
Archivos en Supabase Storage. Pueden colgar de `clinic`, `equipment` o `case`.

### `standards` / `equipment_standards`
Catálogo de normas (ISO 13485, IEC 60601, INVIMA, NTC, …) y mapeo
many-to-many con equipos.

### `alerts`
Generadas automáticamente (`/alerts/sweep`) o manualmente. Tipos:
`preventive_due`, `calibration_due`, `warranty_expiring`, `case_sla`, `custom`.

## Reglas de borrado

- Borrar una clínica: cascada a equipos, casos, alertas y documentos.
- Borrar un equipo: cascada a casos, calibraciones, mantenimientos.
- Borrar un usuario: NO cascada; en `cases.assigned_to` queda en NULL.
