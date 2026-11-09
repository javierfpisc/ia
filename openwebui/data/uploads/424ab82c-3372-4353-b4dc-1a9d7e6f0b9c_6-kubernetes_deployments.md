# Deployment: `nginx-deployment`

Tomando como base el archivo de configuración que se muestra a continuación explicaremos cada componente técnico, su función y cómo se integra en la arquitectura de nuestro clúster de laboratorio. Creemos en nuestro nodo Manager un archivo `deployment-1.yaml` con el siguiente contenido:

```yaml
apiVersion: apps/v1
kind: Deployment
# -------------------------------------------------------------------
# METADATOS DEL DEPLOYMENT
# -------------------------------------------------------------------
metadata:
  name: nginx-deployment
  # Namespace donde se desplegará
  namespace: ejemplos
  # Labels del propio Deployment
  labels:
    app: nginx
    entorno: laboratorio
# -------------------------------------------------------------------
# ESPECIFICACIÓN DEL DEPLOYMENT
# -------------------------------------------------------------------
spec:
  # Número de réplicas (Pods) que queremos ejecutar
  replicas: 3
  # Selector:
  # Indica qué Pods pertenecen a este Deployment/ReplicaSet
  selector:
    matchLabels:
      app: nginx
  # Plantilla del Pod
  # Aquí se define cómo serán los Pods creados
  template:
    metadata:
      # Labels que tendrán los Pods
      labels:
        app: nginx
        version: v1
    spec:
      containers:
        # Nombre interno del contenedor
        - name: nginx-container
          # Imagen que descargará Kubernetes
          image: nginx:latest
          # Puerto expuesto por el contenedor
          ports:
            - containerPort: 80
          # Recursos mínimos/máximos
          # Muy importante para buenas prácticas
          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "250m"
          # Variables de entorno de ejemplo
          env:
            - name: EJEMPLO
              value: "Clase de Kubernetes"
```

---

## Identificación del Objeto: API y Kind

*   **`apiVersion: apps/v1`**: Define la versión del esquema de la API de Kubernetes que se está utilizando. La versión `apps/v1` es la estándar actual para recursos de carga de trabajo como los Deployments.
*   **`kind: Deployment`**: Indica que el objeto a crear es un **Deployment**. Este es un recurso de alto nivel que gestiona aplicaciones de forma declarativa, permitiendo actualizaciones y escalado automático de Pods.

## Metadatos (Metadata)

*   **`name: nginx-deployment`**: Es el nombre único que identifica este despliegue dentro de un Namespace.
*   **`labels`**: Son pares clave-valor (ej: `entorno: laboratorio`) vinculados al objeto. 
    *   **Función:** No afectan al funcionamiento técnico directo, pero son esenciales para la organización y para que el administrador pueda filtrar o agrupar recursos mediante **Selectors**.

## Especificación del Estado Deseado (Spec)
La sección `spec` define el comportamiento que queremos que Kubernetes mantenga de forma persistente.

*   **`replicas: 3`**: Es la instrucción de escalado horizontal. 
    *   **Relación con el entorno:** El **kube-controller-manager** vigilará que siempre existan exactamente 3 Pods en ejecución. Si un nodo worker falla y se pierde un Pod, Kubernetes detectará la discrepancia y arrancará uno nuevo en otro nodo disponible para volver a sumar 3.
*   **`selector`**: Es el mecanismo de "pegamento" en Kubernetes.
    *   **`matchLabels: app: nginx`**: Indica al Deployment que debe hacerse cargo y supervisar a todos los Pods que tengan la etiqueta `app: nginx`. Esta relación es vital para que el Deployment sepa qué Pods le "pertenecen".

## Plantilla del Pod (Template)

*   **`template`**: Es un `PodTemplate` o plano de diseño. Describe cómo deben ser los Pods que el Deployment va a crear.
    *   **Metadatos de la plantilla:** Aquí es obligatorio incluir las etiquetas que coincidan con el `selector` (en este caso, `app: nginx`).
    *   **Dentro de la sección spec** establecemos la definición de los **containers**, `name`, `image`, puerto interno de escucha en el Pod. De este modo los cambios que se realicen dentro de este `template` (como cambiar la imagen de NGINX) dispararán automáticamente una actualización progresiva (**Rolling Update**) de todos los Pods.
    *   **Un apartado interesante es el de resources**: define los recursos de CPU y memoria que el contenedor necesita y puede consumir. Dentro de esta sección existen dos apartados fundamentales: **requests y limits**. La sección `requests` indica los recursos mínimos garantizados para el contenedor. Kubernetes utiliza estos valores durante la planificación del Pod para decidir en qué nodo puede ejecutarse. En este caso el contenedor solicita al menos 64 MiB de memoria RAM y 100 millicores de CPU (0.1 CPU). Esto significa que Kubernetes solo colocará el Pod en un nodo que disponga, como mínimo, de esos recursos libres. Los requests representan por tanto la cantidad de recursos que la aplicación necesita para funcionar correctamente de forma garantizada. La sección `limits` establece el máximo de recursos que el contenedor puede llegar a consumir. En este caso el contenedor podrá utilizar como máximo 128 MiB de memoria y 250 millicores de CPU (0.25 CPU). Si la aplicación intenta superar el límite de CPU, el sistema reducirá su capacidad de ejecución mediante throttling. Si supera el límite de memoria, el contenedor puede ser finalizado automáticamente por el sistema (OOMKilled) para proteger la estabilidad del nodo.

