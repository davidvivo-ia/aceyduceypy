# TODO — Roadmap post v1.0

## v1.1 (próximo)

1. **Política de pagos "fair" (EV ≈ 0)** anticipada en ADR 0005:
   multiplicador exacto `round(1 / p_win)`. Convierte el juego en un
   estudio matemático puro. Estimación: pequeña, ~2 horas.

2. **Modo "shoe": mazo de 6 barajas sin reposición** entre manos.
   Habilita conteo de cartas y refleja la mecánica del Red Dog real de
   casino. Requiere ajustar `odds_between` para que use el conteo
   dinámico del zapato, ya parametrizado.

3. **Tests Textual con `App.run_test()` + `Pilot`** para la TUI. Cubrir
   pantallas, bindings y transiciones. Subir cobertura global por encima
   del 95 %. Estimación: 4-6 horas.

4. **Exportar transcripción de la partida** con `--export-stats path.json`
   y `--export-svg path.svg` (Rich soporta `Console.save_svg`). Útil
   para compartir partidas reproducibles.

5. **Sonido opcional con AY-3-8912 sintético**: `--sound` activa un beep
   sintetizado al revelar la tercera carta. Generado con `numpy` y
   reproducido con `sounddevice`. Solo si el usuario lo activa
   explícitamente.

## v1.2 (más adelante)

- Tabla de récords por dificultad (classic / bonus / fair / shoe).
- Modo multijugador local por turnos.
- Web build con `textual-web` para jugar desde el navegador.

## Limitaciones conocidas v1.0

- La TUI no tiene tests automatizados; se valida manualmente y vía el
  modo `--no-tui` en CI.
- El modo `--demo` se trunca a 50 manos para evitar partidas infinitas
  cuando el bot acumula balance gigante. Es deseable, no un bug.
- No hay i18n: los textos de UI están solo en español.
- En terminales sin soporte Unicode los bordes de cartas y los palos se
  ven como cuadrados. El usuario puede usar `--no-tui` y leer letras +
  símbolo.
