# AGENTS.md

Instructions for AI coding agents (and humans) working in this repository. Read this before making changes. The rules here are requirements, not suggestions.

## Project

Settlers of Catan ("Kolonisten van Catan") with the full rules, including player trading. The UI is in Dutch. See `README.md` for architecture, the API and the state model.

- `backend/`: Python 3.11, one uv project.
  - `src/catan_engine/`: the game engine. **Standard library only.**
    - `board.py`: topology and layouts.
    - `state.py`: `GameState`.
    - `actions.py`
    - `engine.py`: `Game.apply`, `legal_actions`, `pending_actors`.
    - `rules/`
    - `projection.py`: `to_player_view`.
    - `serialize.py`
    - `agents/`: the bot interface, plus random and greedy bots.
    - `sim/`: the `catan-sim` CLI.
  - `src/catan_server/`: FastAPI.
    - `models.py`: wire models, which double as the response allowlist.
    - `wire.py`: engine actions ↔ API actions.
    - `service.py`, `store.py` (SQLite), `auth.py`, `realtime.py`, `api/`.
  - `scripts/check.sh`: the backend quality gate.
  - `scripts/export_contract.py`: writes the OpenAPI schema and fixtures into the frontend.
  - `tests/engine`, `tests/sim`, `tests/server`.
- `frontend/`: React 19 + TypeScript (strict) + Vite, served by nginx, which also proxies `/api`.
  - `src/api/`:
    - `openapi.json` (exported by the backend) and `schema.ts` (generated from it).
    - `client.ts`: the HTTP client.
    - `useGame.ts`: WebSocket plus actions.
  - `src/state/`: `types.ts` (re-exports the generated types), `selectors.ts`, `__fixtures__/` (backend-exported views, for tests only).
  - `src/board/`: SVG board, geometry, clickable `targets`, and the design's SVG `<defs>`.
  - `src/ui/`: panels, `ActionPanel` and the design-system `Button`.
  - `src/pages/`: Lobby, Join and Game. `src/tiles/`: the "Catan Tiles" design sheet.
- `docker-compose.yml`:
  - `frontend`: port `${CATAN_PORT:-8081}`.
  - `backend`: no host port, SQLite on the `catan-data` volume.
  - `sim`: profile `sim`, writes to `./sim-results`.

## Commands

| Where | Command | What it does |
| --- | --- | --- |
| `backend/` | `uv sync --extra server` | install exact locked dependencies |
| `backend/` | `./scripts/check.sh` | **ruff, ruff format, mypy --strict, pytest, pip-audit; must pass** |
| `backend/` | `uv run pytest -m slow -s` | benchmarks (games/s) |
| `backend/` | `uv run python scripts/export_contract.py` | refresh `frontend/src/api/openapi.json` and the fixtures |
| `backend/` | `uv run catan-sim --help` | headless simulations |
| `frontend/` | `npm ci` | install exact locked dependencies |
| `frontend/` | `npm run gen:api` | regenerate `src/api/schema.ts` from `openapi.json` |
| `frontend/` | `npm run check` | **type check, tests, build, npm audit; must pass** |
| `frontend/` | `npm run dev` | dev server; proxies `/api` to a backend on :8000 |
| root | `docker compose up --build` | build (Docker builds run the tests) and start frontend + backend |
| root | `docker compose --profile sim run --rm sim …` | run simulations in a container |

## Definition of done

A change is finished only when all of these hold:

1. **Both quality gates pass:** `backend/scripts/check.sh` and `frontend: npm run check`. That covers lint, strict types, tests and a dependency audit with no moderate-or-higher vulnerabilities. Don't skip, disable or weaken a failing test to get green; fix the cause, or explain why the test is wrong and change it deliberately.
2. **New or changed behaviour has tests** (see Testing).
3. **The contract is current.** If you changed API models, the projection or the sample state:
   - Run `export_contract.py`, then `npm run gen:api`.
   - Commit the results.
   - `tests/server/test_contract.py` fails if you forget.
4. **UI changes were looked at in a browser, with a real backend:**
   - Create a game and open at least two seats in separate private windows.
   - Check the step you changed, the Tegelset page, a wide screen and about 500px width.
   - Type checks don't prove a UI works.
