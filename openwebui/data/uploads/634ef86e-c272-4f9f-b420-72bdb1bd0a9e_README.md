# Odoo AI Lab — Plantilla de desarrollo de módulos Odoo 19

Plantilla docente para desarrollar módulos de **Odoo 19 con ayuda de un agente de programación**, tomando como referencia las convenciones OCA, las fuentes OCB/OCA disponibles en el equipo y las especificaciones del profesor.

Está pensada para alumnado que comienza a desarrollar módulos. Se priorizan una estructura pequeña, instrucciones explícitas y un flujo de trabajo fácil de seguir.

## 1. Qué aporta esta plantilla

- Un `AGENTS.md` con las reglas que debe seguir el agente.
- Un espacio para describir requisitos funcionales en lenguaje natural.
- Un espacio para aportar módulos de ejemplo como referencia de estilo y estructura.
- Referencias documentales web seleccionadas por el profesor.
- Plantillas YAML opcionales para orientar modelos, vistas, acciones y seguridad.
- Un directorio para el módulo Odoo desarrollado.
- Un Docker Compose de ejemplo para conectar el proyecto con las fuentes OCB y PostgreSQL.

**La plantilla no es un generador automático de módulos a partir de YAML.** El agente interpreta los requisitos y las especificaciones, consulta las referencias y genera el código Odoo correspondiente.

## 2. Requisitos previos

El profesor debe proporcionar:

- Docker Engine y Docker Compose.
- Una imagen de Odoo 19 compatible con el entorno del curso.
- Una imagen de PostgreSQL 17.
- Las fuentes OCB/OCA 19 en el host, en `~/odoo/src`.
- El archivo `odoo.conf` utilizado en el curso.
- Un IDE compatible con el agente elegido, por ejemplo Visual Studio Code.
- Acceso al repositorio Git del laboratorio.

La estructura de fuentes esperada dentro del contenedor es:

| Ruta | Contenido |
|---|---|
| `/opt/odoo/src/OCB/addons` | Addons incluidos en OCB |
| `/opt/odoo/src/extra-addons` | Addons propios del laboratorio |
| `/opt/odoo/odoo.conf` | Configuración de Odoo |

El usuario del proceso Odoo dentro de la imagen es `odoo`.

## 3. Estructura del repositorio

```text
odoo-ai-lab/
├── AGENTS.md
├── README.md
├── .gitignore
├── docker-compose.yml
├── .env.example
├── odoo.conf.example
├── requirements/
│   ├── funcionales.md
│   └── tecnicos.yml
├── examples/
│   └── README.md
├── docs/
│   └── referencias.yml
├── templates/
│   ├── models.yml
│   ├── views.yml
│   └── security.yml
└── addons/
    └── .gitkeep
```

### Función de cada elemento

- `AGENTS.md`: instrucciones permanentes para el agente.
- `requirements/funcionales.md`: comportamiento que debe implementar el módulo.
- `requirements/tecnicos.yml`: restricciones técnicas adicionales.
- `examples/`: módulos seleccionados por el profesor. Se consultan como ejemplos, no se modifican.
- `docs/referencias.yml`: documentación web que debe consultar el agente.
- `templates/`: especificaciones YAML opcionales.
- `addons/`: código fuente del módulo o módulos del alumno.
- `docker-compose.yml`: entorno de ejecución de ejemplo.
- `odoo.conf.example`: ejemplo que se debe adaptar a la configuración real del curso.

## 4. Preparar el repositorio para cada alumno

1. El profesor publica esta plantilla en GitHub.
2. El alumno crea su propio repositorio a partir de ella (por ejemplo, mediante **Use this template**) o clona el repositorio y trabaja en una rama propia.
3. El profesor facilita las imágenes Docker, las fuentes OCB/OCA 19 y el `odoo.conf` del curso.
4. El alumno configura `.env` y prepara el archivo `odoo.conf`.
5. El alumno abre el repositorio en su IDE y habilita el agente de programación.

No se deben subir al repositorio credenciales, contraseñas reales ni secretos. El `.env` local está excluido de Git.

## 5. Configurar Docker Compose

### 5.1. Fuentes OCB/OCA

En el host, las fuentes deben estar en:

```text
~/odoo/src
```

El Compose de ejemplo monta ese directorio en:

```text
/opt/odoo/src
```

El montaje de `addons/` del repositorio se realiza sobre:

```text
/opt/odoo/src/extra-addons
```

