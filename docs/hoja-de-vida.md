# Hoja de Vida de Equipo Biomédico

## Sobre el archivo `ASPIRADOR.pdf` (eliminado)

En la raíz del repositorio existió temporalmente un archivo **`ASPIRADOR.pdf`**.
Era el **PDF de referencia** que entregó la clínica: la hoja de vida en papel de un
*Aspirador portátil Pulmo-Med 7E-D*, diligenciada con el formato clínico colombiano
estándar **`MNT-FR-023` — "Hoja de Vida Equipo Biomédico"** (rev. 3/Abril/2018).

Sirvió únicamente como **modelo del formato** a replicar dentro de la aplicación. Una
vez implementada la funcionalidad, **el PDF fue eliminado del repositorio** (no es código
ni dato productivo) y su contenido/estructura quedó documentado aquí de forma explícita.

> El formato vivía en papel/PDF externo. Ahora la hoja de vida se crea, consulta, edita y
> exporta a PDF **directamente sobre cada equipo** dentro de Bamesoft.

## Encabezado

- **Logo y nombre de la clínica**: se toman de la clínica del equipo (`clinics.name`,
  `clinics.logo_url`). No se escribe a mano.
- **Código del formato** (`MNT-FR-023`) y **Fecha del formato** (`3/Abril/2018`): editables.
- Marca **Bamesoft** en el PDF exportado.

## Secciones del formato

1. **Identificación** — código del equipo, activo fijo, registro (RS/PC/NR) + número,
   código del prestador, sede, distintivo, serie, descripción.
2. **Equipo** — nombre, tipo, marca, modelo, referencia/lote, servicio, ubicación,
   movilidad (móvil/fijo), clase de riesgo.
3. **Registro histórico** — forma y documento de adquisición, fechas (compra, acta de
   recibo, instalación, inicio de operación, vencimiento de garantía, fabricación),
   tecnología predominante (eléctrico/electrónico/mecánico/electromecánico/hidráulico/
   neumático), costo, vida útil, proveedor / representante / fabricante (nombre, teléfono,
   correo/país).
4. **Registro técnico de instalación** — fuente de alimentación (agua/gas/aire/vapor/
   electricidad/vacío/otro).
5. **Registro técnico de funcionamiento** — voltaje, corriente, potencia, frecuencia,
   presión, velocidad, peso, temperatura, otros; rangos de operación; accesorios;
   recomendaciones del fabricante.
6. **Registro de apoyo técnico** — manuales (operación/mtto/partes), planos (electrónico/
   eléctrico/neumático/mecánico), clasificación biomédica, clasificación por riesgo.
7. **Componentes** — lista de {nombre, marca, modelo, serie}.
8. **Mantenimiento** — frecuencia de mantenimiento, requiere calibración (sí/no),
   frecuencia de calibración.

## Cómo está implementado

| Capa | Ubicación |
| --- | --- |
| Tabla (1:1 con equipo, cuerpo en JSONB) | `equipment_life_sheets` — migración `infra/supabase/migrations/0004_life_sheets.sql` |
| Modelo | `backend/app/modules/equipment/models.py` → `EquipmentLifeSheet` |
| Schemas (validación del JSONB) | `backend/app/modules/equipment/life_sheet_schemas.py` |
| Service (consulta + upsert + sync a equipo) | `backend/app/modules/equipment/service.py` → `get_life_sheet`, `upsert_life_sheet` |
| Endpoints | `GET/PUT /equipment/{id}/life-sheet` (`routes.py`) |
| Página editable | `frontend/src/routes/(app)/equipment/[id]/hoja-de-vida/+page.svelte` |
| PDF imprimible + export | `components/HojaVidaPrintable.svelte` · `pdf.ts` (jsPDF + html2canvas) |
| Datos de prueba | `infra/supabase/seed.sql` (EQ-0001, EQ-0002) |

**Campos compartidos con el equipo** (no se duplican; se sincronizan en cada guardado):
código, nombre, marca, modelo, serial/serie, fabricante, clase de riesgo, estado,
ubicación, fecha de compra (`acquisition_date`), vencimiento de garantía
(`warranty_until`), foto y notas. El resto de campos del formato viven en `data` (JSONB).

El PDF exportado puede **adjuntarse y guardarse** como documento del equipo
(tipo `life_sheet`), reutilizando el flujo de Documentos + Supabase Storage.
