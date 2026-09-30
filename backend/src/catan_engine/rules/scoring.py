"""Victory points."""

from __future__ import annotations

from ..state import GameState


def public_points(s: GameState, player: int) -> int:
    """Points everyone can see: buildings and awards."""
    pts = sum(2 if kind == "city" else 1 for p, kind in s.buildings.values() if p == player)
    if s.longest_road == player:
        pts += 2
    if s.largest_army == player:
        pts += 2
    return pts


def total_points(s: GameState, player: int) -> int:
    """Including hidden victory point cards."""
    pl = s.players[player]
    return public_points(s, player) + pl.dev_cards["victoryPoint"] + pl.new_dev_cards["victoryPoint"]
