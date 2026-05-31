# Mock Interview

**Candidato:** Juan Sebastian Guerrero Bautista
**Oferta:** job_description1.txt
**Idioma:** es

## Pregunta 1

Hola Juan Sebastian, bienvenido a la entrevista.

Para empezar, me gustaría que nos hablaras un poco sobre tu experiencia con Git y GitHub. ¿Podrías explicarnos qué es Git y por qué es tan fundamental en el desarrollo de software moderno?

## Respuesta

es sistemas de versionado de proyectos en el que se lleva un historial de avance

## Pregunta 2

Entendido. En un escenario de desarrollo en equipo, donde varias personas trabajan en diferentes funcionalidades al mismo tiempo, ¿cómo ayuda Git a gestionar estas líneas de desarrollo paralelas y qué comandos usarías para integrarlas?

## Respuesta

es muy util ya que nos permite dividir el trabajo en nuestro equipo y luego juntar, por ejemplo usando el merge para unir ramas que cada persona creo para hacer su avance

## Pregunta 3

Cuando se trabaja en equipo y se intenta integrar cambios de diferentes ramas, a veces surgen conflictos. ¿Podrías describir qué es un conflicto de fusión (merge conflict) en Git y cómo lo resolverías?

## Respuesta

habria que revisar el conflicto, usualmente por intentar combinar 2 archivos que tuvieron modificaciones, usando diff para verificar donde esta dando el error y resolverlo

## Pregunta 4

Has mencionado `merge` para integrar ramas. ¿Conoces alguna otra forma de integrar cambios de una rama a otra, como `rebase`, y cuándo preferirías usar `rebase` en lugar de `merge`?

## Respuesta

cuando quiera dejar un avance mas lineal usaria rebase

## Pregunta 5

En GitHub, una herramienta clave para la colaboración es la "Pull Request". ¿Podrías explicar qué es una Pull Request y cuál es su propósito principal en un flujo de trabajo de desarrollo en equipo?

## Respuesta

se usa para aprobar y agregar una rama o commit a mi rama principal, esto para verificar que lo que se hizo no genere conflictos o errores

## Pregunta 6

Más allá de la integración técnica, ¿cuál es el rol de una Pull Request en la revisión de código por parte del equipo y cómo contribuye esto a la calidad del software?

## Respuesta

ayuda a detectar errores y defectos antes de produccion

## Pregunta 7

En un proyecto de software más grande, los equipos suelen adoptar estrategias de ramificación específicas para gestionar el desarrollo y las versiones. ¿Podrías describir una estrategia de ramificación de Git que conozcas, como Git Flow o GitHub Flow, y explicar cómo ayuda a mantener la estabilidad del código y a gestionar los lanzamientos?

## Respuesta

github flow crea una rama nueva por cada cambio o funcionalidad, permitiendo trabajar de forma mas segura en ella

## Feedback Final

## Fortalezas
*   Demuestra un conocimiento fundamental de los conceptos clave de Git y GitHub, como el control de versiones, la integración de código y la gestión de ramas.
*   Identifica correctamente el propósito de comandos como `merge` y la utilidad de `rebase` para mantener un historial lineal.
*   Comprende el rol de las Pull Requests para la aprobación e integración de código, así como su contribución a la detección temprana de errores.
*   Conoce la estrategia de ramificación GitHub Flow y su principio básico de trabajar en ramas separadas para cada funcionalidad.

## Debilidades
*   Las respuestas son consistentemente muy concisas y carecen de la profundidad esperada para un ingeniero de software, incluso a nivel junior. Se limitan a describir el "qué" sin profundizar en el "cómo" o el "porqué" en detalle.
*   Falta de detalle en la explicación de la resolución de conflictos de fusión; se mencionó `diff`, pero no se describió el proceso completo de resolución manual o las herramientas de Git para ello.
*   No se elaboró sobre los beneficios de la revisión de código en las Pull Requests más allá de la detección de errores, como el intercambio de conocimiento o el mantenimiento de estándares de calidad.
*   Poca mención de comandos específicos de Git o ejemplos prácticos que demuestren una experiencia más allá de lo teórico.

## Tecnologías a reforzar
*   **Git:** Profundizar en la resolución de conflictos de fusión, comandos avanzados (como `rebase` con más detalle, `cherry-pick`, `stash`), y la implementación práctica de estrategias de ramificación.
*   **GitHub:** Entender a fondo los flujos de trabajo de Pull Request, incluyendo la configuración de revisiones, la gestión de comentarios y la integración continua.

## Score general
6/10 — Juan Sebastian demuestra una comprensión básica y correcta de los conceptos fundamentales de Git y GitHub, lo cual es un buen punto de partida para un rol junior. Sin embargo, la falta de profundidad y detalle en sus respuestas, así como la ausencia de ejemplos prácticos o menciones de comandos específicos más allá de lo básico, sugieren que su experiencia es más teórica o limitada a escenarios sencillos. Necesitaría desarrollar una comprensión más robusta y práctica para manejar situaciones de desarrollo en equipo más complejas.
