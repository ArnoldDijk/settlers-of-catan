"""SQLite persistence. The full GameState lives only here, never in a response."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS games (
    id         TEXT PRIMARY KEY,
    state      TEXT NOT NULL,
    version    INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS seats (
    token_hash TEXT PRIMARY KEY,   -- SHA-256 of the join token; the token itself is never stored
    game_id    TEXT NOT NULL REFERENCES games(id),
    player_id  TEXT NOT NULL,
    UNIQUE (game_id, player_id)
);
"""


class VersionConflict(Exception):
    """Someone else changed the game since it was read."""


class Store:
    def __init__(self, path: str) -> None:
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA foreign_keys=ON")
        self._db.executescript(SCHEMA)
        self._lock = threading.Lock()

    def close(self) -> None:
        self._db.close()

    def create_game(self, game_id: str, state: dict[str, Any], seats: dict[str, str]) -> None:
        """`seats` maps token hash -> player id."""
        with self._lock:
            self._db.execute("BEGIN")
            try:
                self._db.execute(
                    "INSERT INTO games (id, state, version) VALUES (?, ?, 0)", (game_id, json.dumps(state))
                )
                self._db.executemany(
                    "INSERT INTO seats (token_hash, game_id, player_id) VALUES (?, ?, ?)",
                    [(h, game_id, pid) for h, pid in seats.items()],
                )
                self._db.execute("COMMIT")
            except BaseException:
                self._db.execute("ROLLBACK")
                raise

    def seat(self, token_hash: str) -> tuple[str, str] | None:
        with self._lock:
            row = self._db.execute(
                "SELECT game_id, player_id FROM seats WHERE token_hash = ?", (token_hash,)
            ).fetchone()
        return None if row is None else (row[0], row[1])

    def load(self, game_id: str) -> tuple[dict[str, Any], int] | None:
        with self._lock:
            row = self._db.execute("SELECT state, version FROM games WHERE id = ?", (game_id,)).fetchone()
        return None if row is None else (json.loads(row[0]), row[1])

    def save(self, game_id: str, state: dict[str, Any], expected_version: int) -> int:
        """Write if nobody else did in the meantime; returns the new version."""
        with self._lock:
            cur = self._db.execute(
                "UPDATE games SET state = ?, version = version + 1, updated_at = datetime('now') "
                "WHERE id = ? AND version = ?",
                (json.dumps(state), game_id, expected_version),
            )
        if cur.rowcount != 1:
            raise VersionConflict(game_id)
        return expected_version + 1
