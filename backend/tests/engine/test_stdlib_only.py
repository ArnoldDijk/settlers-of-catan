"""The engine must stay importable without any third-party package (headless simulations)."""

import ast
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[2] / "src" / "catan_engine"


def test_engine_imports_only_the_standard_library_and_itself() -> None:
    offenders = []
    for path in ENGINE.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                if top not in sys.stdlib_module_names and top != "catan_engine":
                    offenders.append(f"{path.relative_to(ENGINE)}: {name}")
    assert offenders == []
