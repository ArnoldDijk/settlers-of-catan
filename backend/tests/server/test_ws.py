import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from tests.server.conftest import ORIGIN, Api


def url(game_id: str) -> str:
    return f"/api/games/{game_id}/ws"


def test_socket_sends_own_view_and_pushes_changes(api: Api, client: TestClient) -> None:
    p1, p2 = api.create("Anna", "Bram")
    with client.websocket_connect(url(p2.game_id), headers={**p2.cookie, "Origin": ORIGIN}) as ws:
        first = ws.receive_json()
        assert first["viewerId"] == "p2"
        assert first["version"] == 0
        api.act(p1, api.view(p1)["legalActions"][0])  # p1 places a settlement
        pushed = ws.receive_json()
        assert pushed["viewerId"] == "p2"  # p2 still gets *their own* view
        assert pushed["version"] == 1
        assert len(pushed["buildings"]) == 1


def test_socket_rejects_other_origins(api: Api, client: TestClient) -> None:
    seat = api.create("Anna", "Bram")[0]
    for origin in ("https://evil.example", None):
        headers = dict(seat.cookie)
        if origin:
            headers["Origin"] = origin
        with (
            pytest.raises(WebSocketDisconnect) as err,
            client.websocket_connect(url(seat.game_id), headers=headers),
        ):
            pass
        assert err.value.code == 1008


def test_socket_requires_the_seat_cookie(api: Api, client: TestClient) -> None:
    seat = api.create("Anna", "Bram")[0]
    with (
        pytest.raises(WebSocketDisconnect) as err,
        client.websocket_connect(url(seat.game_id), headers={"Origin": ORIGIN}),
    ):
        pass
    assert err.value.code == 1008
