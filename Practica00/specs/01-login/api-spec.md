# Especificación de la API

Definición de la API REST que el backend debe implementar. Se especifica ANTES de
implementar: el backend (agente-backend) se guía por este documento y el frontend
(agente-front) por este mismo documento para consumirla.

Convenciones:

- Base URL: `http://127.0.0.1:5000`
- Formato de datos: JSON (`Content-Type: application/json`)
- Códigos de estado usados:
  - `200 OK` — éxito
  - `400 Bad Request` — validación de entrada (diferenciar de 401)
  - `401 Unauthorized` — credenciales incorrectas o sesión no válida
  - `404 Not Found` — ruta inexistente
  - `405 Method Not Allowed` — método HTTP no permitido

---

## POST /api/login

Autentica con username y contraseña. Si es correcto, crea la sesión.

### Request

```json
{
  "username": "usuario1",
  "password": "Password123"
}
```

### Respuestas

#### Login exitoso — `200 OK`

```json
{
  "message": "Login exitoso."
}
```

Se crea una cookie de sesión (HttpOnly, SameSite=Lax).

#### Credenciales incorrectas — `401 Unauthorized`

```json
{
  "error": "Username o contraseña incorrectos."
}
```

#### Campos inválidos (vacío / muy corto) — `400 Bad Request`

```json
{
  "error": "...descripción de la validación..."
}
```

### Errores posibles

| Situación              | Status | Cuerpo                                     |
|------------------------|--------|--------------------------------------------|
| JSON mal formado       | 400    | `{"error": "..."}`                         |
| username vacío         | 400    | `{"error": "..."}`                         |
| password vacía         | 400    | `{"error": "..."}`                         |
| username < 3 o > 50    | 400    | `{"error": "..."}`                         |
| password < 8           | 400    | `{"error": "..."}`                         |
| username inexistente   | 401    | `{"error": "Username o contraseña incorrectos."}` |
| password incorrecta    | 401    | `{"error": "Username o contraseña incorrectos."}` |

Regla: username inexistente y password incorrecta producen la MISMA respuesta.

---

## GET /api/session

Comprueba si existe una sesión autenticada.

### Request

Sin cuerpo. Usa la cookie de sesión.

### Respuestas

#### Sesión válida — `200 OK`

```json
{
  "authenticated": true,
  "username": "usuario1"
}
```

#### Sesión inválida — `200 OK` (semánticamente no autenticado)

```json
{
  "authenticated": false
}
```

> Decisión: `GET /api/session` siempre responde `200`; el estado de autenticación se
> informa en el cuerpo (`authenticated: true|false`). Facilita que el frontend consulte
> el estado sin tratar errores HTTP para un caso esperado.

---

## POST /api/logout

Cierra la sesión actual.

### Request

Sin cuerpo. Usa la cookie de sesión.

### Respuestas

#### Logout exitoso — `200 OK`

```json
{
  "message": "Sesión cerrada."
}
```

La cookie de sesión se invalida (se elimina en el cliente y el servidor deja de
reconocer la sesión).

---

## GET /dashboard

Página protegida. Solo accesible con sesión válida.

### Respuestas

#### Con sesión válida — `200 OK`

Devuelve HTML de `dashboard.html`.

#### Sin sesión válida — `401 Unauthorized`

```json
{
  "error": "Sesión no válida."
}
```

O redirige a `/login`. Decisión de implementación: respuesta `401` con JSON si la
solicitud espera JSON, de lo contrario redirección a `/login`.

---

## Reglas de autenticación

1. Una sesión SOLO se crea después de una autenticación exitosa (RF-006).
2. La sesión se invalida al cerrar sesión (RF-008, BR-010).
3. `/dashboard` exige sesión válida (RF-007, BR-009).
4. El mensaje de error genérico es *"Username o contraseña incorrectos."* y NO revela
   si el username existe (RF-005, BR-008).
5. Las cookies de sesión se crean con atributos razonables de seguridad
   (HttpOnly, SameSite=Lax) según `specs/02-security/security-requirements.md`.