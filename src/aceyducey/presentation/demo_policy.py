"""Deterministic betting policy used by the ``--demo`` mode.

The policy is intentionally simple so its behaviour is easy to predict and
verify: bet a fixed fraction of the balance, scaled by win probability.
Used both by the plain driver (for CI smoke) and by the Textual demo.
"""

from __future__ import annotations

from dataclasses import dataclass

_BASE_PERCENT = 10  # tenths of a percent of balance
_MIN_PROB_TO_BET = 0.30
_DEMO_HAND_LIMIT = 50


@dataclass(frozen=True, slots=True)
class DemoBettingPolicy:
    """Decide how much the bot bets given probability and balance.

    Arithmetic stays in integers so the bot survives arbitrarily large
    compounded balances without overflowing to ``float``. The percentage
    is scaled by ``(1 + edge)`` quantised to one decimal place.
    """

    base_percent: int = _BASE_PERCENT
    min_probability: float = _MIN_PROB_TO_BET
    hand_limit: int = _DEMO_HAND_LIMIT

    def decide(self, *, probability: float, multiplier: int, balance: int) -> int:
        if probability < self.min_probability:
            return 0
        edge = probability * multiplier - (1 - probability)
        if edge <= 0:
            return 0
        edge_factor = 10 + min(int(edge * 10), 30)  # capped so bets stay sane
        proposed = (balance * self.base_percent * edge_factor) // 1000
        return max(1, min(proposed, balance))
