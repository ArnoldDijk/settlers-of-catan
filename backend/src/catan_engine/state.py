"""Mutable game state. Only the engine (engine.py / rules/) may change it."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

from .board import RESOURCES, Layout

DEV_CARDS: tuple[str, ...] = ("knight", "roadBuilding", "yearOfPlenty", "monopoly", "victoryPoint")
DEV_DECK: tuple[str, ...] = (
    ("knight",) * 14
    + ("roadBuilding",) * 2
    + ("yearOfPlenty",) * 2
    + ("monopoly",) * 2
    + ("victoryPoint",) * 5
)
PLAYER_COLORS: tuple[str, ...] = ("red", "blue", "orange", "white")

COSTS: dict[str, dict[str, int]] = {
    "road": {"brick": 1, "lumber": 1},
    "settlement": {"brick": 1, "lumber": 1, "wool": 1, "grain": 1},
    "city": {"grain": 2, "ore": 3},
    "devCard": {"wool": 1, "grain": 1, "ore": 1},
}
PIECES = {"roads": 15, "settlements": 5, "cities": 4}
BANK_PER_RESOURCE = 19
WIN_POINTS = 10

Phase = Literal["setup", "playing", "finished"]
Step = Literal[
    "setupSettlement", "setupRoad", "roll", "discard", "moveRobber", "action", "roadBuilding", "finished"
]


def empty_resources() -> dict[str, int]:
    return dict.fromkeys(RESOURCES, 0)


def empty_dev_cards() -> dict[str, int]:
    return dict.fromkeys(DEV_CARDS, 0)


@dataclass(slots=True)
class Player:
    id: str
    name: str
    color: str
    resources: dict[str, int] = field(default_factory=empty_resources)
    dev_cards: dict[str, int] = field(default_factory=empty_dev_cards)  # playable
    new_dev_cards: dict[str, int] = field(default_factory=empty_dev_cards)  # bought this turn
    played_dev_cards: dict[str, int] = field(default_factory=empty_dev_cards)  # face up, public
    knights_played: int = 0
    roads_left: int = PIECES["roads"]
    settlements_left: int = PIECES["settlements"]
    cities_left: int = PIECES["cities"]

    def card_count(self) -> int:
        return sum(self.resources.values())

    def dev_card_count(self) -> int:
        return sum(self.dev_cards.values()) + sum(self.new_dev_cards.values())

    def can_pay(self, cost: dict[str, int]) -> bool:
        return all(self.resources[r] >= n for r, n in cost.items())


@dataclass(slots=True)
class TradeOffer:
    """Open offer from the current player. `give` goes from offerer to the accepter."""

    offerer: str
    give: dict[str, int]
    get: dict[str, int]
    to: list[str]
    responses: dict[str, bool | None]  # addressee -> accepted? (None = not answered yet)


@dataclass(frozen=True, slots=True)
class Config:
    """Rule options. Defaults are the official rules."""

    win_points: int = WIN_POINTS
    #: Cap on trade offers per turn (None = unlimited). Simulations set this so bots can't loop.
    trade_offers_per_turn: int | None = None


@dataclass(slots=True)
class GameState:
    id: str
    layout: Layout
    players: list[Player]
    rng: random.Random
    config: Config = field(default_factory=Config)
    phase: Phase = "setup"
    step: Step = "setupSettlement"
    current: int = 0  # index into players
    turn_number: int = 0  # 0 during setup, then 1, 2, … (one per player turn)
    setup_index: int = 0  # position in the snake order
    robber: int = 0  # land hex index
    buildings: dict[int, tuple[int, str]] = field(default_factory=dict)  # vertex -> (player, kind)
    roads: dict[int, int] = field(default_factory=dict)  # edge -> player
    bank: dict[str, int] = field(default_factory=lambda: dict.fromkeys(RESOURCES, BANK_PER_RESOURCE))
    dev_deck: list[str] = field(default_factory=list)  # hidden order; draw from the end
    dice: tuple[int, int] | None = None
    dev_played_this_turn: bool = False
    pending_discards: dict[int, int] = field(default_factory=dict)  # player -> cards still to discard
    return_step: Step = "action"  # where to go after moveRobber / roadBuilding
    road_building_left: int = 0
    last_setup_vertex: int | None = None
    trade: TradeOffer | None = None
    trade_offers_this_turn: int = 0
    longest_road: int | None = None  # player index
    largest_army: int | None = None
    winner: int | None = None

    def player_index(self, player_id: str) -> int:
        for i, p in enumerate(self.players):
            if p.id == player_id:
                return i
        raise KeyError(player_id)

    @property
    def current_player(self) -> Player:
        return self.players[self.current]
