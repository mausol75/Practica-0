# Criterios de aceptación

Los criterios de aceptación (AC) describen, en formato verificable, cómo se comprueba
que un requisito se cumple. Cada criterio se valida mediante un test automatizado (QA)
o una comprobación manual descrita en `../03-testing/test-plan.md`.

---

## AC-001 — Login exitoso

- **Dado** un usuario registrado con username y contraseña correctos,
- **cuando** introduce ambas credenciales,
- **entonces** el sistema debe autenticarlo y permitirle acceder al dashboard.
- Verificación: `POST /api/login` con credenciales válidas responde `200` y las
  peticiones posteriores a `/api/session` indican sesión autenticada.

## AC-002 — Password incorrecto

- **Dado** un username válido,
- **cuando** se introduce una contraseña incorrecta,
- **entonces** el sistema debe rechazar el acceso.
- Verificación: `POST /api/login` responde `401` con el mensaje genérico y NO crea
  sesión.

## AC-003 — Usuario inexistente

- **Dado** un username que no existe,
- **cuando** se intenta iniciar sesión,
- **entonces** el sistema debe rechazar el acceso utilizando el mismo mensaje genérico.
- Verificación: `POST /api/login` responde `401` con `"Username o contraseña incorrectos."`
  (idéntico al caso AC-002).

## AC-004 — Username vacío

- **Dado** que el username está vacío,
- **cuando** se intenta iniciar sesión,
- **entonces** el sistema debe rechazar la petición.
- Verificación: respuesta `400` y NO se crea sesión.

## AC-005 — Password vacía

- **Dado** que la contraseña está vacía,
- **cuando** se intenta iniciar sesión,
- **entonces** el sistema debe rechazar la petición.
- Verificación: respuesta `400` y NO se crea sesión.

## AC-006 — Acceso protegido

- **Dado** que no existe una sesión válida,
- **cuando** se intenta acceder a `/dashboard`,
- **entonces** el sistema debe impedir el acceso.
- Verificación: `GET /dashboard` sin sesión responde `401` (o redirige al login);
  nunca devuelve el contenido del dashboard.

## AC-007 — Logout

- **Dado** un usuario autenticado,
- **cuando** selecciona cerrar sesión,
- **entonces** la sesión debe invalidarse.
- Verificación: tras `POST /api/logout`, `GET /api/session` indica sesión inválida y
  `GET /dashboard` vuelve a ser rechazado.

## AC-008 — Username demasiado corto

- **Dado** un username con menos de 3 caracteres,
- **cuando** se intenta iniciar sesión,
- **entonces** el sistema debe rechazar la petición.
- Verificación: respuesta `400`.

## AC-009 — Password demasiado corta

- **Dado** una contraseña con menos de 8 caracteres,
- **cuando** se intenta iniciar sesión,
- **entonces** el sistema debe rechazar la petición.
- Verificación: respuesta `400`.

## AC-010 — Contraseña no almacenada en texto plano

- **Dado** un usuario registrado,
- **cuando** se inspecciona la base de datos,
- **entonces** el valor almacenado NO coincide con la contraseña original (es su hash).
- Verificación: consulta a SQLite y comparación directa (el hash nunca es igual al texto
  original), además de comprobar que comienza con el prefijo del algoritmo bcrypt.

## AC-011 — Resistencia básica a SQL Injection

- **Dado** una credencial con intento de inyección (p. ej. `' OR 1=1--`),
- **cuando** se intenta iniciar sesión,
- **entonces** el sistema no debe conceder acceso.
- Verificación: `POST /api/login` con payloads de inyección responde `401`/`400`, nunca
  `200`.

## AC-012 — Mensaje de error sin revelar existencia del usuario

- **Dado** dos peticiones: una con username inexistente y otra con password incorrecta,
- **cuando** se comparan las respuestas,
- **entonces** el mensaje y el código de estado deben ser idénticos.
- Verificación: comparación directa de ambas respuestas.

---

## Trazabilidad AC → RF

| Criterio | Requisito(s) que valida |
|----------|--------------------------|
| AC-001   | RF-004, RF-006           |
| AC-002   | RF-005                   |
| AC-003   | RF-005                   |
| AC-004   | RF-002                   |
| AC-005   | RF-003                   |
| AC-006   | RF-007                   |
| AC-007   | RF-008                   |
| AC-008   | RF-002                   |
| AC-009   | RF-003                   |
| AC-010   | RF-003, BR-006, BR-007   |
| AC-011   | Seguridad (SQL Injection)|
| AC-012   | RF-005, BR-008           |