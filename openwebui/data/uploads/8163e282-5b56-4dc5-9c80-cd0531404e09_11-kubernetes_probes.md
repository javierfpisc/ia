# Despliegue con Health Checks (Probes)
En esta práctica partiremos de un deployment para ilustrar el uso y aplicación de los **Probes** (sondas) en kubernetes. Partiremos de un archivo `nginx-probes.yaml` que define un **Ceployment** al que aplicaremos distintos tipos de **Probes**. El contenido del archivo sería algo como:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-probes-demo
  namespace: ejemplos
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-demo
  template:
    metadata:
      labels:
        app: nginx-demo
    spec:
      containers:
        - name: nginx
          image: nginx:stable
          ports:
            - containerPort: 80
          startupProbe:
            httpGet:
              path: /
              port: 80
            failureThreshold: 30
            periodSeconds: 2
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 10
```
Como siempre lo aplicamos:
```bash
kubectl apply -f nginx-probes.yaml
```
Vemos su estado:
```bash
kubectl -n ejemplos get pods -l app=nginx-demo
```

Vemos a continuación una explicación detallada de cada sección del despliegue, con especial atención en el apartado de chequeo de la salud de los contenedores  para garantizar la auto-reparación (**Self-Healing**) del sistema.

---

## Estructura Básica del Despliegue

*   **`apiVersion: apps/v1`**: Especifica la versión de la API de Kubernetes para recursos de carga de trabajo.
*   **`kind: Deployment`**: Define que el objeto es un Deployment, encargado de gestionar de forma declarativa las réplicas de los Pods.
*   **`metadata.name: nginx-probes-demo`**: El nombre único que identifica este despliegue en el clúster.
*   **`spec.replicas: 1`**: Indica que Kubernetes debe mantener exactamente una instancia (Pod) de la aplicación ejecutándose en todo momento.
*   **`spec.selector.matchLabels`**: Actúa como un filtro para que el Deployment identifique y gestione los Pods que tengan la etiqueta `app: nginx-demo`.

---

## Plantilla del Pod (Template)

La sección `template` describe los Pods que se crearán:

*   **`metadata.labels`**: Etiquetas aplicadas a los Pods creados para que coincidan con el selector del Deployment.
*   **`spec.containers`**: Define las características del contenedor:
    *   **`name: nginx`**: Nombre del contenedor.
    *   **`image: nginx:stable`**: Versión de la imagen de NGINX que se descargará y ejecutará.
    *   **`ports.containerPort: 80`**: El puerto en el que el contenedor está escuchando tráfico interno.

---

## Configuración Detallada de las Probes (Sondas)

Esta es la sección crítica para la monitorización de salud. Kubernetes utiliza el agente **kubelet** para realizar estas comprobaciones.

### A. Startup Probe (Sonda de Inicio)
```yaml
startupProbe:
  httpGet:
    path: /
    port: 80
  failureThreshold: 30
  periodSeconds: 2
```

*   **Función**: Comprueba si la aplicación dentro del contenedor ha arrancado correctamente.
*   **Comportamiento**: Mientras esta sonda esté en curso, las sondas de *liveness* y *readiness* permanecen desactivadas.
*   **Parámetros**: En este caso, el kubelet intentará una conexión HTTP cada 2 segundos (`periodSeconds`). Si falla 30 veces consecutivas (`failureThreshold`), el contenedor se reiniciará. Esto da un margen de 60 segundos para que la aplicación arranque antes de considerarla fallida.

### B. Readiness Probe (Sonda de Disponibilidad)
```yaml
readinessProbe:
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 5
  periodSeconds: 5
```

*   **Función**: Determina si el contenedor está listo para recibir tráfico de red.
*   **Comportamiento**: Si esta sonda falla, el Pod se retira de la lista de endpoints de los **Services** asociados, evitando que los usuarios reciban errores mientras la aplicación no esté lista.
*   **Parámetros**: Espera 5 segundos tras el inicio del contenedor antes de empezar (`initialDelaySeconds`) y repite la prueba cada 5 segundos.

### C. Liveness Probe (Sonda de Supervivencia)
```yaml
livenessProbe:
  httpGet:
    path: /
    port: 80
  initialDelaySeconds: 10
  periodSeconds: 10
