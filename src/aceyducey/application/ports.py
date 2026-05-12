"""Ports the application layer needs from the outside world.

Each port is a ``Protocol`` so adapters can satisfy it structurally
without inheritance.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class RngPort(Protocol):
    """Random number source used by the game session."""

    def shuffle(self, deck: list[object]) -> None: ...

    def random(self) -> float: ...


class HighscorePort(Protocol):
    """Persistent record of the highest balance ever reached."""

    def load(self) -> int: ...

    def save(self, peak: int) -> None: ...


class Clock(Protocol):
    """Wall-clock source, isolated for tests."""

    def now(self) -> datetime: ...
