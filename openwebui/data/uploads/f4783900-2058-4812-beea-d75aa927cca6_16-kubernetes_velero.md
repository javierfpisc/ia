# Backup y Recuperación de Desastres con Velero

**Objetivo:** Configurar una solución profesional de copias de seguridad para el clúster de Kubernetes utilizando **Velero**, utilizando **MinIO** como almacenamiento de objetos y aprovechando las capacidades de **Snapshot** de nuestro sistema de almacenamiento **Ceph**.

---

## 1. Preparación y Gestión de Recursos
Antes de comenzar, es fundamental gestionar los recursos del clúster. En entornos de laboratorio con nodos limitados, la eficiencia es clave.

### Tarea: Limpieza de laboratorios anteriores
Ejecutaremos un bucle para escalar a cero los despliegues de prácticas previas (Odoo, Monitoring, etc.). Esto libera CPU y RAM para los componentes de Velero y MinIO.

```bash
for ns in argocd harbor monitoring odoo wordpress kyverno metrics; do 
  kubectl scale statefulset --all -n $ns --replicas=0
  kubectl scale deployment --all -n $ns --replicas=0
done
```
> **Concepto clave:** El comando `scale` permite modificar el número de réplicas deseadas de forma imperativa. Al ponerlo a 0, Kubernetes detiene los contenedores pero mantiene la configuración intacta para el futuro.

### Creación de Namespace para el despliegue
Creamos namespace para ubicar todos los elementos del despliegue de **Velero**:
```bash
kubectl create namespace velero
```

---

## 2. Infraestructura de Snapshots (CRDs)
Velero no solo copia archivos; también puede realizar "fotos" instantáneas (**Snapshots**) del estado de los discos. Para ello, necesitamos extender la API de Kubernetes.

### Tarea: Instalar los Custom Resource Definitions (CRD)
Los CRDs permiten que Kubernetes entienda nuevos tipos de objetos como `VolumeSnapshot`.

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/v8.2.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotclasses.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/v8.2.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshotcontents.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/external-snapshotter/v8.2.0/client/config/crd/snapshot.storage.k8s.io_volumesnapshots.yaml
```

### Configuración del Driver de Almacenamiento
Debemos definir cómo se comportarán los snapshots en nuestro almacenamiento Ceph. Creamos el archivo `volumesnapshotclass.yaml`:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: ceph-rbd-snapclass
# Driver específico de nuestra infraestructura Ceph
driver: rook-ceph.rbd.csi.ceph.com
# Al borrar el snapshot en K8s, se borra físicamente en Ceph
deletionPolicy: Delete 
```
Ejecutamos:
```bash
kubectl apply -f volumesnapshotclass.yaml
```

---

## 3. Almacenamiento de Objetos (MinIO)
Velero necesita un lugar donde guardar los metadatos y backups de los recursos de la API. Utilizaremos **MinIO**, un servidor compatible con la API de Amazon S3.

El modelo **S3 (Simple Storage Service)** es un paradigma de almacenamiento de objetos creado originalmente por Amazon Web Services. No se basa en archivos ni en bloques tradicionales, sino en objetos almacenados dentro de contenedores llamados buckets. S3 dispone de un una API estándar de almacenamiento de objetos. En este modelo, cada dato se guarda como un objeto independiente que incluye:

* El contenido del fichero
* Metadatos (fecha, tipo, etiquetas, etc.)
* Un identificador único dentro del bucket

Por otro lado MinIO es una implementación open source de almacenamiento de objetos compatible con la API S3. En otras palabras: MinIO “imita” el comportamiento de Amazon S3, pero se puede desplegar on-premise o en Kubernetes.

### Persistencia para MinIO
MinIO requiere un disco persistente para no perder los backups si el pod se reinicia. Usaremos nuestra infraestructura **CephFS**.

**Archivo `minio-pvc.yaml`:**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
  namespace: velero
