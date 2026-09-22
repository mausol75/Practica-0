# Instrucciones para agent-qa

Reglas para crear, ejecutar y reportar las pruebas del proyecto.

## 1. Fuente de verdad

- `specs/01-login/acceptance-criteria.md`
- `specs/03-testing/test-plan.md`
- `specs/02-security/security-validation.md`
- `specs/01-login/requirements.md` y `traceability.md`

## 2. Tareas

### 2.1 Crear pruebas (pytest) en `sistema/backend/tests/`

Cubrir los casos del `test-plan.md`:

- `test_login_success`
- `test_login_unknown_user`
- `test_login_wrong_password`
- `test_login_empty_username`
- `test_login_empty_password`
- `test_login_short_username`
- `test_login_short_password`
- `test_login_creates_session`
- `test_protected_route_authenticated`
- `test_protected_route_unauthenticated`
- `test_logout_invalidates_session`
- `test_password_not_stored_in_plaintext`
- `test_sql_injection`
- `test_error_message_does_not_reveal_username`

Usa fixtures de pytest: `client` (app de test con BD temporal/limpia) y un usuario de
prueba sembrado con hash bcrypt.

### 2.2 Ejecutar las pruebas

```bash
python -m pytest -v
```

Registrar los resultados reales en `specs/03-testing/test-plan.md`
(sección "Registro de resultados").

### 2.3 Comprobaciones manuales

- curl (`curl.exe`) hacia `/api/login`, `/api/session`, `/api/logout` con cookies reales.
- UI en Edge: formulario (RF-001), redirección tras login, dashboard, logout.

## 3. Reporte de problemas

Formato obligatorio al encontrar un fallo:

```
ID: <identificador (QA-001, QA-002, ...)>
Requisito relacionado: <RF/AC/BR/SEC correspondiente>
Problema: <descripción concreta>
Resultado esperado: <según spec>
Resultado obtenido: <real>
Severidad: <Baja | Media | Alta>
Estado: <Abierto | Cerrado>
```

- NO corrijas el código para que la prueba pase.
- Si hay discrepancia código vs spec, repórtala; la corrección la hace el agente
  correspondiente (backend/front) DESPUÉS de actualizar el spec si hace falta.

## 4. Criterios de aprobación para reportar

Un requisito/criterio solo se considera **aprobado** si:

- Existe una prueba que lo ejercita, y
- La prueba fue ejecutada y pasó (o la comprobación manual verificó), y
- El registro en `test-plan.md` / `traceability.md` refleja ese resultado.

## 5. Actualización de trazabilidad

Al terminar, actualizar `specs/01-login/traceability.md`:
- Columna "Prueba": nombre real del test que cubre cada RF.
- Columna "Estado": `Conforme` / `No conforme` con evidencia.