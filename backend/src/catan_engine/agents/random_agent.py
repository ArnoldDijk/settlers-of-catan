"""Uniformly random legal moves (rarely trades, so games keep moving)."""

from __future__ import annotations

import random
from typing import Any

from ..actions import Action, OfferTrade


class RandomAgent:
    name = "random"

    def choose(self, view: dict[str, Any], legal: list[Action], rng: random.Random) -> Action:
        options: list[Action] = [a for a in legal if not isinstance(a, OfferTrade)]
        if not options or (len(options) < len(legal) and rng.random() < 0.05):
            options = legal
        return rng.choice(options)
