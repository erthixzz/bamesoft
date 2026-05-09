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
| `seed.sql`                 | Datos demo (clínica, ingeniero, equipo, normas) |

> **Aviso**: el backend Python usa SQLAlchemy + Alembic como fuente de verdad.
> Estos SQLs son la versión "Supabase-friendly" del esquema, útil cuando
> levantas Supabase Studio o despliegas sin correr Python.
