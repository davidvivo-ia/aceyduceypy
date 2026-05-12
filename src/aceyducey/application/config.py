"""Game configuration value object."""

from __future__ import annotations

from dataclasses import dataclass, field

from aceyducey.domain import PayoutPolicy


@dataclass(frozen=True, slots=True)
class GameConfig:
    """All knobs that change behaviour without touching code."""

    starting_balance: int = 100
    seed: int | None = None
    payout_policy: PayoutPolicy = field(default_factory=PayoutPolicy.tiered)
    show_odds: bool = True

    @property
    def is_classic(self) -> bool:
        return self.payout_policy.name == "classic"