---

## Integración con el Entorno

El despliegue de este archivo YAML desencadena una serie de interacciones entre los componentes del clúster:

1.  **Manager (Control Plane):** El **kube-apiserver** recibe el archivo. El **kube-scheduler** analiza los recursos disponibles en nuestros nodos workers y decide dónde colocar cada una de las 3 réplicas.
2.  **Workers:** El agente **kubelet** de cada nodo worker recibe la orden, contacta con el **Container Runtime** e inicia los contenedores de NGINX basándose en la especificación del `template`.
3.  **Networking (Calico):** Una vez arrancados, vuestro CNI (**Calico**) asigna una IP única a cada uno de los 3 Pods. Calico configura las rutas necesarias para que estos Pods puedan hablarse entre sí a través de los nodos Manager y Worker sin necesidad de NAT [Sources: Historial de chat / Contexto del curso].
4.  **Persistencia (CephFS):** Aunque no se detalla en el fragmento de código, si añadiéramos una sección de `volumes` en el `template` apuntando a un **PersistentVolumeClaim**, Kubernetes se encargaría de montar nuestro sistema de archivos compartido **CephFS** en el directorio que indicaramos dentro del contenedor NGINX.

### Resumen de relaciones
| Elemento | Se relaciona con... | Función en el entorno |
| :--- | :--- | :--- |
| **Labels** | **Selector** | Permite que el Deployment identifique sus Pods. |
| **Replicas** | **Nodes (Workers)** | Distribuye la carga de trabajo para asegurar disponibilidad. |
| **Template** | **Kubelet** | Da las instrucciones técnicas para crear los contenedores. |
| **Deployment** | **ReplicaSet** | El Deployment crea internamente un ReplicaSet para gestionar el número exacto de pods. |

## Desplegando nuestro Deployment
Para desplegarlo, ejecutamos los siguientes pasos desde `kuber1`:

* **Creamos el namespace** (ejemplos) en el que correrá el deployment:
```bash
kubectl create namespace ejemplos
```
* **Desplegamos desde el archivo**:
```bash
kubectl apply -f deployment-1.yaml
```
Una vez desplegado, consultamos el estado de todos los elementos dentro del namespace:
```bash
kubectl get all -n ejemplos
```
La salida debería de ser algo así:
```
NAME                                    READY   STATUS    RESTARTS   AGE
pod/nginx-deployment-6f496b94d7-fqphg   1/1     Running   0          13s
pod/nginx-deployment-6f496b94d7-hsc9n   1/1     Running   0          13s
pod/nginx-deployment-6f496b94d7-jvgzq   1/1     Running   0          13s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nginx-deployment   3/3     3            3           14s

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/nginx-deployment-6f496b94d7   3         3         3       14s
```

### Explicación de la salida del comando
La salida del comando `kubectl get all` proporciona un resumen del estado actual de los objetos más comunes dentro del **Namespace** "ejemplos". La información se divide en tres bloques jerárquicos que muestran cómo Kubernetes está gestionando tu aplicación:

### Los Pods (Unidades de Ejecución)
En la parte superior aparecen **3 Pods** individuales.

*   **Nombre:** Observa que todos comienzan por el nombre del Deployment seguido de un hash (`6f496b94d7`) generado por el ReplicaSet y un sufijo aleatorio para cada instancia única.
*   **READY (1/1):** Indica que el contenedor definido en el pod está listo y funcionando correctamente.
*   **STATUS (Running):** Los pods están activos y han sido asignados a un nodo por el **scheduler**.

### El Deployment (Gestor de alto nivel)
El objeto `deployment.apps/nginx-deployment` es el "cerebro" que define el **estado deseado** de la aplicación.

*   **READY (3/3):** Confirma que hay 3 réplicas funcionando de las 3 que se solicitaron en la especificación.
*   **UP-TO-DATE (3):** Indica que las 3 réplicas han sido actualizadas a la última versión de la configuración definida.
*   **AVAILABLE (3):** Muestra cuántas réplicas están actualmente disponibles para los usuarios.

### El ReplicaSet (Controlador de réplicas)
El `replicaset.apps/nginx-deployment-6f496b94d7` es el componente intermedio creado automáticamente por el Deployment.

*   **Su función:** Se encarga específicamente de garantizar que el número exacto de pods coincida con el valor `DESIRED` (3). 
*   Si uno de los pods fallara, este controlador se daría cuenta y ordenaría la creación de uno nuevo para mantener el estado actual coincidente con el deseado.

### Relación entre los elementos
Esta salida ilustra perfectamente la jerarquía de trabajo que hemos estudiado: el **Deployment** gestiona al **ReplicaSet** (identificado por el código `6f496b94d7`), y este a su vez asegura la existencia de los **3 Pods** individuales que ejecutan el servidor NGINX.