"""Game operations shared by the HTTP and WebSocket routes. No rules live here: every change
goes through catan_engine.Game.apply()."""

from __future__ import annotations

import secrets
from typing import Any

from catan_engine import Game, serialize

from . import auth
from .models import PlayerView, Seat
from .store import Store
from .wire import to_wire


def create_game(store: Store, names: list[str]) -> tuple[str, list[Seat]]:
    game_id = auth.new_game_id()
    game = Game.new(names, seed=secrets.randbits(63), game_id=game_id)
    tokens = {p.id: auth.new_token() for p in game.state.players}
    store.create_game(
        game_id, serialize.dump(game.state), {auth.hash_token(t): pid for pid, t in tokens.items()}
    )
    seats = [
        Seat.model_validate(
            {"playerId": p.id, "name": p.name, "color": p.color, "joinUrl": f"/join#{tokens[p.id]}"}
        )
        for p in game.state.players
    ]
    return game_id, seats


def load_game(store: Store, game_id: str) -> tuple[Game, int] | None:
    row = store.load(game_id)
    if row is None:
        return None
    state, version = row
    return Game(serialize.load(state)), version


def player_view(game: Game, player_id: str, version: int) -> PlayerView:
    """The only way game data leaves the server: the engine's projection, validated against the
    PlayerView allowlist model."""
    data: dict[str, Any] = game.view(player_id)
    data["version"] = version
    data["legalActions"] = [to_wire(a) for a in game.legal_actions(player_id)]
    return PlayerView.model_validate(data, strict=False)
