# Instrucciones para agent-devops

Orden de trabajo y reglas que debe seguir `agent-devops` en este proyecto.

## 1. Objetivo

Garantizar que el proyecto pueda instalarse, configurarse y ejecutarse en el entorno
Windows 11 disponible (Python 3.12.4).

## 2. Tareas (en orden)

1. **Preparar entorno virtual**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. **Instalar dependencias del backend**
   ```powershell
   pip install -r sistema/backend/requirements.txt
   ```

3. **Configurar variables de entorno**
   - Crear `sistema/backend/.env` copiando `.env.example`.
   - Generar un valor aleatorio para `SESSION_SECRET` (no usar un valor fijo
     comprometido).

4. **Ejecutar la aplicación**
   ```powershell
   powershell -ExecutionPolicy Bypass -File sistema/backend/run.ps1
   ```
   (Alternativa manual: `python sistema/backend/app.py` con las variables cargadas.)

5. **Verificar arranque**
   - `GET http://127.0.0.1:5000/api/session` debe responder.
   - Confirmar que `/login` devuelve la página del formulario.

## 3. Reglas

- Usa únicamente lo definido en `specs/00-environment/`. 
- Los pasos 1-2 asumen Python y pip ya presentes (3.12.4 / 25.1.1).
- Si una dependencia no está disponible, detente y reporta; NO improvises la solución.
- NO edites el código funcional de `app.py`, `db.py`, `auth.py` ni del frontend.
- Registra en este documento/README cualquier comando que desvíe del estándar
  (p. ej. flags especiales en Windows).

## 4. Entregables

- Entorno instalado y verificable.
- Variables de entorno configuradas (`.env` local, nunca en repo).
- Documentación breve de cómo ejecutar (queda consolidada en `README.md` raíz).