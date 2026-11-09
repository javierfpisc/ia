# Artefactos (controllers) de Kubernetes para el Despliegue de Microservicios

En Kubernetes, los **objetos o recursos** son abstracciones que representan el estado deseado de nuestro clúster. Para gestionar microservicios, Kubernetes utiliza recursos de "Workload" (Cargas de trabajo) que permiten delegar la gestión del ciclo de vida de los contenedores a la plataforma.

A continuación, se describen los principales artefactos conceptuales y su integración en el entorno, así como la forma de controlarlos mediante los correspondientes **Controllers** (Deployment, StatefulSet, DaemonSet, Job y CronJob).

---

## El Pod: La Unidad Mínima de Ejecución
El **Pod** es el objeto más pequeño y básico que se puede crear y desplegar en Kubernetes. 

*   **Definición:** Representa un proceso único que se ejecuta en el clúster. Puede contener uno o más contenedores que están estrechamente unidos y comparten recursos. Un Pod representa, por tanto, un conjunto de uno o más contenedores de aplicaciones (como Docker) y los recursos compartidos necesarios para esos contenedores. Estos recursos incluyen almacenamiento (volúmenes), una dirección IP de red única y opciones que determinan cómo deben ejecutarse los contenedores
*   **Objetivo:** Agrupar contenedores que deben trabajar juntos. Por ejemplo, un contenedor con la aplicación principal y otro "sidecar" que gestione sus logs. El Pod actúa como una "envoltura" para los contenedores, permitiendo que Kubernetes los gestione como una única entidad.
*   **Integración:** Los contenedores dentro de un mismo Pod comparten la misma dirección IP, espacio de red y pueden acceder a volúmenes de almacenamiento compartidos. Un Pod siempre se ejecuta en un único **Nodo**. El componente **kubelet** en cada nodo es el encargado de recibir las especificaciones del Pod (PodSpecs) y asegurar que los contenedores descritos en ellas estén funcionando y saludables.

## Deployment: Gestión de Aplicaciones Stateless
La mayoría de las aplicaciones web modernas se despliegan como aplicaciones **stateless**, lo que significa que no guardan datos de sesión de forma local y pueden ser reemplazadas en cualquier momento. El **Deployment** es el artefacto más común para desplegar microservicios que no guardan datos de sesión localmente, conocidos como aplicaciones **Stateless** (sin estado).

*   **Definición:** Es un controlador que define el estado deseado para un conjunto de Pods idénticos. Constituye el artefacto de mayor nivel para gestionar estas aplicaciones **stateless**. Su función es proporcionar actualizaciones declarativas para los Pods y los ReplicaSets.
*   **Objetivo:** Proporcionar actualizaciones declarativas. Permite describir cuántas réplicas de una aplicación deben correr y facilita tareas como el escalado horizontal o las actualizaciones progresivas (Rolling Updates) sin caída de servicio.
*   **Funcionamiento**: El administrador describe el "estado deseado" en el Deployment (por ejemplo, "mantener siempre 3 réplicas de la versión 1.2"). El **kube-controller-manager** ejecuta bucles de control para asegurar que el estado actual coincida con este deseo, permitiendo realizar actualizaciones progresivas (Rolling Updates) o volver a versiones anteriores (Rollbacks) de forma automática.
*   **Integración:** Se integra con el **Scheduler** para distribuir las réplicas entre los nodos disponibles y con los **Services** para permitir que el tráfico llegue a los Pods de forma balanceada.

## StatefulSet: Gestión de Aplicaciones Stateful
A diferencia de los stateless, las aplicaciones **stateful** requieren que se mantenga una identidad persistente y un almacenamiento vinculado a cada instancia (como en el caso de bases de datos o sistemas distribuidos tipo ZooKeeper). Cuando un microservicio requiere mantener una identidad persistente o un estado de datos (como una base de datos o un sistema de mensajería), se utiliza un **StatefulSet**.

*   **Definición:** Recurso de carga de trabajo diseñado para gestionar aplicaciones que requieren identificadores de red únicos y persistentes.
*   **Objetivo:** Garantizar que los Pods se creen y se eliminen en un orden específico y que siempre mantengan el mismo nombre y acceso al mismo almacenamiento, incluso si son reprogramados en otro nodo. A diferencia de un Deployment, donde los Pods son intercambiables, el StatefulSet mantiene una identidad persistente para cada Pod. Estos Pods se crean a partir de la misma especificación pero no son intercambiables; cada uno tiene un identificador persistente que mantiene a través de cualquier reprogramación.
*   **Integración:** Es fundamental que el entorno de ejecución o laboratorio disponga de volúmenes persistentes gestionados por algún proveedor de persistencia a nivel de clúster, como **CephFS**, asegurando que cada réplica mantenga su propio volumen de datos.

Un aspecto importante de los **StatefulSets** es el siguiente: En Kubernetes, un `StatefulSet` suele usar un **Headless Service** (`clusterIP: None`) porque sus Pods necesitan tener una identidad de red estable y accesible individualmente, algo fundamental en aplicaciones con estado como bases de datos o clústeres replicados. A diferencia de un `Service` normal, que crea una IP virtual y balancea tráfico entre Pods indistintamente, un Headless Service no hace balanceo ni asigna una ClusterIP, sino que expone directamente las IPs reales de cada Pod mediante DNS. Esto permite que cada instancia del StatefulSet tenga un nombre fijo y resoluble, como `mariadb-0.mariadb.default.svc.cluster.local` o `mariadb-1.mariadb.default.svc.cluster.local`, de modo que los nodos puedan identificarse y comunicarse siempre con el mismo peer, conservar su identidad aunque se reinicien y mantener correctamente replicación, quorum o almacenamiento persistente asociado a cada Pod.

