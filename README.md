# Acey-Ducey

Reimaginación 2026 del clásico *Acey Ducey Card Game* (Bill Palmby,
Creative Computing, 1973). Mismas reglas, mazo de 52 cartas con palos,
TUI con Textual, paleta de fósforo verde y récord persistente.

```text
┌─────────┐  ┌─────────┐  ╔═════════╗
│5        │  │J        │  ║8        ║
│         │  │         │  ║         ║
│    ♥    │  │    ♠    │  ║    ♣    ║
│         │  │         │  ║         ║
│        5│  │        J│  ║        8║
└─────────┘  └─────────┘  ╚═════════╝
   low          high       outcome
```

## Cómo jugar

```bash
uv sync
uv run aceyducey
```

Opciones:

| Flag | Efecto |
|---|---|
| `--seed 42` | Partida reproducible. |
| `--balance 500` | Balance inicial (default 100). |
| `--classic` | Pagos planos 1:1 como en el BASIC original. |
| `--no-odds` | Oculta el panel de probabilidad y EV. |
| `--demo` | Partida automática determinista (útil para grabar GIFs y CI). |
| `--no-tui` | Salida por texto plano sin Textual. |
| `--no-color` | Sin códigos ANSI. |

## Verificación rápida

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
uv run pytest --cov=src
uv run aceyducey --demo --seed 42 --no-tui
```

## Estructura

```
src/aceyducey/
├── domain/         # cartas, mazo, política de pagos
├── application/    # GameSession, puertos
├── infrastructure/ # RNG, persistencia XDG
├── presentation/   # Textual App + CLI + modo demo
└── assets/         # CSS Textual
legacy/             # BASIC original (read-only)
docs/               # análisis, arquitectura, diseño, ADRs
```

## Licencias

Código moderno bajo MIT. El listado BASIC en `legacy/` fue publicado en
*BASIC Computer Games* (1973/1978) para tipeo libre; ver `legacy/SOURCES.md`.
