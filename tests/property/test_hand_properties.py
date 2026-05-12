"""Property-based tests for hand resolution."""

from __future__ import annotations

from hypothesis import assume, given
from hypothesis import strategies as st

from aceyducey.domain import BetOutcome, Card, Hand, PayoutPolicy, Rank, Suit

ranks = st.sampled_from(list(Rank))
suits = st.sampled_from(list(Suit))
cards = st.builds(Card, ranks, suits)
bets = st.integers(min_value=1, max_value=10_000)


@given(low=ranks, high=ranks, drawn=cards, bet=bets)
def test_delta_signs_match_outcome(low: Rank, high: Rank, drawn: Card, bet: int) -> None:
    assume(low < high)
    hand = Hand(low=Card(low, Suit.SPADES), high=Card(high, Suit.HEARTS))
    result = hand.resolve(drawn, bet=bet, policy=PayoutPolicy.tiered())
    if result.outcome is BetOutcome.WIN:
        assert result.delta > 0
    else:
        assert result.delta == -bet


@given(low=ranks, high=ranks, drawn=cards, bet=bets)
def test_win_multiplier_is_policy_multiplier(low: Rank, high: Rank, drawn: Card, bet: int) -> None:
    assume(low < high)
    hand = Hand(low=Card(low, Suit.SPADES), high=Card(high, Suit.HEARTS))
    policy = PayoutPolicy.tiered()
    result = hand.resolve(drawn, bet=bet, policy=policy)
    if result.outcome is BetOutcome.WIN:
        expected = policy.multiplier_for_cards(low, high)
        assert result.multiplier == expected
        assert result.delta == bet * expected
