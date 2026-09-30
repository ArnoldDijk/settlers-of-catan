import json

from catan_engine import Game, serialize
from catan_engine.sample import sample_state
from catan_engine.sim.runner import SIM_CONFIG
from tests.engine.helpers import play_some


def test_round_trip_is_lossless() -> None:
    g = play_some(seed=5, actions=300)
    dumped = serialize.dump(g.state)
    again = serialize.dump(serialize.load(json.loads(json.dumps(dumped))))
    assert again == dumped


def test_loaded_game_continues_identically() -> None:
    a = play_some(seed=9, actions=200)
    b = Game(serialize.load(json.loads(json.dumps(serialize.dump(a.state)))))
    for _ in range(300):
        if a.finished:
            break
        pid = a.pending_actors()[0]
        action = a.legal_actions(pid)[-1]
        a.apply(pid, action)
        b.apply(pid, action)
    assert serialize.dump(a.state) == serialize.dump(b.state)


def test_sample_state_serializes() -> None:
    s = sample_state()
    assert serialize.dump(serialize.load(serialize.dump(s))) == serialize.dump(s)
    assert SIM_CONFIG.trade_offers_per_turn == 2


def test_actions_round_trip_through_json() -> None:
    from catan_engine import action_from_dict, action_to_dict
    from catan_engine import actions as A

    samples = [A.Roll(), A.BuildRoad(3), A.MoveRobber(4, "p2"), A.Discard(A.bundle({"ore": 2, "wool": 1})),
               A.OfferTrade(A.bundle({"ore": 1}), A.bundle({"wool": 2}), ("p2", "p3")), A.ConfirmTrade("p2"),
               A.PlayYearOfPlenty(A.bundle({"grain": 2})), A.BankTrade("ore", "wool")]  # fmt: skip
    for a in samples:
        d = action_to_dict(a)
        assert "type" in d
        assert action_from_dict(json.loads(json.dumps(d))) == a
