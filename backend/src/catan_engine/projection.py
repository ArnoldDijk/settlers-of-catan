"""What one player may see. Port of frontend/src/state/playerView.ts, extended with the
engine's turn details. Everything leaving the engine for a player goes through here.

Hidden: other players' resources and development cards, the order of the development deck,
and the RNG. Public: the board, buildings, card *counts*, open trade offers, pending discards.
"""

from __future__ import annotations

from typing import Any

from .board import TOPOLOGY as T
from .rules import scoring
from .state import DEV_CARDS, GameState


def _vertex(v: int) -> dict[str, int]:
    q, r, k = T.vertex_ref[v]
    return {"q": q, "r": r, "corner": k}


def _edge(e: int) -> dict[str, int]:
    q, r, k = T.edge_ref[e]
    return {"q": q, "r": r, "edge": k}


def _hex(h: int) -> dict[str, int]:
    q, r = T.hexes[h]
    return {"q": q, "r": r}


def shared_view(s: GameState) -> dict[str, Any]:
    """Information that is identical for every player."""
    pid = [p.id for p in s.players]
    trade = None
    if s.trade is not None:
        t = s.trade
        trade = {"offerer": t.offerer, "give": dict(t.give), "get": dict(t.get), "to": list(t.to),
                 "responses": dict(t.responses)}  # fmt: skip
    return {
        "phase": s.phase,
        "turn": {"number": s.turn_number, "currentPlayerId": pid[s.current], "step": s.step},
        "dice": list(s.dice) if s.dice else None,
        "board": {
            "tiles": [
                {"q": q, "r": r, "terrain": s.layout.terrains[i], "number": s.layout.numbers[i]}
                for i, (q, r) in enumerate(T.hexes)
            ],
            "harbors": [{"q": h.q, "r": h.r, "edge": h.edge, "kind": h.kind} for h in s.layout.harbors],
            "robber": _hex(s.robber),
        },
        "buildings": [
            {"owner": pid[p], "kind": kind, "at": _vertex(v)} for v, (p, kind) in sorted(s.buildings.items())
        ],
        "roads": [{"owner": pid[p], "at": _edge(e)} for e, p in sorted(s.roads.items())],
        "bank": {"resources": dict(s.bank), "devCardsLeft": len(s.dev_deck)},
        "awards": {
            "longestRoad": None if s.longest_road is None else pid[s.longest_road],
            "largestArmy": None if s.largest_army is None else pid[s.largest_army],
        },
        "winnerId": None if s.winner is None else pid[s.winner],
        "trade": trade,
        "pendingDiscards": {pid[p]: n for p, n in sorted(s.pending_discards.items())},
        "devCardPlayedThisTurn": s.dev_played_this_turn,
        "roadBuildingLeft": s.road_building_left,
    }


def to_player_view(s: GameState, player_id: str) -> dict[str, Any]:
    me = s.players[s.player_index(player_id)]  # KeyError for unknown viewers
    view = shared_view(s)
    view["gameId"] = s.id
    view["viewerId"] = player_id
    view["players"] = [
        {
            "id": p.id,
            "name": p.name,
            "color": p.color,
            "resourceCount": p.card_count(),
            "devCardCount": p.dev_card_count(),
            "knightsPlayed": p.knights_played,
            "playedDevCards": dict(p.played_dev_cards),
            "piecesLeft": {"roads": p.roads_left, "settlements": p.settlements_left, "cities": p.cities_left},
            "victoryPoints": scoring.public_points(s, i),
        }
        for i, p in enumerate(s.players)
    ]
    view["hand"] = {
        "resources": dict(me.resources),
        # All development cards in hand; `newDevCards` is the part bought this turn (not playable yet).
        "devCards": {c: me.dev_cards[c] + me.new_dev_cards[c] for c in DEV_CARDS},
        "newDevCards": dict(me.new_dev_cards),
    }
    return view