```

*   **Función**: Indica si el contenedor sigue vivo y funcionando correctamente.
*   **Comportamiento**: Si esta sonda falla de forma persistente, el kubelet mata el contenedor y lo reinicia según su política de reinicio. Es útil para detectar aplicaciones bloqueadas o en estados "congelados".
*   **Parámetros**: Empieza a comprobar 10 segundos después del arranque y repite la prueba cada 10 segundos.

---

## Resumen de Mecanismos de Comprobación

En este despliegue, todas las sondas utilizan el método **`httpGet`**, que realiza una petición HTTP al contenedor:

*   **Éxito**: Si el código de respuesta es mayor o igual a 200 y menor que 400.
*   **Fallo**: Cualquier otro código de respuesta o falta de conexión.

Esta configuración asegura que la aplicación tenga tiempo suficiente para arrancar (**Startup**), que no reciba tráfico antes de estar lista (**Readiness**) y que se reinicie automáticamente si deja de responder (**Liveness**).

## Ampliando nuestro Deployment phpmyadmin
En una práctica anterior de **StatefulSet de mariadb** habíamos creado un **Deployment + Service + Ingress** `phpmyadmin.yaml` para desplegar una aplicación de gestión asociada al SGBD. Ahora vamos a añadir las correspondientes sondas al Deployment para ejecutar un despliegue más robusto y monitorizado. Nuestro `phpmyadmin.yaml`, cuya sección de Deployment ha sido modificada (hemos dejado intactos **Service e Ingress** en el archivo), será ahora:
```yaml
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

          # =========================
          # STARTUP PROBE
          # =========================
          startupProbe:
            httpGet:
              path: /
              port: 80
            failureThreshold: 30
            periodSeconds: 5

          # =========================
          # READINESS PROBE
          # =========================
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 2
            failureThreshold: 3

          # =========================
          # LIVENESS PROBE
          # =========================
          livenessProbe:
            httpGet:
              path: /index.php
              port: 80
            initialDelaySeconds: 20
            periodSeconds: 10
            timeoutSeconds: 2
            failureThreshold: 3
```

Podemos por tanto modificar el .yaml original para que incorpore los cambios anteriores, y volver a desplegar:
```bash
kubectl apply -f phpmyadmin.yaml
```
Comprobamos a continuación como han ido los chequeos:
```bash
kubectl describe pod $(kubectl get pods -n ejemplos \
-l app=phpmyadmin -o jsonpath="{.items[0].metadata.name}") -n ejemplos
```
Analizando la salida nos encontraremos expresiones como las siguientes:
```
...
    Liveness:   http-get http://:80/index.php\
    delay=20s timeout=2s period=10s #success=1 #failure=3
    Readiness:  http-get http://:80/ \
    delay=5s timeout=2s period=5s #success=1 #failure=3
    Startup:    http-get http://:80/ \
    delay=0s timeout=1s period=5s #success=1 #failure=30
...
```
Las líneas anteriores evidencian que se han añadido a la descripción del Pod las sondas correspondientes, sin embargo no está dando el estado de su ejecución, solo indica cómo están definidas.
Para ver el estado real de la ejecución del Pod y si, de ser el caso, ha fallado alguna sonda podemos ejecutar:
```bash
kubectl -n ejemplos get pods -l app=phpmyadmin
```
La salida del comando anterior sería algo así:
```
NAME                       READY   STATUS    RESTARTS   AGE
phpmyadmin-b48678d-6x8hf   1/1     Running   0          11m
```
En la columna `READY`el 1/1 indica que de 1 réplica 1 está `READY`, es decir, el **readinessProbe** ha dado OK.
Del mismo modo el `STATUS` a `Running` indica que el **livenessProbe** ha sido exitoso. El hecho de que `RESTARTS` esté a `0` también demuestra que todos los chequeos se han ejecutado correctamente.