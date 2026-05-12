"""Pure helpers that render cards as multi-line ASCII art.

The art is deliberately framework-agnostic: it returns a list of strings,
which the Textual widget mounts with Rich markup and the plain-text
driver prints to stdout.
"""

from __future__ import annotations

from aceyducey.domain import Card

CARD_WIDTH: int = 11
CARD_HEIGHT: int = 7

_SINGLE = (
    "┌─────────┐",
    "│{tl}       │",
    "│         │",
    "│    {s}    │",
    "│         │",
    "│       {tr}│",
    "└─────────┘",
)
_DOUBLE = (
    "╔═════════╗",
    "║{tl}       ║",
    "║         ║",
    "║    {s}    ║",
    "║         ║",
    "║       {tr}║",
    "╚═════════╝",
)


def render_card(card: Card, *, highlighted: bool = False) -> list[str]:
    """Return the seven lines that draw a single card.

    When ``highlighted`` is true, the third (verdict) card style is used:
    a double-line border that stands out against the two bracket cards.
    """
    template = _DOUBLE if highlighted else _SINGLE
    label = card.rank.label
    return [
        line.format(tl=label.ljust(2), tr=label.rjust(2), s=card.suit.symbol) for line in template
    ]


def render_back() -> list[str]:
    return [
        "┌─────────┐",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "│░░░░░░░░░│",
        "└─────────┘",
    ]


def render_row(cards: list[list[str]], *, gap: int = 2) -> str:
    """Join several card art blocks horizontally."""
    if not cards:
        return ""
    sep = " " * gap
    return "\n".join(sep.join(row) for row in zip(*cards, strict=False))
