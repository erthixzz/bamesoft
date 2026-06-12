# Bamesoft — Biomedical Asset Management & Engineering Software

Plataforma web para gestionar el inventario, mantenimiento, casos y cumplimiento
normativo de los equipos médicos de una clínica.

> **Stack**: FastAPI · SvelteKit + TypeScript · Supabase (Postgres / Auth / Storage) · Tailwind · Vercel

---

## Capacidades

| Módulo         | Resumen |
| -------------- | --- |
| **Inventario** | Registro de equipos, categorías, ubicación, foto, QR único por equipo. |
| **Casos**      | Tickets correctivos, preventivos, calibración o instalación. SLA y bitácora. |
| **Historial**  | Trazabilidad por equipo: actividades, repuestos, técnicos, documentos. |
| **Documentos** | Manuales, certificados, hojas de vida y normativa, vinculados a equipo/caso. |
| **Normas**     | Catálogo (ISO 13485, IEC 60601, NTC, INVIMA…) y mapeo a equipos. |
| **Alertas**    | Mantenimiento preventivo vencido, calibración por vencer, casos sin atender. |
| **Reportes**   | KPIs, cronogramas, cumplimiento — exportable para auditorías. |
| **Roles**      | `admin · engineer · client · service · support` con RLS en Supabase. |

## Estructura del repositorio

```
backend/        FastAPI · SQLAlchemy · Pydantic v2 · Alembic
frontend/       SvelteKit · TypeScript · Tailwind · QR (jsQR)
infra/
  supabase/     migraciones SQL, RLS, seeds
docs/           arquitectura, modelo de datos, roles, API, hoja de vida
.github/        CI workflows
```

Cada módulo de `backend/app/modules/<dominio>/` agrupa **models · schemas · service · routes · deps**.
El frontend espeja la misma división en `frontend/src/lib/modules/<dominio>/`.

## Puesta en marcha

### Prerequisitos
- Python 3.11+
- Node 20+ (npm o pnpm)
- Cuenta Supabase (o Postgres local) y Supabase CLI opcional

### Variables de entorno
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```powershell
cd frontend
npm install
npm run dev
```

### Base de datos (Supabase local opcional)
```powershell
cd infra/supabase
supabase start
supabase db reset
```

## Convenciones

- **Conventional Commits** (`feat:`, `fix:`, `chore:`…).
- **Ramas**: `main` (estable) · `dev` (integración) · `feat/*`, `fix/*`.
- **API**: prefijo `/api/v1`.
- **Tests**: `pytest` (backend), `vitest` + `playwright` (frontend).
- **Linters**: `ruff` + `mypy` (backend), `eslint` + `prettier` (frontend).

## Documentación

- [Arquitectura](docs/architecture.md)
- [Modelo de datos](docs/data-model.md)
- [Roles y permisos](docs/roles.md)
- [API](docs/api.md)
- [Hoja de Vida de Equipo Biomédico](docs/hoja-de-vida.md) — formato `MNT-FR-023` (referencia del antiguo `ASPIRADOR.pdf`, ya eliminado)

---

© Bamesoft.
