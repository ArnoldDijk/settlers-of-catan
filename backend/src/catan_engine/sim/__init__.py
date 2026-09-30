"""Headless simulations: no UI, web server or database involved."""

from .runner import GameResult, play_game, replay

__all__ = ["GameResult", "play_game", "replay"]
