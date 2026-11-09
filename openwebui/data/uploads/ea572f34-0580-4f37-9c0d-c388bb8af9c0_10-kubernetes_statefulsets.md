# StatefulSet: `mariadb-statefulset`

## Despliegue de MariaDB utilizando un StatefulSet
Creamos el archivo `mariadb-statefulset.yaml` con el siguiente contenido:
```yaml
# =========================================================
# HEADLESS SERVICE
# Necesario para StatefulSets
# Da identidad de red estable a cada Pod
# =========================================================
apiVersion: v1
kind: Service
metadata:
  name: mariadb-headless
  namespace: ejemplos
  labels:
    app: mariadb
spec:
  clusterIP: None
  selector:
    app: mariadb
  ports:
    - port: 3306
      name: mysql
---
# =========================================================
# SERVICE NORMAL
# Punto de acceso estable para clientes
# =========================================================
apiVersion: v1
kind: Service
metadata:
  name: mariadb-service
  namespace: ejemplos
  labels:
    app: mariadb
spec:
  type: ClusterIP
  selector:
    app: mariadb
  ports:
    - port: 3306
      targetPort: 3306
      name: mysql
---
# =========================================================
# SECRET
# Contraseña de MariaDB
# =========================================================
apiVersion: v1
kind: Secret
metadata:
  name: mariadb-secret
  namespace: ejemplos
type: Opaque
stringData:
  MYSQL_ROOT_PASSWORD: superpassword
---
# =========================================================
# STATEFULSET
# Base de datos MariaDB con almacenamiento persistente
# =========================================================
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mariadb
  namespace: ejemplos
spec:
  # Nombre del Headless Service
  serviceName: mariadb-headless
  # Número de réplicas
  replicas: 1
  selector:
    matchLabels:
      app: mariadb
  template:
    metadata:
      labels:
        app: mariadb
    spec:
      containers:
        - name: mariadb
          image: mariadb:11
          ports:
            - containerPort: 3306
              name: mysql
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mariadb-secret
                  key: MYSQL_ROOT_PASSWORD
          volumeMounts:
            # Punto donde MariaDB guarda datos
            - name: mariadb-data
              mountPath: /var/lib/mysql
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
  # =========================================================
  # VOLUME CLAIM TEMPLATE
  # Cada réplica tendrá su propio PVC
  # =========================================================
  volumeClaimTemplates:
    - metadata:
        name: mariadb-data
      spec:
        accessModes:
          - ReadWriteMany
        storageClassName: ceph-filesystem
        resources:
          requests:
            storage: 5Gi
```

Lo desplegamos desde `kuber1`:
```bash
kubectl apply -f mariadb-statefulset.yaml
```
Vemos el PVC (Physical Volume Claim):
```bash
kubectl get pvc -n ejemplos
```
Mostraría algo como lo siguiente:
```
NAME                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      VOLUMEATTRIBUTESCLASS   AGE
mariadb-data-mariadb-0   Bound    pvc-90f31646-beaf-439a-a7bd-b697d0dcac91   5Gi        RWX            ceph-filesystem   <unset>                 64s
```
Vemos el PV (Physical Volume):
```bash
kubectl get pv -n ejemplos
```
Mostraría:
```
NAME                                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                             STORAGECLASS      VOLUMEATTRIBUTESCLASS   REASON   AGE
pvc-90f31646-beaf-439a-a7bd-b697d0dcac91   5Gi        RWX            Delete           Bound    ejemplos/mariadb-data-mariadb-0   ceph-filesystem   <unset>                          108s
```

### Explicación
Este archivo YAML describe una implementación completa de una base de datos **MariaDB** utilizando un **StatefulSet**. A diferencia de los Deployments convencionales, este recurso está diseñado específicamente para aplicaciones que requieren una **identidad persistente** y un **almacenamiento estable**.

A continuación, se detalla cada uno de los componentes y su función dentro del entorno:

---

#### Headless Service (`mariadb-headless`)
Este servicio es fundamental para el funcionamiento del StatefulSet.

*   **`clusterIP: None`**: Al establecer la IP del clúster como `None`, creamos un **Headless Service**.
*   **Función**: En lugar de actuar como un balanceador de carga con una única IP virtual, este servicio permite que el DNS de Kubernetes devuelva directamente las direcciones IP de los Pods individuales. Esto proporciona una **identidad de red estable** (ej: `mariadb-0.mariadb-headless`), permitiendo que cada réplica de la base de datos sea direccionable de forma única.

