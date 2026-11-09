# AGENTS.md — Laboratorio de desarrollo Odoo 19 con IA

Estas instrucciones son obligatorias para cualquier agente que trabaje en este repositorio.

## 1. Objetivo y ámbito

Desarrolla módulos para **Odoo 19**, ejecutados en el entorno Docker Compose suministrado. El objetivo es implementar los requisitos funcionales del alumno de forma sencilla, mantenible y didáctica.

- Sigue las convenciones de desarrollo de **OCA para la rama 19.0**, siempre que sean aplicables.
- Usa las fuentes OCB/OCA disponibles en el entorno como referencia de implementación.
- No supongas APIs, nombres de métodos, campos ni comportamientos: compruébalos en las fuentes o en documentación fiable.
- No modifiques el código de OCB ni los módulos de terceros.

## 2. Fuentes de contexto y prioridad

Consulta estas fuentes según corresponda:

1. `requirements/funcionales.md`: requisitos funcionales del trabajo.
2. `requirements/tecnicos.yml`: restricciones técnicas del profesor.
3. `templates/`: especificaciones YAML que deban respetarse.
4. `examples/`: módulos de referencia proporcionados por el profesor.
5. `docs/referencias.yml`: documentación web indicada.
6. Fuentes OCB/OCA montadas en `/opt/odoo/src`.

Prioridad cuando haya discrepancias:

1. Requisitos funcionales explícitos.
2. Especificaciones técnicas y plantillas del profesor.
3. Restricciones de este archivo y del entorno.
4. Convenciones OCA y patrones de Odoo 19.
5. Decisiones del agente, siempre justificadas.

Si dos instrucciones del profesor se contradicen, o una plantilla impide cumplir un requisito, **detente y pregunta**. No resuelvas silenciosamente contradicciones funcionales.

## 3. Reglas de implementación

- Implementa exclusivamente lo necesario para satisfacer los requisitos.
- No añadas funcionalidades, campos, menús, automatizaciones ni dependencias por iniciativa propia.
- Antes de crear un modelo o mecanismo nuevo, comprueba si Odoo o un módulo disponible ya proporciona esa funcionalidad.
- Reutiliza los modelos, campos, métodos y patrones estándar cuando sea apropiado.
- Mantén el código explícito, legible y adecuado para alumnado que se inicia en Odoo.
- Evita abstracciones, herencias innecesarias, metaprogramación y patrones complejos si una solución sencilla es suficiente.
- No inventes dependencias: verifica que cada módulo requerido existe en el entorno.
- Usa nombres técnicos coherentes y estables. No renombres modelos o campos ya utilizados sin autorización.
- Incluye comentarios solo cuando aclaren una decisión que no resulte evidente.
- No copies código de un módulo de referencia sin comprobar su compatibilidad con Odoo 19 y su licencia.

## 4. Convenciones del módulo

Como mínimo, respeta la estructura habitual de un módulo Odoo:

- `__init__.py`
- `__manifest__.py`
- directorio `models/`
- directorio `views/`
- directorio `security/` cuando haya permisos o grupos
- `data/` cuando existan datos iniciales o automatizaciones declarativas
- `demo/` solo si se solicitan datos de demostración
- `tests/` para pruebas automatizadas cuando proceda
- `README.md` del módulo

Sigue las convenciones OCA aplicables a Odoo 19. Comprueba en los módulos de referencia la organización y el estilo concretos que se esperan.

En el manifiesto:

- Declara únicamente dependencias necesarias y verificadas.
- Incluye en `data` los XML/CSV que deban cargarse al instalar.
- Mantén una versión compatible con Odoo 19 y coherente con las convenciones del proyecto.
- No marques el módulo como instalable si todavía no puede instalarse.

## 5. Modelos, vistas y seguridad

- Define campos y relaciones a partir de los requisitos, no por intuición.
- Utiliza restricciones Python o SQL cuando sean necesarias para garantizar reglas de negocio.
- No sustituyas una restricción de integridad por una simple validación visual.
- Define ACL en `security/ir.model.access.csv` cuando corresponda.
- Define reglas de registro únicamente cuando exista un requisito de separación o filtrado de registros.
- Comprueba que los grupos y las reglas no bloquean accidentalmente a los usuarios previstos.
- No concedas permisos globales excesivos.
- Usa vistas y acciones compatibles con Odoo 19; verifica la sintaxis en fuentes de la misma versión.
- No introduzcas vistas heredadas, menús o acciones que no sean necesarios.
- Con todos los artefactos generados quiero que elabores un informe que los describa de forma resumida en el archivo addons/MODULE_REPORT.md

