from __future__ import annotations

from aceyducey.domain import Card, Rank, Suit


def test_rank_label_for_pip_card() -> None:
    assert Rank.SEVEN.label == "7"


def test_rank_label_for_face_card() -> None:
    assert Rank.JACK.label == "J"
    assert Rank.QUEEN.label == "Q"
    assert Rank.KING.label == "K"
    assert Rank.ACE.label == "A"


def test_rank_spanish_name() -> None:
    assert Rank.ACE.spanish_name == "AS"
    assert Rank.TEN.spanish_name == "10"


def test_suit_metadata() -> None:
    assert Suit.HEARTS.is_red is True
    assert Suit.CLUBS.is_red is False
    assert Suit.SPADES.symbol == "♠"


def test_card_orders_by_rank_only() -> None:
    two_of_hearts = Card(Rank.TWO, Suit.HEARTS)
    ace_of_clubs = Card(Rank.ACE, Suit.CLUBS)
    assert two_of_hearts < ace_of_clubs
    assert ace_of_clubs > two_of_hearts


def test_card_equality_uses_rank_and_suit() -> None:
    a = Card(Rank.SEVEN, Suit.HEARTS)
    b = Card(Rank.SEVEN, Suit.DIAMONDS)
    assert a != b
    assert a == Card(Rank.SEVEN, Suit.HEARTS)


def test_card_is_hashable() -> None:
    a = Card(Rank.SEVEN, Suit.HEARTS)
    assert {a, a, Card(Rank.SEVEN, Suit.HEARTS)} == {a}


def test_card_str() -> None:
    assert str(Card(Rank.TEN, Suit.SPADES)) == "10♠"
    assert str(Card(Rank.ACE, Suit.HEARTS)) == "A♥"
