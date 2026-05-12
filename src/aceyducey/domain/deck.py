"""Standard 52-card deck factory."""

from __future__ import annotations

from aceyducey.domain.card import Card, Rank, Suit


def build_standard_deck() -> list[Card]:
    """Return a freshly ordered deck of 52 distinct cards.

    Order is deterministic: spades ascending, then hearts, then diamonds,
    then clubs. Callers shuffle through their injected RNG.
    """
    return [Card(rank, suit) for suit in Suit for rank in Rank]
