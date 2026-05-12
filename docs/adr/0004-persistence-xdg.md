# ADR 0004 — Persistencia: JSON en directorio XDG

## Contexto

El original no guarda nada. Para mantener un récord persistente de "pico
de balance" entre partidas necesitamos una ubicación estable, no
intrusiva, y respetuosa con la convención de cada plataforma.

## Opciones consideradas

1. **Fichero en `$HOME`** (`~/.aceyducey_highscore.json`). Funciona, pero
   contamina el home y no respeta XDG.
2. **Directorio del proyecto** (`./.highscore.json`). Ata el récord al
   directorio de invocación; el usuario lo pierde si juega desde otro
   lado.
3. **XDG Base Directory Specification**: `$XDG_DATA_HOME/aceyducey/` o
   `~/.local/share/aceyducey/`. Convención Linux estándar. En macOS y
   Windows se cae a `~/.local/share/aceyducey/` también, que no es
   nativo pero es predecible y aislado.

## Decisión

**Opción 3**, con detección XDG. Implementado en
`infrastructure/paths.py`. El fichero es `highscore.json` con campos
`peak: int`, `last_played: str (ISO 8601)`, `runs: int`.

## Consecuencias

- Dependencia en `platformdirs` para resolver paths cross-platform
  correctamente. Decidimos **no** usar la dependencia: la implementación
  manual XDG-only es trivial (<15 líneas) y nos ahorra una transitiva.
- Manejo robusto de fichero corrupto: si `json.loads` falla, log
  warning y se reinicia el récord a 0 sin abortar.
- Tests: usar `tmp_path` y monkeypatchear `Path.home` (o pasar el path
  por constructor del repo, que es lo que hacemos).
