import json
import sqlite3
from datetime import datetime


class NotificationStore:
    def __init__(self, sqlite_path: str) -> None:
        self.sqlite_path = sqlite_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notification_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    phone TEXT,
                    payload_json TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_key TEXT NOT NULL UNIQUE,
                    response_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def is_healthy(self) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def log_event(
        self,
        event_type: str,
        payload: dict,
        status: str,
        phone: str | None = None,
        error_message: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO notification_logs (event_type, phone, payload_json, status, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    event_type,
                    phone,
                    json.dumps(payload, ensure_ascii=True),
                    status,
                    error_message,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()

    def list_recent(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT id, event_type, phone, payload_json, status, error_message, created_at
                FROM notification_logs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_processed_response(self, request_key: str) -> dict | None:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                SELECT response_json
                FROM processed_requests
                WHERE request_key = ?
                LIMIT 1
                """,
                (request_key,),
            )
            row = cursor.fetchone()

        if not row:
            return None

        return json.loads(row["response_json"])

    def save_processed_response(self, request_key: str, response_data: dict) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO processed_requests (request_key, response_json, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    request_key,
                    json.dumps(response_data, ensure_ascii=True),
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
