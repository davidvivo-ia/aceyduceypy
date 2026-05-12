"""Domain-level exception hierarchy.

Domain errors carry semantic meaning and never expose framework details.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all errors originating in the game domain."""


class InvalidBetError(DomainError):
    """Raised when a bet violates basic dominium invariants.

    Examples are negative bets or bets above the player's balance.
    """

    def __init__(self, amount: int, balance: int) -> None:
        self.amount = amount
        self.balance = balance
        super().__init__(f"invalid bet: amount={amount} is not within [0, {balance}]")


class EmptyDeckError(DomainError):
    """Raised when trying to draw from an empty deck."""

    def __init__(self) -> None:
        super().__init__("cannot draw from an empty deck")
