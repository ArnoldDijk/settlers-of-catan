"""Helpers for agents: read the public board out of a PlayerView."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..board import TERRAIN_RESOURCE, pips
from ..board import TOPOLOGY as T


@dataclass(slots=True)
class BoardInfo:
    me: str
    hex_resource: list[str | None]
    hex_pips: list[int]
    robber: int
    owner_at: dict[int, str]  # vertex -> player id
    kind_at: dict[int, str]  # vertex -> settlement/city
    road_owner: dict[int, str]  # edge -> player id
    harbor_at: dict[int, str]  # vertex -> harbor kind

    @classmethod
    def from_view(cls, view: dict[str, Any]) -> BoardInfo:
        tiles = view["board"]["tiles"]
        res: list[str | None] = [None] * len(T.hexes)
        pp = [0] * len(T.hexes)
        for t in tiles:
            h = T.hex_index[(t["q"], t["r"])]
            res[h] = TERRAIN_RESOURCE[t["terrain"]]
            pp[h] = pips(t["number"])
        rb = view["board"]["robber"]
        harbors: dict[int, str] = {}
        for hb in view["board"]["harbors"]:
            for k in (hb["edge"], (hb["edge"] + 1) % 6):
                harbors[T.vertex_at(hb["q"], hb["r"], k)] = hb["kind"]
        owner_at, kind_at = {}, {}
        for b in view["buildings"]:
            v = T.vertex_at(**b["at"])
            owner_at[v] = b["owner"]
            kind_at[v] = b["kind"]
        roads = {T.edge_at(**r["at"]): r["owner"] for r in view["roads"]}
        return cls(
            view["viewerId"], res, pp, T.hex_index[(rb["q"], rb["r"])], owner_at, kind_at, roads, harbors
        )

    def vertex_value(self, v: int) -> float:
        """Expected production (pips) of a vertex, with a small bonus for resource variety and harbors."""
        total = sum(self.hex_pips[h] for h in T.vertex_hexes[v] if h != self.robber)
        kinds = {self.hex_resource[h] for h in T.vertex_hexes[v] if self.hex_resource[h]}
        return total + 0.5 * len(kinds) + (0.8 if v in self.harbor_at else 0.0)

    def open_spot(self, v: int) -> bool:
        return v not in self.owner_at and all(n not in self.owner_at for n in T.vertex_neighbours[v])

    def road_value(self, e: int) -> float:
        """Best open settlement spot a road on `e` leads to (at its far end or one step further)."""
        best = 0.0
        for v in T.edge_vertices[e]:
            if self.open_spot(v):
                best = max(best, self.vertex_value(v))
            for n in T.vertex_neighbours[v]:
                if self.open_spot(n):
                    best = max(best, 0.6 * self.vertex_value(n))
        return best
