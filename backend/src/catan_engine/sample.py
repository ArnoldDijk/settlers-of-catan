"""The sample mid-game position used by the frontend (port of frontend/src/state/sampleState.ts)."""

from __future__ import annotations

import random

from .board import TOPOLOGY as T
from .board import beginner_layout
from .state import GameState, Player, empty_dev_cards


def _hand(lumber: int, brick: int, wool: int, grain: int, ore: int) -> dict[str, int]:
    return {"lumber": lumber, "brick": brick, "wool": wool, "grain": grain, "ore": ore}


def _dev(**cards: int) -> dict[str, int]:
    d = empty_dev_cards()
    d.update(cards)
    return d


def sample_state() -> GameState:
    layout = beginner_layout()
    players = [
        Player("p1", "Anna", "red", _hand(2, 1, 0, 3, 1), _dev(knight=1, victoryPoint=1), knights_played=1),
        Player("p2", "Bram", "blue", _hand(1, 2, 2, 0, 3), _dev(roadBuilding=1), knights_played=3),
        Player("p3", "Carla", "orange", _hand(0, 0, 4, 1, 0), _dev(knight=2, yearOfPlenty=1)),
        Player("p4", "Daan", "white", _hand(3, 2, 1, 2, 0), _dev(monopoly=1), knights_played=1),
    ]
    for p in players:
        p.roads_left, p.settlements_left, p.cities_left = 12, 4, 3
        p.played_dev_cards["knight"] = p.knights_played
    buildings = [
        (0, "city", 0, -1, 0), (0, "settlement", -1, 1, 1), (1, "settlement", 1, -1, 2),
        (1, "city", -2, 2, 0), (2, "settlement", 1, 1, 1), (2, "city", 0, 1, 3),
        (3, "settlement", -2, 0, 5), (3, "city", 0, 2, 1),
    ]  # fmt: skip
    roads = [
        (0, 0, -1, 0), (0, 0, -1, 5), (0, -1, 1, 0), (1, 1, -1, 1), (1, 1, -1, 2), (1, -2, 2, 5),
        (2, 1, 1, 0), (2, 1, 1, 1), (2, 0, 1, 3), (3, -2, 0, 4), (3, -2, 0, 5), (3, 0, 2, 0),
    ]  # fmt: skip
    deck = ["knight"] * 6 + ["roadBuilding", "yearOfPlenty", "monopoly"] + ["victoryPoint"] * 4
    rng = random.Random(2026)
    rng.shuffle(deck)
    return GameState(
        id="demo-001",
        layout=layout,
        players=players,
        rng=rng,
        phase="playing",
        step="action",
        current=1,
        turn_number=14,
        setup_index=8,
        robber=T.hex_index[(2, 0)],
        buildings={T.vertex_at(q, r, k): (p, kind) for p, kind, q, r, k in buildings},
        roads={T.edge_at(q, r, k): p for p, q, r, k in roads},
        bank=_hand(13, 14, 12, 13, 15),
        dev_deck=deck,
        dice=(3, 5),
        largest_army=1,
    )
