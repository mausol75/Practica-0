# Requisitos de seguridad

Requisitos mínimos de seguridad para la versión preliminar. El objetivo es que la
implementación siga buenas prácticas básicas, no convertir el proyecto en un laboratorio
de explotación.

---

## SEC-001 — Contraseñas

### SEC-001.1 Algoritmo de hashing apropiado

- Se utiliza **bcrypt** para almacenar contraseñas (incluye *salt* automático).
- NO se utilizan: MD5, SHA1 ni SHA256 directo como contraseña almacenada.

### SEC-001.2 Nunca texto plano

- La base de datos SOLO contiene el hash de la contraseña, nunca el valor original.

### SEC-001.3 Verificación con el algoritmo

- La verificación en `POST /api/login` se realiza comparando el hash (función
  `bcrypt.checkpw`), nunca comparando cadenas en texto plano.

---

## SEC-002 — SQL Injection

- Todas las consultas se realizan con **consultas parametrizadas** (placeholder `?` del
  módulo `sqlite3`) o el ORM correspondiente.
- NUNCA se concatena el username recibido del usuario directamente en una cadena SQL.

---

## SEC-003 — Session security

- La sesión se crea ÚNICAMENTE después de una autenticación exitosa (SEC-003.1).
- La sesión se invalida al cerrar sesión (SEC-003.2).
- Configuraciones razonables de seguridad de la cookie:
  - `HttpOnly = True`
  - `SameSite = Lax`
  - `Samesite` y `Secure` acordes al entorno local (en localhost `Secure` no es
    obligatorio, pero se configurará si es posible sin romper el entorno).
- La clave secreta (`SESSION_SECRET`) se toma de una variable de entorno, nunca se
  integra una clave fija comprometida en el código.

---

## SEC-004 — Mensajes de error

- Las fallas de autenticación usan SIEMPRE el mensaje genérico:

  > Username o contraseña incorrectos.

- NO se revela información como *"El usuario existe pero la contraseña es incorrecta."*
- Igual respuesta para "username inexistente" y "password incorrecta".

---

## SEC-005 — Datos de prueba

- El usuario de prueba es local y de desarrollo (`alumno` / `Practica123!`).
- La contraseña almacenada en SQLite debe estar hasheada (nunca `Practica123!` en texto
  plano dentro de la base de datos).
- No se utilizan credenciales reales.

---

## Alcance (límites)

- Esta versión es una práctica educativa local (HTTP en `127.0.0.1`).
- No se implementan captcha, cifrado TLS propio, ni políticas de expiración complejas;
  quedan fuera de alcance y NO se exigen.
- El cumplimiento se comprueba mediante pruebas básicas automatizadas
  (ver `security-validation.md` y `specs/03-testing/`).