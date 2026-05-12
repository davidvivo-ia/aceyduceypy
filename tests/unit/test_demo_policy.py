from __future__ import annotations

from aceyducey.presentation.demo_policy import DemoBettingPolicy


def test_skip_when_probability_below_threshold() -> None:
    policy = DemoBettingPolicy()
    assert policy.decide(probability=0.1, multiplier=5, balance=100) == 0


def test_skip_when_edge_non_positive() -> None:
    policy = DemoBettingPolicy()
    # probability 0.4, multiplier 1 -> edge = 0.4*1 - 0.6 = -0.2
    assert policy.decide(probability=0.4, multiplier=1, balance=100) == 0


def test_bet_is_within_balance() -> None:
    policy = DemoBettingPolicy()
    bet = policy.decide(probability=0.8, multiplier=2, balance=100)
    assert 1 <= bet <= 100


def test_handles_very_large_balance_without_overflow() -> None:
    policy = DemoBettingPolicy()
    huge = 10**400  # well beyond float range
    bet = policy.decide(probability=0.8, multiplier=2, balance=huge)
    assert isinstance(bet, int)
    assert 1 <= bet <= huge
