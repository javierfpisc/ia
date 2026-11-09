# Services en Kubernetes

Un **Service** en Kubernetes es la pieza que otorga una **identidad de red estable** a un conjunto de Pods. Dado que los Pods son efímeros y sus direcciones IP cambian constantemente, el Service actúa como un punto de entrada fijo y un balanceador de carga interno.

A continuación, desglosamos el descriptor YAML dado en el archivo `service-1.yaml` para entender su funcionamiento y su relación con el despliegue anterior. Creamos el archivo `service-1.yaml` con el contenido:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  # Importante: mismo namespace que el Deployment
  namespace: ejemplos
  labels:
    app: nginx
    entorno: laboratorio
spec:
  # Tipo de servicio: expone el servicio fuera del clúster
  type: NodePort
  # Selector: conecta el Service con los Pods del Deployment
  selector:
    app: nginx
  ports:
    # Puerto interno del Service (ClusterIP)
    - name: http
      port: 80
      # Puerto del contenedor (Pod)
      targetPort: 80
      # Puerto expuesto en cada nodo del clúster
      nodePort: 30080
```

Creamos el archivo dentro del nodo Manager `kuber1` y lo aplicamos con kubectl:
```bash
kubectl apply -f service-nginx.yaml
```
Para ver los elementos creados asociados al **Service**
```bash
kubectl get services -n ejemplos
```
El resultado sería algo así:
```
NAME            TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)        AGE
nginx-service   NodePort   10.43.154.33   <none>        80:30080/TCP   95s
```
La salida anterior muestra el Service creado: se llama `nginx-service`, es de tipo `NodePort` (permite acceso desde fuera del clúster a través de un puerto de cualquier nodo), tiene una `CLUSTER-IP` interna (`10.43.154.33`) que se usa para la comunicación dentro del clúster entre Pods y otros recursos, no tiene `EXTERNAL-IP` porque no se ha configurado un balanceador externo, y en `PORT(S)` se indica la traducción de puertos donde el Service escucha, en el puerto 80 internamente, y lo expone en el puerto 30080 hacia fuera del clúster, de forma que cualquier acceso a `IP_del_nodo:30080` será redirigido automáticamente hacia los Pods del Deployment de Nginx que coincidan con las labels del selector del Service.
En resumen, este Service actúa como un punto de acceso estable que se mantiene aunque los Pods cambien, se eliminen o se creen nuevos.

---

## Análisis del Descriptor YAML Punto por Punto

Basándonos en el archivo `service_1`:

*   **`apiVersion: v1`**: Indica la versión de la API. Los Services pertenecen al núcleo de Kubernetes, por lo que usan la versión estable `v1`.
*   **`kind: Service`**: Define que este objeto es un Servicio de red.
*   **`metadata`**:
    *   **`name: nginx-service`**: El nombre único del servicio. Este nombre se convertirá en un registro DNS dentro del clúster (permitiendo que otros Pods lo contacten simplemente usando `nginx-service`).
    *   **`namespace: ejemplos`**: **Crucial.** El Service debe estar en el mismo Namespace que el Deployment para poder "ver" y conectar con sus Pods.
*   **`spec` (Especificación)**:
    *   **`type: NodePort`**: Define cómo se expone el servicio. El tipo `NodePort` permite que la aplicación sea accesible desde fuera del clúster.
    *   **`selector` (`app: nginx`)**: Es el filtro que utiliza el Service para encontrar a sus Pods. Solo enviará tráfico a los Pods que tengan exactamente esa etiqueta.
    *   **`ports`**:
        *  **`name: http`**: Es un nombre identificativo para el puerto. Aunque es opcional en servicios de un solo puerto, es una **buena práctica**. Permite que otros recursos se refieran a este puerto por su nombre en lugar de por su número, lo cual es muy útil si en el futuro decides cambiar el puerto 80 por otro sin tener que actualizar todos los descriptores que lo referencian.
        *  **`port: 80`**: (Puerto del Service / ClusterIP). Es el puerto en el que el **Service** escucha dentro del clúster. Cuando un Pod del clúster quiera hablar con el servicio `nginx-service`, enviará el tráfico a su `ClusterIP` a través de este puerto 80. Este es el puerto "interno" de la IP virtual del servicio.
        *  **`targetPort: 80`**: (Puerto del Contenedor). Es el puerto en el que la aplicación (el contenedor NGINX) está realmente escuchando. Este valor debe coincidir exactamente con el `containerPort` definido en la plantilla del **Pod** del Deployment. El Service recibe el tráfico en su `port` (80) y lo redirige hacia el `targetPort` (80) de uno de los Pods que haya seleccionado mediante las etiquetas.
        *  **`nodePort: 30080`** (Puerto Externo). Es el puerto que se abre en **todos los nodos** del clúster (Manager y Workers) para permitir el acceso desde fuera. Kubernetes reserva por defecto el rango **30000-32767** para este propósito. Al haber fijado `30080`, cualquier persona que tenga acceso a la red de los nodos puede ver la aplicación NGINX simplemente apuntando a la IP de cualquier nodo en ese puerto.

---

## El "Enlace" mediante Etiquetas (Labels)

La interacción entre el **Service** y el **Deployment** no es por nombre, sino por **etiquetas**:

1.  En el `nginx-deployment`, definimos que los Pods tendrían la etiqueta `app: nginx`.
2.  En el `nginx-service`, definimos un **selector** con el valor `app: nginx`.

**Resultado:** El Service monitoriza constantemente el API Server buscando Pods con esa etiqueta. Cuando encuentra uno (sin importar en qué nodo esté), lo añade a su lista de "Endpoints" para enviarle tráfico. Si un Pod muere y el Deployment crea otro, el Service lo detectará por su etiqueta y lo enlazará automáticamente.

---

## Relación entre NodePort y ClusterIP

Es fundamental entender que los tipos de servicios en Kubernetes son jerárquicos:

*   **ClusterIP**: Es el tipo por defecto. Crea una IP virtual interna **solo accesible desde dentro del clúster**. Proporciona balanceo de carga entre los Pods para el tráfico interno.
*   **NodePort**: Es una capa superior. Al declarar un servicio como `NodePort`, Kubernetes realiza dos acciones:
    1.  Crea automáticamente un **ClusterIP** interno para el balanceo básico.
    2.  Reserva un puerto (por defecto entre 30000-32767) en **todos los nodos del clúster** (Manager y Workers).

**La diferencia clave:** Mientras que el `ClusterIP` proporciona una dirección privada para que los componentes internos de tu aplicación se encuentren y hablen entre sí sin salir del clúster, el `NodePort` abre una vía de acceso para que un usuario externo (como tú desde tu navegador) llegue a la aplicación utilizando la dirección IP física de cualquiera de los servidores (nodos). De este modo tenemos dos puntos de vista:

1.  **Tráfico Interno (ClusterIP):** Hay servicios que **no deben verse desde internet** por seguridad (como una base de datos, un sistema de procesamiento de logs o una API privada). Estos usan ClusterIP para que solo otros Pods del clúster puedan contactarlos.
2.  **Tráfico Externo (NodePort):** Solo los servicios que el usuario final necesita tocar (como la web principal o el panel de control) deben exponerse hacia afuera mediante NodePort.

De esta forma, Kubernetes permite que la infraestructura sea **segura por defecto**, dejando lo sensible en el interior (ClusterIP) y solo abriendo puertos específicos para lo que realmente debe ser público (NodePort).

---

## Cómo Acceder al Servicio

Al haber configurado el tipo `NodePort`, el tráfico sigue este camino:

`Usuario -> IP del Nodo:Puerto NodePort -> ClusterIP -> Pod de NGINX`.

### Elementos implicados

1.  **Entrada externa:** El usuario accede a `http://<IP_Nodo_Worker>:30080`.
2.  **Tránsito al Service:** El nodo recibe la petición en el **nodePort** (30080) y la redirige internamente al **port** (80) de la IP virtual del Service (ClusterIP).
3.  **Entrega final:** El Service, actuando como balanceador, elige un Pod saludable y entrega el paquete en el **targetPort** (80) del contenedor.

