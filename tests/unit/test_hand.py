from __future__ import annotations

import pytest

from aceyducey.domain import (
    BetOutcome,
    Card,
    Hand,
    PayoutPolicy,
    Rank,
    Suit,
)


@pytest.fixture
def policy() -> PayoutPolicy:
    return PayoutPolicy.tiered()


def make_hand(low: Rank, high: Rank) -> Hand:
    return Hand(low=Card(low, Suit.SPADES), high=Card(high, Suit.HEARTS))


def test_hand_spread_normal() -> None:
    assert make_hand(Rank.FIVE, Rank.JACK).spread == 5


def test_hand_pair_detected() -> None:
    h = make_hand(Rank.SEVEN, Rank.SEVEN)
    assert h.is_pair is True
    assert h.is_playable is False


def test_hand_consecutive_detected() -> None:
    h = make_hand(Rank.SEVEN, Rank.EIGHT)
    assert h.is_consecutive is True
    assert h.is_playable is False


def test_resolve_chicken_returns_zero_delta(policy: PayoutPolicy) -> None:
    hand = make_hand(Rank.TWO, Rank.JACK)
    result = hand.resolve(Card(Rank.SEVEN, Suit.CLUBS), bet=0, policy=policy)
    assert result.delta == 0
    assert result.multiplier == 0


def test_resolve_win_uses_multiplier(policy: PayoutPolicy) -> None:
    # 2..7 -> spread 4 -> 2x in tiered
    hand = make_hand(Rank.TWO, Rank.SEVEN)
    drawn = Card(Rank.FIVE, Suit.CLUBS)
    result = hand.resolve(drawn, bet=10, policy=policy)
    assert result.outcome is BetOutcome.WIN
    assert result.multiplier == 2
    assert result.delta == 20


def test_resolve_edge_loss(policy: PayoutPolicy) -> None:
    hand = make_hand(Rank.FIVE, Rank.JACK)
    drawn = Card(Rank.JACK, Suit.CLUBS)
    result = hand.resolve(drawn, bet=25, policy=policy)
    assert result.outcome is BetOutcome.EDGE_LOSS
    assert result.delta == -25


def test_resolve_plain_loss(policy: PayoutPolicy) -> None:
    hand = make_hand(Rank.FIVE, Rank.JACK)
    drawn = Card(Rank.TWO, Suit.CLUBS)
    result = hand.resolve(drawn, bet=10, policy=policy)
    assert result.outcome is BetOutcome.LOSS
    assert result.delta == -10
