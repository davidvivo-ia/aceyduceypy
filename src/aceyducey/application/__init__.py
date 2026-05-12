"""Application layer: use cases that orchestrate the domain.

This package defines the ports (``RngPort``, ``HighscorePort``, ``Clock``)
and the orchestration objects that the presentation layer drives. It
imports from ``domain`` but never from ``infrastructure`` or
``presentation``.
"""

from __future__ import annotations

from aceyducey.application.config import GameConfig
from aceyducey.application.events import (
    DealtHandEvent,
    GameEndedEvent,
    GameEvent,
    GameStartedEvent,
    HandResolvedEvent,
    RedealEvent,
)
from aceyducey.application.ports import Clock, HighscorePort, RngPort
from aceyducey.application.session import GameSession
from aceyducey.application.stats import SessionStats

__all__ = [
    "Clock",
    "DealtHandEvent",
    "GameConfig",
    "GameEndedEvent",
    "GameEvent",
    "GameSession",
    "GameStartedEvent",
    "HandResolvedEvent",
    "HighscorePort",
    "RedealEvent",
    "RngPort",
    "SessionStats",
]
