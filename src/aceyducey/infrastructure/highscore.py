"""JSON-backed highscore repository."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class JsonHighscoreRepository:
    """Stores the highest peak balance ever achieved in a JSON file.

    The file is created lazily on the first ``save()`` and is resilient
    to corruption: if the file cannot be parsed, ``load()`` falls back
    to ``0`` and emits a single warning log entry.
    """

    __slots__ = ("_path",)

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> int:
        try:
            text = self._path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return 0
        except OSError:
            logger.warning("highscore: unable to read %s", self._path)
            return 0
        try:
            payload = json.loads(text)
            return int(payload.get("peak", 0))
        except (json.JSONDecodeError, ValueError, TypeError):
            logger.warning("highscore: corrupt file at %s, resetting", self._path)
            return 0

    def save(self, peak: int) -> None:
        previous = self._read_payload()
        runs = _coerce_int(previous.get("runs"), default=0) + 1
        payload = {
            "peak": max(_coerce_int(previous.get("peak"), default=0), int(peak)),
            "runs": runs,
            "last_played": datetime.now(UTC).isoformat(timespec="seconds"),
        }
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        except OSError:
            logger.warning("highscore: unable to write %s", self._path)

    def _read_payload(self) -> dict[str, object]:
        try:
            decoded = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
            return {}
        if isinstance(decoded, dict):
            return {str(k): v for k, v in decoded.items()}
        return {}


def _coerce_int(value: object, *, default: int) -> int:
    """Best-effort conversion of a JSON-decoded value into an int."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default
