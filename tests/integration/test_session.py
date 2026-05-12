from __future__ import annotations

from typing import cast

import pytest

from aceyducey.application import GameConfig, GameSession, HighscorePort, RngPort
from aceyducey.application.events import (
    DealtHandEvent,
    HandResolvedEvent,
    RedealEvent,
)
from aceyducey.domain import BetOutcome, Card, InvalidBetError, PayoutPolicy, Rank, Suit


class StackedDeckRng:
    """Test double whose successive ``shuffle()`` calls walk through a
    pre-recorded script of cards.

    The session can call ``shuffle`` several times per ``deal()`` (one per
    re-deal). Each call places the next ``chunk_size`` cards from the
    script at the top of the deck so that they are the next ones drawn.
    Default ``chunk_size`` is 3 (two brackets + one verdict), but pair and
    consecutive redeals only consume two cards, so the next shuffle must
    pick up where we left off.
    """

    def __init__(self, script: list[Card]) -> None:
        self._script = list(script)
        self._cursor = 0

    def shuffle(self, deck: list[object]) -> None:
        cards = cast(list[Card], deck)
        scripted = self._script[self._cursor : self._cursor + 3]
        self._cursor += 2  # each deal consumes at least two; bet draws the third
        rest = [c for c in cards if c not in scripted]
        cards.clear()
        cards.extend(rest)
        cards.extend(reversed(scripted))

    def random(self) -> float:
        return 0.0


class InMemoryHighscoreRepo:
    def __init__(self, initial: int = 0) -> None:
        self.peak = initial

    def load(self) -> int:
        return self.peak

    def save(self, peak: int) -> None:
        self.peak = peak


@pytest.fixture
def repo() -> InMemoryHighscoreRepo:
    return InMemoryHighscoreRepo()


def make_session(
    script: list[Card],
    *,
    balance: int = 100,
    policy: PayoutPolicy | None = None,
    repo: HighscorePort | None = None,
) -> GameSession:
    config = GameConfig(
        starting_balance=balance,
        payout_policy=policy or PayoutPolicy.tiered(),
        seed=0,
    )
    rng: RngPort = StackedDeckRng(script)
    return GameSession(
        config=config,
        rng=rng,
        highscore_repo=repo or InMemoryHighscoreRepo(),
    )


def test_start_emits_starting_balance(repo: InMemoryHighscoreRepo) -> None:
    session = make_session(script=[], balance=200, repo=repo)
    event = session.start()
    assert event.starting_balance == 200
    assert event.previous_highscore == 0


def test_deal_winning_hand_then_win() -> None:
    low = Card(Rank.FIVE, Suit.SPADES)
    high = Card(Rank.JACK, Suit.HEARTS)
    third = Card(Rank.EIGHT, Suit.CLUBS)
    session = make_session(script=[high, low, third])
    session.start()

    events = list(session.deal())
    assert len(events) == 1
    dealt = events[0]
    assert isinstance(dealt, DealtHandEvent)
    assert dealt.hand.low == low
    assert dealt.hand.high == high
    # spread=5 -> tiered 2x; P = 5*4/50 = 0.4
    assert dealt.multiplier == 2
    assert dealt.win_probability == pytest.approx(0.4)

    resolved = session.place_bet(10)
    assert isinstance(resolved, HandResolvedEvent)
    assert resolved.resolution.outcome is BetOutcome.WIN
    assert resolved.balance == 100 + 10 * 2


def test_pair_triggers_redeal_then_playable() -> None:
    pair1 = Card(Rank.SEVEN, Suit.SPADES)
    pair2 = Card(Rank.SEVEN, Suit.HEARTS)
    low = Card(Rank.FIVE, Suit.CLUBS)
    high = Card(Rank.JACK, Suit.DIAMONDS)
    session = make_session(script=[pair1, pair2, low, high])
    session.start()
    events = list(session.deal())
    assert len(events) == 2
    assert isinstance(events[0], RedealEvent)
    assert events[0].reason == "pair"
    assert isinstance(events[1], DealtHandEvent)


def test_consecutive_triggers_redeal() -> None:
    a = Card(Rank.SEVEN, Suit.SPADES)
    b = Card(Rank.EIGHT, Suit.HEARTS)
    low = Card(Rank.FIVE, Suit.CLUBS)
    high = Card(Rank.JACK, Suit.DIAMONDS)
    session = make_session(script=[a, b, low, high])
    session.start()
    events = list(session.deal())
    assert isinstance(events[0], RedealEvent)
    assert events[0].reason == "consecutive"


def test_place_bet_chicken_does_not_change_balance() -> None:
    session = make_session(
        script=[
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.CLUBS),
        ]
    )
    session.start()
    list(session.deal())
    res = session.place_bet(0)
    assert res.balance == 100
    assert session.stats.chickened_out == 1
    assert session.stats.bets_placed == 0


def test_place_bet_negative_raises() -> None:
    session = make_session(
        script=[
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.CLUBS),
        ]
    )
    session.start()
    list(session.deal())
    with pytest.raises(InvalidBetError):
        session.place_bet(-1)


def test_place_bet_above_balance_raises() -> None:
    session = make_session(
        script=[
            Card(Rank.FIVE, Suit.SPADES),
            Card(Rank.JACK, Suit.HEARTS),
            Card(Rank.SEVEN, Suit.CLUBS),
        ]
    )
    session.start()
    list(session.deal())
    with pytest.raises(InvalidBetError):
        session.place_bet(9999)


def test_finish_persists_new_highscore() -> None:
    repo = InMemoryHighscoreRepo(initial=50)
    low = Card(Rank.FIVE, Suit.SPADES)
    high = Card(Rank.JACK, Suit.HEARTS)
    third = Card(Rank.EIGHT, Suit.CLUBS)
    session = make_session(script=[high, low, third], repo=repo)
    session.start()
    list(session.deal())
    session.place_bet(10)  # balance 120
    end = session.finish()
    assert end.new_highscore is True
    assert repo.peak == 120


def test_place_bet_before_deal_raises() -> None:
    session = make_session(script=[])
    session.start()
    with pytest.raises(RuntimeError):
        session.place_bet(10)
