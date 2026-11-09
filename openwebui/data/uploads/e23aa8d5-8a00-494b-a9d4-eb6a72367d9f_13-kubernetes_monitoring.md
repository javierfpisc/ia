# Monitorización en Kubernetes
Para esta práctica de monitorización necesitaremos **Helm**, el cual se puede instalar fácilmente con el siguente comando:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```
El comando anterior lo instalaremos en nuestro equipo de despliegue con el usuario de trabajo, o bien directamente en `kuber1`con nuestro usuario NO root.

## Inicialización del entorno y repositorios Helm
Suponiendo que hemos instalado Helm en `kuber1`(nuestro Manager), ejecutamos los siguientes comandos para instruir a Helm sobre el entorno de contexto de kubectl:
```bash
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(whoami):$(whoami) ~/.kube/config
chmod 600 ~/.kube/config
echo 'export KUBECONFIG=$HOME/.kube/config' >> ~/.bashrc
```

Creamos el namespace para nuestro despliegue:
```bash
kubectl create namespace monitoring
```

Añadimos el repositorio de Helm:
```bash
helm repo add prometheus-community \
https://prometheus-community.github.io/helm-charts
helm repo add grafana \
https://grafana.github.io/helm-charts

helm repo update
```

Lo siguiente es la definición del archivo `monitoring-values.yaml` para definir las opciones de configuración del Helm Chart para **Prometheus/Grafana**
```yaml
values.yaml:
grafana:
  adminPassword: admin123

  persistence:
    enabled: true
    storageClassName: ceph-filesystem
    size: 2Gi

  service:
    type: ClusterIP

prometheus:
  prometheusSpec:
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: ceph-filesystem
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 5Gi

    retention: 7d

alertmanager:
  enabled: false

kubeControllerManager:
  enabled: false

kubeScheduler:
  enabled: false

kubeEtcd:
  enabled: false
```
## Instalación de Stack kube-prometheus
Para instalar directamente un Chart podemos usar el comando siguiente (que toma como archivo de parámetros el values.yaml pasado en la opción -f):
```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f monitoring-values.yaml
```
El comando anterior:

* Utiliza el namespace **monitoring** para desplegar los artefactos
* Toma como archivo de valores o parámetros de despliegue **monitoring-values.yaml**.

Podemos descargar un Chart de un repo **sin instalarlo de forma directa**, como con el comando anterior, de este modo obtenemos el Chart en un directorio, dentro del cual poder modificar los archivos pertinentes, como el **values.yaml**. Ejecutaríamos para el Chart anterior el comando:
```bash
helm pull prometheus-community/kube-prometheus-stack --untar
```
La instalación a partir de la copia local sería:
```bash
helm install monitoring ./kube-prometheus-stack \
  -n monitoring \
```
Que tomaría el **values.yaml** dentro del directorio (que habremos posiblemente modificado). Si quiero pasar una copia personalizada de ese archivo podríamos usar la opción **-f**
```bash
helm install monitoring ./kube-prometheus-stack \
  -n monitoring \
  -f monitoring-values.yaml
