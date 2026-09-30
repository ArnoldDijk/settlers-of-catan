"""Request dependencies: the store, and the authenticated seat for a game."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, WebSocket

from .. import auth
from ..store import Store


@dataclass(frozen=True, slots=True)
class SeatAuth:
    game_id: str
    player_id: str


def store(request: Request) -> Store:
    s: Store = request.app.state.store
    return s


def check_game_id(game_id: str) -> None:
    if not auth.GAME_ID.match(game_id):
        raise HTTPException(404, detail={"code": "gameNotFound", "detail": "Unknown game"})


def resolve_seat(st: Store, game_id: str, cookies: dict[str, str]) -> SeatAuth:
    """401 without a valid seat cookie; 403 if the cookie belongs to another game."""
    check_game_id(game_id)
    token = cookies.get(auth.cookie_name(game_id))
    if not token or len(token) > 100:
        raise HTTPException(401, detail={"code": "notJoined", "detail": "Join the game first"})
    seat = st.seat(auth.hash_token(token))
    if seat is None:
        raise HTTPException(401, detail={"code": "notJoined", "detail": "Join the game first"})
    if seat[0] != game_id:
        raise HTTPException(403, detail={"code": "wrongGame", "detail": "This seat belongs to another game"})
    return SeatAuth(game_id, seat[1])


def seat(game_id: str, request: Request) -> SeatAuth:
    return resolve_seat(store(request), game_id, dict(request.cookies))


def ws_seat(game_id: str, ws: WebSocket) -> SeatAuth:
    return resolve_seat(ws.app.state.store, game_id, dict(ws.cookies))
