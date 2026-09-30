"""A simple heuristic bot: grab strong spots, build cities, then settlements, dev cards, roads."""

from __future__ import annotations

import random
from typing import Any

from .. import actions as A
from ..board import RESOURCES
from ..board import TOPOLOGY as T
from ..state import COSTS
from .boardinfo import BoardInfo


class GreedyAgent:
    name = "greedy"

    def choose(self, view: dict[str, Any], legal: list[A.Action], rng: random.Random) -> A.Action:
        info = BoardInfo.from_view(view)
        hand: dict[str, int] = view["hand"]["resources"]
        by_type: dict[str, list[A.Action]] = {}
        for a in legal:
            by_type.setdefault(a.type, []).append(a)

        def best(kind: str, score: Any) -> A.Action | None:
            opts = by_type.get(kind)
            return max(opts, key=score) if opts else None

        step = view["turn"]["step"]
        if step == "setupSettlement":
            return (
                best("placeSetupSettlement", lambda a: info.vertex_value(a.vertex) + rng.random() * 0.01)
                or legal[0]
            )
        if step in ("setupRoad", "roadBuilding"):
            kind = "placeSetupRoad" if step == "setupRoad" else "buildRoad"
            return best(kind, lambda a: info.road_value(a.edge) + rng.random() * 0.01) or legal[0]
        if step == "discard":
            return self._discard(hand, by_type["discard"])
        if step == "moveRobber":
            return self._robber(view, info, by_type["moveRobber"])

        if "respondTrade" in by_type:
            return self._respond(view, hand, by_type["respondTrade"])
        if "confirmTrade" in by_type:
            return by_type["confirmTrade"][0]
        if "cancelTrade" in by_type and len(legal) == 1:
            return legal[0]

        if step == "roll":
            if "playKnight" in by_type and self._robber_on_me(info):
                return by_type["playKnight"][0]
            return by_type.get("roll", legal)[0]

        # Main action step.
        for kind, score in (
            ("buildCity", lambda a: info.vertex_value(a.vertex)),
            ("buildSettlement", lambda a: info.vertex_value(a.vertex)),
        ):
            choice = best(kind, score)
            if choice is not None:
                return choice
        if "playKnight" in by_type and self._robber_on_me(info):
            return by_type["playKnight"][0]
        target = self._target(view, info)
        missing = {r: n - hand.get(r, 0) for r, n in COSTS[target].items() if hand.get(r, 0) < n}
        if "playYearOfPlenty" in by_type and missing:
            want = [r for r, n in missing.items() for _ in range(n)][:2]
            want += [max(RESOURCES, key=lambda r: -hand[r])] * (2 - len(want))
            wanted = A.bundle({r: want.count(r) for r in set(want)})
            for a in by_type["playYearOfPlenty"]:
                if isinstance(a, A.PlayYearOfPlenty) and a.resources == wanted:
                    return a
        if "playRoadBuilding" in by_type and target == "road":
            return by_type["playRoadBuilding"][0]
        if target == "road":
            road = best("buildRoad", lambda a: info.road_value(a.edge))
            if road is not None:
                return road
        if "buyDevCard" in by_type and target in ("devCard", "road"):
            return by_type["buyDevCard"][0]
        if missing:
            surplus = {r: hand[r] - COSTS[target].get(r, 0) for r in RESOURCES}
            for a in by_type.get("bankTrade", []):
                if not isinstance(a, A.BankTrade):
                    continue
                rate = 4
                for vv, kind in info.harbor_at.items():
                    if info.owner_at.get(vv) == info.me:
                        rate = min(rate, 2 if kind == a.give else 3 if kind == "any" else 4)
                if a.get in missing and surplus[a.give] >= rate:
                    return a
            for a in by_type.get("offerTrade", []):
                if not isinstance(a, A.OfferTrade):
                    continue
                (give, _), (get, _) = a.give[0], a.get[0]
                if get in missing and surplus[give] >= 2:
                    return a
        return by_type.get("endTurn", legal)[0]

    @staticmethod
    def _robber_on_me(info: BoardInfo) -> bool:
        return any(info.owner_at.get(v) == info.me for v in T.hex_vertices[info.robber])

    @staticmethod
    def _target(view: dict[str, Any], info: BoardInfo) -> str:
        me = next(p for p in view["players"] if p["id"] == info.me)
        mine = [v for v, o in info.owner_at.items() if o == info.me]
        if me["piecesLeft"]["cities"] and any(info.kind_at[v] == "settlement" for v in mine):
            return "city"
        own_roads = {e for e, o in info.road_owner.items() if o == info.me}
        reachable = any(info.open_spot(v) for e in own_roads for v in T.edge_vertices[e])
        if me["piecesLeft"]["settlements"] and reachable:
            return "settlement"
        if me["piecesLeft"]["roads"]:
            return "road"
        return "devCard"

    @staticmethod
    def _discard(hand: dict[str, int], options: list[A.Action]) -> A.Action:
        # Throw away what we hold most of.
        def weight(a: A.Action) -> int:
            return sum(hand[r] * n for r, n in a.resources) if isinstance(a, A.Discard) else -1

        return max(options, key=weight)

    @staticmethod
    def _robber(view: dict[str, Any], info: BoardInfo, options: list[A.Action]) -> A.Action:
        points = {p["id"]: p["victoryPoints"] for p in view["players"]}
        cards = {p["id"]: p["resourceCount"] for p in view["players"]}

        def score(a: A.Action) -> float:
            if not isinstance(a, A.MoveRobber):
                return float("-inf")
            s = 0.0
            for v in T.hex_vertices[a.hex]:
                owner = info.owner_at.get(v)
                if owner is None:
                    continue
                weight = 2 if info.kind_at[v] == "city" else 1
                s += (-10 if owner == info.me else points[owner] + 1) * weight * info.hex_pips[a.hex]
            return s + (cards.get(a.steal_from, 0) * 0.1 if a.steal_from else 0)

        return max(options, key=score)

    def _respond(self, view: dict[str, Any], hand: dict[str, int], options: list[A.Action]) -> A.Action:
        t = view["trade"]
        receive, pay = t["give"], t["get"]
        needed = {r for c in ("city", "settlement") for r in COSTS[c] if hand[r] < COSTS[c][r]}
        spare = all(hand[r] - n >= 1 for r, n in pay.items())
        accept = spare and any(r in needed for r in receive)
        for a in options:
            if isinstance(a, A.RespondTrade) and a.accept == accept:
                return a
        return options[-1]
