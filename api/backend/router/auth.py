from __future__ import annotations

import hashlib
import secrets
import sqlite3
from pathlib import Path
from typing import Optional

DB_FILE = Path(__file__).with_name("auth.db")


def connect_sqlite() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect_sqlite() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def _hash_password(password: str, salt: str) -> str:
    data = f"{salt}:{password}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _hash_token(token: str, salt: str) -> str:
    data = f"{salt}:{token}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def upsert_credentials(username: str, password: str) -> None:
    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    with connect_sqlite() as conn:
        conn.execute(
            """
            INSERT INTO credentials (id, username, password_hash, salt)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username = excluded.username,
                password_hash = excluded.password_hash,
                salt = excluded.salt,
                updated_at = CURRENT_TIMESTAMP
            """,
            (username, password_hash, salt),
        )
        conn.commit()


def get_credentials() -> Optional[sqlite3.Row]:
    with connect_sqlite() as conn:
        row = conn.execute(
            "SELECT username, password_hash, salt FROM credentials WHERE id = 1"
        ).fetchone()
    return row


def verify_credentials(username: str, password: str) -> bool:
    row = get_credentials()
    if row is None:
        return False
    expected_user = row["username"]
    expected_hash = row["password_hash"]
    salt = row["salt"]
    candidate_hash = _hash_password(password, salt)
    return (
        secrets.compare_digest(username, expected_user)
        and secrets.compare_digest(candidate_hash, expected_hash)
    )


def issue_token(username: str, password: str) -> Optional[str]:
    if not verify_credentials(username, password):
        return None
    token = secrets.token_urlsafe(32)
    _store_token(token)
    return token


def _store_token(token: str) -> None:
    salt = secrets.token_hex(16)
    token_hash = _hash_token(token, salt)
    with connect_sqlite() as conn:
        conn.execute("DELETE FROM tokens")
        conn.execute(
            "INSERT INTO tokens (token_hash, salt) VALUES (?, ?)",
            (token_hash, salt),
        )
        conn.commit()


def verify_token(token: str) -> bool:
    with connect_sqlite() as conn:
        rows = conn.execute("SELECT token_hash, salt FROM tokens").fetchall()
    for row in rows:
        candidate = _hash_token(token, row["salt"])
        if secrets.compare_digest(candidate, row["token_hash"]):
            return True
    return False


init_db()
