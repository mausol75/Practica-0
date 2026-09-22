"""
test_login.py — Tests automatizados del sistema de login.

Cubre los criterios de aceptación AC-001 a AC-012.
Ejecutar: python -m pytest tests/ -v
"""

import os
import sys
import sqlite3

import bcrypt
import pytest

# Asegurar que el directorio padre (backend/) esté en sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app as flask_app, _failed_attempts
from db import DB_PATH, init_db, seed_user, get_connection


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def setup_app(tmp_path, monkeypatch):
    """
    Configura la app para tests: usa una DB temporal y limpia el estado
    de rate-limiting entre tests.
    """
    test_db = str(tmp_path / "test_login.db")
    monkeypatch.setattr("db.DB_PATH", test_db)

    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret"

    init_db()
    seed_user()

    _failed_attempts.clear()

    yield


@pytest.fixture
def client():
    """Cliente de test de Flask."""
    return flask_app.test_client()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_USERNAME = "alumno"
VALID_PASSWORD = "Practica123!"
GENERIC_ERROR = "Username o contraseña incorrectos."


def do_login(client, username=VALID_USERNAME, password=VALID_PASSWORD):
    """Helper para hacer POST /api/login."""
    return client.post(
        "/api/login",
        json={"username": username, "password": password},
    )


# ---------------------------------------------------------------------------
# AC-001 — Login exitoso
# ---------------------------------------------------------------------------


class TestAC001LoginExitoso:
    def test_login_exitoso_returns_200(self, client):
        resp = do_login(client)
        assert resp.status_code == 200
        assert resp.get_json()["message"] == "Login exitoso."

    def test_session_is_authenticated_after_login(self, client):
        do_login(client)
        resp = client.get("/api/session")
        data = resp.get_json()
        assert data["authenticated"] is True
        assert data["username"] == VALID_USERNAME


# ---------------------------------------------------------------------------
# AC-002 — Password incorrecto
# ---------------------------------------------------------------------------


class TestAC002PasswordIncorrecto:
    def test_wrong_password_returns_401(self, client):
        resp = do_login(client, password="wrongpassword")
        assert resp.status_code == 401
        assert resp.get_json()["error"] == GENERIC_ERROR

    def test_wrong_password_no_session(self, client):
        do_login(client, password="wrongpassword")
        resp = client.get("/api/session")
        assert resp.get_json()["authenticated"] is False


# ---------------------------------------------------------------------------
# AC-003 — Usuario inexistente
# ---------------------------------------------------------------------------


class TestAC003UsuarioInexistente:
    def test_nonexistent_user_returns_401(self, client):
        resp = do_login(client, username="noexiste")
        assert resp.status_code == 401
        assert resp.get_json()["error"] == GENERIC_ERROR


# ---------------------------------------------------------------------------
# AC-004 — Username vacío
# ---------------------------------------------------------------------------


class TestAC004UsernameVacio:
    def test_empty_username_returns_400(self, client):
        resp = do_login(client, username="")
        assert resp.status_code == 400

    def test_whitespace_username_returns_400(self, client):
        resp = do_login(client, username="   ")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# AC-005 — Password vacía
# ---------------------------------------------------------------------------


class TestAC005PasswordVacia:
    def test_empty_password_returns_400(self, client):
        resp = do_login(client, password="")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# AC-006 — Acceso protegido
# ---------------------------------------------------------------------------


class TestAC006AccesoProtegido:
    def test_dashboard_without_session_redirects(self, client):
        resp = client.get("/dashboard")
        # Debe redirigir al login (302)
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_dashboard_with_session_returns_200(self, client):
        do_login(client)
        resp = client.get("/dashboard")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# AC-007 — Logout
# ---------------------------------------------------------------------------


class TestAC007Logout:
    def test_logout_invalidates_session(self, client):
        do_login(client)
        # Verificar sesión activa
        resp = client.get("/api/session")
        assert resp.get_json()["authenticated"] is True

        # Logout
        resp = client.post("/api/logout")
        assert resp.status_code == 200
        assert resp.get_json()["message"] == "Sesión cerrada."

        # Sesión debe estar inválida
        resp = client.get("/api/session")
        assert resp.get_json()["authenticated"] is False

    def test_dashboard_rejected_after_logout(self, client):
        do_login(client)
        client.post("/api/logout")
        resp = client.get("/dashboard")
        assert resp.status_code == 302  # redirect to login


# ---------------------------------------------------------------------------
# AC-008 — Username demasiado corto
# ---------------------------------------------------------------------------


class TestAC008UsernameMuyCorto:
    def test_short_username_returns_400(self, client):
        resp = do_login(client, username="ab")
        assert resp.status_code == 400

    def test_single_char_username_returns_400(self, client):
        resp = do_login(client, username="x")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# AC-009 — Password demasiado corta
# ---------------------------------------------------------------------------


class TestAC009PasswordMuyCorta:
    def test_short_password_returns_400(self, client):
        resp = do_login(client, password="1234567")
        assert resp.status_code == 400

    def test_7_char_password_returns_400(self, client):
        resp = do_login(client, password="Pas123!")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# AC-010 — Contraseña no almacenada en texto plano
# ---------------------------------------------------------------------------


