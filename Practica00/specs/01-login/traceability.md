# Matriz de trazabilidad

La matriz vincula cada requisito con su implementación y su prueba.

Reglas:

- Es la fuente de verdad sobre el estado de cumplimiento.
- NINGÚN requisito se marca como cumplido si no fue probado por QA.
- La implementación la completa `agent-backend`/`agent-front`; la columna "Prueba" la
  completa `agent-qa`; el "Estado" se actualiza solo tras resultados reales.

Estado: `Pendiente` | `Implementado` | `En prueba` | `Conforme` | `No conforme`

---

| ID     | Requisito                 | Implementación          | Prueba             | Estado     |
|--------|---------------------------|-------------------------|--------------------|------------|
| RF-001 | Mostrar formulario        | Frontend login (`login.html`) | Test UI (inspección/ETL) | Pendiente  |
| RF-002 | Validación username       | Backend (validación en `/api/login`) | `test_login_*` (validación username) | Pendiente  |
| RF-003 | Validación password       | Backend (validación en `/api/login`) | `test_login_*` (validación password) | Pendiente  |
| RF-004 | Autenticación             | Backend `POST /api/login` | `test_login_success` | Pendiente  |
| RF-005 | Rechazo autenticación     | Backend `POST /api/login` (401 + mensaje genérico) | `test_login_*` (credenciales inválidas) | Pendiente  |
| RF-006 | Crear sesión              | Backend (sesión tras login) | `test_session*` | Pendiente  |
| RF-007 | Dashboard protegido       | Backend `GET /dashboard`  | `test_protected_route` | Pendiente  |
| RF-008 | Cerrar sesión             | Backend `POST /api/logout` | `test_logout*` | Pendiente  |

## Vínculos adicionales

| ID     | Elemento                                   | Tipo            |
|--------|--------------------------------------------|-----------------|
| BR-001 a BR-004 | reglas de validación de campos      | regla de negocio |
| BR-005 | unicidad de usernames                      | regla de negocio |
| BR-006, BR-007, BR-010 | seguridad / hashing / logout  | regla de negocio |
| AC-001 a AC-012 | criterios verificables              | criterio de aceptación |
| SEC-*  | requisitos de seguridad                    | ver `specs/02-security/` |

## Nota de implementación

Durante la implementación (Fase 2) esta matriz se actualizará en la columna
"Implementación" sin alterar el "Estado". La columna "Estado" se actualizará únicamente
tras los resultados reales de las pruebas (Fase 3).