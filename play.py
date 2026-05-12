#!/usr/bin/env python3
"""Launcher conveniente: ``python play.py`` desde la raíz del repo.

Sin argumentos extra: lanza la TUI. Acepta los mismos flags que el CLI
principal (``--demo``, ``--seed``, etc.). Si faltan dependencias, da una
pista clara en lugar de un traceback opaco.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite ejecutar desde la raíz sin instalar el paquete: añade src/ al path.
_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _hint_install() -> int:
    msg = (
        "\n[aceyducey] Faltan dependencias.\n"
        "  Instala con:    uv sync\n"
        "  o bien:         pip install -e .\n"
        "Después vuelve a ejecutar:  python play.py\n"
    )
    sys.stderr.write(msg)
    return 1


def main() -> int:
    try:
        from aceyducey.presentation.cli import app  # noqa: PLC0415
    except ModuleNotFoundError as exc:
        if exc.name in {"typer", "textual", "rich", "pydantic", "structlog"}:
            return _hint_install()
        raise
    app()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
