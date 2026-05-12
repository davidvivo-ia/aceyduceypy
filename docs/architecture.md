# Arquitectura

## Visión

Arquitectura hexagonal (puertos & adaptadores) en cuatro capas concéntricas.
El dominio no conoce a nadie; cada capa exterior depende solo de las
interiores. Esto permite testear el juego completo sin tocar Textual ni
disco.

## Diagrama de capas

```
        ┌──────────────────────────────────────────────────┐
        │  presentation/                                   │
        │  - Textual TUI (App, Screens, Widgets)           │
        │  - Typer CLI entrypoint                          │
        │  - assets/ (CSS, ASCII art de cartas)            │
        └────────────────────┬─────────────────────────────┘
                             │ depende de
                             ▼
        ┌──────────────────────────────────────────────────┐
        │  application/                                    │
        │  - GameSession  (estado de partida, orquesta)    │
        │  - DealHand, PlaceBet, EndGame                   │
        └────────────────────┬─────────────────────────────┘
                             │ depende de
                             ▼
        ┌──────────────────────────────────────────────────┐
        │  domain/                                         │
        │  - Card, Rank, Suit                              │
        │  - Deck (factory + shuffle protocol)             │
        │  - Hand, BetOutcome, PayoutPolicy                │
        │  - DomainErrors                                  │
        └──────────────────────────────────────────────────┘

        ┌──────────────────────────────────────────────────┐
        │  infrastructure/  (adaptadores; flecha invertida)│
        │  - SystemRandom adapter (implementa RngPort)     │
        │  - JsonHighscoreRepo (implementa HighscorePort)  │
        │  - XDG paths                                     │
        └──────────────────────────────────────────────────┘
              ▲
              │ implementa puertos definidos en
              │ application/
              └──── (inyección por constructor)
```

## Puertos definidos en `application/ports.py`

- `RngPort`: `shuffle(seq) -> None`, `random() -> float`. Implementado por
  `SystemRandomAdapter` en infraestructura.
- `HighscorePort`: `load() -> int`, `save(peak: int) -> None`. Implementado
  por `JsonHighscoreRepository`.
- `Clock`: `now() -> datetime`. Útil para la cabecera del save y para
  futuras estadísticas temporales.

## Flujo de una mano

```
TUI evento "deal"
        ▼
GameSession.start_hand()
        ├── pide al Deck barajado por RngPort
        ├── reparte 2 cartas, ordena (low, high)
        ├── detecta pareja → re-deal
        ├── detecta consecutivas → re-deal
        └── calcula probabilidad y multiplicador (PayoutPolicy)
TUI muestra cartas + odds
        ▼
TUI evento "bet" con cantidad M
        ▼
GameSession.place_bet(M)
        ├── valida 0 ≤ M ≤ balance
        ├── reparte tercera carta
        ├── compara y resuelve outcome
        ├── actualiza balance y stats
        └── devuelve BetResolution (DTO inmutable)
TUI muestra outcome y refresca panel
        ▼
si balance == 0 → GameSession.finish() → emite final stats →
        HighscoreRepository.save(max(prev, peak))
```

## Reglas que viven en el dominio

- Una carta es `(Rank, Suit)`.
- Un `Deck` se crea ordenado y se baraja inyectando un `RngPort`.
- `Hand` modela la mano actual: cartas reveladas, fase, posibilidad de
  apostar.
- `PayoutPolicy` es un valor inmutable; hay dos políticas (`classic` y
  `bonus`) que el caso de uso elige según la `GameConfig`.
- `BetOutcome` es una enumeración pura: `WIN`, `LOSS`, `EDGE_LOSS`.

## Reglas que viven en aplicación

- `GameSession` mantiene el `balance`, `stats`, `config` y la `Hand`
  activa.
- Validaciones de input (apuesta dentro de rango) son aquí, no en TUI.
- TUI no toca el `Deck` ni la `Random`: pasa intención («apostar M»,
  «pasar», «empezar nueva mano») y recibe estado.

## Reglas que viven en presentación

- Textual `App` con tres pantallas: `SplashScreen`, `TableScreen`,
  `SummaryScreen`.
- CSS en `assets/aceyducey.tcss` define paleta, tipografía y espaciado.
- Widget `CardWidget` renderiza una carta con marco y palo.
- Modo `--demo` ejecuta una `DemoDriver` que simula pulsaciones de
  teclado con un seed fijo y políticas deterministas (apuesta proporcional
  a la probabilidad).
- CLI: `typer` con `--seed`, `--balance`, `--classic`, `--no-odds`,
  `--demo`, `--no-tui` (modo texto plano para CI), `--export-stats`.

## Dependencias

| Capa | Permitido importar | Prohibido |
|---|---|---|
| `domain` | stdlib | todo lo demás |
| `application` | `domain`, stdlib | `infrastructure`, `presentation` |
| `infrastructure` | `domain`, `application`, terceros | `presentation` |
| `presentation` | todo | — |

El `__main__.py` compone: instancia adaptadores concretos, los inyecta en
`GameSession`, y arranca la `App`.

## Testabilidad

- Dominio: 100% testeable con valores. `FrozenRng(values=[...])` falso para
  reproducir cualquier secuencia.
- Aplicación: integración con falsos.
- Infraestructura: pruebas de IO con `tmp_path`.
- Presentación: Textual ofrece `App.run_test()` con `Pilot` para simular
  teclado; el modo `--demo` sirve como E2E.