5. **If you touched Docker or nginx, the stack was rebuilt and checked:** `docker compose up --build`, then play a move, and confirm the backend has no host port and the security headers are present.
6. **Docs match the code.** Update `README.md` and this file when you change structure, commands, the API or rules.

When you report back, say exactly what you ran and what passed. If something could not be verified, say so; never claim a check you did not run.

## Game engine rules

- **All state changes go through `Game.apply()`.** No other code mutates `GameState`: not the server, not agents, not tests of higher layers. Rule helpers in `rules/` only read state.
- **The engine stays standard-library only** and never imports `catan_server`, so simulations run with no web, database or UI dependencies. `tests/engine/test_stdlib_only.py` enforces this.
- **Randomness comes only from `state.rng`,** which is seeded per game. Same seed and same actions give the same game; `--workers` must never change results. Tests check determinism.
- **`legal_actions()` and `apply()` must agree.** Every listed action is accepted; `test_every_listed_legal_action_is_accepted` checks this. Illegal moves raise `RuleError(code)`, and codes are stable because the API and UI use them.
- Keep the invariants: 19 cards per resource, 25 development cards, piece limits, the distance rule, road connectivity. `tests/engine/test_invariants.py` checks them after every action in many seeded bot games. Extend it when you add rules.
- **Agents only get a `PlayerView`** (`game.view(pid)`) and the legal actions, never `GameState`. That way simulations can't cheat and bots play by human information.

## Testing

- Backend: **pytest**. Frontend: **Vitest** (`src/**/*.test.ts`, next to the code).
- **Every rule has a legal-case test and a test for each illegal case.**
- A bug fix starts with a failing test that reproduces the bug.
- **Every new piece of hidden information needs a leak test.** That is any field only some players may see: in `tests/engine/test_projection.py`, and for the API in `tests/server/test_api.py`. The test must prove the field is absent from other players' views.
- **Security boundaries are tested and must not be loosened without an explicit reason in the commit message:**
  - `tests/server/`: auth (401 and 403), acting for another player, stale versions, validation, body size, WebSocket Origin and cookie.
  - `frontend/src/security.test.ts`.
- Keep tests deterministic: seeded RNGs, no real network in unit tests, no sleeping.

## Security

### Hidden information (the core rule)

Each player may only know their own cards.

- **`GameState` never leaves the server.** It is stored in SQLite and never returned.
- **Everything a player receives is built by `service.player_view()`:** the engine's `to_player_view`, validated against `models.PlayerView` (`extra="forbid"`).
  - A field missing from the model can't leak.
  - New fields default to hidden. When you add one, decide explicitly: shared, public per player (`PublicPlayer`), private (`Hand`), or server-only. Then add a leak test.
- **The frontend consumes only `PlayerView`.**
  - It never derives or displays hidden information, including guesses at an opponent's hand.
  - Test fixtures (`src/state/__fixtures__/`) are imported only by tests.
- WebSocket pushes send each connection the view of *its own* seat.

### Authentication

- Seats are authenticated by a random join token (`secrets.token_urlsafe(32)`).
- **Only the token's SHA-256 is stored.** Tokens and cookies are never logged or echoed.
- The join link carries the token in the URL **fragment**. The Join page removes it from the address bar before calling `/api/join`.
- The seat cookie is `HttpOnly`, `Secure`, `SameSite=Strict`, `Path=/api`, one per game.
  - Frontend code never reads or stores it.
  - No `localStorage`, `sessionStorage`, IndexedDB or `document.cookie`.
- Every request resolves `(game, player)` from the cookie. The path's game must match (403 otherwise), and actions are only applied for that player.
- CSRF and WebSockets:
  - JSON bodies are required, and `SameSite=Strict` is set.
  - WebSockets check that `Origin` matches `Host`, and nginx passes `Host` through.
- **Known gaps:**
  - Anyone can create games (no rate limiting).
  - One uvicorn worker, because WebSocket fan-out is in-process.
  - There are no accounts, so a leaked invite link gives access to that seat.

### Code

