# Análisis del programa original

## 1. Encuadre

| Campo | Valor |
|---|---|
| Título | ACEY DUCEY CARD GAME |
| Autor | Bill Palmby (Prairie View, Illinois) |
| Editor | Creative Computing Press (David H. Ahl, ed.) |
| Publicación | *BASIC Computer Games*, 1973 (revisado 1978) |
| Lenguaje | Dartmouth/Microsoft BASIC con numeración de línea |
| Plataforma típica | DEC PDP/teletipo; replicado en CP/M, Apple II, PET, ZX Spectrum, Amstrad CPC |
| Líneas | 100 |
| Estado canónico | Listado en `legacy/creative_computing/aceyducey.bas` |

### Sinopsis funcional

El crupier (ordenador) reparte dos cartas boca arriba con valores 2–14 (As
alto). El jugador, partiendo de $100, decide si apuesta a que la siguiente
carta caerá **estrictamente** entre las dos primeras (en rango). Apuesta 0
significa pasar la mano («CHICKEN!!»). Si gana, cobra la apuesta a 1:1; si
pierde, la descuenta. El juego termina cuando el balance llega a 0, momento
en el que se ofrece reiniciar la partida.

### Lectura crítica

1. **Modelo de cartas sin palos**: el original solo usa el rango (2–14). No
   hay palos, no hay mazo. Cada carta se sortea de forma independiente con
   reposición, lo que técnicamente permitiría repetidos (aunque la rutina
   en línea 270–330 fuerza `A < B` reiniciando la tirada).
2. **Aleatoriedad ingenua**: `INT(14*RND(1))+2` produce valores en `[2,
   15]`. Las líneas 280–290 y 320 lo recortan a `[2, 14]` con reintentos,
   un parche defensivo poco elegante. Hoy se haría con `RND(1)*13+2` o un
   sorteo discreto del intervalo cerrado.
3. **Codificación de figuras**: cada vez que hay que imprimir una carta
   (líneas 350–490, 500–640, 760–890) el programa repite el mismo bloque
   de `IF`s anidados. Esto sería una función `printCard` en cualquier
   BASIC con `DEF FN`, pero el BCG nº1 prefiere repetición lineal.
4. **Control de flujo por GOTO**: el programa es un grafo plano de saltos
   numéricos sin subrutinas; ni siquiera usa `GOSUB`. Es código «espagueti
   pre-estructurado» típico de la primera mitad de los 70.
5. **Sin estado guardado**: cada partida arranca desde cero; no hay
   estadísticas ni récord.
6. **No hay límite de banca**: si el jugador acierta, la banca paga aunque
   estuviera teóricamente quebrada. No es un casino simulado, es un dado.

## 2. Arqueología

### 2.1 Grafo de flujo (ASCII)

```
 ┌─────────────────────────────────────────────────┐
 │ 10–80  splash + reglas                          │
 └─────────────┬───────────────────────────────────┘
               ▼
 ┌────────────────────┐
 │ 100–110 Q := 100   │◄────────── (loop: línea 1030 "YES")
 └─────────────┬──────┘
               ▼
       ┌───────────────┐
       │ 120 print Q$  │◄──────────────────┐
       └───────┬───────┘                   │
               ▼                           │
       ┌───────────────────────────────┐   │
       │ 260 "HERE ARE YOUR NEXT..."   │◄──┼─── 677 "CHICKEN"
       └───────┬───────────────────────┘   │
               ▼                           │
       ┌────────────────────────────┐      │
       │ 270–330 sortear A, B con   │      │
       │   A<B (rerolls 270/300)    │      │
       └───────┬────────────────────┘      │
               ▼                           │
       ┌─────────────────────┐             │
       │ 350–490 print A     │             │
       │ 500–640 print B     │             │
       └───────┬─────────────┘             │
               ▼                           │
       ┌─────────────────────────────┐     │
       │ 660 INPUT M (apuesta)       │     │
       └───────┬─────────────────────┘     │
               │                           │
       ┌───────┴───────────────────────┐   │
       │ M = 0  ──► 675 CHICKEN ───────┼───┘
       │ M > Q  ──► 690 demasiado, vuelve a 650
       │ M ≤ Q  ──► 730
       └───────────────────────────────┘
                   │
                   ▼
       ┌────────────────────────────┐
       │ 730–750 sortear C          │
       │ 760–900 print C            │
       └───────┬────────────────────┘
               ▼
       ┌──────────────────────────────────┐
       │ 910 IF C>A THEN 930              │
       │ 920 GOTO 970   ; C≤A → pierde    │
       │ 930 IF C>=B THEN 970 ; C≥B → pierde │
       │ 950 "YOU WIN!!!" → 210 Q := Q+M  │
       │ 970 "SORRY, YOU LOSE"            │
       │ 980 IF M<Q THEN 240 (Q:=Q-M→120) │
       │      else 990 game over          │
       └──────────────────────────────────┘
                   │
                   ▼ (cuando M >= Q en derrota)
       ┌──────────────────────────────────┐
       │ 1010 "BLEW YOUR WAD"             │
       │ 1020 INPUT A$ "TRY AGAIN"        │
       │ 1030 IF A$="YES" THEN 110        │
       │ 1040 "OK, HOPE YOU HAD FUN!"     │
       │ 1050 END                         │
       └──────────────────────────────────┘
```

