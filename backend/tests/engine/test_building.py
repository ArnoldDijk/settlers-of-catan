import pytest

from catan_engine import RuleError
from catan_engine import actions as A
from catan_engine.board import TOPOLOGY as T
from tests.conftest import E, V, assert_bank_conserved, give, place, playing


def test_road_costs_brick_and_lumber_and_must_connect() -> None:
    g = playing()
    v = V(0, 0, 0)
    place(g, 0, settlements=[v])
    give(g, 0, brick=2, lumber=2)
    far = next(e for e in range(T.num_edges) if v not in T.edge_vertices[e])
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.BuildRoad(far))
    assert err.value.code == "illegalPlacement"
    g.apply("p1", A.BuildRoad(T.vertex_edges[v][0]))
    assert g.state.players[0].resources == {"lumber": 1, "brick": 1, "wool": 0, "grain": 0, "ore": 0}
    assert g.state.players[0].roads_left == 14
    assert_bank_conserved(g)


def test_road_cannot_pass_through_an_opponent_settlement() -> None:
    g = playing()
    a, b = V(0, 0, 0), V(0, 0, 1)
    place(g, 0, roads=[E(0, 0, 0)])  # a-b
    place(g, 1, settlements=[b])
    give(g, 0, brick=1, lumber=1)
    beyond = next(e for e in T.vertex_edges[b] if e != E(0, 0, 0))
    assert A.BuildRoad(beyond) not in g.legal_actions("p1")
    assert a in T.edge_vertices[E(0, 0, 0)]


def test_settlement_needs_own_road_and_distance() -> None:
    g = playing()
    give(g, 0, brick=2, lumber=2, wool=2, grain=2)
    v = V(0, 0, 0)
    with pytest.raises(RuleError):
        g.apply("p1", A.BuildSettlement(v))  # no road
    place(g, 0, roads=[T.vertex_edges[v][0]])
    place(g, 1, settlements=[T.vertex_neighbours[v][0]])
    with pytest.raises(RuleError):
        g.apply("p1", A.BuildSettlement(v))  # neighbour occupied
    del g.state.buildings[T.vertex_neighbours[v][0]]
    g.apply("p1", A.BuildSettlement(v))
    assert g.state.buildings[v] == (0, "settlement")
    assert_bank_conserved(g)


def test_city_replaces_settlement_and_returns_the_piece() -> None:
    g = playing()
    v = V(0, 0, 0)
    place(g, 0, settlements=[v])
    give(g, 0, grain=2, ore=3)
    g.apply("p1", A.BuildCity(v))
    p = g.state.players[0]
    assert g.state.buildings[v] == (0, "city")
    assert (p.settlements_left, p.cities_left) == (5, 3)
    assert p.card_count() == 0


def test_cannot_afford() -> None:
    g = playing()
    place(g, 0, settlements=[V(0, 0, 0)])
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.BuildCity(V(0, 0, 0)))
    assert err.value.code == "cannotAfford"


def test_piece_limits() -> None:
    g = playing()
    v = V(0, 0, 0)
    place(g, 0, settlements=[v])
    g.state.players[0].roads_left = 0
    give(g, 0, brick=1, lumber=1)
    assert not any(isinstance(a, A.BuildRoad) for a in g.legal_actions("p1"))
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.BuildRoad(T.vertex_edges[v][0]))
    assert err.value.code == "noPiecesLeft"


def test_no_building_before_rolling() -> None:
    g = playing()
    g.state.step = "roll"
    place(g, 0, settlements=[V(0, 0, 0)])
    give(g, 0, brick=1, lumber=1)
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.BuildRoad(T.vertex_edges[V(0, 0, 0)][0]))
    assert err.value.code == "wrongStep"
