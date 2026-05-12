# Sistema de diseño

## Concepto en una frase

Un casino de teletipo: la frialdad geométrica de Acey-Ducey de 1973
recubierta de una piel CRT verde fósforo, con cartas dibujadas a borde
ASCII y un panel de probabilidad como única concesión al jugador moderno.

## Paleta

Homenaje a los terminales DEC VT100 (fósforo verde sobre negro) cruzado
con la paleta de carta de poker. Siete colores. Contraste WCAG AA
verificado contra fondo `#0b0d0a`.

| Rol | Nombre | Hex | Uso |
|---|---|---|---|
| `background` | Carbon | `#0b0d0a` | Fondo base de la app |
| `surface` | Slate | `#1a1f1c` | Paneles, tarjetas, modal |
| `primary` | Phosphor | `#7CFF8A` | Texto principal, marcos, énfasis |
| `accent` | Amber | `#F0B14E` | Datos clave (balance, apuesta) |
| `success` | Lime | `#9AE66E` | Victoria, EV positivo |
| `danger` | Crimson | `#E45858` | Derrota, EV negativo, palos rojos |
| `muted` | Ash | `#5C6660` | Texto secundario, instrucciones |

Notas:
- Los palos `♥` y `♦` usan `danger`; `♠` y `♣` usan `primary`.
- Sin "color a secas": cada cambio de estado va acompañado de cambio de
  glifo o texto.

## Tipografía

- **UI**: la fuente del terminal del usuario. Textual respeta la
  configuración; recomendado en README: `JetBrainsMono Nerd Font`,
  `Fira Code`, `Iosevka`, o cualquier monoespaciada con buen ancho.
- **Mono / arte de cartas**: idem; las cartas se dibujan en bordes Unicode
  (`┌─┐│└┘`) que requieren monoespaciado fiable.
- Tamaños: una sola escala — la del terminal. No hay tipografía
  proporcional.
- Pesos: regular para texto, **negrita** para énfasis (banca, resultado).

## Espaciado

Sistema basado en celdas de terminal (1 col, 1 row). Los paneles tienen
márgenes de 1 o 2 celdas. Cartas ocupan 11 columnas × 7 filas y se
separan por 2 celdas entre sí.

## Iconografía

ASCII puro y palos Unicode. Sin Nerd Font glyphs para no requerir fuentes
exóticas. Los marcadores de estado son textuales (`★ Nuevo récord`,
`▲ Subiendo`, `▼ Bajando`).

## Pantallas

### `SplashScreen`
- Título "ACEY-DUCEY" en bloque ASCII centrado.
- Subtítulo: "after Bill Palmby · Creative Computing 1973".
- Mensaje "Pulsa cualquier tecla para empezar".
- Récord anterior visible si existe.
- Duración: hasta tecla.

### `TableScreen` (principal)
- Cabecera fija: balance, manos jugadas, win-rate.
- Centro: zona de cartas (siempre tres huecos; los no revelados se ven
  como reverso `▒▒▒`).
- Panel lateral derecho: probabilidad, multiplicador, EV/$, último
  resultado.
- Pie: input de apuesta (cuando procede) o instrucciones.
- Atajos: `Enter` confirmar apuesta, `0` o `Esc` pasar (gallina),
  `Ctrl+R` reiniciar partida, `Ctrl+Q` salir, `?` ayuda.

### `SummaryScreen`
- Tabla con todas las estadísticas finales.
- Comparación con récord anterior. Si superado, banner `★ NUEVO RÉCORD`.
- Opciones: `n` nueva partida, `q` salir.

## Microinteracciones

- Al revelar la tercera carta, breve "flash" del marco (CSS transition
  120 ms).
- Al ganar, el balance cuenta hacia arriba 20 frames.
- Al perder, el balance parpadea en `danger` una vez.
- Pareja o consecutivas: las dos cartas se atenúan 200 ms y aparece un
  toast "Mano nula, repartiendo de nuevo".

## Toque distintivo

**Bordes de cartas tipo plano de planta del PDP-11**: marcos de doble
línea (`╔═╗ ║ ║ ╚═╝`) solo para la tercera carta en el momento de la
revelación, mientras las dos iniciales mantienen marcos simples. El
contraste subraya cuál es la carta del veredicto sin necesidad de animar
nada. (Es la única decisión "estética con peso", como pide la guía.)

## Estados

| Estado | Descripción visual |
|---|---|
| `splash` | Logo ASCII + récord + invitación a pulsar tecla |
| `dealing` | Cartas con efecto de aparición secuencial |
| `awaiting_bet` | Input numérico habilitado, cursor parpadeante en el campo apuesta |
| `revealing` | Tercera carta con marco doble, panel lateral muestra resultado |
| `chicken` | Toast "¡Gallina!" 1 s y nueva mano automática |
| `redeal` | Toast informativo y nueva mano automática |
| `game_over` | Fade-to-summary screen |
| `summary` | Tabla final |

## Accesibilidad

- Navegación 100% por teclado: el ratón está deshabilitado salvo para
  scroll del historial.
- No se depende solo del color: cada victoria/derrota tiene también un
  glifo (`✔ GANAS` / `✘ PIERDES`).
- El historial textual del panel lateral funciona como lector de
  pantalla básico.
- Modo `--no-color` heredado del CLI desactiva la paleta y respeta solo
  glifos.

## Sonido

Ninguno. Acey-Ducey original era un teletipo silencioso; respetar.
