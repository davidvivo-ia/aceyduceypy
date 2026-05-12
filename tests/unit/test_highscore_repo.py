from __future__ import annotations

import json
from pathlib import Path

from aceyducey.infrastructure import JsonHighscoreRepository


def test_load_returns_zero_when_missing(tmp_path: Path) -> None:
    repo = JsonHighscoreRepository(tmp_path / "missing.json")
    assert repo.load() == 0


def test_save_and_load_roundtrip(tmp_path: Path) -> None:
    repo = JsonHighscoreRepository(tmp_path / "hs.json")
    repo.save(250)
    assert repo.load() == 250


def test_save_keeps_highest_value(tmp_path: Path) -> None:
    repo = JsonHighscoreRepository(tmp_path / "hs.json")
    repo.save(120)
    repo.save(80)
    assert repo.load() == 120


def test_save_increments_runs(tmp_path: Path) -> None:
    repo = JsonHighscoreRepository(tmp_path / "hs.json")
    repo.save(100)
    repo.save(150)
    payload = json.loads(repo.path.read_text())
    assert payload["runs"] == 2


def test_corrupt_file_resets_to_zero(tmp_path: Path) -> None:
    path = tmp_path / "hs.json"
    path.write_text("this is not json")
    repo = JsonHighscoreRepository(path)
    assert repo.load() == 0


def test_save_creates_parent_directory(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "hs.json"
    repo = JsonHighscoreRepository(nested)
    repo.save(50)
    assert nested.exists()
