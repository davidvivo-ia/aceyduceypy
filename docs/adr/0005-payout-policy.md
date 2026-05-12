# ADR 0005 — Política de pagos por riesgo opcional

## Contexto

El original paga 1:1 siempre. El valor esperado de una apuesta media es
neutro o ligeramente negativo (depende de la distribución de huecos), por
lo que el juego se vuelve repetitivo en pocas manos. Queremos mejorar la
tensión sin desvirtuar el original.

## Opciones consideradas

1. **Pagos fijos 1:1** (`classic`). Modo nostalgia.
2. **Pagos por riesgo** (`bonus`). Multiplicadores 5×/3×/2×/1× según el
   hueco entre cartas. Tighter spread → mayor recompensa, mayor riesgo.
3. **Pagos por probabilidad inversa** (`fair`). Multiplicador exacto
   `1 / p_win` redondeado. Convertiría el juego en EV ≈ 0 siempre, lo
   que es matemáticamente puro pero menos tenso.

## Decisión

**Implementar 1 y 2**, con `1` como `--classic` y `2` por defecto. La
opción 3 queda anotada en `TODO.md` para v1.1.

Umbrales de multiplicador:

| Spread (rangos intermedios) | Multiplicador |
|---|---|
| 0 (consecutivas) | (no se apuesta, re-deal) |
| 1 | 5× |
| 2–3 | 3× |
| 4–6 | 2× |
| 7+ | 1× |

## Consecuencias

- La tabla vive en `domain/payout.py` como `frozen=True` con un mapping
  inmutable. Cambiar políticas no requiere tocar la `GameSession`.
- El `--classic` se traduce en `PayoutPolicy.flat()` y el por defecto en
  `PayoutPolicy.tiered()`.
- Tests de propiedad con `hypothesis`: para cualquier par `(low, high)`
  con `spread >= 1`, el multiplicador es ≥ 1 y monotónicamente decrece
  con el spread.
