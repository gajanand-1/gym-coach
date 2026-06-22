"""
Thin JSON persistence layer.
Each feature stores its data in a separate file under DATA_DIR.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any = None) -> Any:
    """Load a JSON file, returning `default` if it doesn't exist."""
    if not path.exists():
        return default if default is not None else {}
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: Path, data: Any) -> None:
    """Persist `data` to a JSON file (creates parent dirs if needed)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def append_to_list(path: Path, entry: Any) -> list:
    """Append a single entry to a JSON array file and return the full list."""
    existing: list = load_json(path, default=[])
    existing.append(entry)
    save_json(path, existing)
    return existing


def load_list(path: Path) -> list:
    """Load a JSON file that should contain a list."""
    return load_json(path, default=[])
