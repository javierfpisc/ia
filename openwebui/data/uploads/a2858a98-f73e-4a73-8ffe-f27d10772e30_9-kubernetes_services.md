# Services en Kubernetes

En Kubernetes, un **Service** es un método abstracto para exponer una aplicación que se ejecuta en un conjunto de **Pods** como un servicio de red. Esta pieza es fundamental porque, como hemos visto, los Pods son efímeros (nacen y mueren con IPs distintas); el Service proporciona la **estabilidad** necesaria para que los microservicios se comuniquen entre sí y con el mundo exterior.

---

## El Concepto: ¿Por qué necesitamos Services?
El problema principal que resuelve un Service es el **descubrimiento de servicios**.

*   **Identidad Fija:** A diferencia de un Pod, un Service recibe una dirección IP estática (llamada **ClusterIP**) y un nombre DNS que no cambian durante la vida del objeto.
*   **Selección Dinámica:** El Service utiliza **Labels (Etiquetas)** y **Selectors** para identificar a qué Pods debe enviar el tráfico. Si un Pod muere y el Deployment crea otro, el Service lo detectará automáticamente gracias a sus etiquetas y lo incluirá en el balanceo de carga.

---

## Tipos de Services y su Jerarquía
Kubernetes ofrece cuatro tipos principales de Service. Es vital entender que estos tipos suelen ser **acumulativos** (uno construye sobre las capacidades del anterior):

### ClusterIP (Por defecto)

*   **Definición:** Expone el servicio en una IP interna del clúster.
*   **Uso:** Comunicación interna entre microservicios (ej: el backend hablando con la base de datos).
*   **Relación:** Es la base de todos los demás servicios.

### NodePort

*   **Definición:** Expone el servicio en un puerto estático en **cada IP de cada Nodo** (Manager y Workers). 
*   **Relación:** Un NodePort **incluye automáticamente un ClusterIP**. El tráfico que llega al puerto del Nodo se redirige al ClusterIP interno.
*   **Uso:** Útil para acceso externo cuando no se tiene un balanceador de carga de nube. En nuestro laboratorio de 3 nodos, este será un método común para probar aplicaciones desde el navegador usando `http://IP_Worker:Puerto`.

### LoadBalancer

*   **Definición:** Utiliza el balanceador de carga de un proveedor de nube (como AWS, Azure o GCP) para exponer el servicio externamente.
*   **Relación:** Un LoadBalancer **incluye automáticamente un NodePort** y, por extensión, un ClusterIP.
*   **Uso:** Es el estándar en entornos de producción en la nube para recibir tráfico de internet.

### ExternalName

*   **Definición:** Mapea el servicio a un nombre DNS externo (un CNAME), no a un selector de Pods.
*   **Uso:** Cuando queremos que una aplicación dentro del clúster acceda a un servicio fuera de él (ej: una base de datos externa) usando un nombre local de Kubernetes.

---

## Integración con el Entorno de Kubernetes

El funcionamiento de los Services depende de dos componentes críticos del clúster que trabajan en segundo plano:

1.  **kube-proxy:** Este componente corre en cada nodo y es el encargado de implementar la "magia" de la red. Mapea el tráfico que llega al Service y lo redirige a los Pods correctos mediante reglas de filtrado de paquetes (usualmente `iptables` o `IPVS`).
2.  **DNS de Kubernetes:** El clúster mantiene un servicio de DNS interno (como CoreDNS). Cuando creas un servicio llamado `mi-web`, Kubernetes asigna automáticamente un nombre DNS (`mi-web.default.svc.cluster.local`) para que otros Pods no necesiten conocer la IP del servicio para comunicarse.

---

## Gestión de los Services
La administración se realiza principalmente mediante la herramienta de línea de comandos **kubectl**:

*   **Creación rápida:** Se puede usar `kubectl expose deployment [nombre]` para generar automáticamente un service a partir de un despliegue existente.
*   **Creación específica:** Se utilizan comandos como `kubectl create service clusterip`, `nodeport` o `loadbalancer` seguidos de los parámetros de puerto.
*   **Inspección:** Para ver el estado y las IPs asignadas, se utiliza `kubectl get svc` y `kubectl describe svc [nombre]`.

---

## Aclaraciones Importantes

*   **Separación de Conceptos:** El Service gestiona **cómo se llega** a la aplicación (Red), mientras que el Deployment gestiona **cómo corre** la aplicación (Carga de trabajo).
*   **Puertos:** No confundir el `port` (puerto donde escucha el Service), el `targetPort` (puerto donde escucha el contenedor dentro del Pod) y el `nodePort` (puerto abierto en el host físico).
*   **Endpoints:** Si un Service no funciona, lo primero que debe revisar un administrador son los **Endpoints**. Los Endpoints son la lista de IPs de Pods que el Service ha detectado como "saludables". Si la lista está vacía, probablemente los **Selectors** (etiquetas) están mal configurados.