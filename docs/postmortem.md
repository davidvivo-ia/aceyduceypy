# Postmortem

Acey-Ducey son cien líneas de Sinclair-Microsoft BASIC publicadas en
1973 por Bill Palmby. Es un programa minúsculo, casi una broma del autor
sobre lo poco que se necesita para entretener: un `RND`, dos `IF`s y un
balance que se vacía.

Cuarenta y tres años después, este puerto pesa 600+ líneas de Python
3.13, cuatro capas de arquitectura, dos políticas de pago, treinta y
nueve tests, dos ADRs sobre cosas que el original ni se planteó. Se
gana en testabilidad, en accesibilidad, en estética; se pierde la
cualidad esencial del listado de revista: que un adolescente pudiera
copiarlo a mano en una tarde y entender cada línea.

El BASIC original es lineal y plano. Saltos numéricos por todas partes,
sí, pero la lectura va de arriba abajo y la variable `Q` está siempre
visible. Mi versión esconde ese mismo balance detrás de un puerto, un
caso de uso, un adaptador y una pantalla Textual. Lo testeo desde tres
ángulos; el original ni siquiera contemplaba que pudiera estar mal.

Lo que más me ha llamado la atención al desensamblar el listado es lo
honesto que era el flujo: `IF M<>0 THEN 680` y luego 680 a continuación.
Lo que sería un bug en cualquier base de código moderna era allí un
recurso pedagógico — un puente entre dos secciones para que un humano
copiando del libro no se perdiera. La elegancia de ayer es la deuda
técnica de hoy.

Si algo dice este ejercicio sobre cómo ha cambiado el oficio es que el
software ha pasado de ser una receta a ser una infraestructura. El BASIC
de Palmby existía solo durante los segundos en que lo tecleabas; mi
versión espera ejecutarse en CIs ajenos, sobrevivir a un mypy 1.11,
seguir siendo modificable en 2032. Ambas cosas son válidas, pero solo
una recordamos con cariño cuarenta años después.
