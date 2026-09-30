import pytest

from catan_engine import RuleError
from catan_engine import actions as A
from catan_engine.board import TOPOLOGY as T
from catan_engine.rules.trading import trade_rates
from catan_engine.state import Config
from tests.conftest import assert_bank_conserved, give, place, playing


def harbor_vertex(g, kind):  # type: ignore[no-untyped-def]
    return next(v for v, k in g.state.layout.harbor_vertices().items() if k == kind)


def test_bank_trade_rates_from_harbors() -> None:
    g = playing()
    assert set(trade_rates(g.state, 0).values()) == {4}
    place(g, 0, settlements=[harbor_vertex(g, "any")])
    assert set(trade_rates(g.state, 0).values()) == {3}
    place(g, 0, settlements=[harbor_vertex(g, "ore")])
    assert trade_rates(g.state, 0)["ore"] == 2
    assert trade_rates(g.state, 0)["wool"] == 3


def test_bank_trade_four_for_one() -> None:
    g = playing()
    give(g, 0, lumber=4)
    with pytest.raises(RuleError):
        g.apply("p1", A.BankTrade("lumber", "lumber"))
    g.apply("p1", A.BankTrade("lumber", "ore"))
    assert g.state.players[0].resources["lumber"] == 0
    assert g.state.players[0].resources["ore"] == 1
    assert_bank_conserved(g)
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.BankTrade("lumber", "ore"))
    assert err.value.code == "cannotAfford"


def offer(g, give_, get, to=("p2", "p3")):  # type: ignore[no-untyped-def]
    g.apply("p1", A.OfferTrade(A.bundle(give_), A.bundle(get), tuple(to)))


def test_player_trade_offer_accept_confirm() -> None:
    g = playing()
    give(g, 0, lumber=2)
    give(g, 2, ore=1)
    offer(g, {"lumber": 2}, {"ore": 1})
    assert g.pending_actors() == ["p2", "p3"]
    assert g.legal_actions("p2") == [A.RespondTrade(False)]  # p2 cannot pay
    g.apply("p2", A.RespondTrade(False))
    g.apply("p3", A.RespondTrade(True))
    assert g.pending_actors() == ["p1"]
    assert A.ConfirmTrade("p3") in g.legal_actions("p1")
    g.apply("p1", A.ConfirmTrade("p3"))
    assert g.state.trade is None
    assert g.state.players[0].resources["ore"] == 1
    assert g.state.players[2].resources["lumber"] == 2
    assert_bank_conserved(g)


def test_offer_closes_when_everyone_declines() -> None:
    g = playing()
    give(g, 0, lumber=1)
    offer(g, {"lumber": 1}, {"ore": 1})
    g.apply("p2", A.RespondTrade(False))
    g.apply("p3", A.RespondTrade(False))
    assert g.state.trade is None


def test_cannot_accept_without_the_cards() -> None:
    g = playing()
    give(g, 0, lumber=1)
    offer(g, {"lumber": 1}, {"ore": 1})
    with pytest.raises(RuleError) as err:
        g.apply("p2", A.RespondTrade(True))
    assert err.value.code == "cannotAfford"


def test_offerer_can_withdraw_while_others_think() -> None:
    g = playing()
    give(g, 0, lumber=1)
    offer(g, {"lumber": 1}, {"ore": 1})
    assert g.legal_actions("p1") == [A.CancelTrade()]
    g.apply("p1", A.CancelTrade())
    assert g.state.trade is None


def test_invalid_offers_are_rejected() -> None:
    g = playing()
    give(g, 0, lumber=1)
    for give_, get, to in [
        ({"lumber": 2}, {"ore": 1}, ("p2",)),  # can't pay
        ({"lumber": 1}, {"lumber": 1}, ("p2",)),  # same resource both ways
        ({"lumber": 1}, {"ore": 1}, ("p1",)),  # offer to yourself
        ({"lumber": 1}, {"ore": 1}, ()),  # nobody
    ]:
        with pytest.raises(RuleError):
            offer(g, give_, get, to)


def test_only_the_current_player_offers_and_not_before_rolling() -> None:
    g = playing()
    give(g, 1, lumber=1)
    with pytest.raises(RuleError):
        g.apply("p2", A.OfferTrade((("lumber", 1),), (("ore", 1),), ("p1",)))
    g.state.step = "roll"
    give(g, 0, lumber=1)
    with pytest.raises(RuleError):
        offer(g, {"lumber": 1}, {"ore": 1})


def test_offer_cap_per_turn() -> None:
    g = playing(config=Config(trade_offers_per_turn=1))
    give(g, 0, lumber=2)
    offer(g, {"lumber": 1}, {"ore": 1})
    g.apply("p1", A.CancelTrade())
    assert not any(isinstance(a, A.OfferTrade) for a in g.legal_actions("p1"))
    with pytest.raises(RuleError) as err:
        offer(g, {"lumber": 1}, {"ore": 1})
    assert err.value.code == "tooManyOffers"


def test_building_is_blocked_while_an_offer_is_open() -> None:
    g = playing()
    v = T.hex_vertices[0][0]
    place(g, 0, settlements=[v])
    give(g, 0, lumber=2, brick=1)
    offer(g, {"lumber": 1}, {"ore": 1})
    with pytest.raises(RuleError) as err:
        g.apply("p1", A.BuildRoad(T.vertex_edges[v][0]))
    assert err.value.code == "notYourTurn"  # others must answer first; p1 may only withdraw
    g.apply("p1", A.CancelTrade())
    g.apply("p1", A.BuildRoad(T.vertex_edges[v][0]))
    assert g.state.roads
