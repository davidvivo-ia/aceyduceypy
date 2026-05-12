from __future__ import annotations

from aceyducey.domain import Card, Rank, Suit
from aceyducey.presentation.card_art import (
    CARD_HEIGHT,
    CARD_WIDTH,
    render_back,
    render_card,
    render_row,
)


def test_single_card_height_and_width() -> None:
    art = render_card(Card(Rank.SEVEN, Suit.HEARTS))
    assert len(art) == CARD_HEIGHT
    for line in art:
        assert len(line) == CARD_WIDTH


def test_ten_keeps_layout() -> None:
    art = render_card(Card(Rank.TEN, Suit.SPADES))
    for line in art:
        assert len(line) == CARD_WIDTH


def test_highlighted_card_uses_double_border() -> None:
    art = render_card(Card(Rank.ACE, Suit.CLUBS), highlighted=True)
    assert art[0].startswith("╔")
    assert art[-1].startswith("╚")


def test_back_matches_card_dimensions() -> None:
    art = render_back()
    assert len(art) == CARD_HEIGHT
    for line in art:
        assert len(line) == CARD_WIDTH


def test_render_row_joins_with_gap() -> None:
    a = render_card(Card(Rank.TWO, Suit.HEARTS))
    b = render_card(Card(Rank.ACE, Suit.SPADES))
    rendered = render_row([a, b], gap=3)
    first_line = rendered.split("\n", 1)[0]
    assert first_line == a[0] + "   " + b[0]
