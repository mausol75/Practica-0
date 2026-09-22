"""
app.py — Aplicación Flask principal del sistema de login + consulta de clima.

Endpoints:
  POST /api/login          — Autenticación (RF-004, RF-005)
  GET  /api/session        — Verificar sesión (RF-006)
  POST /api/logout         — Cerrar sesión (RF-008)
  GET  /api/v1/weather     — Consulta de clima (002-Consulta-clima)
  GET  /dashboard          — Página protegida (RF-007)
  GET  /login              — Formulario de login (RF-001)
  GET  /                   — Redirige a /login
"""

import os
import time
import logging
from functools import wraps

import bcrypt
import requests as http_requests
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    request,
    send_from_directory,
    session,
    url_for,
)

from db import find_user_by_username, init_db, seed_user

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

load_dotenv()


def _load_secret(env_var: str, file_env_var: str, default: str) -> str:
    """Lee un secreto desde archivo (Docker secrets) o variable de entorno."""
    file_path = os.getenv(file_env_var, "")
    if file_path and os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return os.getenv(env_var, default)


app = Flask(__name__, static_folder=None)
app.secret_key = _load_secret(
    "SESSION_SECRET", "SESSION_SECRET_FILE", "dev-secret-key-cambiar-en-prod"
)

# Cookies de sesión seguras (api-spec.md: HttpOnly, SameSite=Lax)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# Ruta al directorio del frontend
FRONTEND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "frontend"
)

# ---------------------------------------------------------------------------
# Rate limiting — BR-011
# Almacena intentos fallidos por IP: {ip: {"count": int, "locked_until": float}}
# ---------------------------------------------------------------------------
_failed_attempts: dict[str, dict] = {}

RATE_LIMIT_MAX_ATTEMPTS = 3
RATE_LIMIT_LOCKOUT_SECONDS = 90


def _check_rate_limit(ip: str) -> str | None:
    """Retorna un mensaje de error si la IP está bloqueada, o None si puede continuar."""
    record = _failed_attempts.get(ip)
    if record and record.get("locked_until"):
        remaining = record["locked_until"] - time.time()
        if remaining > 0:
            return f"Demasiados intentos fallidos. Intente de nuevo en {int(remaining)} segundos."
        else:
            # El bloqueo expiró: reiniciar
            _failed_attempts.pop(ip, None)
    return None


def _register_failed_attempt(ip: str) -> str | None:
    """Registra un intento fallido. Retorna mensaje de bloqueo si se alcanza el límite."""
    record = _failed_attempts.setdefault(ip, {"count": 0, "locked_until": None})
    record["count"] += 1
    if record["count"] >= RATE_LIMIT_MAX_ATTEMPTS:
        record["locked_until"] = time.time() + RATE_LIMIT_LOCKOUT_SECONDS
        return f"Demasiados intentos fallidos. Intente de nuevo en {RATE_LIMIT_LOCKOUT_SECONDS} segundos."
    return None


