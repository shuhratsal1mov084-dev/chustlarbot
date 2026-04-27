import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH


class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    text TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add_player(self, name: str, text: str) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO players (name, text) VALUES (?, ?)",
                    (name, text)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_player(self, player_id: int) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_players(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, text FROM players ORDER BY id")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, text FROM players WHERE id = ?", (player_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_player_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, text FROM players WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None


db = Database()
