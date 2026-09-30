"""Bots for simulations. An agent only ever sees its own PlayerView (plus the legal actions)."""

from .base import Agent, load_agent

__all__ = ["Agent", "load_agent"]
