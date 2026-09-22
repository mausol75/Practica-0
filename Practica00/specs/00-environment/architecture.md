# Arquitectura

## Vista general

```
┌─────────────────────┐
│      FRONTEND       │
│ HTML/CSS/JavaScript │
└──────────┬──────────┘
           │ HTTP (JSON)
           ↓
┌─────────────────────┐
│       BACKEND       │
│       Flask         │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│       SQLite        │
└─────────────────────┘
```

No se utilizan microservicios: es una aplicación monolítica sencilla.

## Componentes

### Frontend (`sistema/frontend/`)

- **Qué es:** la interfaz de usuario. Son páginas estáticas (HTML) con estilos (CSS) y
  lógica en el navegador (JavaScript).
- **Componentes:**
  - `login.html`: formulario de inicio de sesión (username, password, botón "Iniciar sesión").
  - `dashboard.html`: página protegida que solo se muestra con sesión válida.
  - `css/style.css`: estilos.
  - `js/app.js`: validaciones visuales, llamadas a la API, manejo de errores y logout.
- **Responsabilidad:** mostrar el formulario, validar visualmente los campos, enviar las
  credenciales al backend, mostrar errores y reflejar el estado de autenticación.
- **Lo que NO hace:** el frontend NO valida credenciales ni decide si el acceso es válido
  (eso es responsabilidad del backend). La validación del navegador es solo de
  experiencia de usuario.

### Backend (`sistema/backend/`)

- **Qué es:** servidor Flask que expone la API y sirve el frontend estático.
- **Componentes:**
  - `app.py`: aplicación Flask, rutas de la API y de páginas.
  - `db.py`: acceso a SQLite (creación de tablas, consultas parametrizadas).
  - `auth.py`: hashing y verificación de contraseñas (bcrypt) y helpers de sesión.
  - `seed.py`: script que crea el usuario de prueba con contraseña hasheada.
  - `tests/`: pruebas pytest.
- **Responsabilidad:** autenticar usuarios, crear/invalidar sesiones, validar entradas,
  proteger `/dashboard` y manejar errores. Es la única fuente de decisión sobre la
  autenticación.

### Base de datos (SQLite)

- **Qué es:** archivo SQLite local (`instance/login.db`) que almacena los usuarios.
- **Dónde se almacenan los usuarios:** tabla `usuarios` con, al menos, las columnas
  `id`, `username` y `password_hash`.
- **Responsabilidad:** persistir los datos de usuario. La contraseña nunca se guarda en
  texto plano, solo su hash.

## Comunicación

- **Frontend → Backend:** se comunican por HTTP usando JSON en el cuerpo de las
  peticiones (`POST /api/login`, `GET /api/session`, `POST /api/logout`).
- **Backend → Frontend:** responde con JSON y códigos de estado HTTP
  (`200 OK`, `400 Bad Request`, `401 Unauthorized`).
- **Backend → SQLite:** consultas SQL parametrizadas (nunca se concatena entrada del
  usuario directamente en SQL).

## Flujo de una petición de login

1. El navegador envía `POST /api/login` con `{"username": ..., "password": ...}`.
2. Flask valida los campos (reglas RF-002/RF-003/BR-001 a BR-004).
3. Se busca al usuario en SQLite con una consulta parametrizada.
4. Se compara la contraseña usando bcrypt.
5. Si es correcta: se crea una sesión y responde `200 OK`.
6. Si no: responde `401` con el mensaje genérico *"Username o contraseña incorrectos."*

## Responsabilidades por componente (resumen)

| Componente | Responsabilidad principal |
|------------|----------------------------|
| Frontend   | Interfaz, validaciones visuales, comunicación con la API, mostrar errores y estado de sesión |
| Backend    | Autenticación, sesiones, validaciones, protección de `/dashboard`, manejo de errores |
| SQLite     | Almacenar usuarios (username + hash de contraseña) persistentemente |

## Decisiones

- Frontend servido como archivos estáticos por el propio Flask (evita CORS y simplifica
  la ejecución: un solo servidor).
- SQLite embebido (sin servidor) para mantener el proyecto simple y portable.
- No hay microservicios: la separación frontend/backend se mantiene a nivel de capas
  dentro de la misma aplicación.