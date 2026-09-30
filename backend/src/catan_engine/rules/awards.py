"""Longest road and largest army."""

from __future__ import annotations

from ..board import TOPOLOGY as T
from ..state import GameState

MIN_LONGEST_ROAD = 5
MIN_LARGEST_ARMY = 3


def longest_road_length(s: GameState, player: int) -> int:
    """Longest trail (no edge used twice) of the player's roads; it cannot pass through a
    vertex occupied by an opponent."""
    own = [e for e, p in s.roads.items() if p == player]
    if not own:
        return 0
    own_set = set(own)

    def blocked(v: int) -> bool:
        b = s.buildings.get(v)
        return b is not None and b[0] != player

    best = 0

    def walk(v: int, used: set[int], length: int) -> None:
        nonlocal best
        best = max(best, length)
        if blocked(v):
            return
        for e in T.vertex_edges[v]:
            if e in own_set and e not in used:
                a, b = T.edge_vertices[e]
                used.add(e)
                walk(b if a == v else a, used, length + 1)
                used.remove(e)

    for e in own:
        a, b = T.edge_vertices[e]
        walk(b, {e}, 1)
        walk(a, {e}, 1)
    return best


def update_longest_road(s: GameState) -> None:
    lengths = [longest_road_length(s, p) for p in range(len(s.players))]
    holder = s.longest_road
    best = max(lengths)
    if holder is not None and lengths[holder] >= MIN_LONGEST_ROAD and lengths[holder] == best:
        return  # the holder keeps it on a tie
    if best < MIN_LONGEST_ROAD:
        s.longest_road = None
        return
    leaders = [p for p, n in enumerate(lengths) if n == best]
    s.longest_road = leaders[0] if len(leaders) == 1 else None


def update_largest_army(s: GameState, player: int) -> None:
    knights = s.players[player].knights_played
    if knights < MIN_LARGEST_ARMY:
        return
    holder = s.largest_army
    if holder is None or knights > s.players[holder].knights_played:
        s.largest_army = player
