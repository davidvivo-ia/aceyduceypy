"""Typer CLI: the only public entrypoint exposed via ``aceyducey``."""

from __future__ import annotations

import logging
from typing import Annotated

import typer

from aceyducey import __version__
from aceyducey.application import GameConfig
from aceyducey.domain import PayoutPolicy
from aceyducey.infrastructure import (
    JsonHighscoreRepository,
    SystemRandomAdapter,
    highscore_path,
)
from aceyducey.presentation.plain_driver import PlainDriver
from aceyducey.presentation.tui_app import AceyDuceyApp

logger = logging.getLogger("aceyducey")

app = typer.Typer(
    add_completion=False,
    help="Acey-Ducey card game — 2026 port of Bill Palmby's 1973 BASIC classic.",
    no_args_is_help=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"aceyducey {__version__}")
        raise typer.Exit


@app.callback(invoke_without_command=True)
def main(
    balance: Annotated[int, typer.Option("-b", "--balance", min=1, help="Balance inicial.")] = 100,
    seed: Annotated[int | None, typer.Option("-s", "--seed", help="Semilla determinista.")] = None,
    classic: Annotated[bool, typer.Option("--classic/--bonus", help="Pagos planos 1:1.")] = False,
    show_odds: Annotated[
        bool, typer.Option("--odds/--no-odds", help="Mostrar probabilidad y EV.")
    ] = True,
    demo: Annotated[bool, typer.Option("--demo", help="Partida determinista automática.")] = False,
    use_tui: Annotated[
        bool, typer.Option("--tui/--no-tui", help="TUI Textual o texto plano.")
    ] = True,
    show_version: Annotated[
        bool,
        typer.Option(
            "--version", callback=_version_callback, is_eager=True, help="Mostrar versión."
        ),
    ] = False,
) -> None:
    """Inicia la partida con la configuración dada."""
    _ = show_version  # already handled by callback
    config = GameConfig(
        starting_balance=balance,
        seed=seed if seed is not None else (42 if demo else None),
        payout_policy=PayoutPolicy.flat() if classic else PayoutPolicy.tiered(),
        show_odds=show_odds,
    )
    rng = SystemRandomAdapter(seed=config.seed)
    repo = JsonHighscoreRepository(highscore_path())

    if demo or not use_tui:
        driver = PlainDriver(config=config, rng=rng, highscore_repo=repo, demo=demo)
        raise typer.Exit(driver.run())

    AceyDuceyApp(config=config, rng=rng, highscore_repo=repo).run()
