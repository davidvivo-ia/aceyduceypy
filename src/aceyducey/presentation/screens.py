"""Textual screens: splash, table, summary."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from aceyducey.application.stats import SessionStats
from aceyducey.presentation.widgets import CardWidget

if TYPE_CHECKING:
    from aceyducey.domain import Card

_LOGO = r"""
   _    ____ _____   __    ____  _   _  ____ _____   __
  / \  / ___| ____\ / /   |  _ \| | | |/ ___| ____\ / /
 / _ \| |   |  _|  Y /    | | | | | | | |   |  _|  Y /
/ ___ \ |___| |___ / \    | |_| | |_| | |___| |___ / \
/_/   \_\____|_____|_/\_\ |____/ \___/ \____|_____|_/\_\

           after Bill Palmby · Creative Computing · 1973
"""


class SplashScreen(Screen[None]):
    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("enter,space,n", "start", "Empezar"),
        Binding("q", "quit", "Salir"),
    ]

    def __init__(self, previous_highscore: int) -> None:
        super().__init__()
        self._previous = previous_highscore

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(id="splash"):
            yield Static(_LOGO, classes="title")
            if self._previous:
                yield Static(f"Récord anterior: ${self._previous}", classes="subtitle")
            yield Static("Pulsa Enter para empezar  ·  Q para salir", classes="hint")
        yield Footer()

    def action_start(self) -> None:
        self.app.pop_screen()


class TableScreen(Screen[None]):
    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("escape,0", "chicken", "Pasar"),
        Binding("ctrl+q", "quit", "Salir"),
        Binding("?", "help", "Ayuda"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Static("", id="hud")
        with Container(id="table"):
            yield Static("", id="header-bar")
            with Horizontal(id="main"):
                with Vertical(id="cards-pane"):
                    with Horizontal(id="cards-row"):
                        yield CardWidget(widget_id="card-low")
                        yield CardWidget(widget_id="card-high")
                        yield CardWidget(widget_id="card-third")
                    yield Static("", id="toast", classes="toast")
                with Vertical(id="side-pane"):
                    yield Static("Probabilidad", classes="label-muted")
                    yield Static("--", id="odds-value", classes="value-accent")
                    yield Static("Multiplicador", classes="label-muted")
                    yield Static("--", id="mult-value", classes="value-accent")
                    yield Static("EV / $", classes="label-muted")
                    yield Static("--", id="ev-value", classes="value-accent")
                    yield Static("Último resultado", classes="label-muted")
                    yield Static("--", id="last-result")
            with Horizontal(id="bet-row"):
                yield Input(placeholder="Apuesta (0 = pasar)", id="bet-input")
                with Horizontal(id="bet-actions"):
                    yield Button("Apostar", id="bet-button", classes="-primary")
                    yield Button("Pasar", id="chicken-button")
        yield Footer()

    def action_chicken(self) -> None:
        self.app.action_chicken()  # type: ignore[attr-defined]

    def action_help(self) -> None:
        self.app.action_help()  # type: ignore[attr-defined]

    def set_cards(
        self,
        low: Card | None,
        high: Card | None,
        third: Card | None,
    ) -> None:
        self.query_one("#card-low", CardWidget).show(low)
        self.query_one("#card-high", CardWidget).show(high)
        self.query_one("#card-third", CardWidget).show(third, highlighted=third is not None)

    def set_side_panel(
        self, *, probability: float, multiplier: int, ev: float, last_result: str
    ) -> None:
        self.query_one("#odds-value", Static).update(f"{probability:.1%}")
        self.query_one("#mult-value", Static).update(f"{multiplier}:1")
        self.query_one("#ev-value", Static).update(f"{ev:+.2f}")
        self.query_one("#last-result", Static).update(last_result)

    def set_hud(self, *, balance: int, hands: int, win_rate: float) -> None:
        self.query_one("#hud", Static).update(
            f"  Balance ${balance}    Manos {hands}    Win-rate {win_rate:.1%}"
        )

    def set_toast(self, text: str) -> None:
        self.query_one("#toast", Static).update(text)


class SummaryScreen(Screen[None]):
    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("n", "new_game", "Nueva partida"),
        Binding("q", "quit", "Salir"),
    ]

    def __init__(self, stats: SessionStats, *, new_highscore: bool) -> None:
        super().__init__()
        self._stats = stats
        self._new_highscore = new_highscore

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        s = self._stats
        sign = "+" if s.net >= 0 else ""
        delta_cls = "value-success" if s.net >= 0 else "value-danger"
        lines = [
            f"Manos jugadas       : {s.hands_dealt}",
            f"Apuestas hechas     : {s.bets_placed}",
            f"Pasadas (gallina)   : {s.chickened_out}",
            f"Victorias/Derrotas  : {s.wins} / {s.losses}",
            f"Empates con borde   : {s.edge_losses}",
            f"Win-rate            : {s.win_rate:.1%}",
            f"Mayor ganancia      : ${s.biggest_win}",
            f"Mayor pérdida       : ${s.biggest_loss}",
            f"Pico de balance     : ${s.peak_balance}",
        ]
        with Container(id="summary"):
            yield Static("[b]Resumen[/]")
            yield Static("\n".join(lines))
            yield Static(f"Balance final: [b]${s.balance}[/]")
            yield Static(f"[{delta_cls}]{sign}{s.net}[/]")
            if self._new_highscore:
                yield Static("★ NUEVO RÉCORD", classes="value-success")
            yield Static("\nN = nueva partida    Q = salir", classes="label-muted")
        yield Footer()

    def action_new_game(self) -> None:
        self.app.action_new_game()  # type: ignore[attr-defined]
