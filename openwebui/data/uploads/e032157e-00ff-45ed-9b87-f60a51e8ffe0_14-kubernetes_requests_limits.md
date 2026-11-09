# Gestión del uso de recursos en kubernetes
En el ecosistema de Kubernetes, la gestión de recursos es fundamental para garantizar la estabilidad del clúster y el rendimiento de las aplicaciones. Los **requests** y **"limits" (límites)** son los mecanismos clave dentro del subsistema de administración de recursos para Pods y contenedores. Mientras que los **limits** establecen un techo máximo, los **requests** definen el **suelo mínimo garantizado** para que un contenedor pueda funcionar.

La mejor forma de visualizarlo es como un **margen de operación**:

*   **Request (Suelo):** Es lo que el contenedor tiene reservado por contrato. El nodo nunca le quitará estos recursos.
*   **Limit (Techo):** Es lo máximo que puede llegar a consumir si el nodo tiene recursos sobrantes en ese momento.

A continuación, se explican detalladamente estos conceptos basándose en la arquitectura y documentación de Kubernetes.

## Requests

### Definición de Requests
Un **request** es la cantidad mínima de un recurso (CPU o Memoria) que Kubernetes **garantiza** a un contenedor. 

*   Cuando defines un *request*, le estás diciendo a Kubernetes: "Este contenedor necesita al menos esta cantidad de recursos para ejecutarse correctamente".
*   A diferencia de los *limits*, que pueden ser sobrepasados (en el caso de la CPU), los *requests* son una reserva de capacidad que el nodo asegura para el contenedor en todo momento.

### El papel crucial del Scheduler
El mecanismo de *requests* es lo que utiliza el **kube-scheduler** para decidir en qué nodo colocar un Pod.

*   **Cálculo de capacidad:** Cuando llega un nuevo Pod, el scheduler busca un nodo que tenga suficiente **capacidad libre** basándose en la suma de los *requests* de los Pods que ya están corriendo en ese nodo, no en su consumo real en ese momento.
*   **Decisión de ubicación:** Si un nodo tiene 4 CPUs y los Pods que ya están en él tienen *requests* que suman 3.5 CPUs, el scheduler no asignará a ese nodo ningún Pod que solicite más de 0.5 CPUs, incluso si el consumo real actual de esos Pods es muy bajo.

### Clasificación de Calidad de Servicio (QoS)
Como mencionamos en la respuesta anterior, la combinación de ambos valores determina la **prioridad** del Pod ante una crisis de recursos en el nodo:

1.  **Guaranteed (Garantizado):** El Pod tiene `request == limit`. Kubernetes le da la máxima prioridad porque sabe exactamente cuánto va a consumir.
2.  **Burstable (Con ráfagas):** El Pod tiene `request < limit`. Tiene garantizado su mínimo, pero se le permite "crecer" hasta el límite si hay espacio. Es la configuración más común para microservicios web.
3.  **BestEffort:** No tiene definidos ni *requests* ni *limits*. Es el primero en ser expulsado si el nodo se queda sin memoria.

### Aplicación Práctica
En nuestro clúster de 3 nodos (1 Manager y 2 Workers), los *requests* son vitales para evitar la **saturación del scheduler**:

*   Si no se definen *requests*, el scheduler podría amontonar demasiados Pods en un solo nodo Worker, pensando que está vacío, lo que acabaría provocando fallos por falta de memoria (OOM) cuando todos los Pods empiecen a trabajar a la vez.
*   Mediante el uso de **LimitRanges** en los namespaces, puede forzarse a que cada Pod tenga un *request* por defecto, asegurando que el scheduler distribuya la carga de forma equilibrada entre los dos nodos Worker disponibles.

### Ejemplo
Dentro de la especificación del contenedor, se vería así:
```yaml
resources:
  requests:
    memory: "64Mi"   # El nodo reserva esto sí o sí
    cpu: "250m"      # El scheduler busca un nodo con 1/4 de core libre
  limits:
    memory: "128Mi"  # El techo máximo de memoria
    cpu: "500m"      # El techo máximo de CPU
```
## Limits

### Definición Conceptual de Limits
Un **limit** es la cantidad máxima de un recurso (principalmente **CPU** y **memoria**) que Kubernetes permite consumir a un contenedor. 

Mientras que los *requests* definen lo que un contenedor tiene garantizado para poder arrancar, los *limits* actúan como un **techo máximo** de consumo. El agente **kubelet** es el encargado de asegurar que los contenedores en ejecución no sobrepasen estos valores definidos.

---

### Tipos de Recursos Limitables

Los dos recursos más comunes que se gestionan mediante límites son:

*   **CPU:** Se mide en unidades de "cores" o "millicores" (ejemplo: `500m` es medio núcleo). La CPU se considera un recurso **comprimible**. Si un contenedor alcanza su límite, Kubernetes no lo mata, sino que lo **restringe (throttling)**, ralentizando su ejecución pero permitiendo que siga vivo.
*   **Memoria:** Se mide en bytes (normalmente Megabytes o Gibibytes, ej: `256Mi`). La memoria es un recurso **no comprimible**. Si un contenedor intenta sobrepasar su límite de memoria, el sistema lo detendrá (proceso conocido como **OOM Kill** o *Out Of Memory*) para proteger la estabilidad del nodo.

---

### Aplicaciones y Gestión en el Clúster

El uso de límites tiene aplicaciones directas en la administración del entorno:

#### Calidad de Servicio (QoS Classes)
Kubernetes utiliza la relación entre *requests* y *limits* para clasificar los Pods en tres niveles de prioridad en caso de que el nodo se quede sin recursos:

1.  **Guaranteed:** Cuando el límite y el request son iguales. Son los Pods con mayor prioridad.
2.  **Burstable:** Cuando el límite es superior al request. Tienen una prioridad media.
3.  **BestEffort:** Cuando no se definen ni límites ni requests. Son los primeros en ser eliminados si el nodo sufre presión de recursos.

#### Control por Namespace (LimitRanges)
Como administradores, podéis usar el objeto **LimitRange** para establecer políticas automáticas dentro de un namespace:

*   **Límites por defecto:** Si se nos olvida poner límites en el YAML, el LimitRange se los asigna automáticamente.
*   **Restricciones de rango:** Puede impedirse que un Pod pida demasiado (máximo) o demasiado poco (mínimo) recurso.

#### Cuotas Totales (ResourceQuotas)
A diferencia de los límites individuales por Pod, las **ResourceQuotas** limitan la suma total de todos los recursos en un namespace. Por ejemplo, podemos definir que el namespace `ejemplos` no consuma en total más de 4 CPUs y 8GB de RAM, independientemente de cuántos Pods se desplieguen.

---

### Importancia para el Administrador de Sistemas
Entender los límites es vital por dos razones prácticas:

1.  **Evitar el "Efecto Vecino Ruidoso":** Impide que un microservicio con un error (como una fuga de memoria o un bucle infinito) consuma todos los recursos del nodo y afecte a otros microservicios que corren en el mismo servidor físico.
2.  **Predecibilidad:** Permite al **Scheduler** de Kubernetes tomar mejores decisiones sobre en qué nodo colocar cada carga de trabajo, basándose en la capacidad disponible real del clúster.

**Nota importante:** En nuestro laboratorio, configurar límites adecuados asegura que los servicios del sistema (como **Calico** o el propio plano de control) siempre tengan recursos suficientes para mantener el clúster operativo.