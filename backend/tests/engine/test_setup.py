import pytest

from catan_engine import Game, RuleError
from catan_engine import actions as A
from catan_engine.board import TERRAIN_RESOURCE
from catan_engine.board import TOPOLOGY as T
from tests.conftest import V


def new3() -> Game:
    return Game.new(["A", "B", "C"], seed=7, layout="beginner")


def test_snake_order_and_transition_to_play() -> None:
    g = new3()
    order = []
    while g.state.phase == "setup":
        pid = g.pending_actors()[0]
        order.append(pid)
        g.apply(pid, g.legal_actions(pid)[0])
        g.apply(pid, g.legal_actions(pid)[0])
    assert order == ["p1", "p2", "p3", "p3", "p2", "p1"]
    s = g.state
    assert (s.phase, s.step, s.current, s.turn_number) == ("playing", "roll", 0, 1)
    assert all(p.settlements_left == 3 and p.roads_left == 13 for p in s.players)


def test_distance_rule_in_setup() -> None:
    g = new3()
    g.apply("p1", A.PlaceSetupSettlement(V(0, 0, 0)))
    g.apply("p1", A.PlaceSetupRoad(T.vertex_edges[V(0, 0, 0)][0]))
    with pytest.raises(RuleError) as err:
        g.apply("p2", A.PlaceSetupSettlement(V(0, 0, 1)))  # adjacent to p1
    assert err.value.code == "illegalPlacement"
    assert V(0, 0, 1) not in {a.vertex for a in g.legal_actions("p2")}  # type: ignore[union-attr]


def test_setup_road_must_touch_the_new_settlement() -> None:
    g = new3()
    g.apply("p1", A.PlaceSetupSettlement(V(0, 0, 0)))
    far = next(e for e in range(T.num_edges) if V(0, 0, 0) not in T.edge_vertices[e])
    with pytest.raises(RuleError):
        g.apply("p1", A.PlaceSetupRoad(far))


def test_only_the_second_settlement_pays_out() -> None:
    g = new3()
    for _ in range(3):  # first round
        pid = g.pending_actors()[0]
        g.apply(pid, g.legal_actions(pid)[0])
        g.apply(pid, g.legal_actions(pid)[0])
    assert all(p.card_count() == 0 for p in g.state.players)
    pid = g.pending_actors()[0]
    spot = g.legal_actions(pid)[0]
    assert isinstance(spot, A.PlaceSetupSettlement)
    g.apply(pid, spot)
    expected = sum(1 for h in T.vertex_hexes[spot.vertex] if TERRAIN_RESOURCE[g.state.layout.terrains[h]])
    assert g.state.players[g.state.player_index(pid)].card_count() == expected


def test_other_players_cannot_act_in_setup() -> None:
    g = new3()
    with pytest.raises(RuleError) as err:
        g.apply("p2", A.PlaceSetupSettlement(V(0, 0, 0)))
    assert err.value.code == "notYourTurn"
    assert g.legal_actions("p2") == []
