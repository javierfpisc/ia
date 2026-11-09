# Ejemplos de solicitudes para el chat del agente

Puedes copiar y adaptar estas solicitudes.

## Explorar una unidad sin generar documentos

> Analiza la unidad 01. Lee las instrucciones, `contenidos/unidades.yml`, las fuentes de `documentacion/` y las muestras. Devuélveme un inventario de fuentes, un mapa de conceptos, las lagunas detectadas y una propuesta de índice. No generes todavía los materiales finales.

## Generar apuntes

> Genera los apuntes de la unidad 01 siguiendo `AGENTS.md`, `contenidos/instrucciones.txt`, `contenidos/unidades.yml` y las muestras pertinentes. Usa únicamente las fuentes locales autorizadas. Crea los archivos Markdown en `contenidos/unidades/01/`. Antes de sobrescribir cualquier archivo existente, consúltamelo. Al terminar, ejecuta la revisión de calidad e informa de las fuentes y dudas pendientes.

## Generar una práctica

> Prepara una práctica asociada a la unidad 01. Sigue `practicas/instrucciones.txt` y la práctica declarada en `practicas/unidades.yml`, y usa la plantilla correspondiente. La práctica debe ser reproducible y debe distinguir claramente entre comandos, salidas esperadas y explicación. No inventes resultados ni consultes fuentes externas. Si faltan datos del laboratorio, indícalos como pendientes.

## Revisar material existente

> Revisa los archivos de la unidad 01 frente a las fuentes locales y la lista de control de calidad. No reescribas todavía: presenta los errores, las afirmaciones sin respaldo, las omisiones detectadas y una propuesta de corrección.

## Corregir y validar

> Aplica las correcciones autorizadas a la unidad 01. Conserva el contenido válido, evita cambios de estilo innecesarios y vuelve a ejecutar la lista de control. Resume las modificaciones.

## Preparar publicación

> Comprueba qué archivos de la unidad 01 están listos para publicarse. Lee `publicacion/instrucciones.txt` y `publicacion/repositorios.yml`, ejecuta `python3 scripts/publicar.py 01` (sin `--publicar`) para validar y preparar, revisa el estado y las diferencias de Git del repositorio de destino, detecta secretos y prepara un plan. No hagas commit ni push todavía.

## Publicar con autorización

> Autorizo la publicación de la unidad 01 en el repositorio y rama indicados en `publicacion/repositorios.yml`. Ejecuta `python3 scripts/publicar.py 01 --publicar` tras revisar el destino y los cambios una última vez. Si aparecen archivos ajenos a esta unidad, secretos o diferencias inesperadas, detente y consúltamelo. Publica únicamente los archivos acordados e informa del resultado real que devuelva el script.
