"""Local watchlist — persist stock codes in ~/.astock/watchlist.json."""

from __future__ import annotations

import json
from pathlib import Path

WATCHLIST_DIR = Path.home() / ".astock"
WATCHLIST_FILE = WATCHLIST_DIR / "watchlist.json"


def _load() -> list[str]:
    if not WATCHLIST_FILE.exists():
        return []
    try:
        return json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save(codes: list[str]) -> None:
    WATCHLIST_DIR.mkdir(parents=True, exist_ok=True)
    # deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            unique.append(code)
    WATCHLIST_FILE.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")


def list_codes() -> list[str]:
    """Return the current watchlist."""
    return _load()


def add(code: str) -> bool:
    """Add a stock code. Returns True if it was newly added."""
    codes = _load()
    if code in codes:
        return False
    codes.append(code)
    _save(codes)
    return True


def remove(code: str) -> bool:
    """Remove a stock code. Returns True if it was actually present."""
    codes = _load()
    if code not in codes:
        return False
    codes.remove(code)
    _save(codes)
    return True
