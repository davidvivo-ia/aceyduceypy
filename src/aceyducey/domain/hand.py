"""A hand of Acey-Ducey: two bracket cards and one verdict card."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from aceyducey.domain.card import Card
from aceyducey.domain.payout import PayoutPolicy
from aceyducey.domain.probability import ranks_strictly_between


class BetOutcome(Enum):
    """How a placed bet resolved.

    ``WIN`` means the third card landed strictly between the brackets.
    ``EDGE_LOSS`` means it tied one of the brackets in rank — this counts as
    a normal loss but is reported distinctly because it is the worst-feel
    way to lose and worth surfacing in stats.
    ``LOSS`` is the generic loss (third card outside the bracket).
    """

    WIN = "win"
    LOSS = "loss"
    EDGE_LOSS = "edge_loss"


@dataclass(frozen=True, slots=True)
class HandResolution:
    """Outcome of a single bet, all derived values resolved."""

    low: Card
    high: Card
    drawn: Card
    bet: int
    outcome: BetOutcome
    multiplier: int
    delta: int  # signed change to the balance: +winnings or -bet


@dataclass(frozen=True, slots=True)
class Hand:
    """Two bracket cards waiting on a bet decision."""

    low: Card
    high: Card

    @property
    def spread(self) -> int:
        """Number of distinct ranks strictly between the brackets."""
        return ranks_strictly_between(self.low.rank, self.high.rank)

    @property
    def is_pair(self) -> bool:
        return self.low.rank == self.high.rank

    @property
    def is_consecutive(self) -> bool:
        return self.spread == 0 and not self.is_pair

    @property
    def is_playable(self) -> bool:
        """Whether a bet can be meaningfully placed on this hand."""
        return self.spread > 0

    def resolve(
        self,
        drawn: Card,
        *,
        bet: int,
        policy: PayoutPolicy,
    ) -> HandResolution:
        """Compute the outcome for a third card drawn with the given bet.

        ``bet == 0`` is a "chicken" (skip), but the resolution is still
        well-defined and produces ``delta == 0``.
        """
        if bet == 0:
            return HandResolution(
                low=self.low,
                high=self.high,
                drawn=drawn,
                bet=0,
                outcome=BetOutcome.LOSS,
                multiplier=0,
                delta=0,
            )
        if drawn.rank in (self.low.rank, self.high.rank):
            return HandResolution(
                low=self.low,
                high=self.high,
                drawn=drawn,
                bet=bet,
                outcome=BetOutcome.EDGE_LOSS,
                multiplier=0,
                delta=-bet,
            )
        if self.low.rank < drawn.rank < self.high.rank:
            multiplier = policy.multiplier_for_cards(self.low.rank, self.high.rank)
            return HandResolution(
                low=self.low,
                high=self.high,
                drawn=drawn,
                bet=bet,
                outcome=BetOutcome.WIN,
                multiplier=multiplier,
                delta=bet * multiplier,
            )
        return HandResolution(
            low=self.low,
            high=self.high,
            drawn=drawn,
            bet=bet,
            outcome=BetOutcome.LOSS,
            multiplier=0,
            delta=-bet,
        )
