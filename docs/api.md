# API · `/api/v1`

Toda la API requiere `Authorization: Bearer <jwt-supabase>` salvo `/auth/login`.

| Recurso | Endpoints |
| --- | --- |
| **auth**          | `POST /auth/login` · `GET /auth/whoami` |
| **users**         | `GET /users` · `GET /users/me` · `GET /users/{id}` · `POST /users` · `PATCH /users/{id}` · `DELETE /users/{id}` |
| **clinics**       | `GET /clinics` · `POST /clinics` · `GET /clinics/{id}` · `PATCH /clinics/{id}` · `GET /clinics/{id}/locations` · `POST /clinics/{id}/locations` · `PATCH /clinics/locations/{id}` |
| **equipment**     | `GET /equipment` · `POST /equipment` · `GET /equipment/{id}` · `PATCH /equipment/{id}` · `POST /equipment/{id}/regenerate-qr` · `GET /equipment/{id}/qr.png` · `GET /equipment/scan?code=&token=` · `GET /equipment/by-code/{code}` · `GET /equipment/categories` |
| **cases**         | `GET /cases` (filtros: `status`, `assigned_to`, `equipment_id`, `tecnovigilancia`) · `POST /cases` · `GET /cases/{id}` · `GET /cases/by-code/{code}` · `PATCH /cases/{id}` · `POST /cases/{id}/accept` · `PATCH /cases/{id}/tecnovigilancia` · `GET /cases/{id}/activities` · `POST /cases/{id}/activities` |
| **calibrations**  | `GET /calibrations/equipment/{id}` · `POST /calibrations` |
| **maintenance**   | `GET /maintenance/due` · `GET /maintenance/equipment/{id}` · `POST /maintenance` · `PATCH /maintenance/{id}` · `POST /maintenance/{id}/mark-done` |
| **documents**     | `POST /documents` (multipart) · `GET /documents/equipment/{id}` · `GET /documents/case/{id}` · `GET /documents/{id}/signed-url` |
| **standards**     | `GET /standards` · `POST /standards` · `POST /standards/link` · `GET /standards/equipment/{id}` |
| **alerts**        | `GET /alerts` · `POST /alerts` · `POST /alerts/{id}/ack` · `POST /alerts/{id}/resolve` · `POST /alerts/sweep` |
| **reports**       | `GET /reports/dashboard` · `GET /reports/compliance` · `GET /reports/productivity` · `GET /reports/operations` · `GET /reports/equipment` · `GET /reports/services` (filtros: `engineer_id`, `equipment_id`, `satisfaction_min`, `satisfaction_max`, `tecnovigilancia`) · `GET /reports/breakdown` · `GET /reports/tecnovigilancia` (filtro: `stage`) |

## Códigos de respuesta convenidos

| Código | Uso |
| --- | --- |
| 200/201 | Éxito |
| 204 | Sin contenido (deletes) |
| 400 | Validación |
| 401 | Token ausente / inválido |
| 403 | Sin permiso (rol o RLS) |
| 404 | No existe / RLS bloquea lectura |
| 409 | Conflicto (códigos duplicados) |

## Ejemplo: escanear un QR

```http
GET /api/v1/equipment/scan?code=EQ-0001&token=abc... HTTP/1.1
Authorization: Bearer eyJ...
```

```json
{
  "id": "55555555-...",
  "code": "EQ-0001",
  "name": "Ventilador Mecánico Adultos",
  "status": "operational",
  ...
}
```

La OpenAPI completa está en `/openapi.json` y la documentación interactiva en `/docs`.
