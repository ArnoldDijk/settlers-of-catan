"""App factory. Run with: uvicorn catan_server.main:app"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .api import games, ws
from .config import Settings
from .realtime import Hub
from .store import Store


class BodyLimit:
    """Rejects request bodies over `limit` bytes (413) before they are parsed."""

    def __init__(self, app: ASGIApp, limit: int) -> None:
        self.app = app
        self.limit = limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        declared = dict(scope.get("headers", [])).get(b"content-length")
        if declared is not None and (not declared.isdigit() or int(declared) > self.limit):
            await _reject(send)
            return
        seen = 0

        async def limited() -> Message:
            nonlocal seen
            msg = await receive()
            if msg["type"] == "http.request":
                seen += len(msg.get("body", b""))
                if seen > self.limit:
                    raise _TooLarge
            return msg

        try:
            await self.app(scope, limited, send)
        except _TooLarge:
            await _reject(send)


class _TooLarge(Exception):
    pass


async def _reject(send: Send) -> None:
    body = b'{"detail":{"code":"bodyTooLarge","detail":"Request body too large"}}'
    headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]
    await send({"type": "http.response.start", "status": 413, "headers": headers})
    await send({"type": "http.response.body", "body": body})


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.store = Store(settings.db_path)
        yield
        app.state.store.close()

    app = FastAPI(title="Catan API", version="0.1.0", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.settings = settings
    app.state.hub = Hub()
    app.include_router(games.router)
    app.include_router(ws.router)
    app.add_middleware(BodyLimit, limit=settings.max_body_bytes)
    return app


app = create_app()
