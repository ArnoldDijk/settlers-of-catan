"""Where pieces may go: distance rule, road connectivity, piece limits."""

from __future__ import annotations

from ..board import TOPOLOGY as T
from ..state import GameState


def distance_ok(s: GameState, vertex: int) -> bool:
    """Empty vertex with no building on any adjacent vertex."""
    if vertex in s.buildings:
        return False
    return all(n not in s.buildings for n in T.vertex_neighbours[vertex])


def _vertex_blocked_for(s: GameState, vertex: int, player: int) -> bool:
    b = s.buildings.get(vertex)
    return b is not None and b[0] != player


def road_connects(s: GameState, edge: int, player: int) -> bool:
    """An empty edge touching the player's building, or the player's road through a vertex
    that is not occupied by an opponent."""
    if edge in s.roads:
        return False
    for v in T.edge_vertices[edge]:
        b = s.buildings.get(v)
        if b is not None and b[0] == player:
            return True
        if _vertex_blocked_for(s, v, player):
            continue
        if any(s.roads.get(e) == player for e in T.vertex_edges[v] if e != edge):
            return True
    return False


def settlement_spots(s: GameState, player: int) -> list[int]:
    if s.players[player].settlements_left == 0:
        return []
    return [
        v
        for v in range(T.num_vertices)
        if distance_ok(s, v) and any(s.roads.get(e) == player for e in T.vertex_edges[v])
    ]


def setup_settlement_spots(s: GameState) -> list[int]:
    return [v for v in range(T.num_vertices) if distance_ok(s, v)]


def setup_road_spots(s: GameState) -> list[int]:
    if s.last_setup_vertex is None:
        return []
    return [e for e in T.vertex_edges[s.last_setup_vertex] if e not in s.roads]


def road_spots(s: GameState, player: int) -> list[int]:
    if s.players[player].roads_left == 0:
        return []
    return [e for e in range(T.num_edges) if road_connects(s, e, player)]


def city_spots(s: GameState, player: int) -> list[int]:
    if s.players[player].cities_left == 0:
        return []
    return [v for v, (p, kind) in s.buildings.items() if p == player and kind == "settlement"]


def robber_hexes(s: GameState) -> list[int]:
    return [h for h in range(len(T.hexes)) if h != s.robber]


def steal_victims(s: GameState, hex_index: int, thief: int) -> list[int]:
    """Opponents with a building on the hex and at least one card, in seat order."""
    owners = {s.buildings[v][0] for v in T.hex_vertices[hex_index] if v in s.buildings}
    return sorted(p for p in owners if p != thief and s.players[p].card_count() > 0)
