"""HTTP routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from catan_engine import RuleError, serialize

from .. import auth, service
from ..models import (
    ActionRequest,
    CreateGameRequest,
    CreateGameResponse,
    ErrorBody,
    JoinRequest,
    JoinResponse,
    PlayerView,
)
from ..store import Store, VersionConflict
from ..wire import BadReference, to_engine
from .deps import SeatAuth, seat, store

router = APIRouter(prefix="/api")
ERRORS: dict[int | str, dict[str, object]] = {
    401: {"model": ErrorBody}, 403: {"model": ErrorBody}, 404: {"model": ErrorBody},
    409: {"model": ErrorBody}, 422: {"model": ErrorBody},
}  # fmt: skip


def _error(status: int, code: str, detail: str) -> HTTPException:
    return HTTPException(status, detail={"code": code, "detail": detail})


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/games", status_code=201)
def create_game(body: CreateGameRequest, st: Annotated[Store, Depends(store)]) -> CreateGameResponse:
    game_id, seats = service.create_game(st, body.players)
    return CreateGameResponse(gameId=game_id, seats=seats)


@router.post("/join", responses=ERRORS)
def join(
    body: JoinRequest, request: Request, response: Response, st: Annotated[Store, Depends(store)]
) -> JoinResponse:
    found = st.seat(auth.hash_token(body.token))
    if found is None:
        raise _error(404, "invalidToken", "This join link is not valid")
    game_id, player_id = found
    settings = request.app.state.settings
    response.set_cookie(
        auth.cookie_name(game_id),
        body.token,
        max_age=settings.cookie_max_age,
        path="/api",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="strict",
    )
    return JoinResponse(gameId=game_id, playerId=player_id)


@router.get("/games/{game_id}/view", responses=ERRORS)
def get_view(
    game_id: str, me: Annotated[SeatAuth, Depends(seat)], st: Annotated[Store, Depends(store)]
) -> PlayerView:
    loaded = service.load_game(st, me.game_id)
    if loaded is None:
        raise _error(404, "gameNotFound", "Unknown game")
    game, version = loaded
    return service.player_view(game, me.player_id, version)


@router.post("/games/{game_id}/actions", responses=ERRORS)
async def act(
    game_id: str,
    body: ActionRequest,
    request: Request,
    me: Annotated[SeatAuth, Depends(seat)],
    st: Annotated[Store, Depends(store)],
) -> PlayerView:
    # Load, apply and save run without awaiting in between, so actions on one game never interleave.
    loaded = service.load_game(st, me.game_id)
    if loaded is None:
        raise _error(404, "gameNotFound", "Unknown game")
    game, version = loaded
    if body.expectedVersion != version:
        raise _error(409, "staleVersion", "The game changed; reload your view")
    try:
        game.apply(me.player_id, to_engine(body.action))
    except BadReference as err:
        raise _error(422, "badReference", str(err)) from None
    except RuleError as err:
        raise _error(403 if err.code == "notYourTurn" else 422, err.code, "Not allowed right now") from None
    try:
        new_version = st.save(me.game_id, serialize.dump(game.state), version)
    except VersionConflict:
        raise _error(409, "staleVersion", "The game changed; reload your view") from None
    await request.app.state.hub.broadcast(
        me.game_id, lambda pid: service.player_view(game, pid, new_version).model_dump(mode="json")
    )
    return service.player_view(game, me.player_id, new_version)
