# Plan de pruebas

Plan de pruebas que ejecutará `agent-qa`. Define los casos mínimos obligatorios, su
relación con criterios de aceptación (AC) y requisitos (RF), y un registro de
resultados reales.

> Regla: el registro de resultados SOLO se completa con ejecuciones reales (`pytest`
> o comprobaciones manuales). No se anuncia un resultado que no fue obtenido.

---

## Ejecución

```bash
# desde sistema/backend (con el entorno virtual activo)
python -m pytest -v
```

---

## Casos de prueba

### Login (`test_login_*`)

| # | Caso                      | Condición                                   | Resultado esperado        | AC / RF |
|---|---------------------------|---------------------------------------------|---------------------------|---------|
| 1 | Credenciales correctas    | `alumno` / `Practica123!`                   | `200`, sesión creada      | AC-001 (RF-004) |
| 2 | Username inexistente      | `no_existe` / `Practica123!`                | `401`, mensaje genérico   | AC-003 (RF-005) |
| 3 | Password incorrecta       | `alumno` / `ContraseñaMala1`                | `401`, mensaje genérico   | AC-002 (RF-005) |
| 4 | Username vacío            | `""` / `Practica123!`                       | `400`, sin sesión         | AC-004 (RF-002) |
| 5 | Password vacía            | `alumno` / `""`                             | `400`, sin sesión         | AC-005 (RF-003) |
| 6 | Username demasiado corto  | `ab` / `Practica123!`                       | `400`                     | AC-008 (RF-002) |
| 7 | Password demasiado corta  | `alumno` / `corta12`                        | `400`                     | AC-009 (RF-003) |

### Sesión (`test_session_*` / `test_protected_route` / `test_logout_*`)

| # | Caso                                  | Condición                                             | Resultado esperado | AC / RF |
|---|---------------------------------------|-------------------------------------------------------|--------------------|---------|
| 8 | Login crea sesión                     | login correcto → `GET /api/session`                   | `authenticated: true` | AC-001 (RF-006) |
| 9 | Autenticado accede a dashboard        | login correcto → `GET /dashboard`                     | `200`              | AC-001, AC-006 (RF-006, RF-007) |
| 10 | No autenticado NO accede a dashboard  | `GET /dashboard` sin cookie                           | rechazado (`401`/redirección) | AC-006 (RF-007) |
| 11 | Logout invalida sesión                | login → logout → `GET /api/session` y `GET /dashboard` | sesión inválida, dashboard rechazado | AC-007 (RF-008) |

### Seguridad (`test_security_*`)

| # | Caso                                        | Condición                                          | Resultado esperado | AC / RF / SEC |
|---|---------------------------------------------|----------------------------------------------------|--------------------|---------------|
| 12 | Contraseña no almacenada en texto plano     | consultar `password_hash` del usuario `alumno`     | hash bcrypt, `hash != Practica123!` | AC-010 (SEC-001) |
| 13 | SQL Injection básico no concede acceso      | payloads como `' OR 1=1--` en username             | nunca `200`, sin afectar BD | AC-011 (SEC-002) |
| 14 | Mensaje uniforme (no revela existencia)     | comparar respuesta de #2 y #3                      | respuestas idénticas | AC-012 (SEC-004, SEC-005) |

> Los casos 13 y 14 repiten al mínimo necesario de ST-002/ST-005 de
> `specs/02-security/security-validation.md`.

---

## Cobertura de RF

| Requisito | Caso(s) de prueba |
|-----------|-------------------|
| RF-001 | Comprobación manual: `login.html` existe y muestra los 3 elementos (Verificación UI) |
| RF-002 | casos 4 y 6 (+ validación de 50 caracteres en casos de borde) |
| RF-003 | casos 5 y 7 (+ comprobación de hashing en caso 12) |
| RF-004 | caso 1 |
| RF-005 | casos 2, 3 y 14 |
| RF-006 | casos 1 y 8 |
| RF-007 | casos 9 y 10 |
| RF-008 | caso 11 |

---

## Registro de resultados (se completa tras la ejecución)

| # | Resultado pytest / manual | Fecha | Responsable |
|---|---------------------------|-------|-------------|
| 1 | _(pendiente)_             | —     | agent-qa    |
| 2 | _(pendiente)_             | —     | agent-qa    |
| 3 | _(pendiente)_             | —     | agent-qa    |
| 4 | _(pendiente)_             | —     | agent-qa    |
| 5 | _(pendiente)_             | —     | agent-qa    |
| 6 | _(pendiente)_             | —     | agent-qa    |
| 7 | _(pendiente)_             | —     | agent-qa    |
| 8 | _(pendiente)_             | —     | agent-qa    |
| 9 | _(pendiente)_             | —     | agent-qa    |
| 10| _(pendiente)_             | —     | agent-qa    |
| 11| _(pendiente)_             | —     | agent-qa    |
| 12| _(pendiente)_             | —     | agent-qa    |
| 13| _(pendiente)_             | —     | agent-qa    |
| 14| _(pendiente)_             | —     | agent-qa    |

---

## Comprobaciones manuales complementarias (QA, no automatizadas)

- (M1) Verificación UI: con Edge, abrir `/login` y confirmar que existen los campos
  Username, Password y el botón "Iniciar sesión" (RF-001).
- (M2) Verificación UI: tras login correcto, redirige y muestra `/dashboard` con la
  opción de cerrar sesión.
- (M3) curl: ejecutar los mismos endpoints con `curl.exe` para confirmar códigos de
  estado y cookies en un servidor real.
- (M4) Inspección: verificar atributos `HttpOnly; SameSite=Lax` en la cookie
  (V-SEC-006).