## 6. Uso de YAML

Los YAML de `templates/` son especificaciones de entrada, no necesariamente archivos que Odoo vaya a cargar.

- Respeta los nombres, tipos, relaciones, restricciones y estructuras expresamente definidos.
- No presupongas que existe un generador YAML: interpreta las especificaciones y genera los archivos Python/XML/CSV correspondientes.
- Si el YAML es incompleto, conserva la libertad de implementación solo en los aspectos no especificados.
- Si el YAML contiene una estructura imposible o incompatible con Odoo 19, explica el problema antes de alterarla.
- Valida la sintaxis YAML si dispones de una herramienta adecuada.

## 7. Consulta de fuentes

- Consulta primero los módulos de ejemplo más próximos funcionalmente.
- Usa las fuentes OCB/OCA locales para confirmar APIs y patrones de la versión 19.
- Consulta las URL de `docs/referencias.yml` cuando aporten información necesaria.
- Prioriza documentación oficial de Odoo 19 y documentación OCA.
- No uses documentación de otra versión como autoridad para una API de Odoo 19.
- Distingue entre hechos comprobados e hipótesis. Indica las fuentes relevantes en las decisiones técnicas.

## 8. Entorno Docker y límites de escritura

Configuración prevista:

- Fuentes del host: `~/odoo/src`
- Fuentes dentro del contenedor: `/opt/odoo/src`
- Addons OCB: `/opt/odoo/src/OCB/addons`
- Addons propios: `/opt/odoo/src/extra-addons`
- Configuración Odoo: `/opt/odoo/odoo.conf`
- Usuario del proceso Odoo en el contenedor: `odoo`

El agente debe:

- Trabajar únicamente en este repositorio, especialmente en `addons/` y documentación asociada.
- No escribir en `/opt/odoo/src/OCB` ni en otros directorios de fuentes.
- No modificar `odoo.conf`, `docker-compose.yml`, imágenes, volúmenes ni servicios salvo petición expresa.
- No ejecutar comandos destructivos sobre bases de datos, volúmenes o contenedores.
- No borrar datos ni reinicializar la base de datos sin autorización explícita.
- Usar el servicio Compose existente para instalar y probar el módulo.

El montaje de `addons/` en `/opt/odoo/src/extra-addons` permite que el código desarrollado en el host esté disponible en Odoo.

## 9. Validación obligatoria

Antes de dar por terminado un cambio:

1. Revisa el árbol del módulo y sus archivos de inicialización.
2. Comprueba sintaxis Python.
3. Comprueba XML y CSV, incluida la coherencia de identificadores y referencias.
4. Comprueba que el manifiesto incluye los datos y dependencias necesarios.
5. Ejecuta las pruebas disponibles.
6. Intenta instalar o actualizar el módulo en el entorno Docker cuando esté disponible.
7. Revisa los logs de Odoo y corrige los errores atribuibles al módulo.
8. Comprueba los requisitos funcionales uno por uno.

No afirmes que el módulo está probado o instalado si no has ejecutado realmente esas comprobaciones. Si Docker o la base de datos no están disponibles, indícalo claramente y proporciona los comandos que debe ejecutar el alumno.

## 10. Comunicación y entregables

Trabaja de forma incremental. Antes de una implementación amplia:

- Resume qué has entendido.
- Identifica modelos, relaciones, vistas, acciones, permisos y dependencias previsibles.
- Señala dudas o contradicciones que bloqueen el diseño.

Al finalizar, informa de:

- Requisitos implementados y pendientes.
- Archivos creados o modificados.
- Dependencias añadidas y por qué.
- Validaciones ejecutadas y sus resultados.
- Comandos necesarios para instalar/actualizar.
- Limitaciones conocidas.

Actualiza el README del módulo si cambia su uso. No sustituyas el `README.md` principal del laboratorio por documentación del módulo.
