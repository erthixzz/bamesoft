# Roles y permisos

| Rol         | ¿Qué hace? | Acceso típico |
| ----------- | --- | --- |
| **admin**   | Configura el sistema. Crea clínicas, usuarios y normas. Ve todo. | Todo |
| **engineer**(biomédico) | Inventaría equipos, gestiona casos, calibra. | CRUD equipos, casos, calibraciones, mantenimientos |
| **service** | Empresa o técnico de servicio externo. Atiende los casos asignados. | RW casos asignados, lectura equipos |
| **support** | Soporte / mesa de ayuda. Crea casos y enruta. | Crea casos, ve alertas |
| **client**  | Personal de la clínica (médicos, enfermeras). Reporta fallas. | Crea casos, ve sus equipos |

## Matriz de operaciones

| Operación                         | admin | engineer | service | support | client |
|-----------------------------------|:----:|:--------:|:-------:|:-------:|:------:|
| Crear clínica / usuario           |  ✅  |          |         |         |        |
| Crear / editar equipo             |  ✅  |   ✅    |         |         |        |
| Regenerar QR                      |  ✅  |   ✅    |         |         |        |
| Crear caso                        |  ✅  |   ✅    |   ✅    |   ✅    |   ✅   |
| Asignar caso                      |  ✅  |   ✅    |         |   ✅    |        |
| Avanzar caso (in_progress, …)     |  ✅  |   ✅    |   ✅    |   ✅    |        |
| Cerrar caso                       |  ✅  |   ✅    |   ✅    |         |        |
| Subir documento                   |  ✅  |   ✅    |   ✅    |   ✅    |        |
| Registrar calibración             |  ✅  |   ✅    |   ✅    |         |        |
| Crear / editar norma              |  ✅  |          |         |         |        |
| Generar alertas (sweep)           |  ✅  |   ✅    |         |         |        |
| Ver reportes                      |  ✅  |   ✅    |         |   ✅    |        |

> Estas reglas se aplican **dos veces**: en FastAPI (`require_role`) y en Postgres
> (RLS, `current_app_role()`).
