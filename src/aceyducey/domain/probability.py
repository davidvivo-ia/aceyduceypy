"""Probability helpers for Acey-Ducey.

Once two cards have been revealed, exactly 50 cards remain in a 52-card
deck. Of those, only cards whose rank is strictly between ``low`` and
``high`` win the bet; ranks equal to either boundary lose (edge match).
"""

from __future__ import annotations

from aceyducey.domain.card import Rank

_CARDS_PER_RANK: int = 4
_DECK_AFTER_TWO_REVEALED: int = 50


def ranks_strictly_between(low: Rank, high: Rank) -> int:
    """Number of distinct ranks ``r`` with ``low < r < high``.

    Returns 0 if ``low >= high`` or if the cards are consecutive.
    """
    spread = int(high) - int(low) - 1
    return max(spread, 0)


def odds_between(
    low: Rank,
    high: Rank,
    *,
    remaining_cards: int = _DECK_AFTER_TWO_REVEALED,
) -> float:
    """Probability that the next card lands strictly between low and high.

    The default ``remaining_cards = 50`` matches a freshly shuffled 52-card
    deck after revealing exactly two cards.
    """
    if remaining_cards <= 0:
        return 0.0
    favorable = ranks_strictly_between(low, high) * _CARDS_PER_RANK
    return favorable / remaining_cards
