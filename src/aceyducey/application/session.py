"""``GameSession``: the central orchestrator.

The session owns balance and stats, talks to the domain for math, and
asks its injected RNG to shuffle decks. Presentation drives it through
three operations:

* :py:meth:`GameSession.start` — emit the initial events.
* :py:meth:`GameSession.deal` — produce the next playable hand (auto
  re-dealing past pairs and consecutive cards).
* :py:meth:`GameSession.place_bet` — resolve a bet against a third card.

The session never blocks on IO and never touches files or terminals.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from aceyducey.application.config import GameConfig
from aceyducey.application.events import (
    DealtHandEvent,
    GameEndedEvent,
    GameStartedEvent,
    HandResolvedEvent,
    RedealEvent,
)
from aceyducey.application.ports import HighscorePort, RngPort
from aceyducey.application.stats import SessionStats
from aceyducey.domain import (
    Card,
    Hand,
    InvalidBetError,
    build_standard_deck,
    odds_between,
)


@dataclass(slots=True)
class _RoundState:
    """Internal mutable state for the in-flight hand, if any."""

    deck: list[Card] = field(default_factory=list)
    hand: Hand | None = None


class GameSession:
    """Stateful orchestrator for a single game."""

    __slots__ = ("_config", "_highscore_repo", "_prev_highscore", "_rng", "_round", "_stats")

    def __init__(
        self,
        *,
        config: GameConfig,
        rng: RngPort,
        highscore_repo: HighscorePort,
    ) -> None:
        self._config = config
        self._rng = rng
        self._highscore_repo = highscore_repo
        self._stats = SessionStats(
            starting_balance=config.starting_balance,
            balance=config.starting_balance,
        )
        self._round = _RoundState()
        self._prev_highscore = highscore_repo.load()

    # ----- public read-only views --------------------------------------

    @property
    def config(self) -> GameConfig:
        return self._config

    @property
    def stats(self) -> SessionStats:
        return self._stats

    @property
    def balance(self) -> int:
        return self._stats.balance

    @property
    def is_game_over(self) -> bool:
        return self._stats.balance <= 0

    @property
    def previous_highscore(self) -> int:
        return self._prev_highscore

    # ----- driver API --------------------------------------------------

    def start(self) -> GameStartedEvent:
        """Reset round state and announce session start."""
        self._round = _RoundState()
        return GameStartedEvent(
            starting_balance=self._stats.balance,
            previous_highscore=self._prev_highscore,
        )

    def deal(self) -> Iterator[DealtHandEvent | RedealEvent]:
        """Yield events until a playable hand is on the table.

        Pairs and consecutive cards cause :class:`RedealEvent`s; the final
        event is always a :class:`DealtHandEvent` describing the playable
        hand.
        """
        while True:
            deck = build_standard_deck()
            self._rng.shuffle(deck)  # type: ignore[arg-type]
            first = deck.pop()
            second = deck.pop()
            low, high = sorted((first, second))
            hand = Hand(low=low, high=high)
            self._stats.hands_dealt += 1
            if hand.is_pair:
                self._stats.hands_redealt += 1
                yield RedealEvent(reason="pair", revealed=(low, high))
                continue
            if hand.is_consecutive:
                self._stats.hands_redealt += 1
                yield RedealEvent(reason="consecutive", revealed=(low, high))
                continue
            self._round = _RoundState(deck=deck, hand=hand)
            yield DealtHandEvent(
                hand=hand,
                balance=self._stats.balance,
                win_probability=odds_between(low.rank, high.rank, remaining_cards=len(deck)),
                multiplier=self._config.payout_policy.multiplier_for_cards(low.rank, high.rank),
            )
            return

    def place_bet(self, amount: int) -> HandResolvedEvent:
        """Resolve a bet against a third card drawn from the current deck."""
        if self._round.hand is None:
            raise RuntimeError("place_bet called before deal")
        if amount < 0 or amount > self._stats.balance:
            raise InvalidBetError(amount=amount, balance=self._stats.balance)
        hand = self._round.hand
        drawn = self._round.deck.pop()
        resolution = hand.resolve(drawn, bet=amount, policy=self._config.payout_policy)
        if amount == 0:
            self._stats.chickened_out += 1
        else:
            self._stats.bets_placed += 1
            self._stats.record_outcome(resolution.outcome)
            self._stats.apply_delta(resolution.delta)
        self._round = _RoundState()
        return HandResolvedEvent(resolution=resolution, balance=self._stats.balance)

    def finish(self) -> GameEndedEvent:
        """Persist the highscore and emit the closing event."""
        new_high = self._stats.peak_balance > self._prev_highscore
        self._highscore_repo.save(max(self._prev_highscore, self._stats.peak_balance))
        return GameEndedEvent(stats=self._stats, new_highscore=new_high)
