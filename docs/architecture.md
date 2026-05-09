# Arquitectura

```
┌────────────────────┐        HTTPS / JWT          ┌──────────────────────┐
│  SvelteKit (web)   │ ─────────────────────────▶  │   FastAPI (api)      │
│  Vercel · TS · TW  │ ◀──────── JSON ──────────── │  Python 3.11         │
└─────────┬──────────┘                             └─────────┬────────────┘
          │ Auth (Supabase JS)                               │ SQLAlchemy 2 async
          ▼                                                   ▼
┌────────────────────┐                              ┌──────────────────────┐
│   Supabase Auth    │                              │   PostgreSQL (Supabase) │
│   (GoTrue, JWT)    │                              │   RLS por rol/clínica │
└────────────────────┘                              └─────────┬────────────┘
                                                              │ Storage SDK
                                                              ▼
                                                   ┌──────────────────────┐
                                                   │  Supabase Storage    │
                                                   │  (manuales, certif.) │
                                                   └──────────────────────┘
```

## Decisiones clave

- **Modular por dominio**: cada `module/` agrupa modelos, schemas, servicios,
  rutas y dependencias. Acoplamiento bajo entre módulos, alto cohesión interna.
- **Auth delegada a Supabase**: el frontend obtiene el JWT y lo manda al backend
  como `Authorization: Bearer …`. El backend lo valida con el `JWT_SECRET`
  compartido y crea/recupera el perfil en la tabla `users`.
- **Permisos en dos capas**: chequeo en API (`require_role`) + RLS en Postgres
  (defensa en profundidad).
- **QR opaco**: `qr_token` random e invalidable (`/regenerate-qr`). El payload
  versiona el formato (`v=1`) para evolución futura.
- **Async end-to-end**: `asyncpg` + `AsyncSession` evitan bloqueos.
- **Storage**: archivos van a Supabase Storage; las URLs públicas se firman
  con expiración corta.

## Capas backend

```
routes      ← FastAPI router, validación, status codes
service     ← lógica de negocio, transiciones, audit
repository* ← (opcional) acceso a datos crudo
models      ← SQLAlchemy 2.0
schemas     ← Pydantic v2
deps        ← inyecciones (auth, db)
```

## Despliegue sugerido

| Componente | Plataforma |
| --- | --- |
| Frontend  | Vercel (`adapter-vercel`) |
| Backend   | Vercel Functions / Fly.io / Railway / Cloud Run |
| BD + Auth + Storage | Supabase |
| Dominio   | `bamesoft.app` (frontend), `api.bamesoft.app` (api) |
