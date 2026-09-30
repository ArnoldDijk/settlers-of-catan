"""Play games with the built-in bots for property-style tests."""

from __future__ import annotations

import random
from collections.abc import Callable

from catan_engine import Game
from catan_engine.agents.greedy_agent import GreedyAgent
from catan_engine.agents.random_agent import RandomAgent
from catan_engine.sim.runner import SIM_CONFIG


def play_some(
    seed: int,
    actions: int = 10_000,
    players: int = 4,
    on_step: Callable[[Game], None] | None = None,
    max_turns: int = 400,
) -> Game:
    rng = random.Random(seed)
    agents = [GreedyAgent() if (seed + i) % 2 else RandomAgent() for i in range(players)]
    g = Game.new([f"P{i}" for i in range(players)], seed, config=SIM_CONFIG)
    seat = {p.id: i for i, p in enumerate(g.state.players)}
    for _ in range(actions):
        if g.finished or g.state.turn_number > max_turns:
            break
        pid = g.pending_actors()[0]
        g.apply(pid, agents[seat[pid]].choose(g.view(pid), g.legal_actions(pid), rng))
        if on_step:
            on_step(g)
    return g
