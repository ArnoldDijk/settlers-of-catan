"""WebSocket: the player gets their view on connect and after every change to the game."""

from __future__ import annotations

from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from .. import service
from .deps import ws_seat

router = APIRouter(prefix="/api")


def _same_origin(ws: WebSocket) -> bool:
    origin = ws.headers.get("origin")
    host = ws.headers.get("host")
    return bool(origin and host and urlsplit(origin).netloc == host)


@router.websocket("/games/{game_id}/ws")
async def game_socket(game_id: str, ws: WebSocket) -> None:
    if not _same_origin(ws):
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        me = ws_seat(game_id, ws)
    except HTTPException:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    loaded = service.load_game(ws.app.state.store, me.game_id)
    if loaded is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await ws.accept()
    hub = ws.app.state.hub
    hub.add(me.game_id, me.player_id, ws)
    try:
        game, version = loaded
        await ws.send_json(service.player_view(game, me.player_id, version).model_dump(mode="json"))
        while True:
            await ws.receive_text()  # clients don't send anything meaningful; this detects disconnects
    except WebSocketDisconnect:
        pass
    finally:
        hub.remove(me.game_id, me.player_id, ws)
