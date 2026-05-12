"""Random number adapter backed by :class:`random.Random`."""

from __future__ import annotations

import random
from typing import Any


class SystemRandomAdapter:
    """Thin wrapper around :class:`random.Random` exposing the RNG port.

    A dedicated instance — not the module-level functions — is held so
    that ``--seed`` is honoured precisely and tests stay isolated from
    each other.
    """

    __slots__ = ("_rng",)

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def shuffle(self, deck: list[Any]) -> None:
        self._rng.shuffle(deck)

    def random(self) -> float:
        return self._rng.random()
