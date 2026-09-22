# Entorno de desarrollo

Documento que describe el entorno real detectado al momento de definir el proyecto.

> Regla: este documento NO inventa versiones. Cada versión fue obtenida ejecutando el
> comando correspondiente en la máquina de desarrollo.

## Sistema operativo

| Atributo      | Valor                                          |
|---------------|------------------------------------------------|
| Sistema       | Windows 11                                      |
| Build         | 10.0.26200 (Windows-11-10.0.26200-SP0)          |

---

## Versión de Python

| Comando         | Salida                        |
|-----------------|-------------------------------|
| `python --version` | `Python 3.12.4`            |

Intérprete usado: `C:\Users\Anali\AppData\Local\Programs\Python\Python312\python.exe`

| Atributo | Valor        |
|----------|--------------|
| pip      | `pip 25.1.1` |
| venv     | Disponible (`python -m venv`) |

---

## Versión de Node.js

| Comando            | Salida         |
|--------------------|----------------|
| `node --version`   | `v24.18.0`     |
| `npm --version`    | `11.16.0`      |

> Nota: en esta versión de práctica el frontend es HTML/CSS/JavaScript estático sin
> build (no usa Node/npm). Se documentan porque están disponibles, pero el proyecto no
> los requiere para ejecutarse.

---

## Base de datos

| Atributo              | Valor                                              |
|-----------------------|----------------------------------------------------|
| Motor                 | SQLite (vía módulo estándar `sqlite3` de Python)    |
| Versión del motor     | `3.45.3` (`sqlite3.sqlite_version` desde Python)   |
| CLI `sqlite3`         | **No disponible** en la máquina                     |
| Archivo de datos      | `sistema/backend/instance/login.db` (se crea al iniciar) |

---

## Navegador utilizado para pruebas

| Atributo  | Valor                                     |
|-----------|-------------------------------------------|
| Navegador | Microsoft Edge                             |
| Ruta      | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` |

> Google Chrome no está instalado en esta máquina, por lo que las pruebas manuales del
> frontend se realizan con Microsoft Edge.

---

## Herramientas disponibles

| Herramienta | Versión observada      | Comando verificado          |
|-------------|------------------------|-----------------------------|
| Python      | 3.12.4                 | `python --version`          |
| pip         | 25.1.1                 | `pip --version`             |
| venv        | disponible             | `python -m venv --help`     |
| Node.js     | v24.18.0               | `node --version`            |
| npm         | 11.16.0                | `npm --version`             |
| Git         | 2.47.0.windows.2       | `git --version`             |
| curl        | 8.21.0 (curl.exe real de Windows) | `curl --version`  |
| Flask       | 3.1.3                  | `importlib.metadata.version("flask")` |
| Werkzeug    | 3.1.8                  | `importlib.metadata.version("werkzeug")` |
| pytest      | 9.0.2                  | `python -m pytest --version` |
| Microsoft Edge | —                  | ruta de archivo verificada  |

---

## Cómo ejecutar el proyecto

Los pasos completos se describen en `../../README.md`. Resumen:

1. Crear y activar un entorno virtual:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Instalar dependencias del backend:
   ```
   pip install -r sistema/backend/requirements.txt
   ```
3. Configurar la variable de entorno `SESSION_SECRET`.
4. Ejecutar el lanzador (o el equivalente manual):
   ```
   powershell -ExecutionPolicy Bypass -File sistema/backend/run.ps1
   ```
5. Abrir `http://127.0.0.1:5000` en Edge para probar el login.

---

## Variables de entorno necesarias

| Variable         | ¿Obligatoria? | Descripción                                                  |
|------------------|---------------|--------------------------------------------------------------|
| `SESSION_SECRET` | Sí            | Clave secreta usada por Flask para firmar las cookies de sesión.  |

La variable se define en `sistema/backend/.env` (archivo que NO se sube a control de
versiones). Se incluye un `.env.example` como plantilla.

---

## Hallazgos y decisiones

- La CLI `sqlite3.exe` no está instalada. Las comprobaciones de la base de datos se
  realizan con el módulo `sqlite3` de Python (tests) y con SQL desde `curl`/tests.
- Las pruebas indicadas por el instructor con `curl` se harán con el `curl.exe` real
  de Windows (`C:\Windows\System32\curl.exe`), no con el alias de PowerShell.
- Python es la única dependencia imprescindible para que el proyecto funcione.