"""
db.py — Inicialización de SQLite y seed del usuario de prueba.

Tabla `users`:
  - id            INTEGER PRIMARY KEY
  - username      TEXT UNIQUE NOT NULL
  - password_hash TEXT NOT NULL

El usuario seed es: alumno / Practica123!  (hash bcrypt, nunca texto plano).
"""

import os
import sqlite3

import bcrypt

# Ruta de la base de datos (junto a este archivo).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "login.db")


def get_connection() -> sqlite3.Connection:
    """Devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea la tabla `users` si no existe."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_user() -> None:
    """
    Inserta el usuario de prueba si no existe.
    Username: alumno
    Password: Practica123!  (almacenada como hash bcrypt — BR-006, BR-007).
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?", ("alumno",)
        ).fetchone()
        if row is None:
            password_hash = bcrypt.hashpw(
                "Practica123!".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                ("alumno", password_hash),
            )
            conn.commit()
    finally:
        conn.close()


def find_user_by_username(username: str) -> dict | None:
    """Busca un usuario por username.  Devuelve dict o None."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()