spec:
  accessModes: ["ReadWriteOnce"]
  storageClassName: ceph-filesystem
  resources:
    requests:
      storage: 10Gi
```
Lo aplicamos:
```bash
kubectl apply -v minio-pvc.yaml
```
> **Nota:** Aunque usamos `ceph-filesystem` con `ReadWriteOnce`, recordad que este modo permite que un solo nodo escriba a la vez, lo cual es suficiente para un despliegue de MinIO con una sola réplica.

### Despliegue de MinIO
Instalaremos MinIO con las credenciales por defecto `minioadmin/minioadmin123`. Se expone mediante dos puertos: **9000** para la API (usada por Velero) y **9001** para la consola web. Además crearemos un **Ingress** para acceder a través de la URL **https://minio.192.168.56.41.nip.io** y el **Secret** que habilita el acceso con las credenciales:

* usuario: **minioadmin**
* password: **minioadmin123**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: velero
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
        - name: minio
          image: minio/minio:latest
          args:
            - server
            - /data
            - --console-address
            - ":9001"
          env:
            - name: MINIO_ROOT_USER
              value: minioadmin
            - name: MINIO_ROOT_PASSWORD
              value: minioadmin123
          ports:
            - containerPort: 9000
            - containerPort: 9001
          volumeMounts:
            - name: data
              mountPath: /data
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: minio-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: minio
  namespace: velero
spec:
  selector:
    app: minio
  ports:
    - name: api
      port: 9000
      targetPort: 9000
    - name: console
      port: 9001
      targetPort: 9001
---
apiVersion: v1
kind: Secret
metadata:
  name: velero-credentials
  namespace: velero
type: Opaque
stringData:
  cloud: |
    [default]
    aws_access_key_id = minioadmin
    aws_secret_access_key = minioadmin123
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minio
  namespace: velero
  annotations:
    cert-manager.io/cluster-issuer: internal-ca-issuer
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - minio.192.168.56.41.nip.io
      secretName: minio-tls
  rules:
    - host: minio.192.168.56.41.nip.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: minio
                port:
                  number: 9001
```
Aplicamos:
```bash
kubectl apply -f minio.yaml
```
#### Creación del Bucket MinIO para almacenar las backups de Velero
Tras la instalación accederemos a la interfaz web, a través de la URL del Ingress: **https://minio.192.168.56.41.nip.io**, autenticamos con las credenciales del Secret y creamos un Bucket de nombre **velero**. Un bucket en MinIO es un contenedor lógico de objetos, equivalente a una carpeta de nivel superior en un sistema de almacenamiento compatible con S3. Dentro de ese bucket se almacenarán los backups de **Velero**.

---

## 4. Instalación de Velero con Helm
Utilizaremos **Helm** para un despliegue organizado. Velero necesita un **Secret** con las credenciales de acceso a MinIO para poder escribir en el "bucket".

### Configuración de Velero (`velero-values.yaml`)
Este archivo es el corazón de la instalación. Aquí definimos:

1.  **BackupStorageLocation:** Donde se guardan los archivos (nuestro MinIO).
2.  **VolumeSnapshotLocation:** Indica que usaremos snapshots vía CSI (nuestro driver de Ceph).
3.  **Secret** a utilizar para obtener las credenciales de acceso a **MinIO**. Hace referencia al Secret definido anteriormente
3.  **Plugins:** Es vital incluir el plugin de **AWS**, ya que es el que permite a Velero hablar con la API de MinIO.

velero-values.yaml:
```yaml
configuration:
  backupStorageLocation:
    - name: default
      provider: aws
      bucket: velero
      default: true
      config:
        region: minio
        s3ForcePathStyle: "true"
        s3Url: http://minio.velero.svc.cluster.local:9000

  volumeSnapshotLocation:
    - name: default
      provider: csi

initContainers:
  # plugin necesario para S3 (MinIO compatible con AWS plugin)
  - name: velero-plugin-for-aws
    image: velero/velero-plugin-for-aws:v1.10.0
    volumeMounts:
      - mountPath: /target
        name: plugins

snapshotsEnabled: true
deployNodeAgent: true

credentials:
  useSecret: true
  existingSecret: velero-credentials
  secretContents:
    cloud: |
      [default]
      aws_access_key_id = minioadmin
      aws_secret_access_key = minioadmin123

resources:
  requests:
    cpu: 100m
    memory: 128Mi
```

