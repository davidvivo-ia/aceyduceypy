from __future__ import annotations

import pytest

from aceyducey.domain import Rank, odds_between
from aceyducey.domain.probability import ranks_strictly_between


def test_ranks_between_pair_is_zero() -> None:
    assert ranks_strictly_between(Rank.SEVEN, Rank.SEVEN) == 0


def test_ranks_between_consecutive_is_zero() -> None:
    assert ranks_strictly_between(Rank.SEVEN, Rank.EIGHT) == 0


def test_ranks_between_two_and_ace() -> None:
    assert ranks_strictly_between(Rank.TWO, Rank.ACE) == 11


def test_odds_between_two_and_ace_uses_50_card_residual() -> None:
    assert odds_between(Rank.TWO, Rank.ACE) == pytest.approx(44 / 50)


def test_odds_consecutive_is_zero() -> None:
    assert odds_between(Rank.FIVE, Rank.SIX) == 0.0


def test_odds_handles_zero_remaining() -> None:
    assert odds_between(Rank.TWO, Rank.ACE, remaining_cards=0) == 0.0
