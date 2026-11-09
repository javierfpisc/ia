# Uso del patrón sidecar: Logs de aplicación
En esta práctica veremos un modo de centralizar todos los mensajes de nuestras aplicaciones en un solo lugar para poder vigilarlas fácilmente. Se divide en tres pasos muy sencillos:

1.  **Recolección (Sidecar - Fluent Bit):** Un contenedor "sidecar", dentro de un mismo Pod junto al que ejecuta la aplicación principal, se encarga de recoger los mensajes que escribe la aplicación en tiempo real y enviarlos fuera del Pod.
2.  **Almacenamiento (Loki):** Es una base de datos optimizada que recibe todos esos mensajes, los organiza y los guarda para que podamos consultarlos después.
3.  **Visualización (Grafana):** Es la herramienta web donde los administradores acceden para buscar información de logs, errores y ver estadísticas de funcionamiento de forma visual.

**En resumen:** La **App** genera los datos, el **Sidecar** los transporta, **Loki** los archiva y **Grafana** nos los muestra.

## Deployment App logs y Fluent Sidecar
Empecemos por el Deployment de la aplicación de ejemplo y el sidecar que recopila los logs. Creamos el archivo `sidecar_logs_deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sidecar-demo
  namespace: ejemplos
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sidecar-demo
  template:
    metadata:
      labels:
        app: sidecar-demo
    spec:
      volumes:
        - name: logs
          emptyDir: {}
        - name: fluentbit-config
          configMap:
            name: fluentbit-config
      containers:
        # CONTENEDOR PRINCIPAL
        - name: app
          image: busybox
          command:
            - /bin/sh
            - -c
            - |
              estados="alegre triste cohibido taciturno \
              sorprendido eufórico motivado desanimado"

              while true; do
                ESTADO=$(echo $estados | tr ' ' '\n' | shuf -n 1)
                FECHA=$(date '+%d/%m/%Y')
                HORA=$(date '+%H:%M:%S')

                echo "a las $HORA de hoy día $FECHA, me encuentro: \
                $ESTADO" >> /logs/app.log
                sleep 2
              done
          volumeMounts:
            - name: logs
              mountPath: /logs
        # SIDECAR
        - name: fluent-bit
          image: cr.fluentbit.io/fluent/fluent-bit:latest
          volumeMounts:
            - name: logs
              mountPath: /logs
            - name: fluentbit-config
              mountPath: /fluent-bit/etc/
```
Este despliegue ilustra el **patrón Sidecar**, una arquitectura donde un contenedor secundario (el sidecar) se ejecuta junto al contenedor principal dentro del mismo **Pod** para extender o mejorar su funcionalidad, compartiendo el mismo ciclo de vida, red y volúmenes. No lo vamos a desplegar todavía con `kubectl`, lo haremos más adelante ya que necesitaremos crear otros elementos previamente.
A continuación, se detalla cada apartado del archivo YAML:

### Identificación y Namespace

*   **`kind: Deployment`**: Define un recurso que gestiona de forma declarativa un conjunto de réplicas de Pods idénticos.
*   **`namespace: ejemplos`**: Sitúa el recurso dentro del entorno aislado de ese namespace.

### Definición de Volúmenes (El puente de comunicación)
Para que el sidecar pueda gestionar los logs del contenedor principal, deben compartir un espacio de almacenamiento:

*   **`name: logs (emptyDir)`**: Se crea un volumen temporal que se borra cuando el Pod desaparece. Este volumen permite que ambos contenedores lean y escriban en la misma carpeta física del nodo.
*   **`name: fluentbit-config (configMap)`**: Utiliza un objeto **ConfigMap** preexistente para inyectar los archivos de configuración que necesita Fluent Bit para funcionar.

### Contenedor Principal (`app`)

