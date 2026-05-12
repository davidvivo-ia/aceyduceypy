# ADR 0001 — Capa de presentación: Textual TUI

## Contexto

El original es un programa `INPUT/PRINT` puro de 100 líneas sin gráficos,
sin caracteres semigráficos y sin sonido. El espíritu del juego es
textual: cartas representadas por nombres ("JACK", "QUEEN"), apuesta como
input numérico, respuestas SÍ/NO. La regla automática del documento de
encuadre dice: «texto puro → TUI con Textual».

## Opciones consideradas

1. **CLI con Typer + Rich**. Simple, no requiere terminal interactivo
   complejo. Pero pierde la sensación de "casino de teletipo" en vivo y
   complica mostrar el panel lateral con probabilidad sin redibujar
   toda la pantalla.
2. **TUI con Textual**. Componentes reactivos, CSS propio, screens
   navegables, ratón opcional, soporta `App.run_test()` para E2E.
3. **pygame-ce gráfico**. Sobreingeniería: el original no tenía píxeles
   y forzaríamos una identidad ajena.
4. **TUI con curses puro**. Funciona pero implica reinventar layout,
   manejo de teclado, focus. Sin valor frente a Textual.

## Decisión

**Textual**. Cubre el 100% del original con margen de mejora visual
moderado, permite test E2E con `Pilot`, y la doble línea de marco para la
tercera carta — pensada como toque distintivo — se implementa en cinco
líneas de CSS.

## Consecuencias

- Dependencia en `textual` y, transitiva, `rich`. Aceptable: ambas son
  estables y de uso masivo.
- El "modo demo determinista" necesita explícitamente `pilot.press()`
  desde Python para no requerir tty interactivo en CI; añadiremos también
  un `--no-tui` que reproduce la partida por stdout para auditoría
  textual rápida (útil para grabar la transcripción en docs).
- Los assets (CSS) viven en `src/aceyducey/assets/` y se cargan vía
  `Path(__file__).parent / "assets"`.
