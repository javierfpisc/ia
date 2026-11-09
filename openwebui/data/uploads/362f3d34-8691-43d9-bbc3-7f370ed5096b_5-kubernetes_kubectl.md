# Guía de comandos kubectl.

Esta guía es un tutorial práctico para empezar a familiarizarse con **kubectl**, la herramienta de línea de comandos principal para gestionar clústeres de Kubernetes y comunicarse con el **API Server**.

A continuación, se explican algunos comandos, útiles por su función práctica en la administración del clúster.

---

## Información del Clúster y Entorno
Comandos básicos para verificar que la conexión con el clúster (Manager y Workers) es correcta.

*   **`kubectl version`**: Muestra la versión del cliente y del servidor de Kubernetes para asegurar la compatibilidad.
*   **`kubectl cluster-info`**: Proporciona las direcciones de los servicios del plano de control, como el API Server.
*   **`kubectl api-resources`**: Lista todos los tipos de recursos disponibles en el clúster (Pods, Services, etc.) con sus nombres cortos.
*   **`kubectl config get-contexts`**: Muestra los clústeres y usuarios configurados en nuestro entorno de trabajo.
*   **`kubectl config use-context <context>`**: Permite cambiar entre diferentes entornos o clústeres.
*   **`kubectl config current-context`**: Indica en qué clúster estáis trabajando actualmente para evitar errores.

## Inspección de Nodos y Namespaces
Permite ver la infraestructura física y lógica del clúster.

*   **`kubectl get nodes`**: Lista los nodos del clúster (nuestro Manager y los 2 Workers) y su estado actual.
*   **`kubectl get namespaces`**: Muestra los espacios de nombres creados para organizar los recursos.
*   **`kubectl top nodes`**: Muestra el consumo de CPU y memoria de cada nodo en tiempo real.

## Gestión y Visualización de Pods
Los **Pods** son la unidad mínima de ejecución; estos comandos permiten monitorizarlos.

*   **`kubectl get pods`**: Lista los Pods en el namespace actual.
*   **`kubectl get pods -A`**: Lista todos los Pods de todos los namespaces del clúster.
*   **`kubectl get pods -o wide`**: Muestra información extra, como la **dirección IP** del Pod y en qué **nodo** específico está corriendo.
*   **`kubectl describe pod <pod>`**: Ofrece un detalle técnico exhaustivo del Pod, incluyendo su estado, volúmenes y eventos de error.
*   **`kubectl explain pod`**: Proporciona documentación desde la línea de comandos sobre la estructura y campos del objeto Pod.
*   **`kubectl top pods`**: Muestra el uso de recursos de hardware de cada Pod.

## Interacción y Troubleshooting
Comandos esenciales para depurar aplicaciones que fallan.

*   **`kubectl logs <pod>`**: Muestra la salida estándar (logs) del contenedor para ver mensajes de error de la aplicación.
*   **`kubectl logs -f <pod>`**: "Sigue" los logs en tiempo real (streaming).
*   **`kubectl exec -it <pod> -- /bin/sh`**: Abre una terminal interactiva dentro del contenedor para ejecutar comandos internos.
*   **`kubectl get events`**: Muestra un historial de los eventos recientes del clúster, vital para saber por qué un recurso no arranca.

### Gestión de Deployments y Ciclo de Vida
Permite controlar cómo se despliegan y escalan las aplicaciones.

*   **`kubectl get deployments`**: Lista los despliegues activos.
*   **`kubectl describe deployment <name>`**: Detalles de configuración del Deployment, como el número de réplicas y la imagen utilizada.
*   **`kubectl apply -f manifest.yaml`**: Crea o actualiza recursos de forma **declarativa** usando un archivo de configuración.
*   **`kubectl delete -f manifest.yaml`**: Elimina todos los recursos definidos en el archivo YAML.
*   **`kubectl create deployment <name> --image=<image>`**: Crea un despliegue rápido de forma **imperativa** sin necesidad de un archivo YAML.
*   **`kubectl scale deployment <name> --replicas=<n>`**: Cambia el número de réplicas de una aplicación al instante.
*   **`kubectl rollout status/history deployment/<name>`**: Permite ver el estado o el historial de versiones de una actualización.
*   **`kubectl rollout undo deployment/<name>`**: Realiza un **Rollback**, volviendo a la versión anterior de la aplicación si hay fallos.

## Servicios e Ingress (Networking)
Gestión del acceso a las aplicaciones.

*   **`kubectl get services`**: Lista las IPs internas (ClusterIP) o externas (NodePort) de acceso a los Pods.
*   **`kubectl describe service <name>`**: Muestra a qué Pods específicos está enviando tráfico el servicio mediante sus etiquetas.
*   **`kubectl expose deployment <name> --port=<p> --target-port=<tp>`**: Crea automáticamente un Service para un Deployment existente.
*   **`kubectl get ingress`**: Lista las reglas de entrada gestionadas por nuestro Ingress Controller (como Traefik).

## Configuración y Seguridad
*   **`kubectl get configmaps/secrets`**: Lista los objetos que guardan configuraciones o datos sensibles.
*   **`kubectl describe configmap/secret <name>`**: Permite ver los detalles de configuración (los secretos aparecerán codificados por seguridad).