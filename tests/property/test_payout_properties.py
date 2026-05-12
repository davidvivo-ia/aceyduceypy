"""Property-based tests for the payout policy."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from aceyducey.domain import PayoutPolicy

spreads = st.integers(min_value=0, max_value=11)


@given(spread=spreads)
def test_flat_policy_is_one_for_any_spread(spread: int) -> None:
    assert PayoutPolicy.flat().multiplier_for_spread(spread) == 1


@given(spread=spreads)
def test_tiered_multiplier_is_positive(spread: int) -> None:
    assert PayoutPolicy.tiered().multiplier_for_spread(spread) >= 1


@given(a=spreads, b=spreads)
def test_tiered_multiplier_is_monotonic(a: int, b: int) -> None:
    policy = PayoutPolicy.tiered()
    if a <= b:
        assert policy.multiplier_for_spread(a) >= policy.multiplier_for_spread(b)
