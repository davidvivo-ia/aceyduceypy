from __future__ import annotations

from aceyducey.domain import Rank, Suit, build_standard_deck


def test_deck_has_52_cards() -> None:
    assert len(build_standard_deck()) == 52


def test_deck_has_no_duplicates() -> None:
    deck = build_standard_deck()
    assert len(set(deck)) == 52


def test_deck_covers_all_ranks_and_suits() -> None:
    deck = build_standard_deck()
    for rank in Rank:
        for suit in Suit:
            assert any(c.rank is rank and c.suit is suit for c in deck)


def test_deck_is_freshly_allocated() -> None:
    assert build_standard_deck() is not build_standard_deck()