El código de OCB se monta en solo lectura. El alumno debe crear y modificar módulos únicamente en `addons/`.

### 5.2. Imágenes

Copia `.env.example` a `.env` y ajusta los nombres de imagen facilitados por el profesor:

```bash
cp .env.example .env
```

Las variables `ODOO_IMAGE` y `POSTGRES_IMAGE` permiten utilizar las imágenes del curso sin modificar el Compose.

### 5.3. Configuración de Odoo

Copia el archivo de configuración facilitado por el profesor como `odoo.conf` en la raíz del proyecto. Este archivo no se incluye en Git por defecto.

El Compose lo monta en:

```text
/opt/odoo/odoo.conf
```

Comprueba que su `addons_path` incluye, como mínimo, las rutas que correspondan a la imagen y al stack del curso. En este laboratorio se espera que estén disponibles:

```ini
addons_path = /opt/odoo/src/OCB/addons,/opt/odoo/src/extra-addons
```

No reemplaces sin consultar al profesor el resto de parámetros de la configuración suministrada.

### 5.4. Arrancar los servicios

```bash
docker compose config
docker compose up -d
docker compose ps
docker compose logs -f odoo
```

Si la imagen del curso utiliza un comando de arranque o variables diferentes, el profesor debe adaptar el Compose de ejemplo. No se presupone que todas las imágenes personalizadas tengan exactamente el mismo entrypoint.

## 6. Preparar el trabajo funcional

Edita `requirements/funcionales.md` y describe el problema con lenguaje natural.

Incluye, cuando sea posible:

- Qué problema se quiere resolver.
- Quién utilizará la funcionalidad.
- Qué información debe almacenarse.
- Qué operaciones podrá realizar cada usuario.
- Qué reglas de negocio deben cumplirse.
- Qué información debe mostrarse y dónde.
- Ejemplos de uso y casos límite.
- Qué comportamiento se considera correcto.

Evita prescribir una implementación técnica si no es necesario. Por ejemplo, describe «un usuario no puede confirmar una solicitud si no tiene líneas» en lugar de exigir directamente un método Python concreto.

El agente debe traducir el comportamiento a modelos, campos, relaciones, vistas, acciones, permisos y restricciones.

## 7. Añadir módulos de ejemplo

Copia en `examples/` los módulos que el profesor haya seleccionado.

Es recomendable incluir un `README.md` breve por ejemplo explicando:

- Qué aspecto debe observarse.
- Qué convenciones de estilo se quieren reutilizar.
- Qué partes son relevantes.
- Qué partes no deben copiarse porque pertenecen a otra funcionalidad o versión.

Prioriza ejemplos de la rama 19.0. Si un ejemplo procede de otra versión, indícalo expresamente y pide al agente que verifique su compatibilidad antes de reutilizar patrones.

No es necesario copiar repositorios OCA completos: selecciona módulos pequeños y relevantes.

## 8. Documentación de consulta

Añade en `docs/referencias.yml` las URL que el profesor quiera utilizar.

El agente debe priorizar documentación oficial de Odoo 19 y documentación OCA. Las fuentes web complementan, pero no sustituyen, la inspección de las fuentes locales.

Las URL de ejemplo incluidas en la plantilla son puntos de partida; comprueba que la página concreta corresponde a la versión adecuada.

## 9. Especificaciones YAML opcionales

Los archivos de `templates/` permiten al profesor orientar partes del diseño.

- `models.yml`: modelos, campos, relaciones y restricciones.
- `views.yml`: vistas, acciones y menús.
- `security.yml`: grupos, ACL y reglas de registro.

Son ejemplos de formato y pueden adaptarse a cada práctica. No son un lenguaje oficial de Odoo ni se cargan directamente en la base de datos.

El agente debe convertir las especificaciones a los archivos Python, XML y CSV correspondientes. Si una especificación contradice un requisito funcional, debe señalarlo y pedir aclaración.

## 10. Flujo de trabajo recomendado con el agente

### Fase 1 — Análisis

Pide al agente que lea `AGENTS.md`, los requisitos, las plantillas y los ejemplos. Debe devolver:

- Resumen de requisitos.
- Actores y permisos.
- Modelos y relaciones previstos.
- Vistas, acciones y menús necesarios.
- Dependencias Odoo previstas.
- Dudas y contradicciones.

No debe generar código todavía si hay decisiones funcionales importantes sin resolver.

### Fase 2 — Diseño