```
Una vez instalado el Chart, veremos una salida como la siguiente, la cual muestra un resumen del despliegue del Chart y algunos comandos útiles:

<small>
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f monitoring-values.yaml
NAME: monitoring
LAST DEPLOYED: Thu May 21 09:22:23 2026
NAMESPACE: monitoring
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
kube-prometheus-stack has been installed. Check its status by running:
  kubectl --namespace monitoring get pods -l "release=monitoring"

Get Grafana 'admin' user password by running:

  kubectl --namespace monitoring get secrets monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo

Access Grafana local instance:

  export POD_NAME=$(kubectl --namespace monitoring get pod -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=monitoring" -oname)
  kubectl --namespace monitoring port-forward $POD_NAME 3000

Get your grafana admin user password by running:

  kubectl get secret --namespace monitoring -l app.kubernetes.io/component=admin-secret -o jsonpath="{.items[0].data.admin-password}" | base64 --decode ; echo


Visit https://github.com/prometheus-operator/kube-prometheus for instructions on how to create & configure Alertmanager and Prometheus instances using the Operator.
</small>

Para ojear los artefactos creados en el namespace:
```bash
kubectl -n monitoring get all
```
La salida en el estado completo del despliegue mostraría:
Los **Pods**:
```markdown
pod/monitoring-grafana-b797dc946-g6v5h                     3/3     Running   0  46s
pod/monitoring-kube-prometheus-operator-76d8776967-5fr9x   1/1     Running   0  46s
pod/monitoring-kube-state-metrics-676c88cc4-xk8tr          1/1     Running   0  46s
pod/monitoring-prometheus-node-exporter-4ms9d              1/1     Running   0  46s
pod/monitoring-prometheus-node-exporter-bmsmv              1/1     Running   0  46s
pod/monitoring-prometheus-node-exporter-qrzsz              1/1     Running   0  46s
```
Los **Services**:
```markdown
service/monitoring-grafana                     ClusterIP  10.43.78.5     <none>   80/TCP              50s
service/monitoring-kube-prometheus-operator    ClusterIP  10.43.201.26   <none>   443/TCP             50s
service/monitoring-kube-prometheus-prometheus  ClusterIP  10.43.156.67   <none>   9090/TCP,8080/TCP   50s
service/monitoring-kube-state-metrics          ClusterIP  10.43.246.85   <none>   8080/TCP            50s
service/monitoring-prometheus-node-exporter    ClusterIP  10.43.159.111  <none>   9100/TCP            50s
```
Los **DaemonSet**:
```markdown
daemonset.apps/monitoring-prometheus-node-exporter   3   3   3   3   3    kubernetes.io/os=linux   50s
```
Los **Deployment**:
```markdown
deployment.apps/monitoring-grafana                    1/1   1     1     50s
deployment.apps/monitoring-kube-prometheus-operator   1/1   1     1     50s
deployment.apps/monitoring-kube-state-metrics         1/1   1     1     50s
```
Los **ReplicaSet**:
```markdown
replicaset.apps/monitoring-grafana-b797dc946                     1     1     1       50s
replicaset.apps/monitoring-kube-prometheus-operator-76d8776967   1     1     1       50s
replicaset.apps/monitoring-kube-state-metrics-676c88cc4          1     1     1       50s
```

Si por algún motivo (no lo vamos a hacer en principio) necesitamos desinstalar el Chart, procedemos del siguiente modo. En primer lugar obtenemos el nombre del Chart:
```bash
helm list -n monitoring
```
A continuación utilizamos el **name** (monitoring) y ejecutamos:
```bash
helm uninstall -n monitoring monitoring
```
### Ingress para Grafana y Prometheus
Para poder acceder cómodamente a través del navegador a los Services de Prometheus y Grafana creamos en el siguiente archivo, **grafana-prometheus-ingress.yaml**, los objetos Ingress correspondientes:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana
  namespace: monitoring
  annotations:
    cert-manager.io/cluster-issuer: internal-ca-issuer
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - grafanamon.192.168.56.41.nip.io
      secretName: grafana-monitorizacion-tls
  rules:
    - host: grafanamon.192.168.56.41.nip.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: monitoring-grafana
                port:
                  number: 80
                
---

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prometheus
  namespace: monitoring
  annotations:
    cert-manager.io/cluster-issuer: internal-ca-issuer
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - prometheus.192.168.56.41.nip.io
      secretName: prometheus-monitorizacion-tls
  rules:
    - host: prometheus.192.168.56.41.nip.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: monitoring-kube-prometheus-prometheus
                port:
                  number: 9090
```
Los aplicamos:
```bash
 kubectl apply -f grafana-prometheusmonitoring-ingress.yaml 
```

### Dashboards de Grafana
En la sección de Dashboards encontraremos algunos disponibles para activar. También pueden incorporarse, desde la sección **Dashboards->New->Import** algunos ya preconfigurados relacionados con fuentes de análisis ya establecidas en el Stack. Para ello basta con proporcionar el ID del Dashboard y éste se cargará de forma automática. Algunos IDs:

