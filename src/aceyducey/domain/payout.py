"""Payout policy: how much a winning bet pays back.

Two policies are provided. ``PayoutPolicy.flat()`` mirrors the BASIC
original (always 1x). ``PayoutPolicy.tiered()`` rewards risk: the tighter
the spread between the two revealed cards, the larger the multiplier.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aceyducey.domain.card import Rank
from aceyducey.domain.probability import ranks_strictly_between


@dataclass(frozen=True, slots=True)
class PayoutPolicy:
    """Maps the spread between two revealed cards to a payout multiplier.

    ``tiers`` is a tuple of ``(max_spread, multiplier)`` pairs ordered by
    ascending ``max_spread``. ``fallback`` is the multiplier used when no
    tier matches (i.e. spread is wider than every threshold).
    """

    name: str
    tiers: tuple[tuple[int, int], ...]
    fallback: int = field(default=1)

    def multiplier_for_spread(self, spread: int) -> int:
        for max_spread, multiplier in self.tiers:
            if spread <= max_spread:
                return multiplier
        return self.fallback

    def multiplier_for_cards(self, low: Rank, high: Rank) -> int:
        return self.multiplier_for_spread(ranks_strictly_between(low, high))

    @staticmethod
    def flat() -> PayoutPolicy:
        """Classic Acey-Ducey: every winning bet pays 1x."""
        return PayoutPolicy(name="classic", tiers=(), fallback=1)

    @staticmethod
    def tiered() -> PayoutPolicy:
        """Risk-adjusted 2026 default: tight spreads pay more."""
        return PayoutPolicy(
            name="tiered",
            tiers=((1, 5), (3, 3), (6, 2)),
            fallback=1,
        )
