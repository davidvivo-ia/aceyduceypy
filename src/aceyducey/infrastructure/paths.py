"""XDG-aware path resolution for persistent data."""

from __future__ import annotations

import os
from pathlib import Path

_APP_DIRNAME = "aceyducey"


def default_data_dir() -> Path:
    """Return the user-specific data directory for this application.

    Follows the XDG Base Directory Specification: uses
    ``$XDG_DATA_HOME`` when set, otherwise ``~/.local/share``.
    """
    raw = os.environ.get("XDG_DATA_HOME")
    base = Path(raw) if raw else Path.home() / ".local" / "share"
    return base / _APP_DIRNAME


def highscore_path(data_dir: Path | None = None) -> Path:
    """Resolve the file where the persistent highscore lives."""
    return (data_dir or default_data_dir()) / "highscore.json"
