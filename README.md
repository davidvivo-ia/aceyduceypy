# Acey-Ducey

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-69%20passing-brightgreen.svg)](#tests)
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)](#tests)

Reimaginación 2026 del clásico **Acey Ducey Card Game** (Bill Palmby,
*BASIC Computer Games*, Creative Computing, 1973). Mismas reglas, mazo
real de 52 cartas con palos, TUI con Textual, paleta de fósforo verde,
récord persistente, pagos por riesgo opcionales y un bot determinista
para verificación automática.

```text
┌─────────┐  ┌─────────┐  ╔═════════╗
│5        │  │J        │  ║8        ║
│         │  │         │  ║         ║
│    ♥    │  │    ♠    │  ║    ♣    ║
│         │  │         │  ║         ║
│        5│  │        J│  ║        8║
└─────────┘  └─────────┘  ╚═════════╝
   low          high       veredicto
```

## Reglas

El crupier reparte dos cartas boca arriba. Tú apuestas (o pasas
apostando 0) a que la tercera caerá **estrictamente** entre ellas en
rango. Si empata con un borde, pierdes. El juego termina al quedarte
sin dinero.

## Instalación y ejecución

Requiere Python 3.13+. Con [`uv`](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/davidvivo-ia/aceyduceypy.git
cd aceyduceypy
uv sync
uv run aceyducey
```

O sin script de uv, con un solo fichero en la raíz:

```bash
python play.py                 # mismo CLI; acepta los mismos flags
python play.py --demo          # partida automática
```

Y si prefieres `pip` puro:

```bash
pip install -e .
aceyducey                      # script instalado
python -m aceyducey            # módulo
```

## Opciones de línea de comandos

| Flag | Efecto |
|---|---|
| `-b, --balance N` | Balance inicial (default 100). |
| `-s, --seed N` | Semilla para partidas reproducibles. |
| `--classic` | Pagos planos 1:1 como en el BASIC original. |
| `--bonus` | Pagos por riesgo 5×/3×/2×/1× (default). |
| `--no-odds` | Oculta la probabilidad y el EV. |
| `--demo` | Bot determinista, 50 manos, semilla fija (42). |
| `--no-tui` | Salida por texto plano (útil para CI y accesibilidad). |
| `--version` | Imprime versión y sale. |

Ejemplos:

```bash
uv run aceyducey                       # TUI completa con bonificaciones
uv run aceyducey --classic --no-odds   # modo nostalgia 1:1
uv run aceyducey --demo --seed 42      # partida automática reproducible
uv run aceyducey --no-tui              # texto plano interactivo
```

## Atajos de teclado en la TUI

- `Enter`: confirmar la apuesta del campo de entrada.
- `0` o `Esc`: pasar la mano (gallina).
- `Ctrl+R`: reiniciar una partida nueva.
- `Ctrl+Q`: salir del juego.
- `?`: mostrar ayuda en el panel lateral.

## Mejoras sobre el original

- Mazo real de 52 cartas con palos en lugar de enteros con reposición.
- Pagos por riesgo (5×/3×/2×/1× según el spread) además del modo
  clásico 1:1.
- Probabilidad y valor esperado calculados y mostrados antes de cada
  apuesta.
- Re-deal automático en parejas y cartas consecutivas.
- Récord persistente entre sesiones.
- TUI con paleta cuidada y arte ASCII de cartas, frente a los `PRINT`
  por línea del original.
- Bot `--demo` determinista para CI y para grabar transcripciones.

Detalles completos en
[`CHANGELOG.md`](CHANGELOG.md) y bugs del original corregidos en
[`docs/original_program_analysis.md`](docs/original_program_analysis.md).

## Estructura

```
src/aceyducey/
├── domain/         Cartas, mazo, pagos, probabilidad
├── application/    Game session, puertos, eventos
├── infrastructure/ RNG, persistencia XDG, reloj
├── presentation/   Textual TUI + CLI + driver plano + bot demo
└── assets/         CSS para Textual
legacy/             BASIC original intacto (read-only)
docs/               Análisis, arquitectura, diseño, ADRs, postmortem
tests/              unit/ + integration/ + property/
```

## Tests

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy --strict src
uv run pytest --cov=src --cov-report=term-missing
uv run aceyducey --demo --seed 42 --no-tui      # smoke E2E
```

Cobertura actual: **92 %** sobre dominio + aplicación + infraestructura
(la presentación se valida manualmente y vía `--demo`).

## Licencias

- Código moderno: MIT (ver [`LICENSE`](LICENSE)).
- Listado BASIC en `legacy/`: dominio público de hecho (Creative
  Computing, 1973/1978). Procedencia detallada en
  [`legacy/SOURCES.md`](legacy/SOURCES.md).

## Referencias

- *BASIC Computer Games* (David H. Ahl, ed.), Creative Computing, 1978.
- [Acey-Ducey en la edición coding-horror del libro][bcg].
- [Bill Palmby — autor del listado original][palmby].

[bcg]: https://github.com/coding-horror/basic-computer-games/blob/main/00_Alternate_Languages/01_Acey_Ducey/aceyducey.bas
[palmby]: https://stonecoldprofessor.com/basic-computer-games/card-and-board/acey-ducey/