#### Service Normal (`mariadb-service`)

*   **`type: ClusterIP`**: A diferencia del anterior, este es un servicio estándar con una IP virtual interna.
*   **Función**: Sirve como el **punto de acceso estable** para que otras aplicaciones dentro del clúster (como un backend) se conecten a la base de datos sin preocuparse por cuál es el Pod específico que está respondiendo.

#### Secret (`mariadb-secret`)

*   **`type: Opaque`**: Es el tipo por defecto para datos genéricos.
*   **`stringData`**: Permite definir los datos sensibles en texto plano dentro del YAML (Kubernetes los codificará automáticamente en Base64 al procesarlos).
*   **Función**: Almacena de forma segura la **contraseña del usuario root** de MariaDB, evitando que esté escrita directamente en la especificación del contenedor.

#### StatefulSet (`mariadb`)
Este es el artefacto que orquesta la ejecución de la base de datos.

*   **`serviceName: "mariadb-headless"`**: Vincula el StatefulSet con el servicio headless creado anteriormente para gestionar las identidades de red de los Pods.
*   **`replicas: 1`**: Define cuántas instancias de la base de datos queremos ejecutar.
*   **`template`**: Define la plantilla del Pod.
    *   **`env` (`valueFrom`)**: Inyecta la contraseña desde el **Secret** mencionado anteriormente en la variable de entorno `MYSQL_ROOT_PASSWORD` que espera el contenedor.
    *   **`volumeMounts`**: Indica que el volumen llamado `mariadb-data` se montará en la ruta `/var/lib/mysql`, que es donde MariaDB almacena físicamente sus bases de datos.
    *   **`resources` (Requests y Limits)**: Establece los recursos de **CPU y Memoria** garantizados (`requests`) y el máximo que puede consumir (`limits`) para asegurar la estabilidad del nodo worker.

#### Volume Claim Template (`volumeClaimTemplates`)
Esta es la sección más crítica para la persistencia en aplicaciones con estado.

*   **Diferencia clave**: A diferencia de un Deployment (donde todos los Pods suelen compartir el mismo volumen), el `volumeClaimTemplates` asegura que **cada réplica del StatefulSet reciba su propio PersistentVolumeClaim (PVC)** independiente.
*   **`accessModes: ReadWriteMany`**: Permite que el volumen sea montado en modo lectura/escritura por varios nodos simultáneamente (característica soportada por vuestro sistema **CephFS**).
*   **`storageClassName: ceph-filesystem`**: Indica que Kubernetes debe hablar con el orquestador de almacenamiento (Ceph) para **aprovisionar dinámicamente** un volumen de 5Gi de forma automática.

---

#### Resumen de funcionamiento

En este escenario, si el Pod de MariaDB se detiene o se mueve de un nodo worker a otro:
1.  **Mantiene su nombre**: Seguirá llamándose `mariadb-0`.
2.  **Mantiene sus datos**: Kubernetes volverá a conectar automáticamente el mismo volumen de **CephFS** al nuevo Pod, asegurando que la base de datos no pierda información.
3.  **Mantiene su acceso**: Los clientes seguirán conectándose a través de `mariadb-service` de forma transparente.

## Añadiendo interfaz de gestión phpmyadmin

Creamos el archivo `phpmyadmin.yaml` con el siguiente contenido:
```yaml
# =========================================================
# DEPLOYMENT PHPMYADMIN
# Cliente web para MariaDB
# =========================================================
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phpmyadmin
  namespace: ejemplos
spec:
  replicas: 1
  selector:
    matchLabels:
      app: phpmyadmin
  template:
    metadata:
      labels:
        app: phpmyadmin
    spec:
      containers:
        - name: phpmyadmin
          image: phpmyadmin:latest
          ports:
            - containerPort: 80
          env:
            # Service interno de MariaDB
            - name: PMA_HOST
              value: mariadb-service
            - name: PMA_PORT
              value: "3306"
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "250m"
---
# =========================================================
# SERVICE PHPMYADMIN
# =========================================================
apiVersion: v1
kind: Service
metadata:
  name: phpmyadmin-service
  namespace: ejemplos
spec:
  type: ClusterIP
  selector:
    app: phpmyadmin
  ports:
    - port: 80
      targetPort: 80
---
# =========================================================
# INGRESS HTTPS
# Exposición mediante Traefik
# =========================================================
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: phpmyadmin-ingress
  namespace: ejemplos
  annotations:
    cert-manager.io/cluster-issuer: internal-ca-issuer
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - phpmyadmin.192.168.56.41.nip.io
      secretName: phpmyadmin-tls
  rules:
    - host: phpmyadmin.192.168.56.41.nip.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: phpmyadmin-service
                port:
                  number: 80
```
Lo desplegamos desde `kuber1`:
```bash
kubectl apply -f phpmyadmin.yaml
```
Ahora ejecutamos el comando siguiente, para recuperar todos los artefactos del namespace:
```bash
kubectl -n ejemplos get all
```

