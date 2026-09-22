# Validación de seguridad

Cómo se comprueba que la implementación cumple los requisitos de seguridad
(`security-requirements.md`). Cada validación es una actividad de `agent-qa` y se
ejecuta de forma real.

> Regla: no se considera cumplida una validación que no fue ejecutada.

---

## V-SEC-001 — Contraseñas con bcrypt

- **Qué comprobar:** el hash almacenado usa bcrypt y NO coincide con la contraseña
  original.
- **Cómo:**
  1. Insertar/crear el usuario de prueba.
  2. Consultar `password_hash` en `instance/login.db`.
  3. Verificar que el valor comienza con el prefijo bcrypt (`$2b$`, `$2a$` o `$2y$`).
  4. Verificar que `password_hash != "Practica123!"` y que `bcrypt.checkpw` sobre el
     hash sea `True` (es decir, el hash corresponde a esa contraseña, pero no es la
     contraseña en sí).
- **Evidencia:** prueba automatizada `test_password_not_stored_in_plaintext` y consulta
  manual a la base de datos.

## V-SEC-002 — SQL Injection

- **Qué comprobar:** intentos básicos de inyección no conceden acceso.
- **Cómo:** enviar por `POST /api/login` payloads como:
  - username: `' OR 1=1--`, password: `cualquiera123`
  - username: `alumno' --`, password: `cualquiéra123`
  - username: `'; DROP TABLE usuarios;--`, password: `cualquiera123`
- **Resultado esperado:** NI un `200` ni una excepción del servidor; se espera `401`/
  `400`. El estado de la BD no debe alterarse (la tabla `usuarios` sigue existiendo).
- **Evidencia:** prueba parametrizada `test_sql_injection` (pytest) + ejecución con
  `curl` para corroborar en servidor real.

## V-SEC-003 — Sesión solo tras autenticación

- **Qué comprobar:** antes de autenticarse no existe sesión; después de login correcto sí.
- **Cómo:**
  1. `GET /api/session` sin cookies → `authenticated: false`.
  2. `POST /api/login` correcto → `200` y cookie de sesión.
  3. `GET /api/session` con la cookie → `authenticated: true`.
- **Evidencia:** pruebas `test_login_creates_session`, `test_protected_route`.

## V-SEC-004 — Sesión invalidada al logout

- **Qué comprobar:** tras `POST /api/logout`, la sesión anterior ya no vale.
- **Cómo:**
  1. Login correcto.
  2. `POST /api/logout` → `200`.
  3. Reintentar `GET /dashboard` con la cookie anterior → rechazado (`401`/redirección).
- **Evidencia:** prueba `test_logout_invalidates_session`.

## V-SEC-005 — Mensaje genérico (no revela existencia)

- **Qué comprobar:** username inexistente y password incorrecta devuelven la misma
  respuesta.
- **Cómo:** comparar cuerpo y código de estado de:
  - login con username inexistente (`usuario_no_existe`) + password cualquiera.
  - login con username válido (`alumno`) + password incorrecta.
- **Resultado esperado:** respuestas idénticas:
  `401` + `{"error": "Username o contraseña incorrectos."}`
- **Evidencia:** prueba `test_error_message_does_not_reveal_username`.

## V-SEC-006 — Cookie de sesión con atributos razonables

- **Qué comprobar:** la cookie de sesión tiene `HttpOnly` y `SameSite=Lax`.
- **Cómo:** inspeccionar la cabecera `Set-Cookie` de la respuesta de login.
- **Resultado esperado:** `HttpOnly; SameSite=Lax` presentes.
- **Evidencia:** prueba de sesión que inspecciona `response.headers['Set-Cookie']`.

---

## Resumen de evidencias

| Comprobación     | Prueba automatizada                        | Comprobación manual |
|------------------|--------------------------------------------|---------------------|
| V-SEC-001        | `test_password_not_stored_in_plaintext`    | consulta SQLite     |
| V-SEC-002        | `test_sql_injection`                       | curl a `/api/login` |
| V-SEC-003        | `test_login_creates_session`               | curl con cookies    |
| V-SEC-004        | `test_logout_invalidates_session`          | curl con cookies    |
| V-SEC-005        | `test_error_message_does_not_reveal_username` | curl comparando 2 respuestas |
| V-SEC-006        | test de cookie (en pruebas de sesión)      | inspección en navegador |

Resultados reales quedan registrados en `specs/03-testing/test-plan.md`.