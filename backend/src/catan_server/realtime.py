"""Pushes each connected player their own fresh view after every change (single process)."""

from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from fastapi import WebSocket


class Hub:
    def __init__(self) -> None:
        self._conns: dict[str, set[tuple[str, WebSocket]]] = defaultdict(set)

    def add(self, game_id: str, player_id: str, ws: WebSocket) -> None:
        self._conns[game_id].add((player_id, ws))

    def remove(self, game_id: str, player_id: str, ws: WebSocket) -> None:
        self._conns[game_id].discard((player_id, ws))
        if not self._conns[game_id]:
            del self._conns[game_id]

    def connections(self, game_id: str) -> int:
        return len(self._conns.get(game_id, ()))

    async def broadcast(self, game_id: str, view_for: Callable[[str], dict[str, Any]]) -> None:
        """Send every connection the view of *its own* player."""
        conns = list(self._conns.get(game_id, ()))

        async def send(pid: str, ws: WebSocket) -> None:
            try:
                await ws.send_json(view_for(pid))
            except Exception:  # a dead socket must not break the others
                self.remove(game_id, pid, ws)
                with contextlib.suppress(Exception):
                    await ws.close()

        await asyncio.gather(*(send(pid, ws) for pid, ws in conns))