### Comprobar elementos

1.  **Identificar el puerto:** Tras aplicar el YAML, ejecuta `kubectl get svc -n ejemplos`. Verás algo como `80:30080/TCP`. Ese número de 5 cifras es el `NodePort`.
2.  **Identificar la IP:** Puedes usar la IP del nodo **Manager** o de cualquiera de los **Workers**.
3.  **Acceso:** Abre el navegador y escribe:
    `http://192.168.56.41:30080`
    Verás como responde la página de bienvenida de nginx **Welcome to nginx**.

Gracias al componente **kube-proxy** que corre en cada nodo, el tráfico será redirigido correctamente a uno de los 3 Pods de NGINX, independientemente de en qué nodo físico esté corriendo el Pod realmente.

## Resumen

| Concepto | Ubicación | Visibilidad |
| :--- | :--- | :--- |
| **nodePort** | Interfaz física del Nodo | Externa (Navegador del alumno) |
| **port** | Interfaz virtual del Service | Interna (Solo dentro del clúster) |
| **targetPort** | Interfaz del Contenedor | Aplicación (Donde corre NGINX) |

Esta estructura permite una gran flexibilidad: podrías tener un servicio escuchando externamente en el puerto `30080`, que internamente se llama por el puerto `80`, pero que entrega el tráfico a una aplicación que realmente corre en el puerto `8080`, todo ello de forma transparente para el usuario final.