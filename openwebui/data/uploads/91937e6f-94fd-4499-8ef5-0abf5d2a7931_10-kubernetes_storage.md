# Gestión de Almacenamiento en Kubernetes: Persistencia y Abstracción

En el mundo de los contenedores, el almacenamiento es uno de los retos más importantes para un administrador de sistemas. Por definición, los contenedores son **efímeros**: si un contenedor se reinicia o un Pod se elimina, cualquier dato guardado en su sistema de archivos local se pierde para siempre. 

Para solucionar esto, Kubernetes proporciona un subsistema de almacenamiento que permite que los datos sobrevivan al ciclo de vida de los Pods, permitiendo que aplicaciones como bases de datos o sistemas de archivos compartidos funcionen correctamente.

---

## El Objetivo: Desacoplar Computación de Almacenamiento
La filosofía de Kubernetes es separar **quién usa el recurso** de **cómo se provee el recurso**. Esto permite que:

*   **El Desarrollador/Usuario** pida almacenamiento sin saber si es un disco SSD, una cabina SAN o un sistema distribuido como CephFS.
*   **El Administrador** gestione la infraestructura de almacenamiento (vuestro clúster de Ceph) de forma independiente a las aplicaciones.

---

## Los Artefactos Principales

### PersistentVolume (PV)

*   **Definición:** Es un recurso de almacenamiento en el clúster que ha sido aprovisionado por un administrador o dinámicamente mediante una Storage Class.
*   **Analogía:** Si un **Nodo** es un recurso de computación, un **PV** es un recurso de almacenamiento.
*   **Función:** Representa el "disco" o "volumen" real. En vuestro caso, un PV apuntaría a un directorio o volumen específico dentro de vuestro sistema **CephFS**.

### PersistentVolumeClaim (PVC)

*   **Definición:** Es una solicitud de almacenamiento por parte de un usuario.
*   **Función:** El desarrollador o administrador no crea un PV, sino que crea un PVC diciendo: "Necesito 5GB de espacio con acceso de lectura/escritura".
*   **Vínculo:** Kubernetes busca un PV que cumpla los requisitos del PVC y los "vincula" (Binding). Una vez vinculado, el almacenamiento queda reservado para ese usuario.

### StorageClass (SC)

*   **Definición:** Permite a los administradores describir las "clases" o "perfiles" de almacenamiento que ofrecen.
*   **Función:** En lugar de crear manualmente 50 PVs de 5GB, el administrador crea una StorageClass vinculada a, por ejemplo, **CephFS**. Cuando un alumno crea un PVC solicitando esa "clase", Kubernetes habla automáticamente con Ceph para crear el volumen al vuelo. Esto se conoce como **Aprovisionamiento Dinámico**.

---

## Integración en Artefactos de Despliegue
Para que un Pod utilice este almacenamiento, la definición del artefacto (como un Deployment o StatefulSet) debe integrar dos conceptos en su archivo YAML:

1.  **volumes:** Define qué almacenamiento va a usar el Pod, referenciando al **PVC** creado previamente.
2.  **volumeMounts:** Define en qué ruta *dentro del contenedor* se va a montar ese volumen (por ejemplo, en `/var/lib/mysql`).

### Ejemplo Conceptual de Flujo:

1.  **Admin:** Crea una `StorageClass` llamada "ceph-fast".
2.  **Programador o desplegador:** Crea un `PersistentVolumeClaim` (PVC) pidiendo 10GB de la clase "ceph-fast".
3.  **K8s:** Crea automáticamente el volumen en **CephFS** y lo asigna al PVC.
4.  **Programador o desplegador:** En su `Deployment`, añade una sección de `volumes` que apunta a ese PVC y un `volumeMount` para su aplicación.

---

## Resumen: ¿Por qué es necesario?
Sin estos conceptos, no podríamos ejecutar aplicaciones **Stateful** (con estado). Debemos entender que:

*   **PV** es el recurso físico/real (gestionado por infraestructura).
*   **PVC** es la necesidad del microservicio (gestionada por el desarrollador).
*   **StorageClass** es la automatización que une ambos mundos.
*   **Provider (tipo CephFS)** es lo que permite que el almacenamiento sea "móvil" y acompañe al contenedor por todo el clúster.

## Configurando Ceph como proveedor de Storage
En nuestro laboratorio, CephFS actúa como la **capa de almacenamiento compartido**. Esto es vital por una razón:

*   Si un Pod corre en el **Nodo Worker 1** y escribe datos en un PV local, y luego ese Pod se mueve al **Nodo Worker 2**, perdería el acceso a sus datos.
*   Al usar **CephFS**, el volumen está disponible en todos los nodos. Kubernetes puede montar el mismo volumen de CephFS en cualquier nodo donde se ejecute el Pod, garantizando la **alta disponibilidad** de los datos.

### Ceph Block Pool
Un pool de bloques donde Ceph crea discos virtuales (RBD images). Cada PVC dentro es un "disco independiente".
Usos:

* PostgreSQL
* MySQL
* etcd
* Redis persistente

### Ceph Filesystem
Un filesystem distribuido POSIX completo encima de Ceph. Permite:

* Uso compartido de datos entre pods
* Soporta RWX (ReadWriteMany)

Usos típicos:

* web servers (NGINX, Apache)
* uploads compartidos
* media files
* CMS (WordPress)
* pipelines CI/CD

### Comparación Ceph RBD vs CephFS

| Característica        | Ceph Block (RBD)                         | Ceph Filesystem (CephFS)                |
|----------------------|------------------------------------------|-----------------------------------------|
| Tipo                 | Disco virtual (block storage)            | Sistema de archivos distribuido        |
| Abstracción          | `/dev/sdX` (como un disco físico)        | Carpeta POSIX (`/mnt/data`)            |
| Kubernetes usage     | PVC → 1 volumen exclusivo                | PVC → directorio compartido            |
| AccessMode típico    | ReadWriteOnce (RWO)                      | ReadWriteMany (RWX)                    |
| Multi-pod access     | No                                       | Sí                                   |
| Rendimiento          | Muy alto                                 | Medio-alto                          |
| Latencia             | Baja                                     | Media                                   |
| Compartición datos   | No                                       | Sí                                   |
| Complejidad          | Baja                                     | Media (requiere MDS)                    |
| Componentes extra    | OSDs                                     | OSDs + MDS                             |
| Caso de uso típico   | Bases de datos, VMs, etcd                | Web servers, uploads, CI/CD, archivos  |
| Snapshot/clones      | Muy eficiente                            | Disponible pero menos usado          |
| Escalabilidad        | Alta                                     | Alta                                    |
| Consistencia         | Fuerte                                   | Fuerte (POSIX)                          |
| Montaje simultáneo   | Bloqueado                                | Permitido                            |