from __future__ import annotations

from aceyducey.infrastructure import SystemRandomAdapter


def test_seed_makes_shuffle_deterministic() -> None:
    a = SystemRandomAdapter(seed=42)
    b = SystemRandomAdapter(seed=42)
    deck_a = list(range(20))
    deck_b = list(range(20))
    a.shuffle(deck_a)
    b.shuffle(deck_b)
    assert deck_a == deck_b


def test_different_seeds_produce_different_shuffles() -> None:
    a = SystemRandomAdapter(seed=1)
    b = SystemRandomAdapter(seed=2)
    deck_a = list(range(20))
    deck_b = list(range(20))
    a.shuffle(deck_a)
    b.shuffle(deck_b)
    assert deck_a != deck_b


def test_random_in_range() -> None:
    r = SystemRandomAdapter(seed=0).random()
    assert 0.0 <= r < 1.0
