"""Tests para aceyducey.py — usa solo la stdlib (unittest)."""
from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import aceyducey as ad


class TestDeck(unittest.TestCase):
    def test_full_deck_has_52_unique_cards(self) -> None:
        deck = ad.make_deck()
        self.assertEqual(len(deck), 52)
        self.assertEqual(len(set(deck)), 52)

    def test_card_order_by_rank(self) -> None:
        two = ad.Card(ad.Rank.TWO, ad.Suit.SPADES)
        ace = ad.Card(ad.Rank.ACE, ad.Suit.CLUBS)
        self.assertLess(two, ace)


class TestRules(unittest.TestCase):
    def test_payout_classic_is_one(self) -> None:
        for low in ad.Rank:
            for high in ad.Rank:
                if int(high) - int(low) >= 2:
                    self.assertEqual(
                        ad.payout_multiplier(low, high, bonus=False), 1
                    )

    def test_payout_bonus_increases_with_tightness(self) -> None:
        # spread 1 -> 5x, spread 3 -> 3x, spread 5 -> 2x, spread 11 -> 1x
        self.assertEqual(
            ad.payout_multiplier(ad.Rank.TWO, ad.Rank.FOUR), 5
        )
        self.assertEqual(
            ad.payout_multiplier(ad.Rank.TWO, ad.Rank.SIX), 3
        )
        self.assertEqual(
            ad.payout_multiplier(ad.Rank.TWO, ad.Rank.EIGHT), 2
        )
        self.assertEqual(
            ad.payout_multiplier(ad.Rank.TWO, ad.Rank.ACE), 1
        )

    def test_odds_between(self) -> None:
        # Entre 2 y Ace hay 11 rangos intermedios * 4 palos = 44 / 50.
        p = ad.odds_between(ad.Rank.TWO, ad.Rank.ACE)
        self.assertAlmostEqual(p, 44 / 50)
        # Consecutivas: 0
        self.assertEqual(
            ad.odds_between(ad.Rank.FIVE, ad.Rank.SIX), 0.0
        )


class TestStats(unittest.TestCase):
    def test_win_rate_no_bets(self) -> None:
        s = ad.Stats()
        self.assertEqual(s.win_rate, 0.0)

    def test_net_calc(self) -> None:
        s = ad.Stats(starting_balance=100, final_balance=140)
        self.assertEqual(s.net, 40)


class TestPromptInt(unittest.TestCase):
    def test_accepts_valid(self) -> None:
        with patch("builtins.input", side_effect=["42"]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(ad.prompt_int("? ", lo=0, hi=100), 42)

    def test_rejects_then_accepts(self) -> None:
        with patch("builtins.input", side_effect=["abc", "-5", "200", "50"]):
            with redirect_stdout(io.StringIO()):
                self.assertEqual(ad.prompt_int("? ", lo=0, hi=100), 50)


class TestPromptYesNo(unittest.TestCase):
    def test_yes(self) -> None:
        with patch("builtins.input", return_value="s"):
            self.assertTrue(ad.prompt_yes_no("?"))

    def test_no(self) -> None:
        with patch("builtins.input", return_value="no"):
            self.assertFalse(ad.prompt_yes_no("?"))

    def test_default(self) -> None:
        with patch("builtins.input", return_value=""):
            self.assertTrue(ad.prompt_yes_no("?", default=True))
            self.assertFalse(ad.prompt_yes_no("?", default=False))


class TestPlayRound(unittest.TestCase):
    """Construye un mazo determinista y comprueba transiciones de balance."""

    def _stacked_deck(self, cards: list[ad.Card]) -> list[ad.Card]:
        # play_round hace deck.pop() así que el último elemento se reparte primero
        return list(reversed(cards))

    def test_win_pays_multiplier(self) -> None:
        low = ad.Card(ad.Rank.FIVE, ad.Suit.SPADES)
        high = ad.Card(ad.Rank.JACK, ad.Suit.HEARTS)
        third = ad.Card(ad.Rank.EIGHT, ad.Suit.CLUBS)
        deck = self._stacked_deck([low, high, third])
        config = ad.GameConfig(bonus_payouts=True, show_odds=False)
        stats = ad.Stats()
        with patch("builtins.input", return_value="10"):
            with redirect_stdout(io.StringIO()):
                new = ad.play_round(deck, 100, config, stats)
        # spread = 11-5-1 = 5 -> 2x
        self.assertEqual(new, 120)
        self.assertEqual(stats.wins, 1)
        self.assertEqual(stats.biggest_win, 20)

    def test_loss_on_edge_match(self) -> None:
        low = ad.Card(ad.Rank.FIVE, ad.Suit.SPADES)
        high = ad.Card(ad.Rank.NINE, ad.Suit.HEARTS)
        third = ad.Card(ad.Rank.NINE, ad.Suit.CLUBS)
        deck = self._stacked_deck([low, high, third])
        config = ad.GameConfig(bonus_payouts=True, show_odds=False)
        stats = ad.Stats()
        with patch("builtins.input", return_value="25"):
            with redirect_stdout(io.StringIO()):
                new = ad.play_round(deck, 100, config, stats)
        self.assertEqual(new, 75)
        self.assertEqual(stats.losses, 1)

    def test_chicken_no_balance_change(self) -> None:
        low = ad.Card(ad.Rank.FIVE, ad.Suit.SPADES)
        high = ad.Card(ad.Rank.JACK, ad.Suit.HEARTS)
        deck = self._stacked_deck([low, high, ad.Card(ad.Rank.SEVEN, ad.Suit.CLUBS)])
        config = ad.GameConfig(show_odds=False)
        stats = ad.Stats()
        with patch("builtins.input", return_value="0"):
            with redirect_stdout(io.StringIO()):
                new = ad.play_round(deck, 100, config, stats)
        self.assertEqual(new, 100)
        self.assertEqual(stats.chickened_out, 1)
        self.assertEqual(stats.bets_placed, 0)

    def test_pair_redeals(self) -> None:
        a = ad.Card(ad.Rank.SEVEN, ad.Suit.SPADES)
        b = ad.Card(ad.Rank.SEVEN, ad.Suit.HEARTS)
        deck = self._stacked_deck([a, b])
        config = ad.GameConfig(show_odds=False)
        stats = ad.Stats()
        with redirect_stdout(io.StringIO()):
            new = ad.play_round(deck, 100, config, stats)
        self.assertEqual(new, 100)
        self.assertEqual(stats.hands_played, 0)

    def test_consecutive_redeals(self) -> None:
        a = ad.Card(ad.Rank.SEVEN, ad.Suit.SPADES)
        b = ad.Card(ad.Rank.EIGHT, ad.Suit.HEARTS)
        deck = self._stacked_deck([a, b])
        config = ad.GameConfig(show_odds=False)
        stats = ad.Stats()
        with redirect_stdout(io.StringIO()):
            new = ad.play_round(deck, 100, config, stats)
        self.assertEqual(new, 100)
        self.assertEqual(stats.hands_played, 0)


class TestCLI(unittest.TestCase):
    def test_parse_defaults(self) -> None:
        cfg = ad.parse_args([])
        self.assertEqual(cfg.starting_balance, 100)
        self.assertTrue(cfg.bonus_payouts)
        self.assertTrue(cfg.show_odds)

    def test_classic_flag(self) -> None:
        cfg = ad.parse_args(["--classic", "--no-odds", "-b", "500"])
        self.assertEqual(cfg.starting_balance, 500)
        self.assertFalse(cfg.bonus_payouts)
        self.assertFalse(cfg.show_odds)


if __name__ == "__main__":
    unittest.main()