*   **Función**: Simula una aplicación productiva usando una imagen de `busybox`.
*   **Operación**: Ejecuta un bucle infinito que escribe la fecha actual y un mensaje de éxito en el archivo `/logs/app.log` cada 2 segundos.
*   **Montaje**: Tiene el volumen `logs` montado en la ruta `/logs` para poder escribir sus registros.

### Contenedor Sidecar (`fluent-bit`)

*   **Función**: Es el contenedor de apoyo encargado de la **gestión de observabilidad y logs**.
*   **Operación**: Al estar en el mismo Pod, tiene acceso al mismo volumen `logs`. Su tarea es "observar" ese directorio, recolectar los datos producidos por la aplicación y, según su configuración, enviarlos a un sistema externo de monitorización.
*   **Montaje doble**: 
    1.  Monta `/logs` para leer los registros de la aplicación principal.
    2.  Monta `/fluent-bit/etc/` desde el **ConfigMap** para obtener sus propias reglas de procesamiento.

### Resumen del Flujo de Trabajo

1.  La **App** genera datos y los guarda en el volumen compartido `logs`.
2.  El **Sidecar (Fluent Bit)** detecta los nuevos datos en el mismo volumen compartido en tiempo real.
3.  Este patrón permite que la aplicación principal ignore cómo se gestionan sus logs, delegando esa responsabilidad al sidecar y facilitando una arquitectura de microservicios limpia y modular.

## ConfigMap Fluent
A continuación definiremos la configuración de Fluent mediante un objeto **ConfigMap** a través del archivo `fluent_configmap.yaml`

### Logs en stdout
La primera versión del archivo es la siguiente:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentbit-config
  namespace: ejemplos
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        1
        Daemon       Off
        Log_Level    info
    [INPUT]
        Name              tail
        Path              /logs/app.log
        Tag               app.logs
    [OUTPUT]
        Name  stdout
        Match *
```
Vemos claramente la definición del objeto **ConfigMap**, identificado con el nombre **fluentbit-config.yaml**, usado para referenciarlo desde la definición del Pod dentro del Deployment del apartado anterior. Esta primera versión monitoriza el archivo /logs/app.log del Pod del Deployment. Además envía el resultado a la salida estańdar. Para ver el resultado ejecutamos desplegamos:
```bash
kubectl apply -f sidecar_logs_deployment.yaml
kubectl apply -f fluentbit-config.yaml
```
Examinamos los logs:
```bash
kubectl -n ejemplos logs deployment/sidecar-demo -c fluent-bit
```

## Logs en Loki+Grafana
Una variante del ConfigMap anterior nos permitiría configurar Fluent para enviar los logs a **Loki**. Para ello modificamos el archivo **fluentbit-config.yaml**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentbit-config
  namespace: ejemplos
data:
  fluent-bit.conf: |
    [SERVICE]
        Flush        1
        Log_Level    info
    [INPUT]
        Name tail
        Path /logs/app.log
        Tag app.logs
        Read_from_Head true
    [OUTPUT]
        Name loki
        Match *
        Host loki.ejemplos.svc.cluster.local
        Port 3100
        Labels job=fluent-bit,app=sidecar-demo
        Line_Format json
```
## Loki+Grafana
Necesitamos crear los microservicios necesarios y todos los artefactos asociados (Deployments, Services, ConfigMaps) para desplegar la infraestructura de ingesta y gestión de Logs en un stack Loki+Grafana. Creamos para ello el archivo `loki_grafana_bundle.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loki
  namespace: ejemplos
spec:
  replicas: 1
  selector:
    matchLabels:
      app: loki
  template:
    metadata:
      labels:
        app: loki
    spec:
      containers:
        - name: loki
          image: grafana/loki:2.9.0
          args:
            - -config.file=/etc/loki/local-config.yaml
          ports:
            - containerPort: 3100
          volumeMounts:
            - name: config
              mountPath: /etc/loki
      volumes:
        - name: config
          configMap:
            name: loki-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: loki-config
  namespace: ejemplos
data:
  local-config.yaml: |
    auth_enabled: false
    server:
      http_listen_port: 3100
    common:
      path_prefix: /loki
      storage:
        filesystem:
          chunks_directory: /loki/chunks
          rules_directory: /loki/rules
      replication_factor: 1
      ring:
        kvstore:
          store: inmemory
    schema_config:
      configs:
        - from: 2020-10-24
          store: boltdb-shipper
          object_store: filesystem
          schema: v11
          index:
            prefix: index_
            period: 24h
---
apiVersion: v1
kind: Service
metadata:
  name: loki
  namespace: ejemplos
spec:
  selector:
    app: loki
  ports:
    - port: 3100
      targetPort: 3100
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: ejemplos
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
        - name: grafana
          image: grafana/grafana:latest
          ports:
            - containerPort: 3000
          env:
            - name: GF_SECURITY_ADMIN_PASSWORD
              value: admin
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: ejemplos
spec:
  selector:
    app: grafana
  ports:
    - port: 3000
      targetPort: 3000
  type: NodePort
```
A modo resumido el archivo anterior crea la pila de **observabilidad** en nuestro clúster, permitiendo que los logs recolectados (por ejemplo, mediante el sidecar de Fluent Bit visto anteriormente) sean almacenados y visualizados. A continuación, se presenta un resumen de los componentes incluidos en este archivo YAML:

