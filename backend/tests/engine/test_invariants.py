"""Property tests: many seeded bot games, invariants checked after every single action."""

from collections import Counter

import pytest

from catan_engine import Game, RuleError
from catan_engine.board import TOPOLOGY as T
from catan_engine.state import DEV_DECK, PIECES
from tests.conftest import assert_bank_conserved
from tests.engine.helpers import play_some


def check(g: Game) -> None:
    s = g.state
    assert_bank_conserved(g)
    assert all(n >= 0 for n in s.bank.values())
    assert all(n >= 0 for p in s.players for n in p.resources.values())

    cards: Counter[str] = Counter(s.dev_deck)
    for p in s.players:
        cards.update(p.dev_cards)
        cards.update(p.new_dev_cards)
        cards.update(p.played_dev_cards)
        assert p.knights_played == p.played_dev_cards["knight"]
    assert +cards == Counter(DEV_DECK)

    for i, p in enumerate(s.players):
        kinds = Counter(kind for owner, kind in s.buildings.values() if owner == i)
        assert p.settlements_left + kinds["settlement"] == PIECES["settlements"]
        assert p.cities_left + kinds["city"] == PIECES["cities"]
        assert p.roads_left + sum(1 for o in s.roads.values() if o == i) == PIECES["roads"]

    for v in s.buildings:
        assert all(n not in s.buildings for n in T.vertex_neighbours[v]), "distance rule"
    for e, owner in s.roads.items():
        touches = any(
            s.buildings.get(v, (-1, ""))[0] == owner
            or any(s.roads.get(x) == owner for x in T.vertex_edges[v] if x != e)
            for v in T.edge_vertices[e]
        )
        assert touches, "road not connected to its owner's network"


@pytest.mark.parametrize("seed", range(60))
def test_invariants_hold_in_bot_games(seed: int) -> None:
    g = play_some(seed, players=2 + seed % 3, on_step=check)
    assert g.finished or g.state.turn_number > 400


@pytest.mark.parametrize("seed", range(8))
def test_every_listed_legal_action_is_accepted(seed: int) -> None:
    def try_all(g: Game) -> None:
        if g.state.turn_number % 7:
            return
        for pid in g.pending_actors():
            for action in g.legal_actions(pid):
                clone = g.clone()
                try:
                    clone.apply(pid, action)
                except RuleError as err:  # pragma: no cover - this is the failure we look for
                    pytest.fail(f"legal action rejected: {action} ({err.code})")

    play_some(seed, actions=1500, on_step=try_all)


def test_same_seed_same_game() -> None:
    from catan_engine import serialize

    a, b = play_some(123), play_some(123)
    assert serialize.dump(a.state) == serialize.dump(b.state)
    assert serialize.dump(play_some(124).state) != serialize.dump(a.state)
