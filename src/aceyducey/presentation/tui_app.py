"""Top-level Textual application orchestrating the screens."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import App
from textual.binding import Binding
from textual.widgets import Button, Input

from aceyducey.application import (
    DealtHandEvent,
    GameConfig,
    GameSession,
    HighscorePort,
    RngPort,
)
from aceyducey.domain import BetOutcome, InvalidBetError
from aceyducey.presentation.screens import SplashScreen, SummaryScreen, TableScreen

_CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "aceyducey.tcss"


class AceyDuceyApp(App[None]):
    CSS_PATH = _CSS_PATH
    TITLE = "Acey-Ducey"
    SUB_TITLE = "after Bill Palmby · 1973"

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("ctrl+q", "quit", "Salir"),
        Binding("ctrl+r", "new_game", "Reiniciar"),
    ]

    def __init__(
        self,
        *,
        config: GameConfig,
        rng: RngPort,
        highscore_repo: HighscorePort,
    ) -> None:
        super().__init__()
        self._config = config
        self._rng = rng
        self._highscore_repo = highscore_repo
        self._session = GameSession(config=config, rng=rng, highscore_repo=highscore_repo)
        self._dealt: DealtHandEvent | None = None

    def on_mount(self) -> None:
        self.push_screen(TableScreen(), self._after_splash_stub)
        self.push_screen(SplashScreen(self._session.previous_highscore))
        start = self._session.start()
        self._update_hud()
        self.call_after_refresh(self._begin_round)
        _ = start

    def _after_splash_stub(self, _: object) -> None:
        """Placeholder for ``push_screen`` callback signature compliance."""

    # ---------------------------------------------------------------- helpers

    def _table(self) -> TableScreen:
        for screen in reversed(self.screen_stack):
            if isinstance(screen, TableScreen):
                return screen
        msg = "TableScreen not mounted"
        raise RuntimeError(msg)

    def _update_hud(self) -> None:
        stats = self._session.stats
        self._table().set_hud(
            balance=stats.balance,
            hands=stats.hands_dealt,
            win_rate=stats.win_rate,
        )

    def _begin_round(self) -> None:
        if self._session.is_game_over:
            self._show_summary()
            return
        table = self._table()
        table.set_cards(None, None, None)
        table.set_toast("Repartiendo...")
        for event in self._session.deal():
            if event.__class__.__name__ == "RedealEvent":
                table.set_toast("Mano nula. Repartiendo de nuevo.")
                continue
            assert isinstance(event, DealtHandEvent)
            self._dealt = event
            table.set_cards(event.hand.low, event.hand.high, None)
            ev = event.win_probability * event.multiplier - (1 - event.win_probability)
            table.set_side_panel(
                probability=event.win_probability,
                multiplier=event.multiplier,
                ev=ev,
                last_result="--",
            )
            table.set_toast(f"Apuesta entre $0 y ${event.balance}.")
            self.query_one("#bet-input", Input).value = ""
            self.query_one("#bet-input", Input).focus()
            self._update_hud()
            return

    def _resolve(self, amount: int) -> None:
        if self._dealt is None:
            return
        table = self._table()
        try:
            resolved = self._session.place_bet(amount)
        except InvalidBetError as exc:
            table.set_toast(f"Apuesta no válida: {exc.amount} ($0..${exc.balance}).")
            return
        res = resolved.resolution
        table.set_cards(res.low, res.high, res.drawn)
        match res.outcome:
            case BetOutcome.WIN:
                outcome_text = f"GANAS ${res.delta} (x{res.multiplier})"
            case BetOutcome.EDGE_LOSS:
                outcome_text = f"Empate con borde. Pierdes ${res.bet}"
            case BetOutcome.LOSS:
                outcome_text = f"Pierdes ${res.bet}" if res.bet else "Pasada (gallina)"
        table.set_side_panel(
            probability=self._dealt.win_probability,
            multiplier=self._dealt.multiplier,
            ev=(
                self._dealt.win_probability * self._dealt.multiplier
                - (1 - self._dealt.win_probability)
            ),
            last_result=outcome_text,
        )
        self._update_hud()
        self._dealt = None
        self.set_timer(0.8, self._begin_round)

    def _show_summary(self) -> None:
        end = self._session.finish()
        self.push_screen(SummaryScreen(end.stats, new_highscore=end.new_highscore))

    # --------------------------------------------------------------- actions

    def action_chicken(self) -> None:
        self._resolve(0)

    def action_new_game(self) -> None:
        self._session = GameSession(
            config=self._config, rng=self._rng, highscore_repo=self._highscore_repo
        )
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self._session.start()
        self._update_hud()
        self.call_after_refresh(self._begin_round)

    def action_help(self) -> None:
        self._table().set_toast(
            "Apuesta entre $0 (pasar) y tu balance. Enter confirma. Esc/0 pasa."
        )

    # ----------------------------------------------------------- event hooks

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "bet-input":
            return
        text = event.value.strip()
        if not text:
            return
        try:
            amount = int(text)
        except ValueError:
            self._table().set_toast("Introduce un número entero.")
            return
        self._resolve(amount)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "bet-button":
            text = self.query_one("#bet-input", Input).value.strip()
            try:
                amount = int(text) if text else 0
            except ValueError:
                self._table().set_toast("Introduce un número entero.")
                return
            self._resolve(amount)
        elif event.button.id == "chicken-button":
            self._resolve(0)
