"""Shared helpers: build positions directly so each rule can be tested in isolation."""

from __future__ import annotations

import random
from collections.abc import Iterable

import pytest

from catan_engine import Game
from catan_engine.board import TOPOLOGY as T
from catan_engine.state import BANK_PER_RESOURCE, Config


class FixedDice(random.Random):
    """RNG whose dice rolls come from a script; everything else is a normal seeded RNG."""

    def __init__(self, rolls: Iterable[int], seed: int = 0) -> None:
        super().__init__(seed)
        self._rolls = list(rolls)

    def randint(self, a: int, b: int) -> int:
        return self._rolls.pop(0) if self._rolls else super().randint(a, b)


def V(q: int, r: int, corner: int) -> int:
    return T.vertex_at(q, r, corner)


def E(q: int, r: int, edge: int) -> int:
    return T.edge_at(q, r, edge)


def H(q: int, r: int) -> int:
    return T.hex_index[(q, r)]


def playing(n: int = 3, *, config: Config | None = None, seed: int = 1) -> Game:
    """A game on the beginner board, past setup, player 1 in the action step, empty board."""
    g = Game.new(["Anna", "Bram", "Carla", "Daan"][:n], seed, layout="beginner", config=config)
    s = g.state
    s.phase, s.step, s.current, s.turn_number, s.setup_index = "playing", "action", 0, 1, 2 * n
    return g


def give(g: Game, player: int, **cards: int) -> None:
    """Move cards from the bank to a player (keeps the 19-per-resource total intact)."""
    for r, k in cards.items():
        g.state.bank[r] -= k
        g.state.players[player].resources[r] += k


def place(g: Game, player: int, *, settlements: Iterable[int] = (), cities: Iterable[int] = (),
          roads: Iterable[int] = ()) -> None:  # fmt: skip
    s = g.state
    for v in settlements:
        s.buildings[v] = (player, "settlement")
        s.players[player].settlements_left -= 1
    for v in cities:
        s.buildings[v] = (player, "city")
        s.players[player].cities_left -= 1
    for e in roads:
        s.roads[e] = player
        s.players[player].roads_left -= 1


def assert_bank_conserved(g: Game) -> None:
    s = g.state
    for r, left in s.bank.items():
        assert left + sum(p.resources[r] for p in s.players) == BANK_PER_RESOURCE, r


@pytest.fixture
def game3() -> Game:
    return playing(3)
