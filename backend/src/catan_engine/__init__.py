"""Headless Catan game engine. Standard library only: no web, database or UI dependencies."""

from .actions import Action, action_from_dict, action_to_dict
from .engine import Game, RuleError
from .state import Config, GameState

__all__ = ["Action", "Config", "Game", "GameState", "RuleError", "action_from_dict", "action_to_dict"]
