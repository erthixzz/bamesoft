# Bamesoft · Frontend (SvelteKit)

App web responsiva con módulos espejo de la API. Cada dominio vive en
`src/lib/modules/<dominio>/` y trae su `api.ts`, `types.ts` y componentes propios.

## Comandos

```powershell
npm install
npm run dev          # http://localhost:5173
npm run build
npm run preview
npm run lint
npm run typecheck
```

## Variables de entorno

```ini
PUBLIC_API_URL=http://localhost:8000/api/v1
PUBLIC_SUPABASE_URL=
PUBLIC_SUPABASE_ANON_KEY=
```

## Estructura

```
src/
  app.html / app.css / app.d.ts
  hooks.server.ts
  lib/
    api/             cliente HTTP, manejo de auth
    components/      UI base (Button, Input, Card, Sidebar, QRScanner...)
    stores/          stores reactivos (auth, toasts)
    utils/           formatters, permissions
    supabase.ts      cliente Supabase (browser)
    modules/
      auth/  equipment/  cases/  alerts/  reports/  ...
  routes/
    (auth)/login
    (app)/dashboard, equipment, cases, alerts, reports, documents, standards, settings
```