### Explicación
Este nuevo conjunto de artefactos completa el escenario de base de datos permitiendo gestionar **MariaDB** a través de una interfaz web. En este caso, **phpMyAdmin** actúa como un cliente que se comunica con el servicio de base de datos que creamos anteriormente.

A continuación, se detallan los apartados del archivo YAML siguiendo el estilo pedagógico de los materiales anteriores:

---

#### Deployment: La aplicación phpMyAdmin
Este recurso gestiona el ciclo de vida del contenedor de phpMyAdmin.

*   **`replicas: 1`**: Al ser una herramienta de administración, normalmente una sola instancia es suficiente para vuestro laboratorio.
*   **`env` (Variables de Entorno)**: Es la parte más importante de la configuración para la conectividad:
    *   **`PMA_HOST: mariadb-service`**: Aquí es donde ocurre la "magia" del DNS interno de Kubernetes. Le decimos a phpMyAdmin que su base de datos está en el host `mariadb-service`. Kubernetes resolverá automáticamente ese nombre a la IP interna del servicio MariaDB que definimos en el paso anterior.
    *   **`PMA_PORT: "3306"`**: El puerto estándar de comunicación de MariaDB.
*   **`resources`**: Define los límites de consumo. Es una buena práctica para evitar que un proceso web sature los nodos worker del clúster.

#### Service: Comunicación Interna

*   **`type: ClusterIP`**: A diferencia del NGINX que expusimos mediante `NodePort`, aquí usamos un servicio puramente **interno**.
*   **¿Por qué ClusterIP?**: Porque no necesitamos abrir un puerto manual en cada nodo; en su lugar, vamos a utilizar el **Ingress** para gestionar la entrada desde el exterior de forma mucho más elegante y segura.

#### Ingress: Acceso Web y Seguridad HTTPS
Este objeto es el que configura a **Traefik** para que deje pasar el tráfico desde vuestro navegador hacia el pod de phpMyAdmin.

*   **`annotations`**:
    *   **`cert-manager.io/cluster-issuer`**: Le pide al componente `cert-manager` que emita un certificado de seguridad automáticamente usando el emisor que configuramos anteriormente.
    *   **`traefik...websecure`**: Indica a Traefik que este sitio debe estar disponible de forma segura (HTTPS).
*   **`tls`**:
    *   **`hosts`**: Define para qué dominio se cifra el tráfico.
    *   **`secretName: phpmyadmin-tls`**: Es el nombre del "baúl" (Secret) donde se guardará el certificado SSL una vez que se genere.
*   **`rules` (`host: phpmyadmin.192.168.56.41.nip.io`)**: 
    *   Utiliza un servicio llamado `nip.io` que es muy útil en laboratorios: convierte una dirección IP en un nombre de dominio funcional sin necesidad de configurar un servidor DNS externo.
*   **`backend`**: Finalmente, redirige todo el tráfico que llega a ese dominio hacia el puerto 80 del `phpmyadmin-service`.

---

### Resumen de la Interacción Completa

1.  **Entrada:** Accedemos por HTTPS a la URL de `phpmyadmin.192.168.56.41.nip.io`.
2.  **Puerta (Ingress):** **Traefik** recibe la petición, usa el certificado SSL guardado en el **Secret** y la envía internamente al **Service** de phpMyAdmin.
3.  **Aplicación (Deployment):** El Pod de **phpMyAdmin** recibe la petición y, para mostrar las tablas, lanza una consulta interna a `mariadb-service`.
4.  **Base de Datos (StatefulSet):** El **Service de MariaDB** recibe la consulta y la entrega al Pod de la base de datos, que tiene sus datos a salvo en el almacenamiento compartido de **CephFS**.

Este esquema ilustra perfectamente una **arquitectura de microservicios** donde cada pieza tiene una responsabilidad única y se comunican de forma segura y organizada.