* **Kubernetes cluster monitoring:** ID 315
* **Kubernetes / Compute Resources** ID 11074
* **NodeExporter Full:** ID 1860
* **Traefik:** ID 17346
* **Nginx Exporter**: ID 12708 (Útil para el ejemplo que veremos a continuación)

### Monitorizando métricas de Nginx
Veremos a continuación un ejemplo basado en Nginx para ilustrar la captura de métricas y la recepción de éstas por **Prometheus+Grafama**. Definimos el siguiente stack dentro del archivo **nginx-metrics.yaml**:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: metrics

---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-metrics
  namespace: metrics
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-metrics
  template:
    metadata:
      labels:
        app: nginx-metrics
    spec:
      containers:
      #CONTAINER PRINCIPAL
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        volumeMounts:
        - name: nginx-config
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: default.conf
      #CONTAINER SIDECAR
      - name: nginx-exporter
        image: nginx/nginx-prometheus-exporter:1.4.2
        args:
          - -nginx.scrape-uri=http://127.0.0.1:80/stub_status
        ports:
        - containerPort: 9113
          name: metrics
      volumes:
      - name: nginx-config
        configMap:
          name: nginx-config

---

apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: metrics
data:
  default.conf: |
    server {
      listen 80;
      location / {
        root /usr/share/nginx/html;
        index index.html;
      }
      location /stub_status {
        stub_status;
        allow 127.0.0.1;
        deny all;
      }
    }

---

apiVersion: v1
kind: Service
metadata:
  name: nginx-metrics
  namespace: metrics
  labels:
    app: nginx-metrics
spec:
  selector:
    app: nginx-metrics
  ports:
    - name: metrics
      port: 9113
      targetPort: metrics
```

Resumidamente, lo anterior:

Utiliza un **Deployment** con el **patrón Sidecar** para extraer métricas de un servidor NGINX y exponerlas hacia Prometheus. A continuación, se resumen los componentes clave del archivo proporcionado:

### Espacio de Trabajo (Namespace)
**`kind: Namespace`**: Se crea un entorno aislado denominado `metrics` para organizar todos los recursos relacionados con la monitorización de este ejercicio.

### Configuración del Servidor (ConfigMap)

*   **`kind: ConfigMap`**: Define el archivo `default.conf` para NGINX.
*   **Punto clave**: Habilita el módulo `stub_status` en la ruta `/stub_status`. Esta es la fuente de datos interna que permite ver estadísticas básicas de NGINX (conexiones activas, aceptadas, etc.), restringiendo el acceso únicamente a `127.0.0.1` por seguridad.

### El Pod con Patrón Sidecar (Deployment)
El recurso **Deployment** gestiona un Pod que contiene dos contenedores que comparten red y volúmenes:

*   **Contenedor Principal (`nginx`)**: Ejecuta el servidor web estándar. Monta la configuración personalizada desde el ConfigMap para activar el endpoint de métricas.
*   **Contenedor Sidecar (`nginx-exporter`)**: Actúa como un traductor. Su función es conectarse localmente al NGINX (`http://127.0.0.1:80/stub_status`), recolectar las métricas crudas y transformarlas al formato que entiende Prometheus.
*   **Puerto de Métricas**: El sidecar expone estas métricas procesadas en el puerto **9113**.

### Exposición de Métricas (Service)
A través de este **Service** accedemos a las métricas del Pod (generadas por el container sidecar):

*   **`kind: Service`**: Este recurso actúa como la puerta de enlace interna dentro del clúster.
*   **Función**: Apunta al puerto **9113** (nombrado `metrics`) del Pod. Su objetivo es proporcionar un punto único y estable para que Prometheus pueda recolectar los datos (scrape) de forma organizada.

### Resumen del Flujo

1.  **NGINX** genera estadísticas internas en el puerto 80.
2.  El **Exporter (Sidecar)** las lee vía localhost, las traduce y las publica en el puerto 9113.
3.  El **Service** ofrece ese puerto 9113 a la infraestructura de monitorización (Prometheus) para su análisis y posterior visualización en **Grafana**.

