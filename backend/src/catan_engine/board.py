"""Board topology and layouts for the standard 19-tile board.

Coordinates match the frontend (frontend/src/board/geometry.ts): axial pointy-top hexes,
R = 100, centre (x, y) = (173.2 * (q + r/2), 150 * r). Corner k of a hex sits at angle
-90 + 60k degrees; edge k runs from corner k to corner k+1.

Internally every vertex, edge and land hex has an integer index, so rules work on ints.
The topology is static and shared by all games.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

RESOURCES: tuple[str, ...] = ("lumber", "brick", "wool", "grain", "ore")
TERRAIN_RESOURCE: dict[str, str | None] = {
    "forest": "lumber",
    "hills": "brick",
    "pasture": "wool",
    "fields": "grain",
    "mountains": "ore",
    "desert": None,
}

Hex = tuple[int, int]


def _hex_distance(q: int, r: int) -> int:
    return max(abs(q), abs(r), abs(q + r))


def _center(q: int, r: int) -> tuple[float, float]:
    return 173.2 * (q + r / 2), 150.0 * r


def _corner_point(q: int, r: int, k: int) -> tuple[int, int]:
    x, y = _center(q, r)
    a = math.radians(-90 + 60 * k)
    return round(x + 100 * math.cos(a)), round(y + 100 * math.sin(a))


def _ring(radius: int) -> list[Hex]:
    return [
        (q, r)
        for r in range(-radius, radius + 1)
        for q in range(-radius, radius + 1)
        if _hex_distance(q, r) == radius
    ]


LAND_HEXES: tuple[Hex, ...] = tuple(
    (q, r) for r in range(-2, 3) for q in range(-2, 3) if _hex_distance(q, r) <= 2
)
SEA_HEXES: tuple[Hex, ...] = tuple(_ring(3))

# Neighbour of a hex across edge k.
EDGE_NEIGHBOUR: dict[int, Hex] = {0: (1, -1), 1: (1, 0), 2: (0, 1), 3: (-1, 1), 4: (-1, 0), 5: (0, -1)}


@dataclass(frozen=True, slots=True)
class Topology:
    """Static graph of the standard board. All lists are indexed by vertex/edge/hex index."""

    hexes: tuple[Hex, ...]
    hex_index: dict[Hex, int]
    vertex_hexes: tuple[tuple[int, ...], ...]  # land hexes touching each vertex
    vertex_neighbours: tuple[tuple[int, ...], ...]  # adjacent vertices
    vertex_edges: tuple[tuple[int, ...], ...]  # edges touching each vertex
    edge_vertices: tuple[tuple[int, int], ...]
    hex_vertices: tuple[tuple[int, ...], ...]  # 6 vertices per land hex, corner order
    vertex_ref: tuple[tuple[int, int, int], ...]  # canonical (q, r, corner) per vertex
    edge_ref: tuple[tuple[int, int, int], ...]  # canonical (q, r, edge) per edge
    _vertex_by_point: dict[tuple[int, int], int]
    _edge_by_pair: dict[tuple[int, int], int]

    @property
    def num_vertices(self) -> int:
        return len(self.vertex_hexes)

    @property
    def num_edges(self) -> int:
        return len(self.edge_vertices)

    def vertex_at(self, q: int, r: int, corner: int) -> int:
        """Vertex index for a corner of any hex (land or sea); KeyError if not on the land board."""
        return self._vertex_by_point[_corner_point(q, r, corner)]

    def edge_at(self, q: int, r: int, edge: int) -> int:
        a = self.vertex_at(q, r, edge)
        b = self.vertex_at(q, r, (edge + 1) % 6)
        return self._edge_by_pair[(min(a, b), max(a, b))]

    def edge_between(self, a: int, b: int) -> int | None:
        return self._edge_by_pair.get((min(a, b), max(a, b)))


def _build_topology() -> Topology:
    by_point: dict[tuple[int, int], int] = {}
    vertex_ref: list[tuple[int, int, int]] = []
    hex_vertices: list[tuple[int, ...]] = []
    for q, r in LAND_HEXES:
        corners = []
        for k in range(6):
            p = _corner_point(q, r, k)
            if p not in by_point:
                by_point[p] = len(vertex_ref)
                vertex_ref.append((q, r, k))
            corners.append(by_point[p])
        hex_vertices.append(tuple(corners))

    n = len(vertex_ref)
    v_hexes: list[list[int]] = [[] for _ in range(n)]
    for h, hex_corners in enumerate(hex_vertices):
        for v in hex_corners:
            v_hexes[v].append(h)

    by_pair: dict[tuple[int, int], int] = {}
    edge_vertices: list[tuple[int, int]] = []
    edge_ref: list[tuple[int, int, int]] = []
    for h, (q, r) in enumerate(LAND_HEXES):
        ring = hex_vertices[h]
        for k in range(6):
            a, b = ring[k], ring[(k + 1) % 6]
            key = (min(a, b), max(a, b))
            if key not in by_pair:
                by_pair[key] = len(edge_vertices)
                edge_vertices.append(key)
                edge_ref.append((q, r, k))

    v_edges: list[list[int]] = [[] for _ in range(n)]
    v_neigh: list[list[int]] = [[] for _ in range(n)]
    for e, (a, b) in enumerate(edge_vertices):
        v_edges[a].append(e)
        v_edges[b].append(e)
        v_neigh[a].append(b)
        v_neigh[b].append(a)

    return Topology(
        hexes=LAND_HEXES,
        hex_index={h: i for i, h in enumerate(LAND_HEXES)},
        vertex_hexes=tuple(tuple(x) for x in v_hexes),
        vertex_neighbours=tuple(tuple(x) for x in v_neigh),
        vertex_edges=tuple(tuple(x) for x in v_edges),
        edge_vertices=tuple(edge_vertices),
        hex_vertices=tuple(hex_vertices),
        vertex_ref=tuple(vertex_ref),
        edge_ref=tuple(edge_ref),
        _vertex_by_point=by_point,
        _edge_by_pair=by_pair,
    )


TOPOLOGY = _build_topology()


@dataclass(frozen=True, slots=True)
class HarborSpec:
    q: int  # sea hex
    r: int
    edge: int  # edge of the sea hex that faces land
    kind: str  # "any" (3:1) or a resource (2:1)


@dataclass(frozen=True, slots=True)
class Layout:
    """One concrete board: terrain and number per land hex (TOPOLOGY.hexes order) and harbors."""

    terrains: tuple[str, ...]
    numbers: tuple[int | None, ...]
    harbors: tuple[HarborSpec, ...]

    def harbor_vertices(self) -> dict[int, str]:
        """Vertex index -> harbor kind for every vertex with harbor access."""
        out: dict[int, str] = {}
        for h in self.harbors:
            for k in (h.edge, (h.edge + 1) % 6):
                out[TOPOLOGY.vertex_at(h.q, h.r, k)] = h.kind
        return out

    @property
    def desert(self) -> int:
        return self.terrains.index("desert")


# Harbor positions of the standard frame (sea hex + land-facing edge).
HARBOR_SLOTS: tuple[tuple[int, int, int], ...] = (
    (0, -3, 2), (2, -3, 3), (3, -2, 3), (3, 0, 4), (1, 2, 5),
    (-1, 3, 0), (-3, 3, 0), (-3, 1, 1), (-2, -1, 2),
)  # fmt: skip
HARBOR_KINDS: tuple[str, ...] = ("any", "any", "any", "any", *RESOURCES)
TERRAIN_POOL: tuple[str, ...] = (
    ("forest",) * 4 + ("hills",) * 3 + ("pasture",) * 4 + ("fields",) * 4 + ("mountains",) * 3 + ("desert",)
)
NUMBER_POOL: tuple[int, ...] = (2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12)

_BEGINNER: dict[Hex, tuple[str, int | None]] = {
    (0, -2): ("mountains", 10), (1, -2): ("pasture", 2), (2, -2): ("forest", 9),
    (-1, -1): ("fields", 12), (0, -1): ("hills", 6), (1, -1): ("pasture", 4), (2, -1): ("hills", 10),
    (-2, 0): ("fields", 9), (-1, 0): ("forest", 11), (0, 0): ("desert", None), (1, 0): ("forest", 3),
    (2, 0): ("mountains", 8), (-2, 1): ("forest", 8), (-1, 1): ("mountains", 3), (0, 1): ("fields", 4),
    (1, 1): ("pasture", 5), (-2, 2): ("hills", 5), (-1, 2): ("fields", 6), (0, 2): ("pasture", 11),
}  # fmt: skip
_BEGINNER_HARBORS = ("any", "wool", "any", "any", "brick", "lumber", "any", "grain", "ore")


def beginner_layout() -> Layout:
    """The official beginner board (same as frontend/src/state/sampleState.ts)."""
    return Layout(
        terrains=tuple(_BEGINNER[h][0] for h in LAND_HEXES),
        numbers=tuple(_BEGINNER[h][1] for h in LAND_HEXES),
        harbors=tuple(
            HarborSpec(q, r, e, k) for (q, r, e), k in zip(HARBOR_SLOTS, _BEGINNER_HARBORS, strict=True)
        ),
    )


def _hex_neighbours(i: int) -> list[int]:
    q, r = LAND_HEXES[i]
    return [
        TOPOLOGY.hex_index[(q + dq, r + dr)]
        for dq, dr in EDGE_NEIGHBOUR.values()
        if (q + dq, r + dr) in TOPOLOGY.hex_index
    ]


def random_layout(rng: random.Random) -> Layout:
    """Random standard board. Red numbers (6 and 8) are never adjacent."""
    terrains = list(TERRAIN_POOL)
    rng.shuffle(terrains)
    while True:
        numbers = list(NUMBER_POOL)
        rng.shuffle(numbers)
        it = iter(numbers)
        per_hex: list[int | None] = [None if t == "desert" else next(it) for t in terrains]
        hot = {i for i, n in enumerate(per_hex) if n in (6, 8)}
        if all(not (hot & set(_hex_neighbours(i))) for i in hot):
            break
    kinds = list(HARBOR_KINDS)
    rng.shuffle(kinds)
    return Layout(
        terrains=tuple(terrains),
        numbers=tuple(per_hex),
        harbors=tuple(HarborSpec(q, r, e, k) for (q, r, e), k in zip(HARBOR_SLOTS, kinds, strict=True)),
    )


def pips(number: int | None) -> int:
    """Number of ways to roll `number` with two dice (the dots on a token)."""
    return 0 if number is None else 6 - abs(7 - number)
