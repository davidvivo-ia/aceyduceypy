from __future__ import annotations

from pathlib import Path

import pytest

from aceyducey.infrastructure import default_data_dir, highscore_path


def test_xdg_data_home_respected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_DATA_HOME", "/tmp/xdg")
    path = default_data_dir()
    assert str(path).startswith("/tmp/xdg")
    assert path.name == "aceyducey"


def test_default_data_dir_falls_back_to_local_share(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    path = default_data_dir()
    assert ".local/share/aceyducey" in str(path)


def test_highscore_path_uses_data_dir() -> None:
    p = highscore_path(Path("/tmp/x"))
    assert p == Path("/tmp/x/highscore.json")
