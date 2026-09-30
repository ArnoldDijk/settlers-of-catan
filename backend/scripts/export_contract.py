"""Writes the API contract into the frontend:

  frontend/src/api/openapi.json                   -> `npm run gen:api` turns it into TypeScript types
  frontend/src/state/__fixtures__/views/p*.json   -> sample PlayerViews for frontend tests

Run after changing API models or the projection:  uv run python scripts/export_contract.py
tests/server/test_contract.py fails if the committed files are out of date.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from catan_engine import Game
from catan_engine.sample import sample_state
from catan_server.config import Settings
from catan_server.main import create_app
from catan_server.service import player_view

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def contract() -> dict[str, str]:
    """Relative path -> file content."""
    app = create_app(Settings(db_path=":memory:"))
    files = {"src/api/openapi.json": _json(app.openapi())}
    game = Game(sample_state())
    for p in game.state.players:
        view = player_view(game, p.id, version=0).model_dump(mode="json")
        files[f"src/state/__fixtures__/views/{p.id}.json"] = _json(view)
    return files


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    for rel, content in contract().items():
        path = FRONTEND / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote frontend/{rel}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
