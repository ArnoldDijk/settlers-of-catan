"""Actions a player can take. Plain frozen dataclasses; `type` tags them on the wire.

Board locations are integer indices (see board.TOPOLOGY): `vertex`, `edge`, `hex`.
Resource bundles are tuples of (resource, count) pairs so actions stay hashable.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, ClassVar

Bundle = tuple[tuple[str, int], ...]


def bundle(d: dict[str, int]) -> Bundle:
    return tuple(sorted((r, n) for r, n in d.items() if n > 0))


def unbundle(b: Bundle) -> dict[str, int]:
    return dict(b)


@dataclass(frozen=True, slots=True)
class PlaceSetupSettlement:
    type: ClassVar[str] = "placeSetupSettlement"
    vertex: int


@dataclass(frozen=True, slots=True)
class PlaceSetupRoad:
    type: ClassVar[str] = "placeSetupRoad"
    edge: int


@dataclass(frozen=True, slots=True)
class Roll:
    type: ClassVar[str] = "roll"


@dataclass(frozen=True, slots=True)
class Discard:
    type: ClassVar[str] = "discard"
    resources: Bundle


@dataclass(frozen=True, slots=True)
class MoveRobber:
    type: ClassVar[str] = "moveRobber"
    hex: int
    steal_from: str | None = None


@dataclass(frozen=True, slots=True)
class BuildRoad:
    type: ClassVar[str] = "buildRoad"
    edge: int


@dataclass(frozen=True, slots=True)
class BuildSettlement:
    type: ClassVar[str] = "buildSettlement"
    vertex: int


@dataclass(frozen=True, slots=True)
class BuildCity:
    type: ClassVar[str] = "buildCity"
    vertex: int


@dataclass(frozen=True, slots=True)
class BuyDevCard:
    type: ClassVar[str] = "buyDevCard"


@dataclass(frozen=True, slots=True)
class PlayKnight:
    type: ClassVar[str] = "playKnight"


@dataclass(frozen=True, slots=True)
class PlayRoadBuilding:
    type: ClassVar[str] = "playRoadBuilding"


@dataclass(frozen=True, slots=True)
class PlayYearOfPlenty:
    type: ClassVar[str] = "playYearOfPlenty"
    resources: Bundle  # exactly 2 cards


@dataclass(frozen=True, slots=True)
class PlayMonopoly:
    type: ClassVar[str] = "playMonopoly"
    resource: str


@dataclass(frozen=True, slots=True)
class BankTrade:
    type: ClassVar[str] = "bankTrade"
    give: str  # gives `rate` of these (rate from harbors: 4, 3 or 2)
    get: str  # receives one


@dataclass(frozen=True, slots=True)
class OfferTrade:
    type: ClassVar[str] = "offerTrade"
    give: Bundle
    get: Bundle
    to: tuple[str, ...]  # addressees (player ids)


@dataclass(frozen=True, slots=True)
class RespondTrade:
    type: ClassVar[str] = "respondTrade"
    accept: bool


@dataclass(frozen=True, slots=True)
class ConfirmTrade:
    type: ClassVar[str] = "confirmTrade"
    with_player: str


@dataclass(frozen=True, slots=True)
class CancelTrade:
    type: ClassVar[str] = "cancelTrade"


@dataclass(frozen=True, slots=True)
class EndTurn:
    type: ClassVar[str] = "endTurn"


Action = (
    PlaceSetupSettlement | PlaceSetupRoad | Roll | Discard | MoveRobber | BuildRoad | BuildSettlement
    | BuildCity | BuyDevCard | PlayKnight | PlayRoadBuilding | PlayYearOfPlenty | PlayMonopoly | BankTrade
    | OfferTrade | RespondTrade | ConfirmTrade | CancelTrade | EndTurn
)  # fmt: skip

_ACTION_CLASSES: tuple[type[Action], ...] = (
    PlaceSetupSettlement, PlaceSetupRoad, Roll, Discard, MoveRobber, BuildRoad, BuildSettlement, BuildCity,
    BuyDevCard, PlayKnight, PlayRoadBuilding, PlayYearOfPlenty, PlayMonopoly, BankTrade, OfferTrade,
    RespondTrade, ConfirmTrade, CancelTrade, EndTurn,
)  # fmt: skip
ACTION_TYPES: dict[str, type[Action]] = {cls.type: cls for cls in _ACTION_CLASSES}


def action_to_dict(a: Action) -> dict[str, Any]:
    """Internal (index-based) JSON form, used for replays and simulation logs."""
    out: dict[str, Any] = {"type": a.type}
    for f in fields(a):
        name = f.name
        value = getattr(a, name)
        if name in ("resources", "give", "get") and isinstance(value, tuple):
            value = unbundle(value)
        elif isinstance(value, tuple):
            value = list(value)
        out[name] = value
    return out


def action_from_dict(d: dict[str, Any]) -> Action:
    cls = ACTION_TYPES[d["type"]]
    kwargs: dict[str, Any] = {}
    for f in fields(cls):
        name = f.name
        if name not in d:
            continue
        value = d[name]
        if name in ("resources", "give", "get") and isinstance(value, dict):
            value = bundle(value)
        elif isinstance(value, list):
            value = tuple(value)
        kwargs[name] = value
    return cls(**kwargs)
