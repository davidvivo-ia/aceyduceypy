# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/), versionado
semántico.

## [1.0.0] — 2026-05-12

### Preservado del original

- Reglas básicas: dos cartas reveladas, apostar a que la tercera caiga
  estrictamente entre ellas, perder en empate con borde, comenzar con
  $100 y jugar hasta arruinarse.
- Posibilidad de pasar la mano apostando 0 («gallina»).
- Mensaje y bucle de "Try again" tras la bancarrota.

### Modernizado

- Mazo real de 52 cartas con palos (♠♥♦♣) barajado por mano. El original
  sorteaba enteros con reposición.
- Eliminada la variable muerta `N` y los IF anidados duplicados de
  impresión.
- Sorteo por baraja en lugar de bucle de rechazo defensivo.
- TUI con Textual y CSS propio en lugar de PRINTs línea a línea.
- CLI con Typer en lugar de menú implícito.
- Tipado estricto (mypy --strict), inmutabilidad por defecto, arquitectura
  hexagonal con cuatro capas.

### Añadido

- Probabilidad y valor esperado calculados y mostrados antes de cada
  apuesta.
- Pagos por riesgo (5×/3×/2×/1×) según el spread, con `--classic`
  recuperando el comportamiento 1:1.
- Estadísticas de sesión: manos, redeals, win-rate, mayor ganancia,
  mayor pérdida, empates con borde, pico de balance.
- Récord persistente en `~/.local/share/aceyducey/highscore.json` (XDG).
- Modo `--seed` determinista para partidas reproducibles.
- Modo `--demo` que juega solo siguiendo una política de Kelly
  simplificada y tope de 50 manos.
- Modo `--no-tui` para CI y accesibilidad: el juego funciona en texto
  plano sin Textual.
- Re-deal automático en pareja inicial y en cartas consecutivas.
- Tests unitarios, de propiedad (Hypothesis) y de integración (69 tests,
  92 % de cobertura sobre dominio/aplicación/infraestructura).
- Pipeline de CI con matriz Python 3.13 / 3.14, ruff, mypy, pytest y
  smoke del modo demo.

### Bugs corregidos del original

- `N=100` era una variable muerta (línea 100).
- Las ramas `IF A<2 THEN 270` (líneas 280, 320, 740) son inalcanzables.
- El game-over por `M=Q` en derrota (línea 980) no descontaba la última
  apuesta. Ahora siempre se descuenta antes de evaluar la bancarrota.
- La pregunta "TRY AGAIN" (línea 1030) solo aceptaba "YES" literal en
  mayúsculas. Ahora cualquier prefijo de sí/si/yes/y/s en cualquier
  capitalización funciona.

### Licencias creativas tomadas

- Las cartas tienen palos, ausentes en el original. Los palos rojos
  (♥♦) se renderizan en rojo.
- Las cartas consecutivas o iguales se re-reparten automáticamente. En el
  original no se mostraban consecutivas porque `RND` rara vez las daba
  con el reroll forzado A<B, pero podían ocurrir.
- El payout escalonado es un añadido para mantener tensión a lo largo de
  más manos. El modo `--classic` se mantiene fiel al 1:1.
- El programa muestra probabilidad y EV. El original asumía que el
  jugador llevaba las cuentas en la cabeza.
- Récord persistente. El original era amnésico entre partidas.

[1.0.0]: https://github.com/davidvivo-ia/aceyduceypy/releases/tag/v1.0.0
