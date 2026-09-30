"""Converts between engine actions (integer board indices) and API actions (board refs)."""

from __future__ import annotations

from typing import Any

from catan_engine import actions as A
from catan_engine.board import TOPOLOGY as T

from . import models as M


class BadReference(ValueError):
    """A board ref that isn't on the board."""


def _vertex(ref: M.VertexRef) -> int:
    try:
        return T.vertex_at(ref.q, ref.r, ref.corner)
    except KeyError:
        raise BadReference("not a board corner") from None


def _edge(ref: M.EdgeRef) -> int:
    try:
        return T.edge_at(ref.q, ref.r, ref.edge)
    except KeyError:
        raise BadReference("not a board edge") from None


def _hex(ref: M.HexCoord) -> int:
    try:
        return T.hex_index[(ref.q, ref.r)]
    except KeyError:
        raise BadReference("not a land tile") from None


def _bundle(d: dict[Any, int]) -> A.Bundle:
    return A.bundle({str(k): v for k, v in d.items()})


def to_engine(a: M.Action) -> A.Action:
    match a:
        case M.PlaceSetupSettlement():
            return A.PlaceSetupSettlement(_vertex(a.at))
        case M.PlaceSetupRoad():
            return A.PlaceSetupRoad(_edge(a.at))
        case M.Roll():
            return A.Roll()
        case M.Discard():
            return A.Discard(_bundle(a.resources))
        case M.MoveRobber():
            return A.MoveRobber(_hex(a.to), a.stealFrom)
        case M.BuildRoad():
            return A.BuildRoad(_edge(a.at))
        case M.BuildSettlement():
            return A.BuildSettlement(_vertex(a.at))
        case M.BuildCity():
            return A.BuildCity(_vertex(a.at))
        case M.BuyDevCard():
            return A.BuyDevCard()
        case M.PlayKnight():
            return A.PlayKnight()
        case M.PlayRoadBuilding():
            return A.PlayRoadBuilding()
        case M.PlayYearOfPlenty():
            return A.PlayYearOfPlenty(_bundle(a.resources))
        case M.PlayMonopoly():
            return A.PlayMonopoly(a.resource)
        case M.BankTrade():
            return A.BankTrade(a.give, a.get)
        case M.OfferTrade():
            return A.OfferTrade(_bundle(a.give), _bundle(a.get), tuple(a.to))
        case M.RespondTrade():
            return A.RespondTrade(a.accept)
        case M.ConfirmTrade():
            return A.ConfirmTrade(a.withPlayer)
        case M.CancelTrade():
            return A.CancelTrade()
        case M.EndTurn():
            return A.EndTurn()
    raise BadReference(f"unknown action {a!r}")  # pragma: no cover - the union is exhaustive


def _v(v: int) -> dict[str, int]:
    q, r, k = T.vertex_ref[v]
    return {"q": q, "r": r, "corner": k}


def _e(e: int) -> dict[str, int]:
    q, r, k = T.edge_ref[e]
    return {"q": q, "r": r, "edge": k}


def _h(h: int) -> dict[str, int]:
    q, r = T.hexes[h]
    return {"q": q, "r": r}


def to_wire(a: A.Action) -> dict[str, Any]:
    """Engine action -> API JSON (for legalActions)."""
    match a:
        case A.PlaceSetupSettlement() | A.BuildSettlement() | A.BuildCity():
            return {"type": a.type, "at": _v(a.vertex)}
        case A.PlaceSetupRoad() | A.BuildRoad():
            return {"type": a.type, "at": _e(a.edge)}
        case A.Discard() | A.PlayYearOfPlenty():
            return {"type": a.type, "resources": A.unbundle(a.resources)}
        case A.MoveRobber():
            return {"type": a.type, "to": _h(a.hex), "stealFrom": a.steal_from}
        case A.PlayMonopoly():
            return {"type": a.type, "resource": a.resource}
        case A.BankTrade():
            return {"type": a.type, "give": a.give, "get": a.get}
        case A.OfferTrade():
            return {"type": a.type, "give": A.unbundle(a.give), "get": A.unbundle(a.get), "to": list(a.to)}
        case A.RespondTrade():
            return {"type": a.type, "accept": a.accept}
        case A.ConfirmTrade():
            return {"type": a.type, "withPlayer": a.with_player}
    return {"type": a.type}
