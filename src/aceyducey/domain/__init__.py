"""Pure game domain: cards, deck, hand, payouts and outcomes.

Nothing in this package imports from ``application``, ``infrastructure`` or
``presentation``. The domain is the inner ring of the hexagon and must stay
free of IO, randomness sources or framework dependencies.
"""

from __future__ import annotations

from aceyducey.domain.card import Card, Rank, Suit
from aceyducey.domain.deck import build_standard_deck
from aceyducey.domain.errors import DomainError, InvalidBetError
from aceyducey.domain.hand import BetOutcome, Hand, HandResolution
from aceyducey.domain.payout import PayoutPolicy
from aceyducey.domain.probability import odds_between

__all__ = [
    "BetOutcome",
    "Card",
    "DomainError",
    "Hand",
    "HandResolution",
    "InvalidBetError",
    "PayoutPolicy",
    "Rank",
    "Suit",
    "build_standard_deck",
    "odds_between",
]
