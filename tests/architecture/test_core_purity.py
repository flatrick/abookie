"""Core never reads the system clock directly; time comes from the Clock port.

import-linter already forbids ``time`` in core. ``datetime`` is allowed because
core needs its types, so its clock-reading calls are checked here instead.
"""

import ast
from pathlib import Path

import pytest

import abookie.core

pytestmark = pytest.mark.unit

CORE_DIR = Path(abookie.core.__file__).resolve().parent
FORBIDDEN = {
    ("datetime", "now"),
    ("datetime", "today"),
    ("datetime", "utcnow"),
    ("date", "today"),
}


def _class_aliases(tree: ast.Module) -> dict[str, str]:
    """Map local names to ``datetime``/``date`` for ``from datetime import ...``."""
    aliases = {"datetime": "datetime", "date": "date"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "datetime":
            for name in node.names:
                if name.name in ("datetime", "date"):
                    aliases[name.asname or name.name] = name.name
    return aliases


def _clock_reads(source: str, filename: str) -> list[str]:
    tree = ast.parse(source, filename=filename)
    aliases = _class_aliases(tree)
    found: list[str] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        owner = node.func.value
        owner_name = (
            owner.id
            if isinstance(owner, ast.Name)
            else owner.attr
            if isinstance(owner, ast.Attribute)
            else None
        )
        cls = aliases.get(owner_name or "")
        if cls is not None and (cls, node.func.attr) in FORBIDDEN:
            found.append(f"{filename}:{node.lineno}: {cls}.{node.func.attr}()")
    return found


@pytest.mark.parametrize(
    "line",
    [
        "datetime.now()",
        "datetime.datetime.now()",
        "datetime.today()",
        "datetime.utcnow()",
        "date.today()",
        "from datetime import datetime as dt\ndt.now()",
    ],
)
def test_detector_flags_clock_reads(line: str) -> None:
    assert _clock_reads(line, "example.py")


def test_detector_allows_other_datetime_use() -> None:
    assert not _clock_reads("datetime(2026, 1, 1)\nclock.now()", "example.py")


def test_core_does_not_read_system_clock() -> None:
    offenders = [
        hit
        for path in sorted(CORE_DIR.rglob("*.py"))
        for hit in _clock_reads(path.read_text(), str(path.relative_to(CORE_DIR)))
    ]
    assert offenders == []
