import pytest

from catan_engine import RuleError
from catan_engine import actions as A
from catan_engine.board import TOPOLOGY as T
from catan_engine.rules import production
from tests.conftest import FixedDice, H, assert_bank_conserved, give, place, playing


def roll_step(g, rolls):  # type: ignore[no-untyped-def]
    g.state.step = "roll"
    g.state.rng = FixedDice(rolls)


def test_production_pays_settlements_one_and_cities_two() -> None:
    g = playing()
    h = H(0, -1)  # hills, 6
    v1, v2 = T.hex_vertices[h][0], T.hex_vertices[h][3]
    place(g, 0, settlements=[v1])
    place(g, 1, cities=[v2])
    roll_step(g, [3, 3])
    g.apply("p1", A.Roll())
    assert g.state.players[0].resources["brick"] == 1
    assert g.state.players[1].resources["brick"] == 2
    assert g.state.step == "action"
    assert_bank_conserved(g)


def test_robber_blocks_production() -> None:
    g = playing()
    h = H(0, -1)
    place(g, 0, settlements=[T.hex_vertices[h][0]])
    g.state.robber = h
    roll_step(g, [3, 3])
    g.apply("p1", A.Roll())
    assert g.state.players[0].resources["brick"] == 0


def test_bank_shortage_pays_nobody_when_several_players_are_owed() -> None:
    g = playing()
    h = H(0, -1)
    place(g, 0, cities=[T.hex_vertices[h][0]])
    place(g, 1, cities=[T.hex_vertices[h][3]])
    give(g, 2, brick=16)  # bank keeps 3, but 4 are owed
    production.produce(g.state, 6)
    assert g.state.players[0].resources["brick"] == 0
    assert g.state.players[1].resources["brick"] == 0


def test_bank_shortage_gives_the_rest_to_a_single_player() -> None:
    g = playing()
    h = H(0, -1)
    place(g, 0, cities=[T.hex_vertices[h][0]])
    give(g, 2, brick=18)
    production.produce(g.state, 6)
    assert g.state.players[0].resources["brick"] == 1
    assert_bank_conserved(g)


def test_seven_makes_big_hands_discard_then_robber_moves_and_steals() -> None:
    g = playing()
    give(g, 1, lumber=5, brick=4)  # 9 cards -> discard 4
    give(g, 2, wool=7)  # 7 cards -> safe
    place(g, 1, settlements=[T.hex_vertices[H(1, 0)][0]])
    roll_step(g, [3, 4])
    g.apply("p1", A.Roll())
    assert g.state.step == "discard"
    assert g.pending_actors() == ["p2"]
    with pytest.raises(RuleError) as err:
        g.apply("p2", A.Discard(A.bundle({"lumber": 3})))
    assert err.value.code == "wrongAmount"
    g.apply("p2", A.Discard(A.bundle({"lumber": 4})))
    assert g.state.step == "moveRobber"
    assert g.pending_actors() == ["p1"]
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.MoveRobber(H(1, 0)))  # must pick the victim
    assert err.value.code == "illegalVictim"
    g.apply("p1", A.MoveRobber(H(1, 0), "p2"))
    assert g.state.robber == H(1, 0)
    assert g.state.players[0].card_count() == 1
    assert g.state.players[1].card_count() == 4
    assert g.state.step == "action"
    assert_bank_conserved(g)


def test_robber_must_move_and_cannot_steal_from_nobody() -> None:
    g = playing()
    g.state.step = "moveRobber"
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.MoveRobber(g.state.robber))
    assert err.value.code == "illegalRobberHex"
    with pytest.raises(RuleError):
        g.apply("p1", A.MoveRobber(H(1, 0), "p2"))
    g.apply("p1", A.MoveRobber(H(1, 0)))


def test_cannot_steal_from_yourself_or_empty_hands() -> None:
    g = playing()
    v = T.hex_vertices[H(1, 0)]
    place(g, 0, settlements=[v[0]])
    place(g, 1, settlements=[v[3]])  # p2 has no cards
    g.state.step = "moveRobber"
    assert A.MoveRobber(H(1, 0)) in g.legal_actions("p1")
    assert not any(a.steal_from for a in g.legal_actions("p1") if a.hex == H(1, 0))  # type: ignore[union-attr]


def test_roll_only_once() -> None:
    g = playing()
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.Roll())
    assert err.value.code == "wrongStep"


def test_discard_legal_actions_cover_every_split() -> None:
    g = playing()
    give(g, 1, lumber=4, ore=4)
    g.state.step = "discard"
    g.state.pending_discards = {1: 4}
    splits = {a.resources for a in g.legal_actions("p2")}  # type: ignore[union-attr]
    assert len(splits) == 5  # 4+0, 3+1, 2+2, 1+3, 0+4
