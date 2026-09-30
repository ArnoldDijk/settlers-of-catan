"""Hidden information must never leak into another player's view (port of the frontend's tests)."""

import json

import pytest

from catan_engine.projection import to_player_view
from catan_engine.sample import sample_state
from tests.engine.helpers import play_some

PUBLIC_PLAYER_KEYS = sorted([
    "color", "devCardCount", "id", "knightsPlayed", "name", "piecesLeft", "playedDevCards", "resourceCount",
    "victoryPoints",
])  # fmt: skip


@pytest.mark.parametrize("viewer", ["p1", "p2", "p3", "p4"])
def test_viewer_gets_only_their_own_hand(viewer: str) -> None:
    s = sample_state()
    view = to_player_view(s, viewer)
    me = s.players[s.player_index(viewer)]
    assert view["viewerId"] == viewer
    assert view["hand"]["resources"] == me.resources
    for p in view["players"]:
        assert sorted(p) == PUBLIC_PLAYER_KEYS


def test_no_hidden_data_anywhere_in_views_during_real_games() -> None:
    for seed in range(6):
        g = play_some(seed, actions=800)
        s = g.state
        for p in s.players:
            view = to_player_view(s, p.id)
            text = json.dumps(view)
            # Exactly one hand and the bank carry resource dicts; one hand carries dev cards.
            assert text.count('"resources"') == 2
            assert text.count('"devCards"') == 1
            assert "devDeck" not in text and "rng" not in text
            others = [o for o in view["players"] if o["id"] != p.id]
            assert all("resources" not in o and "devCards" not in o for o in others)
            assert view["bank"]["devCardsLeft"] == len(s.dev_deck)


def test_public_points_exclude_hidden_victory_cards() -> None:
    s = sample_state()
    anna_seen_by_bram = next(p for p in to_player_view(s, "p2")["players"] if p["id"] == "p1")
    assert anna_seen_by_bram["victoryPoints"] == 3  # Anna also holds a secret VP card
    bram = next(p for p in to_player_view(s, "p2")["players"] if p["id"] == "p2")
    assert bram["victoryPoints"] == 5  # settlement + city + largest army


def test_unknown_viewer_is_rejected() -> None:
    with pytest.raises(KeyError):
        to_player_view(sample_state(), "nobody")
