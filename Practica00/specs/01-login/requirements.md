# Requisitos funcionales del login

Los requisitos funcionales (RF) definen QUÉ debe hacer el sistema de login. Son la
fuente de verdad para la implementación.

> Si un requisito debe cambiar durante la implementación, PRIMERO se actualiza este
> documento y DESPUÉS se modifica el código. Nunca al revés.

---

## RF-001 — Mostrar formulario

El sistema debe mostrar un formulario con:

- Campo `Username`
- Campo `Password`
- Botón "Iniciar sesión"

## RF-002 — Validar username

El username:

- Es obligatorio.
- No puede estar vacío.
- Debe tener entre 3 y 50 caracteres.
- No debe contener espacios al inicio o final.

## RF-003 — Validar password

La contraseña:

- Es obligatoria.
- Debe tener mínimo 8 caracteres.
- No debe almacenarse en texto plano.

## RF-004 — Autenticar usuario

El sistema debe verificar que:

- El username exista.
- La contraseña proporcionada corresponda con la contraseña almacenada.

Si ambas condiciones se cumplen, el login debe ser exitoso.

## RF-005 — Rechazar autenticación

Si las credenciales son incorrectas:

- El acceso debe ser rechazado.
- No debe crearse una sesión válida.
- Debe mostrarse un mensaje genérico.

Mensaje genérico obligatorio:

> Username o contraseña incorrectos.

El mensaje NO debe revelar si el username existe.

## RF-006 — Crear sesión

Cuando la autenticación sea correcta:

- El backend debe crear una sesión.
- El usuario debe poder acceder a un recurso protegido.

## RF-007 — Recurso protegido

Debe existir una ruta protegida: `/dashboard`.

- Solo usuarios autenticados pueden acceder.
- Un usuario NO autenticado debe ser rechazado o redirigido al login.

## RF-008 — Cerrar sesión

Debe existir una opción para cerrar sesión.

Al cerrar sesión:

- La sesión debe invalidarse.
- El usuario no debe poder acceder nuevamente al dashboard utilizando la sesión anterior.

---

## Atributos

- **Prioridad:** todos los RF son necesarios para la versión preliminar (práctica).
- **Estado:** no se marcará ningún RF como cumplido hasta que sea probado por QA.