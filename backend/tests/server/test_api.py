import json
import random
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from catan_server.config import Settings
from catan_server.main import create_app
from tests.server.conftest import ORIGIN, Api


def test_health(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_create_game_returns_one_join_link_per_seat(api: Api) -> None:
    seats = api.create("Anna", "Bram", "Carla")
    assert [s.player_id for s in seats] == ["p1", "p2", "p3"]
    assert len({s.token for s in seats}) == 3
    assert all(len(s.token) >= 40 for s in seats)


def test_tokens_are_stored_only_as_hashes(api: Api, db_path: str) -> None:
    seats = api.create("Anna", "Bram")
    dump = "\n".join(sqlite3.connect(db_path).iterdump())
    assert all(s.token not in dump for s in seats)


def test_create_game_validation(client: TestClient) -> None:
    for players in ([], ["solo"], ["a", "b", "c", "d", "e"], ["", "b"], ["x" * 25, "b"]):
        assert client.post("/api/games", json={"players": players}).status_code == 422


def test_join_sets_a_locked_down_cookie(api: Api, client: TestClient) -> None:
    seat = api.create("Anna", "Bram")[1]
    r = client.post("/api/join", json={"token": seat.token})
    assert r.status_code == 200
    assert r.json() == {"gameId": seat.game_id, "playerId": "p2"}
    cookie = r.headers["set-cookie"]
    assert cookie.startswith(f"catan_seat_{seat.game_id}={seat.token};")
    for flag in ("HttpOnly", "Secure", "SameSite=strict", "Path=/api"):
        assert flag.lower() in cookie.lower()


def test_join_with_a_bad_token(client: TestClient) -> None:
    assert client.post("/api/join", json={"token": "x" * 43}).status_code == 404
    assert client.post("/api/join", json={"token": "bad token!"}).status_code == 422


def test_view_requires_the_seat_cookie(api: Api, client: TestClient) -> None:
    seat = api.create("Anna", "Bram")[0]
    r = client.get(f"/api/games/{seat.game_id}/view")
    assert r.status_code == 401
    assert r.json()["detail"]["code"] == "notJoined"
    forged = {"Cookie": f"catan_seat_{seat.game_id}={'y' * 43}"}
    r = client.get(f"/api/games/{seat.game_id}/view", headers=forged)
    assert r.status_code == 401


def test_a_seat_cookie_does_not_work_for_another_game(api: Api, client: TestClient) -> None:
    a = api.create("Anna", "Bram")[0]
    b = api.create("Carla", "Daan")[0]
    r = client.get(f"/api/games/{b.game_id}/view", headers={"Cookie": f"catan_seat_{b.game_id}={a.token}"})
    assert r.status_code == 403
    assert r.json()["detail"]["code"] == "wrongGame"


def test_view_contains_only_the_viewers_hand(api: Api) -> None:
    seats = api.create("Anna", "Bram", "Carla")
    for seat in seats:
        view = api.view(seat)
        assert view["viewerId"] == seat.player_id
        text = json.dumps(view)
        assert text.count('"resources"') == 2  # own hand + bank
        assert "devDeck" not in text and "rng" not in text and seat.token not in text
        for p in view["players"]:
            assert "resources" not in p and "devCards" not in p


def test_players_cannot_act_for_each_other(api: Api) -> None:
    p1, p2 = api.create("Anna", "Bram")
    spot = api.view(p1)["legalActions"][0]
    assert api.view(p2)["legalActions"] == []
    r = api.act(p2, spot)
    assert r.status_code == 403
    assert r.json()["detail"]["code"] == "notYourTurn"
    assert api.act(p1, spot).status_code == 200


def test_stale_version_is_rejected(api: Api) -> None:
    p1, _ = api.create("Anna", "Bram")
    view = api.view(p1)
    assert api.act(p1, view["legalActions"][0], version=view["version"]).status_code == 200
    road = api.view(p1)["legalActions"][0]
    r = api.act(p1, road, version=view["version"])  # old version
    assert r.status_code == 409
    assert r.json()["detail"]["code"] == "staleVersion"


def test_rule_violations_and_bad_refs(api: Api) -> None:
    p1, _ = api.create("Anna", "Bram")
    r = api.act(p1, {"type": "roll"})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "wrongStep"
    r = api.act(p1, {"type": "placeSetupSettlement", "at": {"q": 3, "r": 3, "corner": 0}})
    assert r.status_code == 422 and r.json()["detail"]["code"] == "badReference"
    r = api.act(p1, {"type": "hack"})
    assert r.status_code == 422
    r = api.act(p1, {"type": "roll", "extra": 1})
    assert r.status_code == 422


def test_json_content_type_is_required(api: Api, client: TestClient) -> None:
    p1, _ = api.create("Anna", "Bram")
    body = json.dumps({"expectedVersion": 0, "action": api.view(p1)["legalActions"][0]})
    r = client.post(f"/api/games/{p1.game_id}/actions", content=body,
                    headers={**p1.cookie, "Content-Type": "text/plain"})  # fmt: skip
    assert r.status_code == 422


def test_oversized_bodies_are_rejected(client: TestClient) -> None:
    r = client.post("/api/games", content=b"x" * 20_000, headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_unknown_or_malformed_game_ids(api: Api, client: TestClient) -> None:
    seat = api.create("Anna", "Bram")[0]
    assert client.get("/api/games/..%2F..%2Fetc/view", headers=seat.cookie).status_code == 404
    assert client.get("/api/games/nosuchgame123/view").status_code == 401


def test_games_survive_a_restart(db_path: str) -> None:
    app = create_app(Settings(db_path=db_path))
    with TestClient(app, base_url=ORIGIN) as c:
        seat = Api(c).create("Anna", "Bram")[0]
        Api(c).act(seat, Api(c).view(seat)["legalActions"][0])
        before = Api(c).view(seat)
    with TestClient(create_app(Settings(db_path=db_path)), base_url=ORIGIN) as c:
        after = Api(c).view(seat)
    assert after == before
    assert Path(db_path).exists()


def test_a_whole_game_through_the_api(api: Api) -> None:
    """Every legalAction the API lists must be accepted; play until someone wins."""
    rng = random.Random(1)
    seats = {s.player_id: s for s in api.create("Anna", "Bram", "Carla")}
    view = api.view(seats["p1"])
    for _ in range(4000):
        if view["phase"] == "finished":
            break
        turn = view["turn"]
        if view["pendingDiscards"]:
            actor = next(iter(view["pendingDiscards"]))
        elif view["trade"] and any(v is None for v in view["trade"]["responses"].values()):
            actor = next(p for p, v in view["trade"]["responses"].items() if v is None)
        else:
            actor = turn["currentPlayerId"]
        mine = api.view(seats[actor])
        options = mine["legalActions"]
        assert options, f"{actor} has nothing to do in {turn}"
        preferred = [a for a in options if a["type"] in ("buildCity", "buildSettlement", "confirmTrade")]
        no_offers = [a for a in options if a["type"] != "offerTrade"]
        action = rng.choice(preferred or no_offers or options)
        r = api.act(seats[actor], action, version=mine["version"])
        assert r.status_code == 200, (action, r.text)
        view = r.json()
    assert view["phase"] == "finished"
    assert view["winnerId"] in seats
