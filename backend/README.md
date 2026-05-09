# Bamesoft · Backend (FastAPI)

API REST modular por dominio. Cada módulo en `app/modules/<dominio>/`
agrupa: `models.py · schemas.py · service.py · routes.py · deps.py`.

## Capas

```
routes      ← FastAPI router, validación, status codes
service     ← lógica de negocio, orquestación
repository  ← (opcional) acceso a datos crudo
models      ← SQLAlchemy 2.0 (mapeado a Postgres / Supabase)
schemas     ← Pydantic v2 (entrada/salida HTTP)
```

## Comandos

```powershell
# Crear venv e instalar
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Migraciones
alembic revision --autogenerate -m "msg"
alembic upgrade head

# Desarrollo
uvicorn app.main:app --reload --port 8000

# Calidad
ruff check . ; ruff format .
mypy app
pytest -q
```

## Variables de entorno

Ver `.env.example`. Las claves clave:

| Var                     | Uso |
| ----------------------- | --- |
| `DATABASE_URL`          | Postgres (Supabase pooler 6543 o directo 5432) |
| `SUPABASE_URL`          | URL del proyecto Supabase |
| `SUPABASE_ANON_KEY`     | Clave anon (front) |
| `SUPABASE_SERVICE_KEY`  | Service role (sólo server) |
| `JWT_SECRET`            | Firma de los tokens (Supabase JWT) |
| `CORS_ORIGINS`          | Orígenes permitidos separados por coma |
