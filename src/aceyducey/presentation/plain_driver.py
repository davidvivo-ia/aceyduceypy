"""Plain-text driver used in ``--demo`` and ``--no-tui`` modes.

It exercises the full application stack without Textual: useful for CI
smoke checks, recording transcripts, and accessibility fallback.
"""

from __future__ import annotations

from collections.abc import Iterator

from rich.console import Console

from aceyducey.application import (
    DealtHandEvent,
    GameConfig,
    GameSession,
    HandResolvedEvent,
    HighscorePort,
    RedealEvent,
    RngPort,
)
from aceyducey.application.stats import SessionStats
from aceyducey.domain import BetOutcome
from aceyducey.presentation.card_art import render_card, render_row
from aceyducey.presentation.demo_policy import DemoBettingPolicy


class PlainDriver:
    """Runs a game session against stdin/stdout using Rich markup."""

    def __init__(
        self,
        *,
        config: GameConfig,
        rng: RngPort,
        highscore_repo: HighscorePort,
        demo: bool = False,
    ) -> None:
        self._session = GameSession(config=config, rng=rng, highscore_repo=highscore_repo)
        self._demo = demo
        self._policy = DemoBettingPolicy()
        self._console = Console(highlight=False)

    def run(self) -> int:
        c = self._console
        start = self._session.start()
        c.rule("[bold cyan]ACEY-DUCEY[/]")
        c.print(f"Balance inicial: [bold]${start.starting_balance}[/]")
        if start.previous_highscore:
            c.print(f"Récord anterior: [dim]${start.previous_highscore}[/]")
        c.print()

        hands_played = 0
        try:
            while not self._session.is_game_over:
                if self._demo and hands_played >= self._policy.hand_limit:
                    c.print(f"[dim]Límite de demo alcanzado ({self._policy.hand_limit} manos).[/]")
                    break
                dealt = self._await_playable_hand()
                bet = self._decide_bet(dealt)
                resolved = self._session.place_bet(bet)
                self._render_resolution(resolved)
                hands_played += 1
        except KeyboardInterrupt:
            c.print("[yellow]Interrumpido por el usuario.[/]")
            return 130

        end = self._session.finish()
        self._render_summary(end.stats, new_highscore=end.new_highscore)
        return 0

    # ------------------------------------------------------------------ helpers

    def _await_playable_hand(self) -> DealtHandEvent:
        events: Iterator[DealtHandEvent | RedealEvent] = self._session.deal()
        for event in events:
            if isinstance(event, RedealEvent):
                self._render_redeal(event)
                continue
            self._render_dealt(event)
            return event
        raise RuntimeError("session.deal exhausted without DealtHandEvent")

    def _decide_bet(self, dealt: DealtHandEvent) -> int:
        if self._demo:
            bet = self._policy.decide(
                probability=dealt.win_probability,
                multiplier=dealt.multiplier,
                balance=dealt.balance,
            )
            self._console.print(f"[dim]demo bot apuesta:[/] [bold]${bet}[/]")
            return bet
        return self._prompt_bet(max_bet=dealt.balance)

    def _prompt_bet(self, *, max_bet: int) -> int:
        while True:
            raw = self._console.input(f"¿Cuánto apuestas? (0 = pasar, máx ${max_bet}): ").strip()
            try:
                value = int(raw)
            except ValueError:
                self._console.print("[yellow]Introduce un número entero.[/]")
                continue
            if value < 0 or value > max_bet:
                self._console.print(f"[yellow]Rango válido: 0..{max_bet}[/]")
                continue
            return value

    def _render_dealt(self, event: DealtHandEvent) -> None:
        c = self._console
        hand = event.hand
        art = render_row([render_card(hand.low), render_card(hand.high)])
        c.print(art)
        edge = event.win_probability * event.multiplier - (1 - event.win_probability)
        edge_color = "green" if edge > 0 else "red"
        if self._session.config.show_odds:
            c.print(
                f"[dim]P(ganar) ≈ {event.win_probability:.1%}  ·  "
                f"pago {event.multiplier}:1  ·  "
                f"EV/$ [{edge_color}]{edge:+.2f}[/][/]"
            )
        c.print(f"Balance: [bold cyan]${event.balance}[/]")

    def _render_redeal(self, event: RedealEvent) -> None:
        c = self._console
        a, b = event.revealed
        art = render_row([render_card(a), render_card(b)])
        c.print(art)
        if event.reason == "pair":
            c.print(f"[magenta]Pareja de {a.rank.spanish_name}. Se reparte de nuevo.[/]")
        else:
            c.print("[yellow]Cartas consecutivas — imposible ganar. Se reparte de nuevo.[/]")
        c.print()

    def _render_resolution(self, event: HandResolvedEvent) -> None:
        c = self._console
        res = event.resolution
        if res.bet == 0:
            c.print("[magenta]¡Gallina![/]\n")
            return
        c.print(render_row([render_card(res.drawn, highlighted=True)]))
        match res.outcome:
            case BetOutcome.WIN:
                c.print(f"[bold green]✔ GANAS ${res.delta} (x{res.multiplier})[/]")
            case BetOutcome.EDGE_LOSS:
                c.print(f"[bold red]✘ Empate con borde. Pierdes ${res.bet}[/]")
            case BetOutcome.LOSS:
                c.print(f"[bold red]✘ Pierdes ${res.bet}[/]")
        c.print(f"Balance: [bold cyan]${event.balance}[/]\n")

    def _render_summary(self, stats: SessionStats, *, new_highscore: bool) -> None:
        c = self._console
        c.rule("[bold]Resumen[/]")
        c.print(f"  Manos jugadas       : {stats.hands_dealt}")
        c.print(f"  Apuestas hechas     : {stats.bets_placed}")
        c.print(f"  Pasadas (gallina)   : {stats.chickened_out}")
        c.print(f"  Victorias / Derrotas: {stats.wins} / {stats.losses}")
        c.print(f"  Empates con borde   : {stats.edge_losses}")
        c.print(f"  Win-rate            : {stats.win_rate:.1%}")
        c.print(f"  Mayor ganancia      : ${stats.biggest_win}")
        c.print(f"  Mayor pérdida       : ${stats.biggest_loss}")
        c.print(f"  Pico de balance     : ${stats.peak_balance}")
        delta_color = "green" if stats.net >= 0 else "red"
        sign = "+" if stats.net >= 0 else ""
        c.print(
            f"  Balance final       : [bold]${stats.balance}[/] "
            f"([{delta_color}]{sign}{stats.net}[/])"
        )
        if new_highscore:
            c.print("\n[bold green]★ NUEVO RÉCORD[/]")
