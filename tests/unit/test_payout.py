from __future__ import annotations

from aceyducey.domain import PayoutPolicy, Rank


def test_flat_policy_always_pays_one() -> None:
    policy = PayoutPolicy.flat()
    for spread in range(0, 13):
        assert policy.multiplier_for_spread(spread) == 1


def test_tiered_policy_tight_spread_pays_most() -> None:
    policy = PayoutPolicy.tiered()
    assert policy.multiplier_for_spread(1) == 5
    assert policy.multiplier_for_spread(2) == 3
    assert policy.multiplier_for_spread(3) == 3
    assert policy.multiplier_for_spread(4) == 2
    assert policy.multiplier_for_spread(6) == 2
    assert policy.multiplier_for_spread(7) == 1
    assert policy.multiplier_for_spread(11) == 1


def test_tiered_for_card_pair() -> None:
    policy = PayoutPolicy.tiered()
    # 2 to 4 has spread 1 -> 5x
    assert policy.multiplier_for_cards(Rank.TWO, Rank.FOUR) == 5
    # 2 to 8 has spread 5 -> 2x
    assert policy.multiplier_for_cards(Rank.TWO, Rank.EIGHT) == 2


def test_policy_has_name() -> None:
    assert PayoutPolicy.flat().name == "classic"
    assert PayoutPolicy.tiered().name == "tiered"
