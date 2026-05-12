# ADR 0002 — Modelo de dominio: cartas con palos sobre mazo de 52

## Contexto

El BASIC original trata las cartas como enteros 2–14 sorteados con
reposición. No hay mazo, no hay palos, no hay agotamiento. Esto era
suficiente para el alcance del listado pero rompe la suspensión de
incredulidad y modela mal el azar (dos manos seguidas pueden producir un
6♥ idéntico desde el ojo del jugador, lo que en un casino real sería
imposible si comparten zapato).

## Opciones consideradas

1. **Calcar el original**: enteros con reposición. Mínimo esfuerzo, máxima
   fidelidad histórica, peor modelo.
2. **Mazo de 52 con reposición entre manos**: cada mano se baraja un mazo
   fresco. Realista por mano, simple, no introduce conteo entre manos.
3. **Mazo de 52 sin reposición hasta agotamiento**: realismo de casino
   con zapato compartido. Permite conteo de cartas pero requiere ciclar
   el zapato y reintroduce complejidad de borde (¿qué pasa si quedan 2
   cartas?).

## Decisión

**Opción 2**: mazo de 52 cartas barajado al inicio de cada mano. Razones:

- Fidelidad al espíritu (3 cartas por mano, ningún rastro entre manos).
- Modela palos de forma natural, que es prerrequisito para la
  presentación visual.
- Probabilidad calculable con cuentas exactas: con 50 cartas restantes
  tras revelar dos, P(intermedia) = `(spread * 4) / 50`.
- La política `--classic` cubre la nostalgia: deshabilita las
  bonificaciones de pago, pero mantiene el mazo realista (no degrada la
  simulación, solo los pagos).

## Consecuencias

- `Card(rank: Rank, suit: Suit)` es inmutable `frozen=True, slots=True`.
- `Rank` es `IntEnum` 2–14 para comparaciones aritméticas naturales.
- `Suit` es `Enum` con propiedades `symbol` y `is_red`.
- `Deck` es una lista; se baraja inyectando `RngPort`; se reparte con
  `pop()` desde el final.
- El cálculo de probabilidad y el `PayoutPolicy` se basan únicamente en
  rangos.
