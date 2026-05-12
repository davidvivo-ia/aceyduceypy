"""Real-time clock adapter."""

from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """Wall-clock adapter returning UTC timestamps."""

    def now(self) -> datetime:
        return datetime.now(UTC)
