"""The agent interface and agent loading."""

from __future__ import annotations

import importlib
import random
from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from ..actions import Action


@runtime_checkable
class Agent(Protocol):
    """Decides moves. `view` is the player's PlayerView (the same JSON the frontend gets);
    `legal` is non-empty. Must return one of `legal` (or another valid trade offer)."""

    name: str

    def choose(self, view: dict[str, Any], legal: list[Action], rng: random.Random) -> Action: ...


BUILTIN = {
    "random": "catan_engine.agents.random_agent:RandomAgent",
    "greedy": "catan_engine.agents.greedy_agent:GreedyAgent",
}


def load_agent(spec: str) -> Callable[[], Agent]:
    """Agent factory from 'random', 'greedy' or 'package.module:ClassName'."""
    target = BUILTIN.get(spec, spec)
    module_name, sep, cls_name = target.partition(":")
    if not sep or not module_name or not cls_name:
        raise ValueError(f"agent must be 'random', 'greedy' or 'module:Class', got {spec!r}")
    cls = getattr(importlib.import_module(module_name), cls_name)
    if not callable(cls):
        raise TypeError(f"{spec!r} is not a class")

    def make() -> Agent:
        agent = cls()
        if not isinstance(agent, Agent):
            raise TypeError(f"{spec!r} does not implement Agent (needs .name and .choose())")
        return agent

    return make
