"""Settings from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _flag(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True, slots=True)
class Settings:
    db_path: str = "/data/catan.db"
    #: Send the seat cookie only over HTTPS. Browsers treat http://localhost as secure, so this can
    #: stay on for local Docker; turn it off only for plain-HTTP test setups.
    cookie_secure: bool = True
    cookie_max_age: int = 60 * 60 * 24 * 30
    max_body_bytes: int = 16 * 1024

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            db_path=os.environ.get("CATAN_DB_PATH", "/data/catan.db"),
            cookie_secure=_flag("CATAN_COOKIE_SECURE", True),
        )
