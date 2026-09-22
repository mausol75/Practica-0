# Instrucciones para agent-backend

Orden de trabajo y reglas para implementar el backend.

## 1. Fuente de verdad (obligatoria)

- `specs/01-login/requirements.md`
- `specs/01-login/business-rules.md`
- `specs/01-login/api-spec.md`
- `specs/01-login/acceptance-criteria.md`
- `specs/02-security/security-requirements.md`
- `specs/02-security/security-validation.md`

Si durante el desarrollo descubres una contradicción o la necesidad de cambiar un
requisito: DETENTE y documenta el problema (agrégalo al reporte). NO cambies código
antes de que el spec sea actualizado.

## 2. Archivos a crear en `sistema/backend/`

| Archivo | Contenido |
|---------|-----------|
| `app.py` | App Flask: carga config desde entorno, registra rutas, sirve frontend estático. |
| `db.py`  | Conexión a SQLite (`instance/login.db`), creación de tabla `usuarios` (`id`, `username` UNIQUE, `password_hash`), funciones de búsqueda de usuario con consultas parametrizadas. |
| `auth.py` | `hash_password`, `verify_password` (bcrypt) y helpers de sesión. |
| `seed.py` | Crea el usuario de prueba `alumno` con `Practica123!` hasheada (bruto local). |
| `requirements.txt` | `flask`, `bcrypt`, `pytest` (dependencias de desarrollo). |
| `.env.example` | Plantilla con `SESSION_SECRET=...` |
| `run.ps1`  | Lanza el servidor cargando `.env` en Windows. |
| `tests/`   | Pruebas pytest (definidas en `specs/03-testing/test-plan.md`). |

## 3. Contratos obligatorios

### POST /api/login
- Request JSON: `{"username": "...", "password": "..."}`.
- Errores de validación (400) según RF-002/RF-003 (obligatorio, 3-50, ≥8).
- Credenciales inválidas (401) → `{"error": "Username o contraseña incorrectos."}`.
- Válido (200) → crear sesión, `{"message": "Login exitoso."}`.
- Userna existente o no → misma respuesta 401 (BR-008, SEC-004).

### GET /api/session
- `200` siempre, `{"authenticated": bool, "username": "..."} (solo si autenticado)`.

### POST /api/logout
- Invalida sesión, `{"message": "Sesión cerrada."}` (200).

### GET /dashboard
- Autenticado → HTML del dashboard.
- No autenticado → `401` JSON si se pidió JSON, o redirección a `/login`.

## 4. Reglas de seguridad (no negociables)

- bcrypt para hashing (SEC-001). NUNCA MD5/SHA1/SHA256 directo.
- Consultas SIEMPRE parametrizadas (SEC-002). NUNCA concatenar username en SQL.
- Sesión solo tras auth exitosa (SEC-003.1); invalidar en logout (SEC-003.2).
- Cookie: `HttpOnly`, `SameSite=Lax`.
- `SESSION_SECRET` desde variable de entorno (`os.environ`), nunca fijo en código.

## 5. Estilo

- Código simple y legible; sin abstracciones innecesarias.
- Sin comentarios innecesarios; nombres claros.
- No agregues funcionalidades fuera de alcance.