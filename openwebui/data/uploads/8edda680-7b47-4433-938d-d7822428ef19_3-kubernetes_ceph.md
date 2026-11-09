# Almacenamiento distribuido en Kubernetes con Ceph

## Añadir discos adionales a las MVs para Ceph
Antes de nada creamos un grupo de máquinas en VirtualBox, **Orquestacion**, para agrupar los nodos del clúster. Este paso es necesario para añadir los discos, 2 discos por nodo de 50GB, que definirán los OSDs de Ceph. Ejecutamos:
```bash
VBoxManage modifyvm kuber1 --groups "/Orquestacion"
VBoxManage modifyvm kuber2 --groups "/Orquestacion"
VBoxManage modifyvm kuber3 --groups "/Orquestacion"
```

Ejecutar desde el host y con las MVs apagadas:
```bash
for m in kuber1 kuber2 kuber3
do
    VM_DIR="$HOME/VirtualBox VMs/Orquestacion/$m"

    # Disco 1
    if [ ! -f "ceph_${m}_disk1.vdi" ]; then
        VBoxManage createmedium disk \
            --filename "$VM_DIR/ceph_${m}_disk1.vdi" \
            --size 50000
    fi

    VBoxManage storageattach "$m" \
        --storagectl "SATA Controller" \
        --port 1 --device 0 --type hdd \
        --medium "$VM_DIR/ceph_${m}_disk1.vdi"

    # Disco 2
    if [ ! -f "ceph_${m}_disk2.vdi" ]; then
        VBoxManage createmedium disk \
            --filename "$VM_DIR/ceph_${m}_disk2.vdi" \
            --size 50000
    fi

    VBoxManage storageattach "$m" \
        --storagectl "SATA Controller" \
        --port 2 --device 0 --type hdd \
        --medium "$VM_DIR/ceph_${m}_disk2.vdi"

done
```

!!! import "IMPORTANTE"
    Una vez iniciamos las MVs de nuevo deberemos comprobar que los discos añadidos se han montado como sdb y sdc respectivamente. Para ello podemos ejecutar `lsblk`
    De no ser el caso comprobar que en VirtualBox se han añadido en los puertos correctos y reiniciar

## Instalar Rook
Desde el nodo Manager lanzamos:
```bash
kubectl apply -f \
https://raw.githubusercontent.com/rook/rook/release-1.14/deploy/examples/crds.yaml
kubectl apply -f \
https://raw.githubusercontent.com/rook/rook/release-1.14/deploy/examples/common.yaml
kubectl apply -f \
https://raw.githubusercontent.com/rook/rook/release-1.14/deploy/examples/operator.yaml
```

Los comandos anteriores crearán los artefactos necesarios en el Cluster para gestionar Ceph. Veámoslos:
```bash
kubectl get all -n rook-ceph
```

La salida mostrará los objetos creados en el namespace **rook-ceph**: pods, deployments, replicaSets y jobs

## Crear Cluster Ceph
Creamos el archivo de despiegue **ceph-cluster.yaml**
```yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  cephVersion:
    image: quay.io/ceph/ceph:v18

  dataDirHostPath: /var/lib/rook

  network:
    provider: host

  mon:
    count: 3
    allowMultiplePerNode: false

  storage:
    useAllNodes: true
    useAllDevices: false
    devices:
      - name: sdb
      - name: sdc
```

Lo aplicamos:
```bash
kubectl apply -f ceph-cluster.yaml
```

La creación del cluster ceph llevará su tiempo, para ver el estado del mismo (y del proceso de creación y configuración)
```bash
kubectl describe cephclusters.ceph.rook.io -n rook-ceph
```

El cluster estará creado cuando veamos en la salida del comando anterior `Message: Cluster created successfully`


### Creamos Ceph Block Pool
Creamos el archivo **ceph-blockpool.yaml**:
```yaml
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: replicapool
  namespace: rook-ceph
spec:
  failureDomain: host
  replicated:
    size: 2
```

Lo creamos:
```bash
kubectl apply -f ceph-blockpool.yaml
```

Comprobamos su estado tras la creación:
```bash
kubectl describe cephblockpools.ceph.rook.io -n rook-ceph
```

Deberíamos de ver en la salida anterior el mensaje `successfully configured CephBlockPool "rook-ceph/replicapool"`

### Creamos Ceph FS
Creamos el archivo **ceph-fs.yaml**:
```yaml
apiVersion: ceph.rook.io/v1
kind: CephFilesystem
metadata:
  name: ceph-filesystem
  namespace: rook-ceph
spec:
  metadataPool:
    replicated:
      size: 3
  dataPools:
    - replicated:
        size: 3
  preservePoolsOnDelete: true
  metadataServer:
    activeCount: 1
    activeStandby: true
```

Lo creamos:
```bash
kubectl apply -f ceph-fs.yaml
```

Comprobamos su estado tras la creación:
```bash
kubectl describe -n rook-ceph cephfilesystems.ceph.rook.io
```

### Creamos Storage Classes

#### Storage Class para Ceph Block Pool
Creamos el archivo **ceph-block-sc.yaml**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  pool: replicapool
  clusterID: rook-ceph
  imageFormat: "2"
  imageFeatures: layering
  csi.storage.k8s.io/fstype: ext4

  csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph

  csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph

reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: Immediate
```
Lo creamos:
```bash
kubectl apply -f ceph-block-sc.yaml
```

Comprobamos la creación:
```bash
kubectl describe storageclasses.storage.k8s.io ceph-block
```

#### Storage Class para Ceph FS
Creamos el archivo **ceph-fs-sc.yaml**:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ceph-filesystem
provisioner: rook-ceph.cephfs.csi.ceph.com
parameters:
  clusterID: rook-ceph
  fsName: ceph-filesystem

  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph

  csi.storage.k8s.io/node-stage-secret-name: rook-csi-cephfs-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph

reclaimPolicy: Delete
allowVolumeExpansion: true
```
Lo creamos:
```bash
kubectl apply -f ceph-fs-sc.yaml
```

Comprobamos la creación:
```bash
kubectl describe storageclasses.storage.k8s.io ceph-filesystem
```

### Creamos PVC (Physical Volume Claim) de prueba
Creamos el archivo **test-pvc.yaml**:
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ceph-block
  resources:
    requests:
      storage: 1Gi
```
Lo creamos:
```bash
kubectl apply -f test-pvc.yaml
```

Una vez creado lo inspeccionamos con:
```bash
kubect get pvc test-ceph
```
Debiendo ver en la salida la columan STATUS a `Bound`