# Explicación de Spec-Driven Development (SDD)

Documento de apoyo, en español sencillo, para explicar el trabajo al docente.

---

## ¿Qué es Spec-Driven Development?

Spec-Driven Development (SDD) es una forma de desarrollar software en la que la
**especificación se escribe ANTES que el código** y es la **fuente de verdad** del
proyecto.

En vez de "ir programando y viendo qué sale", primero se definen:

- **qué** debe hacer el sistema (requisitos),
- **cómo** se comporta (reglas de negocio),
- **qué** debe cumplir para aceptarse (criterios de aceptación),
- **qué** responde la API (contratos),
- **cómo** se relaciona cada requisito con su código y su prueba (trazabilidad).

Después se implementa siguiendo esas definiciones y se comprueba (QA) que el código
cumple exactamente lo especificado.

## ¿Cómo se aplicó en este proyecto?

```
Spec (especificación)
  ↓
Agentes (devops → backend + front → qa)
  ↓
Implementación
  ↓
QA / pruebas (pytest + manuales)
  ↓
Validación contra la spec (trazabilidad + auditoría)
```

Pasos concretos:

1. Se definió el entorno con datos reales (`specs/00-environment/`).
2. Se escribió la especificación del login (`specs/01-login/`): requisitos, reglas de
   negocio, criterios de aceptación, API y trazabilidad.
3. Se especificó la seguridad (`specs/02-security/`).
4. Se planificaron las pruebas (`specs/03-testing/`).
5. Con los specs ya cerrados, los agentes implementaron:
   - `agent-devops` preparó el entorno y la ejecución.
   - `agent-backend` implementó la API, la base de datos y la seguridad.
   - `agent-front` implementó el formulario y el dashboard.
6. `agent-qa` ejecutó las pruebas y revisó que el código cumpla los specs.
7. Se actualizó la trazabilidad con los resultados reales.

## ¿Cuál es el papel de cada carpeta?

| Carpeta   | Papel                                                             |
|-----------|-------------------------------------------------------------------|
| `sistema/`| El código de la aplicación: backend (Flask + SQLite) y frontend (HTML/CSS/JS). |
| `agents/` | Los roles de cada agente: devops, front, backend y qa. Definen quién hace qué. |
| `specs/`  | La especificación (fuente de verdad): entorno, login, seguridad y testing. |

## ¿Cuál es el papel de cada agente?

| Agente        | Papel                                                                    |
|---------------|--------------------------------------------------------------------------|
| `agent-devops`| Prepara el entorno, instala dependencias, configura variables de entorno y verifica que el proyecto arranque. |
| `agent-front` | Implementa la interfaz de login, el dashboard, las validaciones visuales y la comunicación con la API. |
| `agent-backend`| Implementa la API, el acceso a SQLite, el hash con bcrypt, las sesiones y las validaciones del servidor. |
| `agent-qa`    | Crea y ejecuta las pruebas, y busca discrepancias entre el código y los specs. Reporta (no oculta) los fallos. |

## ¿Qué es un Spec?

Un spec (especificación) es un documento que dice **qué debe hacer** el sistema y
**qué condiciones** debe cumplir, antes de escribir el código.

Ejemplo con el login:

- Requisito (RF-004): *"El sistema debe verificar que el username exista y que la
  contraseña proporcionada corresponda con la almacenada."*
- Criterio de aceptación (AC-001): *"Si el usuario existe y la contraseña es correcta,
  se autentica y entra al dashboard."*
- Regla de seguridad (SEC-004): *"El error debe ser genérico, sin revelar si el usuario
  existe."*

Eso es lo que guía la implementación y las pruebas.

## Ejemplo de trazabilidad

```
RF-004
"El sistema debe autenticar al usuario"
        ↓
POST /api/login   (backend)
        ↓
test_login_success   (agent-qa)
        ↓
PASS   (ejecutado por pytest)
```

*(Estado pendiente hasta que se ejecuten las pruebas reales; se actualizará en la Fase
de QA.)*

## Diferencia entre SDD y Vibe Coding

- **Vibe Coding:** se le pide a la IA *"hazme un login"* y se itera sin plan, ajustando
  a ciegas. No hay una fuente de verdad. Se acepta lo que salga mientras *"se vea bien"*.
- **SDD:** primero se escribe la especificación (`specs/`) y *después* se le pide a la IA
  que la cumpla. Si algo cambia, se cambia el spec y luego el código.

Ejemplo concreto en este proyecto:

- En SDD, la validación del username (RF-002: obligatorio, de 3 a 50 caracteres) está
  **escrita** en `specs/01-login/requirements.md` antes de que el backend la implemente.
- En Vibe Coding esa regla no estaría escrita en ninguna parte: dependería de lo que la
  IA *"decida"* por su cuenta.

## Posibles preguntas del docente (con respuestas)

### ¿Qué es SDD?
Es desarrollo guiado por especificaciones: primero se define el spec y luego se
implementa y valida contra él. Los specs son la fuente de verdad.

### ¿Cuál es la fuente de verdad?
La carpeta `specs/`. Está antes que el código: ningún requisito se implementa si no está
en los specs, y ninguna afirmación se da por cierta sin prueba.

### ¿Qué es un requisito?
Un requisito funcional (RF-XXX) define *qué* debe hacer el sistema. Ejemplo RF-001:
*mostrar el formulario con username, password y botón "Iniciar sesión"*.

### ¿Qué es un criterio de aceptación?
Una condición concreta y comprobable. Ejemplo AC-001: *"con credenciales correctas se
obtiene 200 y se accede al dashboard"*.

### ¿Qué es trazabilidad?
La relación Requisito → código → prueba. Se documenta en
`specs/01-login/traceability.md`. Cada requisito sabe qué código lo implementa y qué
prueba lo comprueba.

### ¿Qué hace cada agente?
Devops prepara el entorno; backend implementa la API, la base de datos y la seguridad;
front implementa la interfaz; QA prueba y reporta.

### ¿Qué papel tiene OpenCode?
Es el orquestador del SDD: lee los specs, coordina a los agentes para implementar solo
lo definido y ejecuta las pruebas registrando los resultados.

### ¿Por qué no es simplemente Vibe Coding?
Porque el código no es improvisado: todo lo que se implementa está primero escrito en
`specs/` (validaciones, códigos de estado, mensajes genéricos, hashing bcrypt, etc.), y
QA comprueba que se cumpla.

### ¿Qué sucede si quiero cambiar un requisito?
Se sigue el proceso SDD: se actualiza primero el spec (por ejemplo, `requirements.md` o
`api-spec.md`) y después se cambia el código. Nunca al revés.

### ¿Cómo se comprobó que el código cumple el Spec?
De dos formas: (1) pruebas automatizadas con pytest que cubren cada requisito del
`test-plan.md`, y (2) comprobaciones manuales con curl y navegador. Los resultados se
registran en `traceability.md`.

### ¿Por qué existe un agente QA?
Porque el objetivo es mostrar que el código cumple lo especificado, y QA es quien lo
verifica de forma independiente. QA no oculta errores: los reporta.

### ¿Por qué la contraseña no se guarda directamente?
Por seguridad. Almacenamos solo el **hash** con bcrypt. Así, aunque alguien obtenga la
base de datos, no obtiene las contraseñas reales. Además se cumple BR-007 ("nunca
almacenar contraseñas en texto plano").