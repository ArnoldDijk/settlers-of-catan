# Targets:
#   sim    - headless simulator (entrypoint: catan-sim). Engine only: no web server, database or UI.
#   server - FastAPI server on port 8000; state in SQLite under /data.
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /usr/local/bin/uv
WORKDIR /app

# --- Quality gate: images are only built if lint, types and tests pass ---
FROM base AS test
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra server --no-install-project
COPY . .
RUN uv sync --frozen --extra server \
 && uv run ruff check . \
 && uv run ruff format --check . \
 && uv run mypy \
 && uv run pytest -q -p no:cacheprovider \
 && touch /tested

# --- Production virtualenvs: runtime dependencies only ---
FROM base AS build-engine
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

FROM base AS build-server
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra server --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --extra server --no-editable

FROM python:3.11-slim AS runtime
RUN useradd --create-home --uid 10001 app
# Depend on the test stage so a failing test fails the build.
COPY --from=test /tested /app/.tested
ENV PATH=/app/.venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /home/app

FROM runtime AS sim
COPY --from=build-engine /app/.venv /app/.venv
USER app
ENTRYPOINT ["catan-sim"]
CMD ["--help"]

FROM runtime AS server
COPY --from=build-server /app/.venv /app/.venv
RUN mkdir /data && chown app:app /data
USER app
ENV CATAN_DB_PATH=/data/catan.db
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"]
# One worker: WebSocket fan-out is in-process.
CMD ["uvicorn", "catan_server.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-server-header"]
