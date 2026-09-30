"""The frontend's API types and fixtures must match the backend."""

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "export_contract.py"


def test_committed_contract_is_current() -> None:
    spec = importlib.util.spec_from_file_location("export_contract", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not mod.FRONTEND.is_dir():
        pytest.skip("frontend/ not present (e.g. in the backend Docker build context)")
    stale = [
        rel
        for rel, content in mod.contract().items()
        if not (mod.FRONTEND / rel).exists() or (mod.FRONTEND / rel).read_text(encoding="utf-8") != content
    ]
    assert stale == [], f"out of date, run `uv run python scripts/export_contract.py`: {stale}"
