# Introducción a Helm: El Gestor de Paquetes para Kubernetes

Hasta ahora, hemos estado gestionando aplicaciones de forma individual, aplicando archivos YAML uno a uno. Sin embargo, a medida que las aplicaciones crecen, gestionar decenas de archivos YAML se vuelve complejo. Aquí es donde entra **Helm**. Aunque los archivos proporcionados se centran en la gestión de objetos nativos de Kubernetes mediante `kubectl`, como los **Deployments**, **Services** y **ConfigMaps**, se hace necesario un paso más hacia una abstracción funcional que permita mejorar la gestión y eficiencia a la hora de orquestar los despliegues en nuestra infraestructura. la herramienta **Helm** es el siguiente paso lógico para conseguirlo. 

## ¿Qué es Helm?
Helm es conocido como el **"Package Manager" (Gestor de Paquetes)** para Kubernetes. Si en Linux usamos `apt` o `yum`, y en Python usamos `pip`, en Kubernetes usamos **Helm**. Su función principal es empaquetar todos los recursos necesarios para una aplicación (Deployments, Services, ConfigMaps, Ingress, etc.) en una sola unidad fácil de desplegar y versionar.

## Conceptos Clave
Para que podamos entender los fundamentos de Helm, debemos conocer sus tres pilares:

*   **Chart:** Es el "paquete" de Helm. Es un conjunto de archivos organizados en una carpeta que describen un conjunto relacionado de recursos de Kubernetes. Por ejemplo, podríais tener un "Chart de Odoo" que incluya todo lo que necesitamos configurar para desplegar esa solución ERP (Deployment, StatefulSet para la base de datos, Services, Ingress, etc).
*   **Release:** Es una instancia específica de un Chart ejecutándose en el clúster. Podemos instalar el mismo Chart tres veces en namespaces distintos; cada una será una "Release" diferente.
*   **Repository:** Es un lugar donde se almacenan y comparten los Charts (similar a un repositorio de Docker Hub).

## Conociendo la estructura de un Chart
Como hemos visto, **Helm** es el gestor de paquetes por excelencia para Kubernetes. Para que podamos pasar de gestionar archivos YAML sueltos a administrar aplicaciones complejas, es fundamental profundizar en el concepto de **Chart**.

### ¿Qué es un Chart?
Un **Chart** es un paquete de Helm que contiene todas las definiciones de recursos necesarias para ejecutar una aplicación, herramienta o servicio dentro de un clúster de Kubernetes. Podemos pensarlo como una "receta" que agrupa los **Deployments, Services, ConfigMaps y Secrets** que hemos estado creando manualmente para nuestros proyectos prácticos.

### Estructura de un Chart
Cuando creamos o descargamos un Chart, veremos una estructura de directorios estandarizada. Los componentes más importantes son los siguientes:

*   **`Chart.yaml`**: Es el archivo de metadatos. Contiene información básica como el nombre del chart, la versión de la aplicación y una descripción.
*   **`values.yaml`**: Es el archivo más importante para el usuario. Contiene los **valores por defecto** para las variables que se usarán en las plantillas. Por ejemplo, aquí podríamos definir la imagen de NGINX o el tamaño del PVC, o cualquier aspecto específico que afecte a nuestro despliegue en particular.
*   **`templates/`**: Una carpeta que contiene los archivos de manifiesto de Kubernetes. Lo especial es que estos archivos no tienen valores fijos, sino que usan el lenguaje de plantillas de Go para leer los datos de `values.yaml`.
*   **`charts/`**: Una carpeta opcional donde se guardan otros charts de los que este dependa.

### ¿Cómo modificar un Chart?
Existen dos niveles para modificar el comportamiento de una aplicación en Helm:

#### A. Modificación por el Usuario (Fácil)
El desplegador no suele tocar los archivos dentro de `templates/`. En su lugar, modifica los valores para adaptar el despliegue a sus necesidades:

*   **Editar `values.yaml`**: Se cambian los parámetros directamente en el archivo antes de instalar.
*   **Sobrescribir por comando**: Al instalar, se pueden pasar valores específicos sin tocar el archivo original:
    ```bash
    helm install mi-odoo ./odoo-chart --set replicaCount=3
    ```

#### Modificación por el Desarrollador (Avanzado)
Si el desplegador está creando su propio Chart, deberá trabajar en la carpeta `templates/`:

*   **Uso de Plantillas**: En lugar de escribir `replicas: 2`, escribirá `replicas: {{ .Values.replicaCount }}`.
*   **Lógica Condicional**: Helm permite usar `if/else` dentro de los YAML. Podríamos crear un **Ingress** solo si una variable en `values.yaml` está marcada como `true`.

### Ciclo de Vida y Desarrollo
Helm ofrece herramientas para asegurar que las modificaciones son correctas antes de aplicarlas al clúster:

*   **`helm lint`**: Examina el chart en busca de errores estructurales o de sintaxis.
*   **`helm install --dry-run --debug`**: Simula la instalación y muestra por pantalla cómo quedarían los YAML finales tras aplicar los valores, pero sin llegar a crear nada en el clúster.

Esta estructura permite que podamos descargar aplicaciones complejas desde **repositorios** públicos y personalizarlas simplemente editando un pequeño archivo de texto (`values.yaml`), manteniendo toda la complejidad técnica oculta y organizada.

## ¿Por qué usar Helm en lugar de YAMLs sueltos?
Helm introduce una ventaja competitiva fundamental para los técnicos de sistemas: el uso de plantillas o **Templating**.

*   **Variables:** En lugar de tener valores fijos en el YAML (como el nombre del host o la memoria), usamos etiquetas. Los valores reales se guardan en un archivo llamado `values.yaml`.
*   **Reutilización:** Permite desplegar la misma aplicación en "Entorno de Laboratorio" o "Producción" simplemente cambiando el archivo de valores, sin tocar la lógica del despliegue.
*   **Gestión de Versiones:** Helm guarda un historial. Si una actualización falla, podemos volver a la versión anterior con un solo comando (**Rollback**).

## Comandos Básicos para iniciarse
Para que podamos empezar a interactuar con Helm en nuestro clúster, tenemos algunos comandos esenciales:

| Comando | Función |
| :--- | :--- |
| `helm repo add` | Añade un repositorio externo de aplicaciones. |
| `helm install <nombre> <chart>` | Despliega una aplicación completa en el clúster. |
| `helm list` | Muestra todas las aplicaciones instaladas (Releases). |
| `helm upgrade` | Actualiza una aplicación a una nueva versión o cambia su configuración. |
| `helm rollback` | Vuelve a una versión anterior si algo sale mal. |
| `helm uninstall` | Borra todos los recursos asociados a esa aplicación de una sola vez. |

## Relación con lo aprendido
Helm no sustituye lo aprendido sobre **kubectl**; lo complementa. Mientras que `kubectl` es excelente para depurar y gestionar objetos atómicos, Helm es la herramienta profesional para el **despliegue de productos software** complejos de forma organizada y repetible.