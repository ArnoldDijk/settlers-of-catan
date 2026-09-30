"""Full GameState <-> JSON (server storage and replays). Never send this to a player:
it contains every hand, the deck order and the RNG state. Use projection.to_player_view."""

from __future__ import annotations

import random
from typing import Any

from .board import HarborSpec, Layout
from .state import Config, GameState, Player, TradeOffer

FORMAT_VERSION = 1


def dump(s: GameState) -> dict[str, Any]:
    version, internal, gauss = s.rng.getstate()
    return {
        "format": FORMAT_VERSION,
        "id": s.id,
        "layout": {
            "terrains": list(s.layout.terrains),
            "numbers": list(s.layout.numbers),
            "harbors": [{"q": h.q, "r": h.r, "edge": h.edge, "kind": h.kind} for h in s.layout.harbors],
        },
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "color": p.color,
                "resources": p.resources,
                "devCards": p.dev_cards,
                "newDevCards": p.new_dev_cards,
                "playedDevCards": p.played_dev_cards,
                "knightsPlayed": p.knights_played,
                "roadsLeft": p.roads_left,
                "settlementsLeft": p.settlements_left,
                "citiesLeft": p.cities_left,
            }
            for p in s.players
        ],
        "rng": [version, list(internal), gauss],
        "config": {"winPoints": s.config.win_points, "tradeOffersPerTurn": s.config.trade_offers_per_turn},
        "phase": s.phase,
        "step": s.step,
        "current": s.current,
        "turnNumber": s.turn_number,
        "setupIndex": s.setup_index,
        "robber": s.robber,
        "buildings": [[v, p, kind] for v, (p, kind) in sorted(s.buildings.items())],
        "roads": [[e, p] for e, p in sorted(s.roads.items())],
        "bank": s.bank,
        "devDeck": s.dev_deck,
        "dice": list(s.dice) if s.dice else None,
        "devPlayedThisTurn": s.dev_played_this_turn,
        "pendingDiscards": [[p, n] for p, n in sorted(s.pending_discards.items())],
        "returnStep": s.return_step,
        "roadBuildingLeft": s.road_building_left,
        "lastSetupVertex": s.last_setup_vertex,
        "trade": None
        if s.trade is None
        else {
            "offerer": s.trade.offerer,
            "give": s.trade.give,
            "get": s.trade.get,
            "to": s.trade.to,
            "responses": s.trade.responses,
        },
        "tradeOffersThisTurn": s.trade_offers_this_turn,
        "longestRoad": s.longest_road,
        "largestArmy": s.largest_army,
        "winner": s.winner,
    }


def load(d: dict[str, Any]) -> GameState:
    if d.get("format") != FORMAT_VERSION:
        raise ValueError(f"unsupported state format: {d.get('format')!r}")
    rng = random.Random()
    version, internal, gauss = d["rng"]
    rng.setstate((version, tuple(internal), gauss))
    lay = d["layout"]
    return GameState(
        id=d["id"],
        layout=Layout(
            terrains=tuple(lay["terrains"]),
            numbers=tuple(lay["numbers"]),
            harbors=tuple(HarborSpec(**h) for h in lay["harbors"]),
        ),
        players=[
            Player(
                id=p["id"],
                name=p["name"],
                color=p["color"],
                resources=dict(p["resources"]),
                dev_cards=dict(p["devCards"]),
                new_dev_cards=dict(p["newDevCards"]),
                played_dev_cards=dict(p["playedDevCards"]),
                knights_played=p["knightsPlayed"],
                roads_left=p["roadsLeft"],
                settlements_left=p["settlementsLeft"],
                cities_left=p["citiesLeft"],
            )
            for p in d["players"]
        ],
        rng=rng,
        config=Config(
            win_points=d["config"]["winPoints"], trade_offers_per_turn=d["config"]["tradeOffersPerTurn"]
        ),
        phase=d["phase"],
        step=d["step"],
        current=d["current"],
        turn_number=d["turnNumber"],
        setup_index=d["setupIndex"],
        robber=d["robber"],
        buildings={v: (p, kind) for v, p, kind in d["buildings"]},
        roads={e: p for e, p in d["roads"]},
        bank=dict(d["bank"]),
        dev_deck=list(d["devDeck"]),
        dice=(d["dice"][0], d["dice"][1]) if d["dice"] else None,
        dev_played_this_turn=d["devPlayedThisTurn"],
        pending_discards={p: n for p, n in d["pendingDiscards"]},
        return_step=d["returnStep"],
        road_building_left=d["roadBuildingLeft"],
        last_setup_vertex=d["lastSetupVertex"],
        trade=None if d["trade"] is None else TradeOffer(**d["trade"]),
        trade_offers_this_turn=d["tradeOffersThisTurn"],
        longest_road=d["longestRoad"],
        largest_army=d["largestArmy"],
        winner=d["winner"],
    )
