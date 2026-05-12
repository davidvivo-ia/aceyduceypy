"""Events emitted by the game session.

These are the contract between application and presentation: the TUI never
reads private session state; it reacts to events.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from aceyducey.application.stats import SessionStats
from aceyducey.domain import Card, Hand, HandResolution

RedealReason = Literal["pair", "consecutive"]


@dataclass(frozen=True, slots=True)
class GameStartedEvent:
    starting_balance: int
    previous_highscore: int


@dataclass(frozen=True, slots=True)
class DealtHandEvent:
    hand: Hand
    balance: int
    win_probability: float
    multiplier: int


@dataclass(frozen=True, slots=True)
class RedealEvent:
    reason: RedealReason
    revealed: tuple[Card, Card]


@dataclass(frozen=True, slots=True)
class HandResolvedEvent:
    resolution: HandResolution
    balance: int


@dataclass(frozen=True, slots=True)
class GameEndedEvent:
    stats: SessionStats
    new_highscore: bool


GameEvent = GameStartedEvent | DealtHandEvent | RedealEvent | HandResolvedEvent | GameEndedEvent