def _clear_failed_attempts(ip: str) -> None:
    """Limpia los intentos fallidos tras un login exitoso."""
    _failed_attempts.pop(ip, None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def login_required(f):
    """Decorador que protege rutas: exige sesión autenticada."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            # Si el cliente espera JSON, responder 401 JSON; si no, redirigir.
            if request.accept_mimetypes.best == "application/json":
                return jsonify({"error": "Sesión no válida."}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)

    return decorated


# ---------------------------------------------------------------------------
# Endpoints — API
# ---------------------------------------------------------------------------


@app.route("/api/login", methods=["POST"])
def api_login():
    """
    POST /api/login
    Autentica con username y contraseña.
    Respuestas: 200 (éxito), 400 (validación), 401 (credenciales).
    """

    # — Rate limit (BR-011) ---------------------------------------------------
    client_ip = request.remote_addr or "unknown"
    rate_error = _check_rate_limit(client_ip)
    if rate_error:
        return jsonify({"error": rate_error}), 429

    # — Parsear JSON ----------------------------------------------------------
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "El cuerpo de la petición debe ser JSON válido."}), 400

    username = data.get("username", "")
    password = data.get("password", "")

    # — Validaciones de campo (RF-002, RF-003) --------------------------------

    # Username obligatorio / vacío (BR-001)
    if not username or not username.strip():
        return jsonify({"error": "El username es obligatorio."}), 400

    # Trim de espacios (RF-002: no debe contener espacios al inicio o final)
    username = username.strip()

    # Longitud username (BR-002)
    if len(username) < 3:
        return jsonify({"error": "El username debe tener al menos 3 caracteres."}), 400
    if len(username) > 50:
        return jsonify({"error": "El username no debe superar los 50 caracteres."}), 400

    # Password obligatoria / vacía (BR-003)
    if not password:
        return jsonify({"error": "La contraseña es obligatoria."}), 400

    # Longitud password (BR-004)
    if len(password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres."}), 400

    # — Autenticación (RF-004) ------------------------------------------------
    user = find_user_by_username(username)

    # Mensaje genérico idéntico para username inexistente y password incorrecta
    # (RF-005, BR-008, AC-012).
    generic_error = "Username o contraseña incorrectos."

    if user is None:
        _register_failed_attempt(client_ip)
        return jsonify({"error": generic_error}), 401

    if not bcrypt.checkpw(
        password.encode("utf-8"), user["password_hash"].encode("utf-8")
    ):
        _register_failed_attempt(client_ip)
        return jsonify({"error": generic_error}), 401

    # — Login exitoso (RF-006) ------------------------------------------------
    _clear_failed_attempts(client_ip)
    session.clear()
    session["authenticated"] = True
    session["username"] = user["username"]

    return jsonify({"message": "Login exitoso."}), 200


@app.route("/api/session", methods=["GET"])
def api_session():
    """
    GET /api/session
    Siempre responde 200; el estado viene en el cuerpo (api-spec.md).
    """
    if session.get("authenticated"):
        return jsonify({
            "authenticated": True,
            "username": session.get("username"),
        }), 200

    return jsonify({"authenticated": False}), 200


@app.route("/api/logout", methods=["POST"])
def api_logout():
    """
    POST /api/logout
    Invalida la sesión actual (RF-008, BR-010).
    """
    session.clear()
    return jsonify({"message": "Sesión cerrada."}), 200


# ---------------------------------------------------------------------------
# Endpoints — Clima (002-Consulta-clima)
# ---------------------------------------------------------------------------

# Mapeo de códigos WMO a descripciones en español
_WMO_CODES: dict[int, str] = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    56: "Llovizna helada ligera",
    57: "Llovizna helada intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia intensa",
    66: "Lluvia helada ligera",
    67: "Lluvia helada intensa",
    71: "Nevada ligera",
    73: "Nevada moderada",
    75: "Nevada intensa",
    77: "Granizo",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos intensos",
    85: "Nevada ligera intermitente",
    86: "Nevada intensa intermitente",
    95: "Tormenta eléctrica",
    96: "Tormenta con granizo ligero",
    99: "Tormenta con granizo intenso",
}

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@app.route("/api/v1/weather", methods=["GET"])
@login_required
def api_weather():
    """
    GET /api/v1/weather?location={country_or_region_name}
    Consulta el clima actual de una ubicación.
    Requiere sesión autenticada.
    """
    location = request.args.get("location", "").strip()

    if not location:
        return jsonify({"error": "El parámetro 'location' es obligatorio."}), 400

    try:
        # --- Paso 1: Geocoding (nombre → coordenadas) -------------------------
        geo_resp = http_requests.get(
            GEOCODING_URL,
            params={"name": location, "count": 1, "language": "es"},
            timeout=10,
        )
        geo_resp.raise_for_status()
        geo_data = geo_resp.json()

        results = geo_data.get("results")
        if not results:
            return jsonify({"error": f"No se encontró la ubicación '{location}'."}), 404

        place = results[0]
        lat = place["latitude"]
        lon = place["longitude"]
        resolved_name = place.get("name", location)
        country = place.get("country", "")
        display_location = f"{resolved_name}, {country}" if country else resolved_name

        # --- Paso 2: Clima actual ---------------------------------------------
        weather_resp = http_requests.get(
            WEATHER_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,weather_code",
            },
            timeout=10,
        )
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()

        current = weather_data.get("current", {})
        temperature = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        weather_code = current.get("weather_code", 0)
        condition = _WMO_CODES.get(weather_code, "Desconocido")

        return jsonify({
            "location": display_location,
            "temperature": f"{temperature}°C",
            "condition": condition,
            "humidity": f"{humidity}%",
        }), 200

    except http_requests.exceptions.Timeout:
        return jsonify({"error": "Tiempo de espera agotado al consultar el clima."}), 504
    except http_requests.exceptions.ConnectionError:
        return jsonify({"error": "No se pudo conectar al servicio de clima."}), 503
    except Exception as e:
        logging.exception("Error inesperado en /api/v1/weather")
        return jsonify({"error": "Error interno al consultar el clima."}), 500


# ---------------------------------------------------------------------------
# Endpoints — Health Check (Elastic Beanstalk)
# ---------------------------------------------------------------------------


@app.route("/health", methods=["GET"])
def health_check():
    """GET /health — Health check para el Load Balancer de Elastic Beanstalk."""
    return jsonify({"status": "healthy"}), 200


# ---------------------------------------------------------------------------
# Endpoints — Páginas
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Redirige la raíz al formulario de login."""
    return redirect(url_for("login_page"))


@app.route("/login")
def login_page():
    """Sirve el formulario de login (RF-001)."""
    return send_from_directory(FRONTEND_DIR, "login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Página protegida (RF-007). Solo con sesión válida."""
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


# ---------------------------------------------------------------------------
# Archivos estáticos del frontend (CSS, JS)
# ---------------------------------------------------------------------------


@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, "js"), filename)


# ---------------------------------------------------------------------------
# Inicio
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    seed_user()
    app.run(host="0.0.0.0", port=5000, debug=False)
