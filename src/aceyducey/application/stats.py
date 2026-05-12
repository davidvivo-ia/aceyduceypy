"""Session-wide statistics, accumulated as the player makes decisions."""

from __future__ import annotations

from dataclasses import dataclass, field

from aceyducey.domain import BetOutcome


@dataclass(slots=True)
class SessionStats:
    """Mutable accumulator for one game session."""

    starting_balance: int
    balance: int
    peak_balance: int = field(init=False)
    hands_dealt: int = 0
    hands_redealt: int = 0
    bets_placed: int = 0
    chickened_out: int = 0
    wins: int = 0
    losses: int = 0
    edge_losses: int = 0
    biggest_win: int = 0
    biggest_loss: int = 0

    def __post_init__(self) -> None:
        self.peak_balance = self.balance

    @property
    def net(self) -> int:
        return self.balance - self.starting_balance

    @property
    def win_rate(self) -> float:
        return self.wins / self.bets_placed if self.bets_placed else 0.0

    def apply_delta(self, delta: int) -> None:
        self.balance += delta
        if delta > 0:
            self.peak_balance = max(self.peak_balance, self.balance)
            self.biggest_win = max(self.biggest_win, delta)
        elif delta < 0:
            self.biggest_loss = max(self.biggest_loss, -delta)

    def record_outcome(self, outcome: BetOutcome) -> None:
        match outcome:
            case BetOutcome.WIN:
                self.wins += 1
            case BetOutcome.EDGE_LOSS:
                self.edge_losses += 1
                self.losses += 1
            case BetOutcome.LOSS:
                self.losses += 1
