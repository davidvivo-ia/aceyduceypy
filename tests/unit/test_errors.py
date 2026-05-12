from __future__ import annotations

import pytest

from aceyducey.domain.errors import DomainError, EmptyDeckError, InvalidBetError


def test_invalid_bet_carries_amount_and_balance() -> None:
    err = InvalidBetError(amount=-5, balance=100)
    assert err.amount == -5
    assert err.balance == 100
    assert "-5" in str(err)
    assert "100" in str(err)


def test_invalid_bet_is_domain_error() -> None:
    with pytest.raises(DomainError):
        raise InvalidBetError(amount=200, balance=100)


def test_empty_deck_error_is_domain_error() -> None:
    with pytest.raises(DomainError):
        raise EmptyDeckError