### Loki: El Almacén de Logs
Loki es el componente encargado de recibir, indexar y guardar los logs de las aplicaciones.

*   **Deployment (`loki`)**: Crea un Pod que ejecuta el motor de logs. Utiliza **volúmenes** para inyectar su configuración desde un ConfigMap.
*   **ConfigMap (`loki-config`)**: Contiene el archivo de configuración técnica `local-config.yaml`. Aquí se define, por ejemplo, que los logs se guarden en el sistema de archivos local del contenedor y que no se requiere autenticación inicial para el laboratorio.
*   **Service (`loki`)**: Expone a Loki internamente en el puerto **3100**. Otros componentes, como el sidecar de Fluent Bit, usarán este nombre de servicio para enviarle los registros.

### Grafana: Visualización de Datos
Grafana es la interfaz gráfica donde podremos consultar los logs de forma visual.

*   **Deployment (`grafana`)**: Despliega la aplicación de tablero de control.
    *   **Variables de Entorno**: Se utiliza el campo `env` para definir la contraseña de administrador (`admin`) de forma sencilla, permitiendo el acceso inmediato tras el despliegue.
*   **Service (`grafana`)**: 
    *   **Tipo `NodePort`**: A diferencia de Loki, este servicio se configura como `NodePort` para que sea **accesible desde fuera del clúster**. 
    *   **Uso práctico**: Podremos entrar a la interfaz de Grafana usando la dirección IP de cualquiera de los nodos y el puerto asignado por Kubernetes (normalmente en el rango 30000-32767).

### Resumen de la interacción

1.  **Loki** espera en el puerto 3100 a que lleguen los logs.
2.  **Grafana** se conecta a Loki internamente para leer esos datos.
3.  **El usuario** accede a Grafana desde su navegador a través del puerto físico del nodo (**NodePort**) para monitorizar todo lo que ocurre en el clúster.

Desplegamos todo de una vez, desde el directorio en el que residen los archivos .yaml:
```bash
kubectl apply -f .
```

## Visualización en Grafana
Recuperamos puerto del NodePort:
```bash
kubectl -n ejemplos get svc grafana \
-o jsonpath='{.spec.ports[0].nodePort}{"\n"}'
```
Accedemos a la URL de Grafana:
http://192.168.56.41:<puerto>
Entramos con:

* usuario: **admin**
* password: **admin**

Una vez dentro desde **Connections->Data sources** damos de alta un origen de datos **Loki** con URL asociada: **http://loki:3100**
Desde el menú **Explore**, seleccionamos ese origen de datos y luego consultamos los logs con una expresión: `app=sidecar-demo`