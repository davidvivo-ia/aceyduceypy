# ADR 0003 — RNG inyectable en lugar de `random.random()` global

## Contexto

El BASIC original usa `RND(1)` global con `RANDOMIZE` opcional al
arrancar. Para tener:
- modo `--seed N` reproducible,
- modo `--demo` determinista,
- tests unitarios que reproducen secuencias exactas,

el RNG no puede ser una llamada global.

## Opciones consideradas

1. **`random.seed(N)` global**: simple pero contagia procesos vecinos en
   tests y rompe el aislamiento.
2. **`random.Random(seed)` instancia, pasada por inyección**: encapsulada,
   testeable, reentrante.
3. **`Protocol`-based port + adaptador**: máxima limpieza, permite
   sustituir por `FrozenRng` en tests.

## Decisión

**Opción 3**. Definimos `RngPort` en `application/ports.py` con dos
métodos (`shuffle(seq)` y `random()`). En infraestructura un
`SystemRandomAdapter` envuelve `random.Random(seed)`. En tests un
`FrozenRng(values=[...])` devuelve la secuencia deseada y baraja como
identidad para verificar pagos exactos.

## Consecuencias

- Cero usos de `random.X` global en el código de producción. Lint regla
  custom no necesaria: `mypy --strict` y revisión de PR lo cubren.
- El precio es una clase extra. Aceptable.
- El `seed` se propaga por `GameConfig` y se inicializa una sola vez en
  `__main__.py`.
