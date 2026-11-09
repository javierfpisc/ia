# Lista de control de calidad

## Fidelidad a las fuentes
- [ ] Las afirmaciones técnicas importantes tienen respaldo localizable.
- [ ] No se han añadido hechos externos sin autorización.
- [ ] Se han señalado lagunas y contradicciones relevantes.
- [ ] No se han inventado páginas, referencias, resultados ni versiones.

## Material de alumnado (automatizado con `scripts/calidad.py`)
- [ ] Sin referencias a documentación original ni comentarios docentes; solo URLs oficiales.
- [ ] Extensión dentro del presupuesto de `contenidos/unidades.yml`.
- [ ] Número de diagramas Mermaid cumplido y válido.
- [ ] `estado` del apartado actualizado por el profesor tras la revisión.

## Calidad didáctica
- [ ] El orden de los apartados facilita el aprendizaje.
- [ ] Se definen los términos antes de usarlos de forma intensiva.
- [ ] Los ejemplos aclaran el concepto y no introducen hechos no sustentados.
- [ ] La profundidad respeta las instrucciones y las muestras.
- [ ] Se evitan repeticiones innecesarias y afirmaciones ambiguas.

## Markdown y estructura
- [ ] Existe un título claro y una jerarquía correcta de encabezados.
- [ ] Las listas, tablas y bloques de código están bien formados.
- [ ] Los enlaces son válidos o están marcados como pendientes.
- [ ] Los nombres de archivo son consistentes.
- [ ] Los enlaces relativos funcionan desde la ubicación del archivo.

## Prácticas (automatizado en parte con `scripts/calidad.py practicas/unidades/NN`)
- [ ] La práctica está declarada en `practicas/unidades.yml` y cubre sus procedimientos, entregables y comprobaciones.
- [ ] Objetivo, requisitos y entorno están especificados, sin datos de entorno inventados.
- [ ] Los pasos son numerados y reproducibles.
- [ ] Se distinguen comandos, qué comprobar y explicación; cada paso tiene una comprobación observable.
- [ ] Cada comando y opción está respaldado por la documentación oficial de la práctica.
- [ ] Hay verificación final, entregables y limpieza.
- [ ] Los riesgos y operaciones destructivas están señalados.
- [ ] No se afirma que algo se ha probado sin evidencia de ejecución.

## Publicación
- [ ] La unidad y el repositorio de destino están identificados.
- [ ] No hay credenciales ni datos sensibles.
- [ ] `git status` y las diferencias se han revisado.
- [ ] No se incluyen archivos temporales o de extracción.
- [ ] Existe autorización para la publicación.
