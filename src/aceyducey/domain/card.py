"""Cards: rank, suit, immutable card value object."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum


class Rank(IntEnum):
    """Card rank, two through ace.

    Values are aligned with the original BASIC range 2..14 so that
    spread arithmetic stays trivial.
    """

    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def label(self) -> str:
        """One- or two-character glyph used when drawing the card."""
        return _RANK_LABELS[self]

    @property
    def spanish_name(self) -> str:
        """Long Spanish name, used for user-facing prose."""
        return _RANK_SPANISH[self]


class Suit(Enum):
    """The four French suits, with display metadata."""

    SPADES = ("♠", False)
    HEARTS = ("♥", True)
    DIAMONDS = ("♦", True)
    CLUBS = ("♣", False)

    @property
    def symbol(self) -> str:
        return self.value[0]

    @property
    def is_red(self) -> bool:
        return self.value[1]


@dataclass(frozen=True, slots=True)
class Card:
    """Immutable card value object.

    Cards order by ``rank`` only, intentionally ignoring suit so that
    ``sorted((card_a, card_b))`` returns the low/high pair the game needs.
    Equality and hashing, however, take both rank and suit into account so
    that the 52-card deck has 52 distinct elements.
    """

    rank: Rank
    suit: Suit

    def __lt__(self, other: Card) -> bool:
        return self.rank < other.rank

    def __le__(self, other: Card) -> bool:
        return self.rank <= other.rank

    def __gt__(self, other: Card) -> bool:
        return self.rank > other.rank

    def __ge__(self, other: Card) -> bool:
        return self.rank >= other.rank

    def __str__(self) -> str:
        return f"{self.rank.label}{self.suit.symbol}"


_RANK_LABELS: dict[Rank, str] = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K",
    Rank.ACE: "A",
}

_RANK_SPANISH: dict[Rank, str] = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "JOTA",
    Rank.QUEEN: "REINA",
    Rank.KING: "REY",
    Rank.ACE: "AS",
}
