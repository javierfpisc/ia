# Flujo de trabajo del agente

## 1. Preparación del encargo

Identifica:
- unidad o tema;
- entregable: apuntes, resumen, práctica, laboratorio, revisión o publicación;
- alcance y profundidad;
- fuentes permitidas;
- si se solicita borrador, revisión o versión final.

Si falta un dato esencial, formula una pregunta concreta. Si solo faltan preferencias menores, adopta una opción conservadora y declárala.

## 2. Inventario local

Antes de escribir:
- lee los archivos de instrucciones pertinentes;
- comprueba `contenidos/unidades.yml` (presupuesto de palabras, diagramas, estado);
- localiza fuentes por nombre, contenido y formato;
- revisa las muestras disponibles;
- detecta material existente para evitar duplicados.

Ejecuta `python3 scripts/ingesta.py documentacion/<unidad> <apartado-id>` y trabaja con `trabajo/<unidad>/<apartado-id>/indice.md` en lugar de leer los originales completos.

No supongas que un nombre de archivo implica que su contenido sea el esperado.

## 3. Análisis de las fuentes

Crea un mapa de conceptos que relacione:
- concepto o procedimiento;
- fuente;
- página, sección o encabezado cuando se pueda identificar;
- grado de cobertura: explícito, parcialmente cubierto o no encontrado;
- dudas o discrepancias.

No es obligatorio entregar este mapa en cada tarea pequeña, pero sí usarlo internamente y reflejar las lagunas relevantes.

## 4. Producción de apuntes

- Sigue `contenidos/instrucciones.txt` (generales) y `contenidos/instrucciones-modulo.txt` (específicas del módulo), `contenidos/unidades.yml` y la plantilla `plantillas/contenido_unidad.md`.
- Explica los conceptos progresivamente, con terminología consistente.
- Incluye ejemplos solo si están respaldados por las fuentes o son claramente ejemplos didácticos derivados que no añaden hechos externos.
- Distingue definiciones de explicaciones, ejemplos, advertencias y conclusiones.
- El texto va dirigido al alumnado: sin referencias a las fuentes originales ni comentarios docentes; solo URLs oficiales.
- Evita repetir el mismo contenido en varios archivos salvo que sea útil para el aprendizaje.
- No inventes objetivos curriculares, criterios de evaluación ni duración.

Tras redactar, ejecuta `python3 scripts/calidad.py <archivo>` y corrige los errores. Tras cambios en la documentación oficial, `python3 scripts/comprobar_urls.py` indica qué fuentes han cambiado y, por tanto, qué apartados revisar. El ciclo de revisión humana se refleja en `estado` (borrador → revisado → aprobado) en `unidades.yml`.

## 5. Producción de prácticas

- Sigue `practicas/instrucciones.txt` (generales) y `practicas/instrucciones-modulo.txt` (específicas del módulo), `practicas/unidades.yml` y `plantillas/practica.md`. Solo se genera lo declarado en `unidades.yml`.
- Obtén las fuentes con `python3 scripts/ingesta.py documentacion/<unidad> <practica-id>` y registra trazabilidad y datos de entorno pendientes en `trabajo/<unidad>/<practica-id>/informe.md`.
- Valida con `python3 scripts/calidad.py practicas/unidades/NN/<practica>.md`. El documento del alumnado no lleva estado ni marcadores `[POR DEFINIR]`; los datos de entorno que falten se preguntan al profesor.
- Comprueba que la práctica está relacionada con los contenidos de la unidad.
- Declara requisitos previos, entorno, materiales, pasos, resultados esperados y comprobaciones solo cuando se puedan justificar.
- No inventes salidas de comandos ni afirmes que una práctica se ha probado si no se ha ejecutado.
- Para operaciones potencialmente destructivas, incluye advertencias, medidas de seguridad y alternativas seguras.
- Cuando falten datos del entorno (versión, IP, sistema operativo, credenciales de laboratorio), no los adivines: anótalos en el informe de trabajo y pregunta al profesor.

## 6. Revisión

Aplica `instrucciones/control_calidad.md`. Corrige errores de formato y coherencia que puedas resolver a partir de las fuentes. Las contradicciones de contenido se elevan al profesor.

## 7. Publicación

Solo tras autorización explícita:
1. lee `publicacion/instrucciones.txt` y `publicacion/repositorios.yml`;
2. prepara con `python3 scripts/publicar.py NN` (sin `--publicar`), que valida y genera `trabajo/publicacion/NN/stage/`;
3. comprueba que `rama` y `mkdocs` están definidas en `repositorios.yml` y que la rama existe; revisa la lista de archivos y los avisos del script;
4. verifica que no se publican secretos ni archivos auxiliares;
5. presenta el plan de publicación si el alcance no está completamente especificado;
6. solicita confirmación final antes de ejecutar `python3 scripts/publicar.py NN --publicar` si no existe autorización inequívoca;
7. registra el resultado real de la operación que informa el script.
