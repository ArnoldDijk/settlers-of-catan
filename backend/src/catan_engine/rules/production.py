"""Resource production after a dice roll, and the second setup settlement."""

from __future__ import annotations

from ..board import RESOURCES, TERRAIN_RESOURCE
from ..board import TOPOLOGY as T
from ..state import GameState


def produce(s: GameState, total: int) -> None:
    """Pay out every tile with `total`, except the robber's. If the bank cannot pay everyone
    for a resource, nobody gets it — unless only one player is owed, who gets what is left."""
    owed: dict[str, dict[int, int]] = {r: {} for r in RESOURCES}
    for h, number in enumerate(s.layout.numbers):
        if number != total or h == s.robber:
            continue
        res = TERRAIN_RESOURCE[s.layout.terrains[h]]
        if res is None:
            continue
        for v in T.hex_vertices[h]:
            b = s.buildings.get(v)
            if b is not None:
                p, kind = b
                owed[res][p] = owed[res].get(p, 0) + (2 if kind == "city" else 1)
    for res, owed_to in owed.items():
        need = sum(owed_to.values())
        if need == 0:
            continue
        payout = owed_to
        if need > s.bank[res]:
            if len(owed_to) != 1:
                continue
            (p,) = owed_to
            payout = {p: s.bank[res]}
        for p, n in payout.items():
            s.players[p].resources[res] += n
            s.bank[res] -= n


def setup_income(s: GameState, player: int, vertex: int) -> None:
    """Second setup settlement: one card per adjacent producing tile."""
    for h in T.vertex_hexes[vertex]:
        res = TERRAIN_RESOURCE[s.layout.terrains[h]]
        if res is not None and s.bank[res] > 0:
            s.players[player].resources[res] += 1
            s.bank[res] -= 1
