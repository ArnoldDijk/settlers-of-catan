from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from catan_server.config import Settings
from catan_server.main import create_app

ORIGIN = "https://testserver"


@dataclass
class Seat:
    game_id: str
    player_id: str
    token: str

    @property
    def cookie(self) -> dict[str, str]:
        return {"Cookie": f"catan_seat_{self.game_id}={self.token}"}


class Api:
    """One TestClient; each call says which seat it acts as (cookies are sent explicitly)."""

    def __init__(self, client: TestClient) -> None:
        self.c = client

    def create(self, *names: str) -> list[Seat]:
        r = self.c.post("/api/games", json={"players": list(names)})
        assert r.status_code == 201, r.text
        body = r.json()
        return [Seat(body["gameId"], s["playerId"], s["joinUrl"].split("#", 1)[1]) for s in body["seats"]]

    def view(self, seat: Seat) -> dict[str, Any]:
        r = self.c.get(f"/api/games/{seat.game_id}/view", headers=seat.cookie)
        assert r.status_code == 200, r.text
        return r.json()  # type: ignore[no-any-return]

    def act(self, seat: Seat, action: dict[str, Any], version: int | None = None) -> Any:
        if version is None:
            version = self.view(seat)["version"]
        return self.c.post(
            f"/api/games/{seat.game_id}/actions",
            json={"expectedVersion": version, "action": action},
            headers=seat.cookie,
        )


@pytest.fixture
def db_path(tmp_path: Path) -> str:
    return str(tmp_path / "catan.db")


@pytest.fixture
def client(db_path: str) -> Iterator[TestClient]:
    app = create_app(Settings(db_path=db_path))
    with TestClient(app, base_url=ORIGIN) as c:
        yield c


@pytest.fixture
def api(client: TestClient) -> Api:
    return Api(client)
