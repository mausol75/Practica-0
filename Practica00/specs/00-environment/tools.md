# Definición de herramientas

Cada herramienta utilizada en este proyecto, su propósito, dónde se usa y por qué se eligió.

Formato por herramienta:

- **Herramienta:** nombre
- **Propósito:** para qué sirve
- **Dónde se utiliza:** componente/carpeta/proceso
- **Por qué se eligió:** justificación

> Regla: no se agregan herramientas que no se necesiten.

---

## Desarrollo

### Python

- **Herramienta:** Python 3.12.4
- **Propósito:** lenguaje principal del backend; también ejecuta las pruebas (pytest).
- **Dónde se utiliza:** `sistema/backend/` y `sistema/backend/tests/`.
- **Por qué se eligió:** es la base de Flask y de las herramientas de testing; ya está
  instalado en la máquina (no requiere instalación adicional).

### Flask

- **Herramienta:** Flask 3.1.3 (con Werkzeug 3.1.8)
- **Propósito:** framework web del backend; define las rutas de la API y sirve el
  frontend estático.
- **Dónde se utiliza:** `sistema/backend/app.py` (rutas `/api/login`, `/api/session`,
  `/api/logout`, `/dashboard`).
- **Por qué se eligió:** es simple, adecuado para un proyecto educativo y permite
  exponer una API REST mínima y servir HTML estático sin herramientas adicionales.

### HTML

- **Herramienta:** HTML5
- **Propósito:** estructura de las páginas de login y dashboard.
- **Dónde se utiliza:** `sistema/frontend/login.html`, `sistema/frontend/dashboard.html`.
- **Por qué se eligió:** es el lenguaje estándar para la interfaz; no requiere build.

### CSS

- **Herramienta:** CSS3 (hoja `style.css`)
- **Propósito:** presentación visual del formulario y el dashboard.
- **Dónde se utiliza:** `sistema/frontend/css/style.css`.
- **Por qué se eligió:** permite una interfaz limpia y funcional sin dependencias de
  frameworks externos; mantiene el proyecto simple.

### JavaScript

- **Herramienta:** JavaScript (ES6+, ejecutado en el navegador)
- **Propósito:** validaciones visuales, comunicación con la API de login/logout/session
  y manejo de errores en la interfaz.
- **Dónde se utiliza:** `sistema/frontend/js/app.js`.
- **Por qué se eligió:** es el lenguaje natural del navegador y evita cargar librerías
  adicionales para un alcance pequeño.

### SQLite

- **Herramienta:** SQLite (módulo `sqlite3` de Python, motor v3.45.3)
- **Propósito:** almacenar los usuarios del sistema de login.
- **Dónde se utiliza:** `sistema/backend/db.py` (creación de tablas y consultas);
  archivo `instance/login.db`.
- **Por qué se eligió:** base de datos embebida, sin servidor, ideal para demostraciones
  pequeñas; no requiere instalación.

---

## Control de versiones

### Git

- **Herramienta:** Git 2.47.0.windows.2
- **Propósito:** control de versiones y seguimiento de cambios.
- **Dónde se utiliza:** repositorio raíz del proyecto.
- **Por qué se eligió:** estándar de control de versiones; la carpeta ya es un
  repositorio Git. Además sostiene la trazabilidad de los specs con el código.

---

## Testing

### pytest

- **Herramienta:** pytest 9.0.2
- **Propósito:** escribir y ejecutar las pruebas automatizadas del backend.
- **Dónde se utiliza:** `sistema/backend/tests/`.
- **Por qué se eligió:** es simple, la sintaxis de funciones `test_*` es directa, genera
  reportes claros y permite afirmaciones nativas de Python.

---

## API / debugging

### curl

- **Herramienta:** curl 8.21.0 (curl.exe real de Windows)
- **Propósito:** probar manualmente los endpoints de la API con HTTP real.
- **Dónde se utiliza:** validación manual de `POST /api/login`, `GET /api/session`,
  `POST /api/logout`.
- **Por qué se eligió:** permite verificar respuestas, códigos de estado y cookies de
  sesión sin depender del navegador.

---

## Calidad

### ruff (linting Python)

- **Herramienta:** ruff (linter de Python)
- **Propósito:** detectar problemas de estilo y errores en el código Python del backend.
- **Dónde se utiliza:** `sistema/backend/` (módulos y tests).
- **Por qué se eligió:** ligero y rápido; aplica reglas estándar de calidad sin
  configuración compleja.

### ESLint (linting JavaScript)

- **Herramienta:** ESLint (linter de JavaScript)
- **Propósito:** detectar problemas de estilo y errores en `app.js` del frontend.
- **Dónde se utiliza:** `sistema/frontend/js/app.js`.
- **Por qué se eligió:** estándar para JavaScript; se usa con configuración mínima.

> Las herramientas de calidad se usan de forma de soporte: la aprobación final la
> determinan las pruebas (pytest) y el cumplimiento de los specs.

---

## Seguridad

### bcrypt

- **Herramienta:** bcrypt (librería de Python)
- **Propósito:** hashing de contraseñas con salt incorporado. No se guarda la
  contraseña en texto plano.
- **Dónde se utiliza:** `sistema/backend/auth.py` (hashear al registrar/sembrar y
  verificar en `POST /api/login`).
- **Por qué se eligió:** es un algoritmo de hashing apropiado para contraseñas (el spec
  de seguridad lo menciona explícitamente) y su uso en Python es directo.

### Pruebas de seguridad básicas

- **Herramienta:** tests de `sistema/backend/tests/` (casos de inyección SQL y de
  mensajes de error genéricos)
- **Propósito:** comprobar que la implementación resiste intentos básicos de SQL
  Injection, que la contraseña no se guarda en texto plano y que el error no revela si
  el usuario existe.
- **Dónde se utiliza:** `specs/03-testing/test-plan.md` (sección de seguridad).
- **Por qué se eligió:** verifica la seguridad sin convertir el proyecto en un
  laboratorio de explotación.

---

## IA / agentes

### OpenCode

- **Herramienta:** OpenCode (asistente de desarrollo)
- **Propósito:** ejecutar el proceso SDD: leer los specs, dirigir a los agentes
  (devops, front, backend, qa) para implementar lo definido, ejecutar pruebas y
  mantener la trazabilidad.
- **Dónde se utiliza:** todo el proyecto, actuando como coordinador de los agentes.
- **Por qué se eligió:** permite que el desarrollo sea guiado por los specs (fuente de
  verdad) en lugar de desarrollarse por improvisación (Vibe Coding).

---

## Tabla resumen

| Herramienta | Categoría       | Dónde se usa                                 |
|-------------|-----------------|----------------------------------------------|
| Python 3.12.4 | Desarrollo    | Backend y tests                              |
| Flask 3.1.3   | Desarrollo    | API + servir frontend                        |
| HTML5         | Desarrollo    | Páginas del frontend                         |
| CSS3          | Desarrollo    | Estilos del frontend                         |
| JavaScript    | Desarrollo    | Lógica del frontend                          |
| SQLite        | Desarrollo    | Almacenamiento de usuarios                   |
| Git          | Control de versiones | Repositorio del proyecto                |
| pytest       | Testing        | Pruebas automatizadas del backend            |
| curl         | API/debugging  | Pruebas manuales de endpoints                |
| ruff         | Calidad        | Lint de Python (backend)                     |
| ESLint       | Calidad        | Lint de JavaScript (frontend)                |
| bcrypt       | Seguridad      | Hashing de contraseñas                       |
| OpenCode     | IA / agentes   | Coordinación SDD de todo el proyecto         |