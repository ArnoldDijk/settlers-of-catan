"""Bank and harbor trade rates."""

from __future__ import annotations

from functools import lru_cache

from ..board import RESOURCES, Layout
from ..state import GameState


@lru_cache(maxsize=256)
def _harbor_vertices(layout: Layout) -> tuple[tuple[int, str], ...]:
    return tuple(layout.harbor_vertices().items())


def trade_rates(s: GameState, player: int) -> dict[str, int]:
    """Resource -> how many of it buy one card from the bank (4, 3 or 2)."""
    kinds = {
        kind
        for v, kind in _harbor_vertices(s.layout)
        if (b := s.buildings.get(v)) is not None and b[0] == player
    }
    base = 3 if "any" in kinds else 4
    return {r: 2 if r in kinds else base for r in RESOURCES}