### 2.2 Inventario de variables

| Símbolo | Tipo | Vida | Uso |
|---|---|---|---|
| `N` | int | global, inalterada | Establecida a 100 en línea 100; **nunca se usa**. Vestigio. |
| `Q` | int | global | Balance del jugador. |
| `M` | int | mano actual | Apuesta. |
| `A` | int | mano actual | Primera carta repartida (2–14). |
| `B` | int | mano actual | Segunda carta repartida (2–14), siempre > A. |
| `C` | int | mano actual | Tercera carta (a evaluar). |
| `A$` | str | post-game | Respuesta «YES»/«NO» a reiniciar. |

### 2.3 Subrutinas

Cero. No hay `GOSUB`/`RETURN`. Toda la lógica es lineal con `GOTO`.

### 2.4 IO y dispositivos

- Entrada: `INPUT` clásico para `M` (apuesta numérica) y `A$` (texto sí/no).
- Salida: solo `PRINT` con `TAB()` para centrar el título. Sin gráficos,
  sin sonido, sin caracteres semigráficos. **Programa text-only puro**.

### 2.5 Algoritmos identificados

- **Sorteo de carta válida**: bucle de rechazo (líneas 270–290) sobre
  `INT(14*RND(1))+2`. Aceptación efectiva sería `value in [2, 14]`; los
  reintentos son defensivos.
- **Orden forzado A<B**: línea 330 `IF A>=B THEN 270` re-sortea ambas
  cartas. Curiosidad: con `A` y `B` independientes, esto reduce la
  distribución conjunta a triángulo superior estricto.
- **Comparación de tercera carta**: pertenencia al intervalo abierto
  `(A, B)`. Empate con borde = pierde.
- **Estado de bancarrota**: línea 980 `IF M<Q THEN 240`. Detecta game over
  por «la apuesta perdedora es igual o mayor que el balance restante».

### 2.6 Bugs y rarezas

| Línea | Descripción | Severidad |
|---|---|---|
| 100 | `N=100` se asigna y nunca se lee. Variable muerta. | Cosmética |
| 270 | `IF A<2 THEN 270`: imposible que `INT(14*RND(1))+2 < 2`. Rama muerta. | Cosmética |
| 290 | `IF A>14 THEN 270`: posible si `RND(1)` devuelve exactamente 1.0 (algunos intérpretes lo permiten). Defensa válida en su época. | Necesario en algunos dialectos |
| 640 | `640 PRINT` redundante: cuando `B=14` salta a 630 que imprime "ACE", luego 640 imprime una línea en blanco, pero el caso normal (B<14) llega a 650 sin pasar por 640. Resulta en un blanco extra solo cuando B es As. | Inconsistencia |
| 670 | `IF M<>0 THEN 680` con 680 a continuación es un no-op estructural. | Cosmética |
| 980 | `IF M<Q THEN 240`: descuenta y sigue; si `M=Q` exactamente, considera bancarrota **sin descontar** la última apuesta. El balance final se imprime con el valor pre-derrota. | Bug menor |
| 1030 | Compara `A$="YES"` sin convertir a mayúsculas. "yes" o "Yes" se interpretan como "NO". | Bug de UX |
| 270/300/330 | El bucle reroll cuando `A>=B` puede en teoría ser largo. En la práctica, irrelevante. | Cosmética |

### 2.7 Bugs corregidos en el port 2026

- `N=100` desaparece como variable muerta.
- El sorteo de cartas se realiza desde un mazo real de 52, no por
  rechazo: además de eliminar las ramas muertas, modela mejor el juego
  («carta» = (rango, palo)).
- El game over por `M=Q` con derrota se contabiliza correctamente: el
  balance se decrementa antes de cerrar la mano.
- La pregunta de reinicio acepta cualquier prefijo case-insensitive de
  «sí», «s», «yes», «y».

### 2.8 [LICENCIA CREATIVA] decisiones de diseño 2026

Documentadas formalmente en `CHANGELOG.md`. Las más relevantes:

- Cartas con palos (♠♥♦♣) y mazo real de 52 cartas barajado por mano.
- Pagos por riesgo (5×/3×/2×/1×) según el hueco entre las dos cartas
  iniciales, recuperables al modo clásico 1:1 con `--classic`.
- Estadísticas de sesión y récord persistente XDG.
- Probabilidad y valor esperado mostrados como guía al jugador.
- TUI con Textual y CSS propio, en lugar de PRINTs por línea.
- Pareja inicial y cartas consecutivas re-reparten automáticamente.