class TestAC010PasswordNoTextoPlano:
    def test_password_stored_as_bcrypt_hash(self, client):
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT password_hash FROM users WHERE username = ?",
                (VALID_USERNAME,),
            ).fetchone()
            assert row is not None
            stored_hash = row["password_hash"]
            # El hash NO es la contraseña original
            assert stored_hash != VALID_PASSWORD
            # El hash comienza con el prefijo bcrypt ($2b$ o $2a$)
            assert stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$")
            # Verificar que el hash es válido con bcrypt
            assert bcrypt.checkpw(
                VALID_PASSWORD.encode("utf-8"), stored_hash.encode("utf-8")
            )
        finally:
            conn.close()


# ---------------------------------------------------------------------------
# AC-011 — Resistencia básica a SQL Injection
# ---------------------------------------------------------------------------


class TestAC011SQLInjection:
    @pytest.mark.parametrize(
        "payload",
        [
            "' OR 1=1--",
            "' OR '1'='1",
            "admin'--",
            "'; DROP TABLE users;--",
            "\" OR 1=1--",
        ],
    )
    def test_sql_injection_username_rejected(self, client, payload):
        resp = do_login(client, username=payload, password="anything123")
        assert resp.status_code in (400, 401)
        assert resp.status_code != 200

    @pytest.mark.parametrize(
        "payload",
        [
            "' OR 1=1--",
            "anything' OR '1'='1",
        ],
    )
    def test_sql_injection_password_rejected(self, client, payload):
        resp = do_login(client, username=VALID_USERNAME, password=payload)
        assert resp.status_code in (400, 401)
        assert resp.status_code != 200


# ---------------------------------------------------------------------------
# AC-012 — Mensaje de error sin revelar existencia del usuario
# ---------------------------------------------------------------------------


class TestAC012MensajeGenerico:
    def test_same_error_for_nonexistent_user_and_wrong_password(self, client):
        # Usuario inexistente
        resp1 = do_login(client, username="noexiste", password="cualquier123")
        # Password incorrecta
        resp2 = do_login(client, username=VALID_USERNAME, password="wrongpassword")

        assert resp1.status_code == resp2.status_code == 401
        assert resp1.get_json()["error"] == resp2.get_json()["error"] == GENERIC_ERROR


# ---------------------------------------------------------------------------
# Tests adicionales — API session, JSON malformado
# ---------------------------------------------------------------------------


class TestAPIMisc:
    def test_session_unauthenticated_returns_200(self, client):
        """GET /api/session sin sesión siempre devuelve 200."""
        resp = client.get("/api/session")
        assert resp.status_code == 200
        assert resp.get_json()["authenticated"] is False

    def test_login_without_json_returns_400(self, client):
        """POST /api/login sin JSON válido devuelve 400."""
        resp = client.post(
            "/api/login",
            data="esto no es json",
            content_type="text/plain",
        )
        assert resp.status_code == 400

    def test_login_with_empty_json_returns_400(self, client):
        resp = client.post("/api/login", json={})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Tests — Consulta de Clima (002-Consulta-clima)
# ---------------------------------------------------------------------------


class TestWeatherAPI:
    """Tests del endpoint GET /api/v1/weather."""

    def test_weather_without_session_redirects(self, client):
        """Sin sesión, debe redirigir al login (302)."""
        resp = client.get("/api/v1/weather?location=Peru")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_weather_missing_location_returns_400(self, client):
        """Con sesión pero sin parámetro location, debe devolver 400."""
        do_login(client)
        resp = client.get("/api/v1/weather")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_weather_empty_location_returns_400(self, client):
        """Con sesión y location vacío, debe devolver 400."""
        do_login(client)
        resp = client.get("/api/v1/weather?location=")
        assert resp.status_code == 400

    def test_weather_valid_location_returns_200(self, client, monkeypatch):
        """Con sesión y ubicación válida (mockeada), debe devolver 200 con JSON correcto."""
        from unittest.mock import MagicMock

        # Mock de la respuesta de geocoding
        mock_geo_response = MagicMock()
        mock_geo_response.status_code = 200
        mock_geo_response.raise_for_status = MagicMock()
        mock_geo_response.json.return_value = {
            "results": [
                {
                    "name": "Lima",
                    "latitude": -12.0464,
                    "longitude": -77.0428,
                    "country": "Perú",
                }
            ]
        }

        # Mock de la respuesta de clima
        mock_weather_response = MagicMock()
        mock_weather_response.status_code = 200
        mock_weather_response.raise_for_status = MagicMock()
        mock_weather_response.json.return_value = {
            "current": {
                "temperature_2m": 24.0,
                "relative_humidity_2m": 60,
                "weather_code": 0,
            }
        }

        call_count = 0

        def mock_get(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_geo_response
            return mock_weather_response

        monkeypatch.setattr("app.http_requests.get", mock_get)

        do_login(client)
        resp = client.get("/api/v1/weather?location=Peru")
        assert resp.status_code == 200

        data = resp.get_json()
        assert "location" in data
        assert "temperature" in data
        assert "condition" in data
        assert "humidity" in data
        assert "Lima" in data["location"]
        assert "24" in data["temperature"]
        assert "°C" in data["temperature"]
        assert "60%" == data["humidity"]
        assert data["condition"] == "Despejado"

    def test_weather_nonexistent_location_returns_404(self, client, monkeypatch):
        """Ubicación no encontrada debe devolver 404."""
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {}  # No "results" key

        def mock_get(url, **kwargs):
            return mock_response

        monkeypatch.setattr("app.http_requests.get", mock_get)

        do_login(client)
        resp = client.get("/api/v1/weather?location=xyznotaplace999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert "error" in data

