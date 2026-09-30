"""Plays one game between agents."""

from __future__ import annotations

import random
from dataclasses import asdict, dataclass, field
from typing import Any

from ..actions import action_from_dict
from ..agents import load_agent
from ..engine import Game, RuleError
from ..state import Config

#: Simulation default: bots may make at most two trade offers per turn, so games can't stall.
SIM_CONFIG = Config(trade_offers_per_turn=2)


@dataclass(slots=True)
class GameResult:
    seed: int
    agents: list[str]
    winner: int | None  # seat index; None if the turn cap was hit
    turns: int
    points: list[int]  # final points per seat, including hidden VP cards
    longest_road: int | None
    largest_army: int | None
    hit_turn_cap: bool
    actions: int
    history: list[tuple[str, dict[str, Any]]] | None = field(default=None, repr=False)

    def to_json(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("history")
        return d


def play_game(
    agent_specs: list[str],
    seed: int,
    *,
    max_turns: int = 500,
    layout: str = "random",
    config: Config = SIM_CONFIG,
    record: bool = False,
) -> GameResult:
    """Play one game. Fully determined by `seed` and the agents."""
    agents = [load_agent(spec)() for spec in agent_specs]
    names = [f"{a.name}-{i + 1}" for i, a in enumerate(agents)]
    game = Game.new(names, seed, layout=layout, config=config, record=record)
    agent_rng = random.Random(seed ^ 0x5EED)
    seat = {p.id: i for i, p in enumerate(game.state.players)}
    actions = 0
    action_cap = max_turns * 200  # guards against an agent that never ends its turn
    while not game.finished and game.state.turn_number <= max_turns and actions < action_cap:
        pid = game.pending_actors()[0]
        legal = game.legal_actions(pid)
        action = agents[seat[pid]].choose(game.view(pid), legal, agent_rng)
        try:
            game.apply(pid, action)
        except RuleError as err:
            raise RuleError(
                err.code, f"agent {agent_specs[seat[pid]]!r} played an illegal {action!r}"
            ) from err
        actions += 1
    s = game.state
    return GameResult(
        seed=seed,
        agents=list(agent_specs),
        winner=s.winner,
        turns=s.turn_number,
        points=[game.points(p.id) for p in s.players],
        longest_road=s.longest_road,
        largest_army=s.largest_army,
        hit_turn_cap=not game.finished,
        actions=actions,
        history=game.history,
    )


def replay(log: dict[str, Any], config: Config = SIM_CONFIG) -> Game:
    """Rebuild a game from a --save-games log (seed + actions)."""
    names = [f"seat-{i + 1}" for i in range(len(log["agents"]))]
    game = Game.new(names, log["seed"], layout=log.get("layout", "random"), config=config, record=True)
    for step in log["actions"]:
        game.apply(step["player"], action_from_dict(step["action"]))
    return game
