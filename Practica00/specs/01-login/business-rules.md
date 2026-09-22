# Reglas de negocio del login

Las reglas de negocio (BR) precisan las restricciones que el sistema debe respetar
para ser consistente con el dominio. Complementan a los requisitos funcionales.

---

## BR-001 — El username es obligatorio

El sistema no puede procesar un intento de login sin un username.

## BR-002 — El username debe tener entre 3 y 50 caracteres

Los límites (3 y 50) se aplican al valor limpio de espacios al inicio y final.

## BR-003 — La contraseña es obligatoria

El sistema no puede procesar un intento de login sin contraseña.

## BR-004 — La contraseña debe tener al menos 8 caracteres

Se exige un mínimo de 8 caracteres.

## BR-005 — Los usernames deben ser únicos

Dos usuarios no pueden compartir el mismo username. Esto se garantiza, al menos, con
una restricción de unicidad en la tabla de usuarios.

## BR-006 — Las contraseñas deben almacenarse mediante un algoritmo de hashing apropiado

Se utiliza **bcrypt**, que incorpora un *salt* aleatorio en cada hash.
No se usan: MD5, SHA1 ni SHA256 directo como contraseña almacenada.

## BR-007 — Nunca almacenar contraseñas en texto plano

En la base de datos SOLO existe el hash de la contraseña, nunca el valor original.

## BR-008 — Las credenciales incorrectas deben producir un mensaje genérico

Tanto si el username no existe como si la contraseña es errónea, la respuesta debe ser
la misma: *"Username o contraseña incorrectos."*
Nunca: *"El usuario existe pero la contraseña es incorrecta."*

## BR-009 — Solo un usuario autenticado puede acceder a /dashboard

Si no hay una sesión válida, el acceso a `/dashboard` se rechaza o redirige al login.

## BR-010 — Cerrar sesión debe invalidar la sesión actual

Tras `logout`, la sesión deja de ser válida y no puede reutilizarse.

## BR-011 — Tiempo de espera por fallo de inicio de sesión

Tras 3 intentos de inicio de sesión fallidos se impide el inicio de sesión por 90 segundos.
---

## Relación con los requisitos funcionales

| Regla  | Vínculo          |
|--------|------------------|
| BR-001 | RF-002            |
| BR-002 | RF-002            |
| BR-003 | RF-003            |
| BR-004 | RF-003            |
| BR-005 | DB (seed/registro)|
| BR-006 | RF-003, seguridad |
| BR-007 | RF-003, seguridad |
| BR-008 | RF-005            |
| BR-009 | RF-007            |
| BR-010 | RF-008            |