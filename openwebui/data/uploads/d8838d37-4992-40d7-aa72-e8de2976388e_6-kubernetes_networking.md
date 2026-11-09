# Networking en Kubernetes: Conectividad y Seguridad

El networking en Kubernetes es uno de los componentes más críticos y, a menudo, el que presenta mayor complejidad inicial. Para un administrador de sistemas, es fundamental entender que Kubernetes impone un modelo de **red plana** donde todos los Pods pueden comunicarse entre sí sin necesidad de NAT, independientemente del nodo en el que se encuentren.

---

## El Modelo de Red y la Interconexión de Nodos
Kubernetes no gestiona la red directamente, sino que define un estándar de conectividad. Para que el clúster funcione, se deben cumplir tres condiciones básicas:

*   Todos los Pods pueden comunicarse con todos los demás Pods sin NAT.
*   Todos los Nodos pueden comunicarse con todos los Pods (y viceversa) sin NAT.
*   La IP que un Pod ve de sí mismo es la misma que los demás ven de él.

## Comunicación entre Nodos: El Corazón del Clúster

En un clúster de Kubernetes, la comunicación entre nodos se divide conceptualmente en dos planos: el **Plano de Control** (comunicación administrativa) y el **Plano de Datos** (tráfico de las aplicaciones).

### Comunicación con el Plano de Control
Todos los nodos deben comunicarse con el **kube-apiserver**, que actúa como el único punto de entrada al plano de control. 

*   **De los Nodos al Plano de Control:** El agente **kubelet**, que corre en cada nodo worker, se conecta al API Server para recibir instrucciones sobre qué Pods ejecutar y para informar sobre el estado del nodo. Esta comunicación está protegida mediante certificados **PKI** y TLS para asegurar que solo nodos autorizados se unan al clúster.
*   **Del Plano de Control a los Nodos:** El API Server puede iniciar conexiones con los nodos para tareas como obtener logs de los contenedores o ejecutar comandos (`kubectl exec`).

### Comunicación Nodo a Nodo (Data Plane)
Para que las aplicaciones funcionen, Kubernetes exige que cualquier Pod pueda comunicarse con otro Pod en un nodo diferente sin necesidad de traducir direcciones de red (NAT). Esto se logra mediante:

*   **Kube-proxy:** Este componente corre en cada nodo y es responsable de mantener las reglas de red (usualmente mediante iptables o IPVS). Su función es asegurar que, cuando un paquete va dirigido a un **Service**, este se redirija correctamente a uno de los Pods que lo respaldan, sin importar en qué nodo físico se encuentren.
*   **El Rol del CNI (como Calico):** Como Kubernetes no crea las interfaces de red de los contenedores, utiliza el **Container Network Interface (CNI)**. En nuestro laboratorio con **Calico**, este se encarga de crear una "red superpuesta" (overlay) o usar enrutamiento directo para que el tráfico viaje de un nodo a otro de forma transparente.

## ¿Qué es el CNI (Container Network Interface)?

Dado que Kubernetes delega la implementación de la red, utiliza el estándar **CNI**. Un CNI es un plugin que se encarga de:
1.  Asignar direcciones IP a los Pods.
2.  Configurar las interfaces de red en los contenedores.
3.  Asegurar que el tráfico fluya correctamente entre los nodos del clúster.

En nuestro clúster de laboratorio, utilizaremos **Calico** como CNI. Calico es muy popular porque utiliza protocolos de enrutamiento estándar (como BGP) para interconectar los nodos de forma eficiente.

---

## Network Policies: El Firewall de los Pods
Por defecto, en Kubernetes todo el tráfico está permitido. Las **Network Policies** son objetos de la API que permiten controlar el flujo de tráfico a nivel de IP o puerto (Capas 3 y 4). Las **Network Policies** aseguran que solo el tráfico legítimo fluya entre Pods.

*   **Función:** Actúan como un firewall distribuido. Permiten definir qué Pods pueden hablar con quién, basándose en **Labels** (etiquetas) y selectores.
*   **Implementación:** Es importante saber que las Network Policies son "declaraciones de intención". Para que funcionen, el CNI instalado (como **Calico**) debe ser capaz de interpretarlas y aplicar las reglas de filtrado.
*   **Uso común:** Aislar entornos (ej: que los Pods del Namespace "desarrollo" no hablen con "producción") o proteger bases de datos permitiendo solo tráfico desde el backend.

### Plugins de Red (CNI) y Calico
El plugin CNI es el software que realmente conecta los contenedores a la red del host. Construye los "túneles" o rutas para que los nodos se comuniquen.

*   **Funciones del CNI:** Asigna direcciones IP únicas a cada Pod (IPAM) y configura el enrutamiento para que los paquetes salgan del nodo hacia el destino correcto.
*   **Network Policies con Calico:** Kubernetes permite definir **Network Policies** para controlar qué flujos de tráfico están permitidos entre Pods. Calico no solo interconecta los nodos, sino que actúa como el "brazo ejecutor" de estas políticas, filtrando el tráfico a nivel de host para garantizar que, por ejemplo, un Pod de base de datos solo acepte conexiones de su backend autorizado.

---

## Comunicación entre Servicios: El Recurso "Service"
Debido a que los Pods son efímeros y sus IPs cambian, Kubernetes utiliza los **Services** para proporcionar estabilidad. Si un Pod muere y se recrea, su dirección IP cambia. Para que una aplicación pueda encontrar a otra de forma estable, usamos el objeto **Service**. Los **Services** dan una identidad fija a las aplicaciones, independiente de los Pods.