Solicita una propuesta técnica sencilla. El agente debe comprobar en OCB/OCA 19 si existen modelos o funcionalidades reutilizables.

Revisa la propuesta antes de autorizar la implementación.

### Fase 3 — Desarrollo

Autoriza la generación del módulo dentro de `addons/`. El agente debe respetar las convenciones OCA aplicables y no modificar las fuentes originales.

### Fase 4 — Validación

Solicita al agente que:

- Compruebe sintaxis Python, XML, CSV y YAML.
- Revise el manifiesto y las dependencias.
- Compruebe identificadores y referencias XML.
- Instale o actualice el módulo en el entorno Docker.
- Ejecute las pruebas disponibles.
- Revise los logs y corrija errores.

Comandos orientativos (sustituye `nombre_modulo` por el nombre técnico real):

```bash
docker compose exec odoo \
  python3 /opt/odoo/src/OCB/odoo-bin --config=/opt/odoo/odoo.conf \
  -d nombre_base -i nombre_modulo --stop-after-init
```

Para actualizar un módulo ya instalado:

```bash
docker compose exec odoo \
  python3 /opt/odoo/src/OCB/odoo-bin --config=/opt/odoo/odoo.conf \
  -d nombre_base -u nombre_modulo --stop-after-init
```

Estos comandos son orientativos. Comprueba el nombre de la base de datos, el comando disponible y la configuración de la imagen del curso. Si el contenedor ya ejecuta un proceso Odoo, puede ser necesario ejecutar una instancia puntual con el mismo entorno de configuración, evitando conflictos de procesos o puertos.

### Fase 5 — Documentación y entrega

El módulo debe incluir su propio README con:

- Objetivo y funcionalidades.
- Dependencias.
- Instalación.
- Uso básico.
- Grupos y permisos.
- Pruebas realizadas y limitaciones.

Antes de entregar, revisa `git status`, comprueba que no se incluyen secretos ni ficheros temporales y realiza un commit.

## 11. Criterios de calidad

Un módulo se considera listo cuando:

- Cumple los requisitos funcionales acordados.
- Sigue una estructura reconocible de módulo Odoo y las convenciones OCA aplicables.
- Solo incorpora dependencias justificadas.
- Tiene permisos coherentes y no concede acceso excesivo.
- Se instala sin errores en el entorno de Odoo 19 del curso.
- Las pruebas disponibles se ejecutan correctamente.
- El código es legible y comprensible para el alumno.
- La documentación describe lo que realmente se ha implementado.

El agente debe diferenciar siempre entre comprobaciones ejecutadas y comprobaciones pendientes.

## 12. Git y trabajo del alumno

Flujo mínimo recomendado:

```bash
git status
git add requirements examples docs templates addons README.md AGENTS.md
git commit -m "Desarrolla el módulo solicitado"
git push
```

No es necesario versionar bases de datos, filestore, logs, entornos virtuales, secretos ni el archivo local `odoo.conf`.

## 13. Resolución de problemas

- **No aparece el módulo:** comprueba el montaje de `addons/`, `addons_path` y el nombre técnico del directorio.
- **No conecta con PostgreSQL:** revisa el nombre del servicio, las variables de entorno y `db_host` en `odoo.conf`.
- **No puede escribir en `extra-addons`:** revisa permisos del directorio del host y el UID/GID utilizado por el usuario `odoo` dentro del contenedor.
- **No encuentra una dependencia:** comprueba que el addon está presente en las rutas montadas y que figura en `addons_path`.
- **Falla una vista:** revisa el log completo de Odoo y verifica la sintaxis contra ejemplos de Odoo 19.
- **El agente propone APIs dudosas:** pídele que localice la definición o uso en las fuentes OCB/OCA 19 antes de continuar.

## 14. Nota para el profesor

Esta plantilla es un punto de partida. Antes de distribuirla:

1. Adapta `.env.example` a las imágenes reales.
2. Revisa `docker-compose.yml` con la imagen Odoo del curso.
3. Distribuye el `odoo.conf` correspondiente por un canal adecuado.
4. Añade ejemplos OCA/OCB 19 seleccionados.
5. Sustituye las referencias documentales de ejemplo por las que se usarán en la práctica.
6. Comprueba el arranque y la instalación de un módulo de prueba en una copia limpia.

La plantilla evita acoplarse a un proveedor concreto de agentes. Cualquier agente que lea `AGENTS.md` y pueda inspeccionar y editar el repositorio podrá seguir este flujo.
