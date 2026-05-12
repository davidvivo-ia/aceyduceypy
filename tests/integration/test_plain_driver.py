from __future__ import annotations

import io
from pathlib import Path

from rich.console import Console

from aceyducey.application import GameConfig
from aceyducey.infrastructure import (
    JsonHighscoreRepository,
    SystemRandomAdapter,
)
from aceyducey.presentation.plain_driver import PlainDriver


def test_demo_finishes_with_seed(tmp_path: Path) -> None:
    """Demo mode is fully deterministic and terminates within the hand cap."""
    driver = PlainDriver(
        config=GameConfig(starting_balance=100, seed=42),
        rng=SystemRandomAdapter(seed=42),
        highscore_repo=JsonHighscoreRepository(tmp_path / "hs.json"),
        demo=True,
    )
    # Swap stdout for a buffer so the test stays quiet.
    driver._console = Console(file=io.StringIO(), highlight=False, force_terminal=False)
    code = driver.run()
    assert code == 0


def test_demo_deterministic_balance_with_seed(tmp_path: Path) -> None:
    """Two demo runs with the same seed end with the same balance."""

    def _final_balance() -> int:
        driver = PlainDriver(
            config=GameConfig(starting_balance=100, seed=7),
            rng=SystemRandomAdapter(seed=7),
            highscore_repo=JsonHighscoreRepository(tmp_path / "hs.json"),
            demo=True,
        )
        driver._console = Console(file=io.StringIO(), highlight=False, force_terminal=False)
        driver.run()
        return driver._session.stats.balance

    assert _final_balance() == _final_balance()
