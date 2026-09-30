import random

from catan_engine.board import (
    NUMBER_POOL,
    TERRAIN_POOL,
    _hex_neighbours,
    beginner_layout,
    random_layout,
)  # fmt: skip
from catan_engine.board import (
    TOPOLOGY as T,
)
from tests.conftest import E, V


def test_standard_board_counts() -> None:
    assert len(T.hexes) == 19
    assert T.num_vertices == 54
    assert T.num_edges == 72
    assert sum(len(x) for x in T.vertex_hexes) == 19 * 6


def test_shared_corners_resolve_to_one_vertex() -> None:
    # Top corner of the centre tile is corner 2 of (0,-1) and corner 4 of (1,-1).
    assert V(0, 0, 0) == V(0, -1, 2) == V(1, -1, 4)


def test_shared_edges_resolve_to_one_edge() -> None:
    assert E(0, 0, 1) == E(1, 0, 4)
    assert E(0, 0, 0) == E(1, -1, 3)


def test_canonical_refs_round_trip() -> None:
    for v, (q, r, k) in enumerate(T.vertex_ref):
        assert T.vertex_at(q, r, k) == v
    for e, (q, r, k) in enumerate(T.edge_ref):
        assert T.edge_at(q, r, k) == e


def test_every_harbor_touches_two_land_vertices() -> None:
    assert len(beginner_layout().harbor_vertices()) == 18


def test_random_layouts_use_standard_pools_and_separate_red_numbers() -> None:
    for seed in range(200):
        lay = random_layout(random.Random(seed))
        assert sorted(lay.terrains) == sorted(TERRAIN_POOL)
        assert sorted(n for n in lay.numbers if n is not None) == sorted(NUMBER_POOL)
        assert lay.numbers[lay.desert] is None
        hot = {i for i, n in enumerate(lay.numbers) if n in (6, 8)}
        assert all(not (hot & set(_hex_neighbours(i))) for i in hot)
        assert sorted(h.kind for h in lay.harbors) == sorted(
            ["any"] * 4 + ["brick", "grain", "lumber", "ore", "wool"]
        )
