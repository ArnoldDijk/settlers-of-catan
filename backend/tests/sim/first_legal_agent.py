"""A custom agent used to test loading agents via 'module:Class'."""

from __future__ import annotations

import random
from typing import Any

from catan_engine.actions import Action


class FirstLegalAgent:
    name = "first-legal"

    def choose(self, view: dict[str, Any], legal: list[Action], rng: random.Random) -> Action:
        return legal[-1] if view["turn"]["step"] == "action" else legal[0]
