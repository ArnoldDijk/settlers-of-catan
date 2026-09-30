"""Seat tokens and the seat cookie.

A join token is 32 random bytes. The database stores only its SHA-256. After /api/join the
token lives in an HttpOnly, SameSite=Strict cookie scoped to /api, so page scripts can't read it.
"""

from __future__ import annotations

import hashlib
import re
import secrets

GAME_ID = re.compile(r"^[A-Za-z0-9_-]{8,32}$")


def new_token() -> str:
    return secrets.token_urlsafe(32)


def new_game_id() -> str:
    return secrets.token_urlsafe(9)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("ascii")).hexdigest()


def cookie_name(game_id: str) -> str:
    return f"catan_seat_{game_id}"
