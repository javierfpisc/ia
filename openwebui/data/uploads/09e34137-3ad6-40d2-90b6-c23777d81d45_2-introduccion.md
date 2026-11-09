# Introducción a Kubernetes (K8s)

Dentro del ámbito de esta unidad, relativo a **Orquestación, Monitorización y Seguridad Digital**, tomaremos como base de trabajo y herramienta fundamental para el desarrollo conceptual a Kubernetes. Esto constituye un desafío, ya que es una tecnología compleja y hasta se podría decir que difícil, pero constituye el estándar más utilizado y demandado en relación al ámbito tecnológico que nos ocupa.

Kubernetes es una plataforma **portátil, extensible y de código abierto** diseñada para la gestión de cargas de trabajo y servicios mediante contenedores. Facilita tanto la **configuración declarativa** como la **automatización**, permitiendo orquestar infraestructuras complejas de manera eficiente.

## Orígenes y Respaldo
Kubernetes fue desarrollado originalmente por ingenieros de **Google** (basándose en su experiencia con sistemas internos como Borg), aunque este detalle específico de Google no aparece en los fragmentos de las fuentes, estas confirman que actualmente es un proyecto de **The Linux Foundation** y está mantenido por "**The Kubernetes Authors**".

Su respaldo es masivo, contando con un **ecosistema grande y en rápido crecimiento**. La comunidad participa activamente a través de Grupos de Interés Especial (SIGs), foros como Stack Overflow y repositorios en GitHub para reportar problemas o sugerir mejoras.

## Necesidades que cubre
En la administración de sistemas moderna, Kubernetes resuelve problemas críticos de la era cloud:

*   **Gestión de contenedores a escala:** Automatiza el despliegue de múltiples instancias de aplicaciones.
*   **Disponibilidad:** Asegura que las aplicaciones sigan funcionando mediante mecanismos de **auto-reparación (Self-healing)**.
*   **Orquestación de almacenamiento:** Permite montar sistemas de almacenamiento de forma automática, ya sean locales o en la nube.
*   **Service Discovery y Balanceo de Carga:** Kubernetes puede exponer un contenedor usando un nombre DNS o su propia dirección IP y balancear el tráfico para estabilizar el despliegue.

## Factores Innovadores
Lo que diferencia a Kubernetes de las aproximaciones tradicionales de administración es su modelo:

*   **Modelo Declarativo:** En lugar de ejecutar una serie de comandos, el administrador define el "estado deseado" (por ejemplo: "quiero 3 réplicas de este servicio") y Kubernetes se encarga de que la realidad coincida con esa definición.
*   **Control de recursos:** Permite especificar cuánta CPU y memoria necesita cada contenedor, optimizando el uso del hardware.
*   **Extensibilidad:** A través de Custom Resources (CRDs) y APIs de agregación, es posible añadir funciones personalizadas al clúster sin modificar el código fuente de Kubernetes.

## Arquitectura Básica
Un clúster de Kubernetes se divide principalmente en:

*   **Control Plane:** El "cerebro" del clúster. Incluye componentes como el `kube-apiserver` (punto de entrada REST), el `kube-scheduler` (decide dónde colocar los pods) y el `kube-controller-manager` (gestiona los bucles de control).
*   **Nodos (Worker Nodes):** Las máquinas donde corren las aplicaciones. Cada nodo tiene un agente llamado `kubelet` que asegura que los contenedores estén funcionando según lo previsto.
*   **Pods:** Es la unidad mínima de computación que se puede desplegar; representa uno o más contenedores compartiendo almacenamiento y red.

## Ventajas e Inconvenientes

| Ventajas | Inconvenientes / Desafíos |
| :--- | :--- |
| **Portabilidad:** Funciona igual en nubes públicas, privadas o híbridas. | **Curva de aprendizaje:** Es un sistema complejo con una vasta cantidad de APIs y conceptos. |
| **Escalabilidad masiva:** Capacidad para gestionar clústeres grandes y múltiples zonas. | **Sobrecarga operativa:** Requiere una gestión cuidadosa de certificados, redes y seguridad. |
| **Actualizaciones sin interrupción:** Soporta rollouts y rollbacks automáticos. | **Recursos mínimos:** Mantener el control plane requiere recursos que pueden ser excesivos para apps muy simples. |

## Uso y Aplicaciones
Kubernetes se utiliza para una amplia variedad de tareas en entornos cloud:

*   **Aplicaciones Stateless (sin estado):** Despliegues rápidos que pueden escalarse horizontalmente con facilidad.
*   **Aplicaciones Stateful (con estado):** Gestión de bases de datos o sistemas distribuidos (como MySQL o Cassandra) que requieren identidad persistente.
*   **Tareas por lotes (Batch Jobs):** Ejecución de trabajos que corren hasta completarse o tareas programadas (CronJobs).

---


