# Settlers of Catan

Catan with the full rules, including player-to-player trading. The project has three parts:

- **`backend/catan_engine`**: the game engine. It uses only the Python standard library, and runs headless for simulations.
- **`backend/catan_server`**: a FastAPI server. It holds games in SQLite, authenticates each seat, and pushes each player only their own view over a WebSocket.
- **`frontend/`**: a React/TypeScript board in the Claude Design "Catan Tiles" style, served by nginx. The UI is in Dutch.

Contributors and AI agents: follow [`AGENTS.md`](AGENTS.md).

```
 browser ──► nginx (frontend container, :8081)
               ├─ static React app
               └─ /api/*, WebSocket ──► FastAPI (backend container, no host port)
                                          └─ catan_engine ◄─► SQLite (/data volume)

 catan-sim (CLI or sim container) ──► catan_engine          (no UI, no web server, no database)
```

## Play

```sh
docker compose up --build
```

1. Open http://localhost:8081 and enter 2–4 names.
2. You get one personal invite link per player. Send each player their own link.
3. Opening a link signs that browser in as that player. To test several players on one computer, open each link in a separate private window.

To use a different port, set `CATAN_PORT`, e.g. `CATAN_PORT=3000 docker compose up --build`.

Games are stored in the `catan-data` Docker volume and survive restarts.

## Simulate (headless)

Simulations use only the engine: no frontend, server or database is involved.

```sh
cd backend
uv sync
uv run catan-sim --games 1000 --agents greedy,random,random,random --seed 42 --workers 8 --out results.jsonl
```

Or in Docker (only the simulator container starts):

```sh
docker compose --profile sim run --rm sim --games 1000 --workers 4 --out /out/results.jsonl   # -> ./sim-results/
```

| Option | Meaning |
| --- | --- |
| `--agents` | 2–4 seats: `random`, `greedy` or your own `package.module:ClassName` |
| `--seed` | master seed; the same seed and agents give identical results, whatever `--workers` is |
| `--games`, `--workers`, `--max-turns`, `--layout random\|beginner` | run size and settings |
| `--out` | one JSON line per game: `seed`, `agents`, `winner` (seat), `turns`, `points`, awards, `hit_turn_cap` |
| `--save-games DIR` | replayable action logs; `catan_engine.sim.replay(log)` rebuilds the game |

The run ends with a printed summary: win rate per agent and per seat, and average game length.

### Writing an agent

An agent sees exactly what a human player sees: its own `PlayerView` (the same JSON the browser gets) plus the list of legal actions.

```python
import random
from catan_engine.actions import Action, BuildCity

class CityFirst:
    name = "city-first"

    def choose(self, view: dict, legal: list[Action], rng: random.Random) -> Action:
        cities = [a for a in legal if isinstance(a, BuildCity)]
        return cities[0] if cities else rng.choice(legal)
```

```sh
uv run catan-sim --agents mybots:CityFirst,greedy,greedy --games 500
```

`catan_engine.agents.boardinfo.BoardInfo.from_view(view)` gives helpers such as vertex production values, open spots and harbors.

Board positions in actions are integer indices; see `catan_engine.board.TOPOLOGY`.

## Develop

```sh
# backend (Python 3.11, uv)
cd backend
uv sync --extra server
CATAN_DB_PATH=./dev.db uv run uvicorn catan_server.main:app --reload --port 8000
./scripts/check.sh                          # ruff, format, mypy --strict, pytest, pip-audit
uv run python scripts/export_contract.py    # after changing API models or the projection

# frontend (proxies /api to :8000)
cd frontend
npm install
npm run dev          # http://localhost:5173
npm run gen:api      # regenerate src/api/schema.ts from src/api/openapi.json
npm run check        # type-check, tests, build, npm audit
```

## API

All endpoints are under `/api` and same-origin (nginx proxies them).

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/health` | – | liveness |
| POST | `/api/games` | – | `{players: [names]}` returns `{gameId, seats: [{playerId, name, color, joinUrl}]}` |
| POST | `/api/join` | token in body | sets the HttpOnly seat cookie; returns `{gameId, playerId}` |
| GET | `/api/games/{id}/view` | seat cookie | the caller's `PlayerView` (with `version` and `legalActions`) |
| POST | `/api/games/{id}/actions` | seat cookie | `{expectedVersion, action}`; returns the new view |
| WS | `/api/games/{id}/ws` | seat cookie, same Origin | the caller's view on connect and after every change |

Error responses:

- **401**: not joined.
- **403**: another game's cookie, or not your turn.
- **409**: stale `expectedVersion`.
- **422**: `{detail: {code}}` for a rule violation.

The full schema is in `frontend/src/api/openapi.json`.

## The state model

**`GameState`** (`catan_engine/state.py`) is the complete game: every hand, the shuffled development deck and the RNG. It exists only inside the engine and the server's database.

**`PlayerView`** (`catan_engine/projection.py`, `catan_server/models.py`) is what one player may see:

| Part | Contents |
| --- | --- |
| Shared | board (tiles, harbors, robber), buildings, roads, turn/step, dice, bank, awards, open trade offer, pending discards |
| Per player (`players[]`) | name, colour, resource *count*, development card *count*, played development cards, pieces left, visible victory points |
| Own (`hand`) | resources and development cards, split into playable and bought this turn |
| `legalActions` | everything the viewer may do right now |

Board refs are axial, pointy-top coordinates:

- `{q, r}` is a hex, and `{0, 0}` is the centre.
- Corner `k` sits at −90° + 60°·k.
- Edge `k` runs from corner `k` to corner `k+1`.
