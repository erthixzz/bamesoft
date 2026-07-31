# Bamesoft · Infra (Supabase)

Migraciones SQL idempotentes que reproducen el esquema de SQLAlchemy
y aplican Row-Level Security alineado con los roles del backend.

## Scripts

```powershell
supabase start                # arranca Postgres + GoTrue + Storage local
supabase db reset             # corre migrations/*.sql + seed.sql
supabase migration new <slug> # crea archivo nuevo
```

## Archivos

| Archivo | Contenido |
| --- | --- |
| `migrations/0001_init.sql` | Tipos enum, tablas y FKs |
| `migrations/0002_rls.sql`  | Políticas RLS por rol |
| `check_rls.sql`            | Auditoría: tablas de `public` expuestas vía PostgREST |
| `seed.sql`                 | Datos demo (clínica, ingeniero, equipo, normas) |

## Regla: toda tabla nueva lleva RLS

Supabase expone el esquema `public` vía **PostgREST** con la anon key, que viaja
en el bundle del frontend. Una tabla sin RLS es legible y escribible desde
internet **sin pasar por FastAPI**. Toda migración que cree una tabla debe
incluir, en el mismo archivo:

```sql
alter table <tabla> enable row level security;
revoke all on table <tabla> from anon, authenticated;
```

Sin políticas, eso equivale a *deny-all* para PostgREST y la app sigue igual: el
backend se conecta como **owner** de las tablas y en Postgres el owner omite RLS.
Si la tabla sí debe leerse desde el cliente, añade políticas explícitas.

> **Nunca uses `force row level security`**: haría que el owner deje de omitir
> RLS y el backend perdería acceso a la tabla.

Esto lo verifica `backend/tests/test_rls_coverage.py` en cada PR (análisis
estático de estos SQL, sin DB). Para comprobar la BD **real** —y detectar tablas
creadas a mano en Studio— corre `check_rls.sql`; debe devolver cero filas.

> **Aviso**: el backend Python usa SQLAlchemy + Alembic como fuente de verdad.
> Estos SQLs son la versión "Supabase-friendly" del esquema, útil cuando
> levantas Supabase Studio o despliegas sin correr Python.
