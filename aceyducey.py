"""Acey-Ducey — port y modernización del clásico de BASIC Computer Games (1973).

Original de Bill Palmby (Creative Computing, Morristown NJ).
Esta versión usa un mazo real de 52 cartas, pagos por riesgo, estadísticas,
récord persistente, probabilidad calculada y arte ASCII a color.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass
from enum import Enum, IntEnum
from pathlib import Path


# ───────────────────────── Presentación ─────────────────────────

class Ansi:
    """Códigos ANSI; se vacían si la salida no es un TTY o con --no-color."""
    RESET = "\x1b[0m"
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    MAGENTA = "\x1b[35m"
    CYAN = "\x1b[36m"
    WHITE = "\x1b[37m"

    @classmethod
    def disable(cls) -> None:
        for name in ("RESET", "BOLD", "DIM", "RED", "GREEN", "YELLOW",
                     "BLUE", "MAGENTA", "CYAN", "WHITE"):
            setattr(cls, name, "")


# ───────────────────────── Modelo de cartas ─────────────────────

class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def label(self) -> str:
        return {
            Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K", Rank.ACE: "A",
        }.get(self, str(self.value))

    @property
    def name_es(self) -> str:
        return {
            Rank.JACK: "JOTA", Rank.QUEEN: "REINA",
            Rank.KING: "REY", Rank.ACE: "AS",
        }.get(self, str(self.value))


class Suit(Enum):
    SPADES = ("♠", False)
    HEARTS = ("♥", True)
    DIAMONDS = ("♦", True)
    CLUBS = ("♣", False)

    @property
    def symbol(self) -> str:
        return self.value[0]

    @property
    def is_red(self) -> bool:
        return self.value[1]


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    def __lt__(self, other: "Card") -> bool:
        return self.rank < other.rank

    def __str__(self) -> str:
        color = Ansi.RED if self.suit.is_red else Ansi.WHITE
        return f"{color}{self.rank.label}{self.suit.symbol}{Ansi.RESET}"

    def ascii_art(self) -> list[str]:
        c = Ansi.RED if self.suit.is_red else ""
        r = self.rank.label
        rl, rr = r.ljust(2), r.rjust(2)
        s = self.suit.symbol
        return [
            "┌─────────┐",
            f"│{c}{rl}{Ansi.RESET}       │",
            "│         │",
            f"│    {c}{s}{Ansi.RESET}    │",
            "│         │",
            f"│       {c}{rr}{Ansi.RESET}│",
            "└─────────┘",
        ]


def make_deck() -> list[Card]:
    return [Card(r, s) for r in Rank for s in Suit]


def render_cards(cards: list[Card]) -> str:
    rows = zip(*(c.ascii_art() for c in cards))
    return "\n".join("  ".join(row) for row in rows)


# ───────────────────────── Reglas y matemáticas ─────────────────

def odds_between(low: Rank, high: Rank, deck_size: int = 50) -> float:
    """Probabilidad de que la siguiente carta caiga estrictamente entre low y high."""
    favorable = (int(high) - int(low) - 1) * 4
    return favorable / max(deck_size, 1)


def payout_multiplier(low: Rank, high: Rank, *, bonus: bool = True) -> int:
    """Pagos por riesgo. Sin bonificación es 1:1 como el BASIC original."""
    if not bonus:
        return 1
    spread = int(high) - int(low) - 1
    if spread <= 1:
        return 5
    if spread <= 3:
        return 3
    if spread <= 6:
        return 2
    return 1


# ───────────────────────── Estado y estadísticas ────────────────

@dataclass
class Stats:
    hands_played: int = 0
    bets_placed: int = 0
    chickened_out: int = 0
    wins: int = 0
    losses: int = 0
    biggest_win: int = 0
    biggest_loss: int = 0
    starting_balance: int = 100
    final_balance: int = 100
    peak_balance: int = 100

    @property
    def win_rate(self) -> float:
        return self.wins / self.bets_placed if self.bets_placed else 0.0

    @property
    def net(self) -> int:
        return self.final_balance - self.starting_balance


@dataclass
class GameConfig:
    starting_balance: int = 100
    seed: int | None = None
    bonus_payouts: bool = True
    show_odds: bool = True


HIGHSCORE_FILE = Path.home() / ".aceyducey_highscore.json"


def load_highscore() -> int:
    try:
        return int(json.loads(HIGHSCORE_FILE.read_text()).get("peak", 0))
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        return 0


def save_highscore(peak: int) -> None:
    try:
        HIGHSCORE_FILE.write_text(json.dumps({"peak": peak}))
    except OSError:
        pass


# ───────────────────────── Entrada del usuario ──────────────────

def prompt_int(prompt: str, *, lo: int | None = None, hi: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print(f"{Ansi.YELLOW}Introduce un número entero.{Ansi.RESET}")
            continue
        if lo is not None and value < lo:
            print(f"{Ansi.YELLOW}Mínimo: {lo}.{Ansi.RESET}")
            continue
        if hi is not None and value > hi:
            print(f"{Ansi.YELLOW}Máximo: {hi}.{Ansi.RESET}")
            continue
        return value


def prompt_yes_no(prompt: str, *, default: bool = True) -> bool:
    suffix = " [S/n] " if default else " [s/N] "
    while True:
        raw = input(prompt + suffix).strip().lower()
        if not raw:
            return default
        if raw in {"s", "si", "sí", "y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print(f"{Ansi.YELLOW}Responde 's' o 'n'.{Ansi.RESET}")


# ───────────────────────── Bucle de juego ───────────────────────

def play_round(
    deck: list[Card], balance: int, config: GameConfig, stats: Stats,
) -> int:
    """Juega una mano. Devuelve el nuevo balance. Mutates stats."""
    a, b = deck.pop(), deck.pop()
    if a.rank == b.rank:
        print(f"\n{Ansi.MAGENTA}¡Pareja de {a.rank.name_es}! Se reparte de nuevo.{Ansi.RESET}")
        return balance

    low, high = sorted((a, b))
    print(f"\n{Ansi.BOLD}Tus dos cartas:{Ansi.RESET}")
    print(render_cards([low, high]))

    spread = int(high.rank) - int(low.rank) - 1
    if spread == 0:
        print(f"{Ansi.YELLOW}Cartas consecutivas — imposible ganar. "
              f"Se reparte de nuevo.{Ansi.RESET}")
        return balance

    if config.show_odds:
        p = odds_between(low.rank, high.rank, deck_size=len(deck))
        mult = payout_multiplier(low.rank, high.rank, bonus=config.bonus_payouts)
        ev = p * mult - (1 - p)
        ev_color = Ansi.GREEN if ev > 0 else Ansi.RED
        print(f"{Ansi.DIM}P(ganar) ≈ {p:.1%}  ·  pago {mult}:1  ·  "
              f"EV/$ {ev_color}{ev:+.2f}{Ansi.RESET}")
    print(f"{Ansi.CYAN}Balance: ${balance}{Ansi.RESET}")

    bet = prompt_int(f"¿Cuánto apuestas? (0 = pasar, máx ${balance}): ",
                     lo=0, hi=balance)
    stats.hands_played += 1
    if bet == 0:
        print(f"{Ansi.MAGENTA}¡Gallina!{Ansi.RESET}")
        stats.chickened_out += 1
        return balance

    stats.bets_placed += 1
    third = deck.pop()
    print(f"\n{Ansi.BOLD}Tercera carta:{Ansi.RESET}")
    print(render_cards([third]))

    if low.rank < third.rank < high.rank:
        mult = payout_multiplier(low.rank, high.rank, bonus=config.bonus_payouts)
        winnings = bet * mult
        balance += winnings
        stats.wins += 1
        stats.biggest_win = max(stats.biggest_win, winnings)
        print(f"{Ansi.GREEN}{Ansi.BOLD}¡GANASTE ${winnings}! "
              f"(x{mult}){Ansi.RESET}")
    else:
        balance -= bet
        stats.losses += 1
        stats.biggest_loss = max(stats.biggest_loss, bet)
        if third.rank in (low.rank, high.rank):
            print(f"{Ansi.RED}{Ansi.BOLD}¡La carta toca un borde! "
                  f"Pierdes ${bet}.{Ansi.RESET}")
        else:
            print(f"{Ansi.RED}{Ansi.BOLD}Pierdes ${bet}.{Ansi.RESET}")

    stats.peak_balance = max(stats.peak_balance, balance)
    stats.final_balance = balance
    return balance


def play(config: GameConfig) -> Stats:
    rng = random.Random(config.seed)
    balance = config.starting_balance
    stats = Stats(
        starting_balance=balance,
        final_balance=balance,
        peak_balance=balance,
    )

    print_rules(config)
    print(f"{Ansi.CYAN}Comienzas con ${balance}.{Ansi.RESET}")

    while balance > 0:
        deck = make_deck()
        rng.shuffle(deck)
        # Cada mano usa 2-3 cartas; barajamos uno nuevo por mano para simplicidad
        # estadística (cada mano es un experimento independiente sobre 52).
        balance = play_round(deck, balance, config, stats)

    print(f"\n{Ansi.RED}{Ansi.BOLD}¡Te quedaste sin dinero!{Ansi.RESET}")
    return stats


# ───────────────────────── UI / impresión ───────────────────────

def print_banner() -> None:
    print(f"""{Ansi.CYAN}{Ansi.BOLD}