A continuación crearemos el componente que conecta el stack Prometheus con el Servicio a monitorizar, para ello definimos un **ServiceMonitor** en el namespace de monitorización a partir del siguiente archivo **nginx-monitoring-sm.yaml** 
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nginx-metrics
  namespace: monitoring
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: nginx-metrics
  namespaceSelector:
    matchNames:
      - metrics
  endpoints:
    - port: metrics
      interval: 15s
      path: /metrics
```
!!! important "ACLARACIÓN"
    Un **ServiceMonitor** es un recurso personalizado (CRD) del stack de Prometheus que define de forma declarativa cómo deben descubrirse y recolectar las métricas de un conjunto de Pods a través de un **Service**. Su función principal es automatizar el proceso de *scraping* basándose en etiquetas (labels), permitiendo que Prometheus configure automáticamente los objetivos de monitorización sin intervención manual en su archivo de configuración.

El extracto anterior define un **ServiceMonitor**, que es el recurso encargado de decirle a Prometheus exactamente a qué **Service** debe "escuchar" para recoger métricas. Como hemos visto es el puente entre el exportador que desplegamos antes y el sistema de monitorización central. Los aspectos de su definición son los que siguen:

### Etiquetas de Selección (`metadata.labels`)
**release:** `monitoring`: Es fundamental. Prometheus suele estar configurado para buscar únicamente los `ServiceMonitors` que tengan una etiqueta específica (en este caso, la que suele poner Helm al instalar el stack). Si esta etiqueta no coincide con lo que busca Prometheus, ignorará el recurso.

### Selección del Objetivo (`spec.selector`)
**matchLabels:** `app: nginx-metrics`: Aquí es donde ocurre la magia. El `ServiceMonitor` busca en el clúster cualquier **Service** que tenga la etiqueta `app: nginx-metrics`. No apunta directamente a los Pods, sino al Service que los agrupa.

### Filtro de Namespace (`spec.namespaceSelector`)
**matchNames:** `- metrics`: Por seguridad y orden, le indicamos que solo busque el servicio dentro del namespace `metrics` que creamos en el paso anterior. Esto evita que Prometheus intente recoger métricas de otros servicios con nombres similares en otros proyectos.

### Configuración del "Scraping" (`spec.endpoints`)
Aquí definimos el **cómo** recoger los datos:

*   **`port: metrics`**: No usamos un número de puerto (como 9113), sino el **nombre** que le dimos al puerto en la definición del Service.
*   **`interval: 15s`**: Es la frecuencia. Prometheus preguntará por nuevos datos cada 15 segundos.
*   **`path: /metrics`**: Es la ruta URL donde el `nginx-exporter` (el sidecar) publica la información traducida.

**En resumen:** Si el **Deployment** es el que genera la información y el **Service** es la puerta de acceso, el **ServiceMonitor** es la "orden de trabajo" que le entregamos a Prometheus para que sepa que debe pasar por esa puerta cada 15 segundos a recoger los datos.

Una vez desplegados los artefactos de ambos archivos:
```bash
 kubectl apply -f nginx-metrics.yaml
 kubectl apply -f nginx-monitoring-sm.yaml
```
Podremos comprobar desde la interfaz de Prometheus `https://prometheus.192.168.56.41.nip.io`, en la sección **Targets** la presencia del **ServiceMonitor** creado para la ocasión.
Desde la sección **Query** de Prometheus podremos lanzar consultas en relación a las métricas enviadas por nginx, por ejemplo:

* nginx_connections_active
* rate(nginx_http_requests_total[1m])
* nginx_http_requests_total
* etc.


## Instalación de Stack Loki
En una práctica anterior vimos como gestionar logs de una app o servicio mediante un container **sidecar** dentro de un Pod corriendo Fluent. La idea era que ese container recopile los logs generados por "otro" container dentro del Pod y los envíe a algún stack de recepción, por lo general corriendo **Loki**.
A continuación se ilustra un sencillo procedimiento con **Helm** para la instalación de un stack de recepción de logs en kubernetes basado en Loki.
```bash
helm install loki grafana/loki-stack -n monitoring --set grafana.enabled=false
```