```bash
helm install velero vmware-tanzu/velero -n velero -f velero-values.yaml
```

---

## 5. Operaciones con Velero CLI
Para gestionar los backups instalaremos la herramienta de línea de comandos en el equipo local o en el manager.

### Instalación del Velero CLI
Ejecutamos los pasos siguientes:
```bash
wget https://github.com/vmware-tanzu/velero/releases/latest/download/velero-linux-amd64.tar.gz
tar xzf velero-linux-amd64.tar.gz
sudo mv velero-*/velero /usr/local/bin/
sudo chmod +x /usr/local/bin/velero
```

### Comandos Velero
Una vez instalado, vamos a realizar una primera copia de seguridad del namespace `default`:

*   **Crear backup:** `velero backup create test --include-namespaces default`
*   **Ver estado:** `velero backup get`
*   **Describir detalles:** `velero backup describe test`

Veamos algunos ejemplos de comandos de backup con Velero:
```bash
velero backup create backup-multi \
  --include-namespaces wordpress,harbor,odoo
velero backup create backup-cluster-except \
  --exclude-namespaces kube-system,monitoring,argocd
velero backup create backup-deployments \
  --include-resources deployments.apps
velero backup create backup-services \
  --include-resources services
velero backup create backup-labeled-apps \
  --selector app=frontend
```
Los comandos anteriores son autoexplicativos. En el siguiente backup incluímos **Snapshot**, adecuado para entornos con PVCs:
```bash
velero backup create backup-db \
  --include-namespaces postgres \
  --snapshot-volumes
```
También podemos realizar backups solo con metadata:
```bash
velero backup create backup-metadata-only \
  --include-namespaces wordpress \
  --snapshot-volumes=false
```
O bien incluyendo programación del backup:
```bash
velero schedule create daily-backup \
  --schedule "0 2 * * *" \
  --include-namespaces wordpress
```
Podemos incluir parámetros para borrado automático (TTL):
```bash
velero backup create backup-temporal \
  --include-namespaces wordpress \
  --ttl 24h
```
Por último se muestra un backup de migración de clúster:
```bash
velero backup create migration-backup \
  --exclude-namespaces kube-system,velero \
  --include-cluster-resources=true
```

A continuación vamos a simular un sencillo procedimiento de recuperación de desastre. En primer lugar creamos el backup:
```bash
velero backup create argocd \
  --include-namespaces argocd \
```
Borramos (por accidente) los **Deployments** del namespace:
```bash
kubectl -n argocd delete deployments.apps \
argocd-applicationset-controller argocd-redis \
argocd-repo-server argocd-server
```
Para recuperar los objetos borrados con el comando anterior (resultado de un error humano o una catástrofe) ejecutamos:
```bash
velero restore create --from-backup argocd
```
> **Nota:** Tras la ejecución del comando de recuperación anterior podremos ver como dentro del Bucket de MinIO (velero) se ha creado una nueva carpeta "restores" donde veremos un archivo por cada proceso de recuperación ejecutado.

---

## Ideas para hacer pruebas de backups en nuestro laboratorio
*   **Escenario de Desastre:** Podemos probar a borrar un Deployment y recuperarlo posteriormente con `velero restore create --from-backup test`.
*   **Seguridad:** Relaciona el uso del `velero-credentials` Secret con el concepto de **RBAC**, de modo que solo Velero debería tener permisos para leer ese secreto.
*   **Monitorización:** Podemos buscar en Grafana si existen dashboards para monitorizar el éxito o fallo de los backups de Velero.









