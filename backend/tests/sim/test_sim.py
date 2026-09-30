import json
import time
from pathlib import Path

import pytest

from catan_engine.agents import load_agent
from catan_engine.sim import play_game, replay
from catan_engine.sim.cli import main

RESULT_KEYS = {
    "seed",
    "agents",
    "winner",
    "turns",
    "points",
    "longest_road",
    "largest_army",
    "hit_turn_cap",
    "actions",
}


def test_play_game_is_deterministic() -> None:
    a = play_game(["greedy", "random", "random"], seed=11)
    b = play_game(["greedy", "random", "random"], seed=11)
    assert a.to_json() == b.to_json()
    assert a.winner is not None and a.points[a.winner] >= 10


def test_cli_writes_jsonl_and_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "r.jsonl"
    assert main(["--games", "6", "--agents", "greedy,random", "--seed", "3", "--workers", "2",
                 "--out", str(out), "--quiet"]) == 0  # fmt: skip
    lines = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(lines) == 6
    assert all(set(line) == RESULT_KEYS for line in lines)
    summary = capsys.readouterr().out
    assert "Games: 6" in summary and "greedy" in summary


def test_cli_results_do_not_depend_on_worker_count(tmp_path: Path) -> None:
    one, two = tmp_path / "1.jsonl", tmp_path / "2.jsonl"
    main(["--games", "4", "--seed", "8", "--workers", "1", "--out", str(one), "--quiet"])
    main(["--games", "4", "--seed", "8", "--workers", "2", "--out", str(two), "--quiet"])
    assert one.read_text() == two.read_text()


def test_saved_games_replay_to_the_same_result(tmp_path: Path) -> None:
    out = tmp_path / "r.jsonl"
    main(
        ["--games", "2", "--seed", "4", "--save-games", str(tmp_path / "games"), "--out", str(out), "--quiet"]
    )
    results = [json.loads(line) for line in out.read_text().splitlines()]
    for i, result in enumerate(results, 1):
        log = json.loads((tmp_path / "games" / f"game-{i:06d}.json").read_text())
        game = replay(log)
        assert game.state.winner == result["winner"]
        assert game.state.turn_number == result["turns"]


def test_custom_agent_by_module_path() -> None:
    make = load_agent("tests.sim.first_legal_agent:FirstLegalAgent")
    assert make().name == "first-legal"
    r = play_game(["tests.sim.first_legal_agent:FirstLegalAgent", "random"], seed=2, max_turns=60)
    assert r.turns >= 1


@pytest.mark.parametrize("spec", ["nope", "os:path", "catan_engine.agents.base:Nope"])
def test_bad_agent_specs_are_rejected(spec: str) -> None:
    with pytest.raises((ValueError, TypeError, AttributeError, ImportError)):
        load_agent(spec)()


def test_cli_rejects_bad_arguments() -> None:
    with pytest.raises(SystemExit):
        main(["--agents", "random"])
    with pytest.raises(SystemExit):
        main(["--games", "0"])


@pytest.mark.slow
def test_benchmark_games_per_second() -> None:
    n = 200
    start = time.perf_counter()
    for seed in range(n):
        play_game(["greedy"] * 4, seed=seed)
    rate = n / (time.perf_counter() - start)
    print(f"\n{rate:.1f} games/s (4 greedy agents, one process)")
    assert rate > 5
