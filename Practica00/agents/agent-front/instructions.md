# Instrucciones para agent-front

Orden de trabajo y reglas para implementar el frontend.

## 1. Fuente de verdad

- `specs/01-login/requirements.md` (RF-001, RF-002, RF-003, RF-008).
- `specs/01-login/api-spec.md` (contratos de la API).
- `specs/00-environment/architecture.md` (cómo se comunica con el backend).

## 2. Archivos a crear en `sistema/frontend/`

| Archivo | Contenido |
|---------|-----------|
| `login.html` | Formulario (username, password, botón "Iniciar sesión"). Mensaje de error. Redirección a `/dashboard` al autenticarse. |
| `dashboard.html` | Mensaje de bienvenida (username), botón "Cerrar sesión". Se muestra solo si hay sesión. |
| `css/style.css` | Estilos del formulario y dashboard. |
| `js/app.js` | Lógica: validar, `POST /api/login`, `GET /api/session`, `POST /api/logout`, redirecciones, mostrar errores. |

## 3. Comportamiento esperado

- `login.html`:
  - Al enviar, validar que username no esté vacío y tenga 3+ caracteres, y password no
    esté vacía y tenga 8+ caracteres (UX). En caso de error mostrar mensaje amigable.
  - Enviar `POST /api/login` con JSON `{username, password}`.
  - Si `200`: redirigir a `/dashboard`.
  - Si `400` o `401`: mostrar `error` del cuerpo (o un mensaje genérico del backend).
- `dashboard.html`:
  - Al cargar, validar sesión con `GET /api/session`.
  - Si `authenticated: false` → redirigir a `/login`.
  - Botón "Cerrar sesión" → `POST /api/logout` → redirigir a `/login`.
- `js/app.js`: usar `fetch` con `credentials: 'include'` (las cookies de sesión se
  envían automáticamente en la misma-origin).

## 4. Reglas

- NO duplicar la lógica de validación de seguridad del backend: la autenticación real la
  decide el backend. Las validaciones del frontend son de UX.
- NO crear funcionalidades fuera de alcance (captcha, registro, etc.).
- El código debe ser simple y legible (proyecto educativo).