## Deployments vs StatefulSets
Como vimos en el apartado anterior un **StatefulSet** proporciona una **identidad estable** para los Pods. La pregunta es obvia, en qué se materializa este requisito?.
La “identidad estable” significa que cada Pod mantiene siempre el mismo nombre, DNS y asociación con su almacenamiento aunque sea recreado. En un Deployment, los Pods son desechables e intercambiables: si uno muere, Kubernetes crea otro con un nombre distinto, por ejemplo:
```
mariadb-7f8c9d6b5-xk92p
```
y tras reiniciarse:
```
mariadb-7f8c9d6b5-lp4zt
```
Para Kubernetes eso es “la misma aplicación”, pero para una base de datos no siempre da igual, porque puede haber replicación, clustering, cachés, locks, peers conocidos o configuraciones que esperan identificar nodos concretos. En cambio, un StatefulSet crea Pods con nombres permanentes y predecibles:
```
mariadb-0
mariadb-1
mariadb-2
```
Si mariadb-0 se cae, Kubernetes vuelve a crear exactamente mariadb-0, con el mismo DNS y normalmente el mismo volumen persistente asociado. Así, la aplicación puede asumir que “ese nodo” sigue siendo el mismo aunque haya cambiado el contenedor internamente. Esto es especialmente importante en sistemas distribuidos donde los nodos se conocen entre sí por nombre. En el caso concreto de una sola réplica de MariaDB y almacenamiento Ceph compartido, la ventaja práctica inmediata es menor, y probablemente un Deployment también funcionaría; pero el StatefulSet sigue siendo el modelo correcto porque Kubernetes entiende que esa carga tiene estado y debe preservar identidad, almacenamiento y orden de recreación.

## DaemonSet: Servicios de Infraestructura
Un **DaemonSet** garantiza que todos (o una selección específica) de los Nodos del clúster ejecuten una copia de un Pod determinado. A medida que se añaden nodos al clúster, los Pods del DaemonSet se añaden automáticamente a ellos. Cuando se eliminan nodos, esos Pods se limpian por el recolector de basura.

*   **Definición:** Un controlador que asegura la presencia de un Pod específico en cada nodo worker.
*   **Objetivo:** Desplegar servicios que deben correr "en segundo plano" en toda la infraestructura, como recolectores de logs, agentes de monitorización o el propio plugin de red (**Calico**). Se utilizan típicamente para servicios que deben correr en cada nodo, como agentes de almacenamiento, proxies de red o recolectores de logs de nodos.
*   **Integración:** A medida que se añaden nuevos nodos al clúster, el DaemonSet despliega automáticamente el Pod en ellos sin intervención manual.

## Jobs y CronJobs: Tareas por Lotes
No todos los microservicios deben estar corriendo indefinidamente. Para tareas puntuales se utilizan los **Jobs**. Es decir, no todos los procesos en un clúster de microservicios deben ser servicios persistentes. Para tareas que tienen un inicio y un fin definido, se utilizan los **Jobs**.

*   **Job:** Crea uno o más Pods y asegura que un número específico de ellos termine con éxito. Se usa para tareas de procesamiento por lotes que corren hasta completarse.
*   **CronJob:** Es un Job que se ejecuta basándose en una programación temporal (estilo cron de Linux). Es ideal para tareas recurrentes como copias de seguridad o generación de informes.

---

## Relación con los Componentes del Plano de Control
Para que estos artefactos funcionen, dependen de la infraestructura lógica de Kubernetes:

*   **kube-apiserver:** Es el punto central donde se validan y configuran todos los datos de estos objetos (Pods, Deployments, Services).
*   **kube-scheduler:** Es el componente que observa los Pods recién creados que no tienen un nodo asignado y selecciona el mejor nodo para que se ejecuten, basándose en recursos y políticas.
*   **kube-proxy:** Mantiene las reglas de red en los nodos, permitiendo la comunicación de red hacia los Pods desde dentro o fuera del clúster.

### Resumen de Relaciones y Funciones

En nuestro entorno de microservicios, los **Pods** ejecutan el código, los **Deployments** aseguran que siempre haya suficientes copias de, por ejemplo nuestra web, los **StatefulSets** protegen las bases de datos, y los **Services** (gestionados por el kube-proxy) permiten que todos estos componentes se encuentren y hablen entre sí de forma estable.

| Artefacto | Tipo de Carga | Objetivo Principal | Ejemplo de Uso |
| :--- | :--- | :--- | :--- |
| **Pod** | Base | Ejecutar contenedores | Contenedor de app + Sidecar. |
| **Deployment** | Stateless | Disponibilidad y escalado | Servidor web (NGINX), API. |
| **StatefulSet** | Stateful | Identidad y persistencia | Base de datos (MySQL), Redis. |
| **DaemonSet** | Infraestructura | Cobertura total de nodos | Agente de logs (Fluentd). |
| **Job / CronJob**| Batch | Ejecución hasta finalizar | Migración de DB, Backup. |

Estos artefactos se integran con el **Plano de Control** de Kubernetes, que monitoriza constantemente si el estado real coincide con el definido en estos objetos, activando los mecanismos de **auto-reparación** si algún componente falla.