╔════════════════════════════════════════╗
║          ACEY-DUCEY CARD GAME          ║
║         Python edition · v2.0          ║
╚════════════════════════════════════════╝{Ansi.RESET}
""")


def print_rules(config: GameConfig) -> None:
    bonus = ("Pagos bonificados según el riesgo (5x / 3x / 2x / 1x)."
             if config.bonus_payouts else "Pagos clásicos 1:1.")
    print(f"""{Ansi.BOLD}Reglas:{Ansi.RESET}
  · Te reparten dos cartas boca arriba.
  · Apuesta si crees que la siguiente caerá ESTRICTAMENTE entre ellas.
  · Apuesta 0 para pasar la mano.
  · Si la tercera carta empata con un borde, pierdes la apuesta.
  · {bonus}
""")


def print_summary(stats: Stats, prev_high: int) -> None:
    print(f"\n{Ansi.BOLD}── Resumen de la partida ──{Ansi.RESET}")
    print(f"  Manos jugadas       : {stats.hands_played}")
    print(f"  Apuestas hechas     : {stats.bets_placed}")
    print(f"  Pasadas (gallina)   : {stats.chickened_out}")
    print(f"  Victorias / Derrotas: {stats.wins} / {stats.losses}")
    print(f"  Tasa de victorias   : {stats.win_rate:.1%}")
    print(f"  Mayor ganancia      : ${stats.biggest_win}")
    print(f"  Mayor pérdida       : ${stats.biggest_loss}")
    print(f"  Pico de balance     : ${stats.peak_balance}")
    sign = "+" if stats.net >= 0 else ""
    color = Ansi.GREEN if stats.net >= 0 else Ansi.RED
    print(f"  Balance final       : ${stats.final_balance} "
          f"({color}{sign}{stats.net}{Ansi.RESET})")
    if stats.peak_balance > prev_high:
        print(f"\n{Ansi.GREEN}{Ansi.BOLD}🏆 ¡Nuevo récord! "
              f"Anterior: ${prev_high}{Ansi.RESET}")


# ───────────────────────── CLI ──────────────────────────────────

def parse_args(argv: list[str] | None = None) -> GameConfig:
    parser = argparse.ArgumentParser(
        prog="aceyducey",
        description="Acey-Ducey card game (port y mejora del BASIC de 1973).",
    )
    parser.add_argument("-b", "--balance", type=int, default=100,
                        help="balance inicial (por defecto 100)")
    parser.add_argument("-s", "--seed", type=int, default=None,
                        help="semilla para reproducir partidas")
    parser.add_argument("--classic", action="store_true",
                        help="pagos 1:1 como el BASIC original")
    parser.add_argument("--no-odds", action="store_true",
                        help="no mostrar probabilidad ni EV")
    parser.add_argument("--no-color", action="store_true",
                        help="desactivar colores ANSI")
    args = parser.parse_args(argv)

    if args.no_color or not sys.stdout.isatty():
        Ansi.disable()

    if args.balance < 1:
        parser.error("--balance debe ser >= 1")

    return GameConfig(
        starting_balance=args.balance,
        seed=args.seed,
        bonus_payouts=not args.classic,
        show_odds=not args.no_odds,
    )


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv)
    print_banner()
    prev_high = load_highscore()
    if prev_high:
        print(f"{Ansi.DIM}Récord anterior: ${prev_high}{Ansi.RESET}\n")

    try:
        while True:
            stats = play(config)
            print_summary(stats, prev_high)
            new_high = max(prev_high, stats.peak_balance)
            save_highscore(new_high)
            prev_high = new_high
            if not prompt_yes_no("\n¿Otra partida?", default=True):
                break
    except (KeyboardInterrupt, EOFError):
        print(f"\n{Ansi.YELLOW}Partida interrumpida. ¡Hasta pronto!{Ansi.RESET}")
        return 130

    print(f"{Ansi.CYAN}¡Espero que te hayas divertido!{Ansi.RESET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