Un Service proporciona una **IP virtual estática** (ClusterIP) y un nombre DNS único que redirige el tráfico hacia un conjunto de Pods.

### Tipos de Service principales:

1.  **ClusterIP (Por defecto):** El servicio solo es accesible desde **dentro del clúster**. Es ideal para comunicación interna entre microservicios. Proporciona una IP estable accesible solo internamente.
2.  **NodePort:** Expone el servicio en un puerto estático (rango 30000-32767) en **cada IP de los nodos** del clúster. Permite el acceso externo rudimentario enviando tráfico a `IP_del_Nodo:Puerto`. Por tanto, abre un puerto específico en todos los nodos (Manager y Workers), permitiendo acceso externo a través de la IP de cualquier nodo.
3.  **LoadBalancer:** Crea un balanceador de carga externo (típicamente en nubes públicas como AWS o Azure) que redirige el tráfico hacia el servicio dentro del clúster. Se puede integrar con proveedores de nube para exponer el servicio mediante un balanceador externo.

---

## Acceso Externo: Ingress e Ingress Controllers
Mientras que un Service de tipo LoadBalancer o NodePort trabaja a nivel de transporte (TCP/UDP), el **Ingress** gestiona el acceso a nivel de aplicación (HTTP/HTTPS). Permite usar nombres de dominio y rutas (ej: `empresa.com/api`) para dirigir el tráfico a distintos servicios internos, optimizando el uso de IPs públicas. Los objetos **Ingress** serán la puerta de entrada principal para vuestros usuarios finales a través de la web.

*   **Ingress:** Es una colección de reglas que permiten que el tráfico externo llegue a los servicios del clúster. Permite configurar cosas como **nombres de dominio** (ej: `api.miapp.com`), rutas URL y terminación SSL/TLS.
*   **Ingress Controller:** Kubernetes no trae un controlador de Ingress por defecto. Se debe instalar uno (como NGINX Ingress Controller o HAProxy) para que lea las reglas del objeto Ingress y gestione el tráfico entrante.

### Ingress Controller. Traefik
Traefik es un **proxy inverso y balanceador de carga** moderno y nativo de la nube. En Kubernetes, funciona como un **Ingress Controller**, lo que significa que "escucha" continuamente al API Server de Kubernetes.

!!! important "NOTA"
    En nuestra implementación de kubernetes para laboratorio, basada en k3s, Traefik ya viene instalado por defecto como Ingress Controller.

Cuando publicas un nuevo objeto de tipo `Ingress` con reglas para un dominio (ej: `app.midominio.com`), Traefik detecta el cambio instantáneamente y auto-configura sus rutas internas sin necesidad de reiniciar el servicio ni recargar archivos de configuración manuales.

#### Factores Clave de Traefik
Aunque la documentación oficial de Kubernetes se centra en los conceptos generales de Ingress, Traefik destaca en entornos educativos y profesionales por lo siguiente:

*   **Descubrimiento Automático:** Traefik analiza los servicios y pods de tu clúster y crea las rutas necesarias basándose en etiquetas (annotations) y objetos Ingress.
*   **Soporte de protocolos:** Maneja nativamente HTTP/HTTPS, pero también TCP y UDP, lo cual es útil si en el futuro desplegáis servicios que no sean web.
*   **Dashboard Nativo:** Ofrece una interfaz visual (muy útil para alumnos) donde se pueden ver en tiempo real los "Routers", "Middlewares" y "Services" configurados.
*   **Gestión de Certificados:** Se integra muy bien con Let's Encrypt para gestionar certificados SSL/TLS de forma automática.

#### Cómo se utiliza en el clúster (Flujo de trabajo)
Para utilizar Traefik en nuestro clúster de 3 nodos, el flujo suele ser el siguiente:

1.  **Despliegue del Controlador:** Se instala Traefik normalmente mediante un `Deployment` o un `DaemonSet`. 
    *   *Nota:* Como administrador, puedes exponer Traefik hacia el exterior usando un `Service` de tipo **NodePort** (mapeando el puerto 80 del clúster a un puerto como el 30080 en los nodos) o, si tuvieras un balanceador externo, de tipo **LoadBalancer**.
2.  **Configuración de Reglas (Ingress):** No se configura Traefik directamente. En su lugar, se crea un manifiesto YAML de tipo `Ingress` donde define el host y el servicio de destino.
3.  **Procesamiento:** Traefik lee ese manifiesto del API Server y empieza a dirigir el tráfico que llega a la IP de vuestros nodos hacia los Pods correspondientes.

#### Relación con los otros componentes de la red
En nuestro laboratorio:

*   **Calico:** Se encarga de que Traefik pueda "llegar" a los Pods de los servicios en cualquier nodo.
*   **CephFS:** Podríais usarlo para que Traefik guarde de forma persistente los certificados SSL generados, asegurando que si el pod de Traefik se mueve de nodo, no pierda la información.

Es importante mencionar que, aunque la documentación habla de los objetos `Ingress` estándar de Kubernetes, Traefik también utiliza sus propios **Custom Resource Definitions (CRDs)** como el `IngressRoute`. Estos ofrecen funciones más avanzadas que el objeto Ingress estándar, como un control más fino sobre los middlewares (redirecciones, autenticación, etc.), lo cual es una práctica recomendada en despliegues modernos de Traefik.

---