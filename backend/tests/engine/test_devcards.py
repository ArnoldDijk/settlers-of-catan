import pytest

from catan_engine import RuleError
from catan_engine import actions as A
from catan_engine.board import TOPOLOGY as T
from catan_engine.rules import scoring
from tests.conftest import H, V, assert_bank_conserved, give, place, playing


def test_buying_draws_from_the_hidden_deck() -> None:
    g = playing()
    give(g, 0, wool=1, grain=1, ore=1)
    top = g.state.dev_deck[-1]
    g.apply("p1", A.BuyDevCard())
    p = g.state.players[0]
    assert p.new_dev_cards[top] == 1
    assert len(g.state.dev_deck) == 24
    assert_bank_conserved(g)


def test_card_bought_this_turn_cannot_be_played() -> None:
    g = playing()
    g.state.dev_deck.append("knight")
    give(g, 0, wool=1, grain=1, ore=1)
    g.apply("p1", A.BuyDevCard())
    assert A.PlayKnight() not in g.legal_actions("p1")
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.PlayKnight())
    assert err.value.code == "noSuchCard"
    g.apply("p1", A.EndTurn())
    assert g.state.players[0].dev_cards["knight"] == 1  # playable from now on


def test_one_development_card_per_turn() -> None:
    g = playing()
    g.state.players[0].dev_cards["monopoly"] = 2
    g.apply("p1", A.PlayMonopoly("ore"))
    assert g.legal_actions("p1") == [a for a in g.legal_actions("p1") if not isinstance(a, A.PlayMonopoly)]
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.PlayMonopoly("ore"))
    assert err.value.code == "devCardAlreadyPlayed"


def test_knight_before_rolling_returns_to_the_roll() -> None:
    g = playing()
    g.state.step = "roll"
    g.state.players[0].dev_cards["knight"] = 1
    assert A.PlayKnight() in g.legal_actions("p1")
    g.apply("p1", A.PlayKnight())
    assert g.state.step == "moveRobber"
    g.apply("p1", A.MoveRobber(H(1, 0)))
    assert g.state.step == "roll"
    assert g.state.players[0].knights_played == 1
    assert g.state.players[0].played_dev_cards["knight"] == 1


def test_road_building_places_two_free_roads() -> None:
    g = playing()
    v = V(0, 0, 0)
    place(g, 0, settlements=[v])
    g.state.players[0].dev_cards["roadBuilding"] = 1
    g.apply("p1", A.PlayRoadBuilding())
    assert g.state.step == "roadBuilding"
    e1 = T.vertex_edges[v][0]
    g.apply("p1", A.BuildRoad(e1))
    other = next(a for a in g.legal_actions("p1") if isinstance(a, A.BuildRoad))
    g.apply("p1", other)
    assert g.state.step == "action"
    assert g.state.players[0].roads_left == 13
    assert g.state.players[0].card_count() == 0


def test_year_of_plenty_takes_two_from_the_bank() -> None:
    g = playing()
    g.state.players[0].dev_cards["yearOfPlenty"] = 1
    with pytest.raises(RuleError):
        g.apply("p1", A.PlayYearOfPlenty(A.bundle({"ore": 3})))
    g.apply("p1", A.PlayYearOfPlenty(A.bundle({"ore": 1, "wool": 1})))
    assert g.state.players[0].resources["ore"] == 1
    assert g.state.players[0].resources["wool"] == 1
    assert_bank_conserved(g)


def test_monopoly_collects_every_card_of_one_resource() -> None:
    g = playing()
    give(g, 1, ore=3, wool=1)
    give(g, 2, ore=2)
    g.state.players[0].dev_cards["monopoly"] = 1
    g.apply("p1", A.PlayMonopoly("ore"))
    assert [p.resources["ore"] for p in g.state.players] == [5, 0, 0]
    assert g.state.players[1].resources["wool"] == 1


def test_victory_point_cards_count_but_cannot_be_played() -> None:
    g = playing()
    g.state.players[0].dev_cards["victoryPoint"] = 2
    assert not any("victory" in a.type.lower() for a in g.legal_actions("p1"))
    assert scoring.total_points(g.state, 0) == 2
    assert scoring.public_points(g.state, 0) == 0
