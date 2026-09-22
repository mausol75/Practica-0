# proyecto-login

Aplicación de login desarrollada como práctica con **Spec-Driven Development (SDD)**:
la especificación (`specs/`) es la fuente de verdad y guía la implementación, las
pruebas y la documentación.

> Estado del documento: refleja la especificación y la estructura objetivo. Los
> resultados de las pruebas se registran tras ejecutarlas (Fase de QA).

---

## 1. Objetivo

Demostrar el flujo de desarrollo guiado por especificaciones:

```
Definición del entorno → Definición de herramientas → Especificación →
Planificación → Implementación → QA/Pruebas → Validación contra la especificación
```

La aplicación en sí es mínima: un login con username y contraseña, una página
protegida (`/dashboard`) y cierre de sesión.

## 2. Arquitectura

```
┌─────────────────────┐
│      FRONTEND       │
│ HTML/CSS/JavaScript │
└──────────┬──────────┘
           │ HTTP/JSON
           ↓
┌─────────────────────┐
│       BACKEND       │
│       Flask         │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│       SQLite        │
└─────────────────────┘
```

Detalle en `specs/00-environment/architecture.md`.

## 3. Tecnologías

| Capa        | Tecnología                 |
|-------------|----------------------------|
| Frontend    | HTML5, CSS3, JavaScript    |
| Backend     | Python 3.12, Flask 3.1.3   |
| Base datos  | SQLite (módulo `sqlite3`)  |
| Hashing     | bcrypt                     |
| Testing     | pytest 9.0.2                |
| Versionado  | Git                        |
| IA / SDD    | OpenCode (agentes)         |

## 4. Estructura de carpetas

```
proyecto-login/
│
├── sistema/
│   ├── backend/          ← API Flask, DB SQLite, hashing, tests
│   └── frontend/         ← login.html, dashboard.html, css/, js/
│
├── agents/
│   ├── agent-devops/     ← entorno, dependencias, ejecución
│   ├── agent-front/      ← interfaz de usuario
│   ├── agent-backend/    ← API, seguridad, sesiones
│   └── agent-qa/         ← pruebas, validación contra specs
│
├── specs/                ← fuente de verdad
│   ├── 00-environment/   ← environment.md, tools.md, architecture.md
│   ├── 01-login/         ← requirements, business-rules, acceptance-criteria, api-spec, traceability
│   ├── 02-security/      ← security-requirements, security-validation
│   └── 03-testing/       ← test-plan.md
│
├── README.md
└── EXPLICACION_SDD.md
```

## 5. Instalación

Requisitos: Windows 11, Python 3.12.4, pip 25.1.1.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r sistema/backend/requirements.txt
```

## 6. Configuración

1. Copia `sistema/backend/.env.example` a `sistema/backend/.env`.
2. Define `SESSION_SECRET` con un valor aleatorio largo.

## 7. Ejecución

```powershell
powershell -ExecutionPolicy Bypass -File sistema/backend/run.ps1
```

Luego abre en el navegador (Edge recomendado en esta máquina):
`http://127.0.0.1:5000`

## 8. Usuario de prueba

| Campo    | Valor          |
|----------|----------------|
| Username | `alumno`       |
| Password | `Practica123!` |

La contraseña se almacena en SQLite **hasheada con bcrypt** (nunca en texto plano).
Solo para desarrollo local.

## 9. Ejecución de tests

```powershell
# desde sistema/backend
python -m pytest -v
```

El plan de pruebas y el registro de resultados está en
`specs/03-testing/test-plan.md`.

## 10. Ubicación de los specs

- Entorno: `specs/00-environment/`
- Funcional (login): `specs/01-login/`
- Seguridad: `specs/02-security/`
- Pruebas: `specs/03-testing/`

## 11. Rol de los agentes

| Agente          | Responsabilidad                                        |
|-----------------|--------------------------------------------------------|
| agent-devops    | Entorno, dependencias, ejecución, variables de entorno |
| agent-front     | Interfaz, validaciones visuales, llamadas a la API     |
| agent-backend   | API, SQLite, hashing, sesiones, validaciones           |
| agent-qa        | Pruebas, reporte de discrepancias, validación          |

Detalles e instrucciones en cada carpeta `agents/<agente>/`.

## 12. Flujo SDD del proyecto

```
Entorno (00-environment)                    specs/00-environment/
  → Especificación funcional (01-login)     specs/01-login/
  → Seguridad (02-security)                 specs/02-security/
  → Plan de pruebas (03-testing)            specs/03-testing/
  → Implementación                          agent-devops → agent-backend + agent-front
  → Validación                              agent-qa (pytest + pruebas manuales)
  → Actualización de trazabilidad           specs/01-login/traceability.md
```

Explicación completa en `EXPLICACION_SDD.md`.