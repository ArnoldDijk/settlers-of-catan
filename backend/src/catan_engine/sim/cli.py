"""catan-sim: run many headless games between agents.

catan-sim --games 1000 --agents greedy,random,random,random --seed 42 --workers 8 --out results.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections.abc import Iterator
from multiprocessing import Pool
from pathlib import Path

from ..actions import action_to_dict  # noqa: F401  (re-exported for custom tooling)
from ..agents import load_agent
from .runner import GameResult, play_game
from .stats import Summary


def _parse(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(prog="catan-sim", description="Run headless Catan simulations.")
    ap.add_argument("--games", type=int, default=100, help="number of games (default 100)")
    ap.add_argument(
        "--agents",
        default="greedy,random,random,random",
        help="comma-separated agents per seat: random, greedy or module:Class (2-4 seats)",
    )
    ap.add_argument("--seed", type=int, default=0, help="master seed; per-game seeds derive from it")
    ap.add_argument("--workers", type=int, default=1, help="parallel worker processes")
    ap.add_argument("--max-turns", type=int, default=500, help="stop a game after this many turns")
    ap.add_argument("--layout", choices=["random", "beginner"], default="random")
    ap.add_argument("--out", type=Path, help="write one JSON line per game to this file")
    ap.add_argument("--save-games", type=Path, help="directory for replayable action logs (seed + actions)")
    ap.add_argument("--quiet", action="store_true", help="only print the summary")
    args = ap.parse_args(argv)
    args.agent_list = [a.strip() for a in args.agents.split(",") if a.strip()]
    if not 2 <= len(args.agent_list) <= 4:
        ap.error("--agents needs 2 to 4 entries")
    if args.games < 1 or args.workers < 1 or args.max_turns < 1:
        ap.error("--games, --workers and --max-turns must be positive")
    for spec in set(args.agent_list):
        try:
            load_agent(spec)
        except (ImportError, AttributeError, ValueError, TypeError) as err:
            ap.error(f"cannot load agent {spec!r}: {err}")
    return args


def _job(job: tuple[list[str], int, int, str, bool]) -> GameResult:
    agents, seed, max_turns, layout, record = job
    return play_game(agents, seed, max_turns=max_turns, layout=layout, record=record)


def game_seeds(master: int, n: int) -> list[int]:
    rng = random.Random(master)
    return [rng.getrandbits(63) for _ in range(n)]


def run(args: argparse.Namespace) -> Iterator[GameResult]:
    record = args.save_games is not None
    jobs = [
        (args.agent_list, s, args.max_turns, args.layout, record) for s in game_seeds(args.seed, args.games)
    ]
    if args.workers == 1:
        yield from map(_job, jobs)
    else:
        with Pool(args.workers) as pool:
            yield from pool.imap(_job, jobs, chunksize=max(1, len(jobs) // (args.workers * 8)))


def main(argv: list[str] | None = None) -> int:
    args = _parse(argv)
    summary = Summary()
    out = args.out.open("w", encoding="utf-8") if args.out else None
    if args.save_games:
        args.save_games.mkdir(parents=True, exist_ok=True)
    try:
        for i, result in enumerate(run(args), 1):
            summary.add(result)
            if out:
                out.write(json.dumps(result.to_json()) + "\n")
            if args.save_games and result.history is not None:
                log = {"seed": result.seed, "agents": result.agents, "layout": args.layout,
                       "actions": [{"player": p, "action": a} for p, a in result.history]}  # fmt: skip
                (args.save_games / f"game-{i:06d}.json").write_text(json.dumps(log), encoding="utf-8")
            if not args.quiet and i % max(1, args.games // 10) == 0:
                print(f"  {i}/{args.games} games", file=sys.stderr)
    finally:
        if out:
            out.close()
    print(summary.format())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
