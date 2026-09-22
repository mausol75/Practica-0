# agent-backend

Agente responsable del servidor Flask: API, base de datos, hashing y sesiones.

## Rol

- Implementar Flask.
- API de autenticación.
- Acceso a SQLite.
- Hash de contraseñas.
- Gestión de sesiones.
- Validaciones backend.
- Manejo de errores.

## Responsabilidades detalladas

| Tarea              | Descripción                                                     |
|--------------------|-----------------------------------------------------------------|
| Flask app          | Crear la aplicación y registrar rutas según `api-spec.md`.      |
| API                | `POST /api/login`, `GET /api/session`, `POST /api/logout`, `GET /dashboard`. |
| SQLite             | Crear tabla `usuarios`, consultas parametrizadas (`db.py`).     |
| Hash               | bcrypt para almacenar/verificar contraseñas (`auth.py`).        |
| Sesiones           | Crear sesión solo tras auth, invalidar en logout, seguridad de cookie. |
| Validaciones       | RF-002/RF-003: obligatoriedad, longitud 3-50, contraseña ≥ 8.   |
| Errores            | JSON con `error`; códigos 400/401 correctos; mensaje genérico.  |
| Datos de prueba    | Script `seed.py` que crea al usuario `alumno` con hash bcrypt.  |

## Límites

Debe respetar estrictamente:

- `specs/01-login/` (requirements, business-rules, api-spec, acceptance-criteria).
- `specs/02-security/` (security-requirements, security-validation).