- Treat all input as untrusted:
  - Strict Pydantic models with limits (names, token format, game id pattern, 16 KB body limit) on the server.
  - `unknown` plus narrowing in the client.
  - Validate and encode anything that goes into a URL.
- Render text through React; never build HTML strings.
  - `dangerouslySetInnerHTML` is allowed **only** in `board/SvgDefs.tsx`, for the static design defs. Never pass it data.
  - No `eval`, `new Function`, or `innerHTML =`.
- The frontend talks only to its own origin (`/api`, same-host WebSocket). External resources are Google Fonts only.
- No secrets in the repo, bundles or images. Configuration comes from environment variables (`CATAN_DB_PATH`, `CATAN_COOKIE_SECURE`).
- Python library code has no `assert` for control flow (asserts are stripped under `-O`). Use explicit checks.

### Dependencies and infrastructure

- Add a dependency only if it clearly earns its place. The engine has none.
- Commit `uv.lock` and `package-lock.json`. Docker uses `uv sync --frozen` and `npm ci`.
- `pip-audit` and `npm audit --audit-level=moderate` stay clean. Upgrade to patched versions; don't add ignores.
- **Docker:**
  - Keep multi-stage builds. Each image's test stage must pass before the image builds.
  - Runtime images hold no build tools, source or dev dependencies, and run as a non-root user.
  - The backend runs `read_only`, with `cap_drop: ALL` and `no-new-privileges`, and has no host port.
- **nginx:**
  - Every location includes `security-headers.conf` (CSP without `unsafe-inline`, `nosniff`, `no-referrer`, `DENY` framing). nginx drops server-level `add_header` in locations that set their own, hence the include.
  - Unknown paths fall back to `index.html`.

## Code conventions

- **Python:** ruff (config in `pyproject.toml`), `mypy --strict`, type hints everywhere, no `type: ignore` without a reason. The engine uses dataclasses and integer board indices; Pydantic appears only at the API boundary.
- **TypeScript:**
  - Strict, no `any`. Don't use `@ts-ignore`; explain any unavoidable `@ts-expect-error`.
  - API types come from the generated `schema.ts`, via `state/types.ts`; don't hand-write copies.
- **Rules live in the engine, once.** The frontend offers exactly what `legalActions` lists and lets the server decide; display-only derivations such as `tradeRates` are allowed. Server routes contain no rules either.
- Match the surrounding code: small focused modules, named exports, function components, comments only where the *why* isn't obvious.
- Board coordinates are axial `{q, r}`, pointy-top. Corner `k` sits at −90° + 60°·k, and edge `k` runs from corner `k` to `k+1`. Use the helpers (`board.TOPOLOGY`, `frontend/src/board/geometry.ts`); don't hand-compute positions.
- **Design fidelity.** Visuals come from the Claude Design project "Catan Tiles.dc.html".
  - Keep `board/defsMarkup.ts` verbatim.
  - Use design tokens (`var(--bb-*)`, `--space-*`, `--radius-*`) instead of new hard-coded colours.
  - Reuse `ui/Button.tsx` and the existing card styles.
- **UI copy is Dutch.** Code, identifiers, comments, error codes and commit messages are English.
- Accessibility:
  - Controls are real `<button>`, `<a>`, `<input>` or `<select>` elements. Clickable SVG targets have `role="button"`, `tabIndex`, Enter/Space handling and an `aria-label`.
  - Focus is visible, and colour is never the only signal.
  - Animations respect `prefers-reduced-motion`.
- Layout works from about 500px wide up, with no horizontal page scroll.

## Workflow and git

- Work on a branch; don't commit directly to `main`. Keep commits small and focused, with imperative messages ("Add trade offer to PlayerView").
- Don't commit `node_modules/`, `dist/`, `.venv/`, databases, `sim-results/` output or local env files.
- Don't reformat or refactor unrelated code in a feature change.
- Ask before destructive or hard-to-reverse actions: deleting files you didn't create, force-pushing, rewriting history, dropping the `catan-data` volume, changing ports or other shared infrastructure. Other services may already use port 8080 on developer machines.
- When a requirement is ambiguous and the choice matters, ask instead of guessing.
