# Manual de Herramientas CLI de Proxmox VE
A continuación se enumeran algunas de las herramientas de línea de comandos (CLI) para la gestión de un entorno **Proxmox VE** moderno. Estas utilidades permiten administrar desde recursos individuales hasta la infraestructura completa del clúster de forma eficiente y programática.

## 1. Gestión General del Sistema
Estas herramientas permiten controlar el comportamiento global de los nodos y el acceso al sistema.

*   **`pvesh`**: Es la interfaz de shell para la **API RESTful** de Proxmox. Permite ejecutar cualquier función de la API de forma directa, facilitando la integración con herramientas externas de automatización.
*   **`pvenode`**: Herramienta para la gestión de configuraciones específicas del **nodo**, como la administración de certificados SSL, la configuración de Wake-on-LAN y la inspección del historial de tareas.
*   **`pveum`**: Gestor de usuarios (**User Manager**). Se utiliza para administrar el Control de Acceso Basado en Roles (RBAC), incluyendo la creación de usuarios, grupos, dominios de autenticación (realms) y tokens de API.
*   **`pveversion`**: Comando sencillo cuya utilidad es mostrar la **versión actual** instalada de los paquetes de Proxmox VE y del kernel.
*   **`pvesm`**: Gestor de almacenamiento (**Storage Manager**). Permite configurar pools de almacenamiento, escanear recursos de red (NFS/CIFS) y asignar o liberar volúmenes de disco.
*   **`pveperf`**: Script de **benchmarking** que proporciona una visión rápida del rendimiento de la CPU y la latencia de entrada/salida (I/O) de los discos locales.
*   **`pvecm`**: Gestor de clúster (**Cluster Manager**). Su función es crear clústeres, unir nuevos nodos, gestionar el quórum de Corosync y visualizar el estado de comunicación entre los miembros.
*   **`ha-manager`**: Gestiona la **Alta Disponibilidad**. Se encarga de supervisar los recursos protegidos para realizar failover automático en caso de fallo de un nodo.

---

## 2. Máquinas Virtuales (KVM/QEMU)
Herramientas enfocadas en el ciclo de vida y la configuración del hardware virtualizado.

*   **`qm`**: Es la herramienta principal para gestionar **máquinas virtuales KVM**. Permite crear, destruir, configurar hardware, realizar snapshots y controlar el estado de ejecución (inicio/parada) de las VMs.
*   **`qmrestore`**: Utilidad específica para la **restauración** de máquinas virtuales a partir de archivos de respaldo generados por `vzdump`.
*   **`qemu-img`**: Comando de bajo nivel utilizado para la manipulación y conversión de **imágenes de disco** (formatos como qcow2, raw, vmdk).
*   **`virsh`**: Herramienta estándar de la librería libvirt, útil en Proxmox para tareas avanzadas de **depuración** y consulta de recursos de virtualización. Para utilizarla es necesario tener instalado el paquete `libvirt-clients`

---

## 3. Backup y Restauración
Utilidades dedicadas a la protección de datos y recuperación ante desastres.

*   **`vzdump`**: Motor de copias de seguridad de Proxmox. Realiza **backups completos** de VMs y contenedores, incluyendo sus archivos de configuración y datos de disco.
*   **`pbs-client`**: Herramienta de cliente para interactuar con un **Proxmox Backup Server (PBS)** externo, permitiendo backups incrementales y deduplicados.

---

## 4. Gestión de Almacenamiento
Comandos nativos para la administración de capas de almacenamiento subyacentes.

*   **`zfs` / `zpool`**: Herramientas de administración para el sistema de archivos **ZFS**, utilizadas para gestionar datasets, pools, replicación y snapshots nativos.
*   **`pvs` / `vgs` / `lvs`**: Comandos para listar objetos de **LVM** (volúmenes físicos, grupos de volúmenes y volúmenes lógicos respectivamente).
*   **`lvcreate` / `lvremove`**: Utilidades para la creación y eliminación manual de volúmenes lógicos LVM.

---

## 5. Ceph (Almacenamiento Distribuido)
Comandos para gestionar la infraestructura hiperconvergente de almacenamiento.

*   **`pveceph`**: Wrapper de Proxmox que simplifica la instalación y gestión de servicios **Ceph** (monitores, OSDs, MDS) directamente desde Proxmox.
*   **`ceph`**: Herramienta nativa para consultar la salud, el estado de los pools y la configuración general del **clúster Ceph**.
*   **`rbd`**: Utilidad para gestionar imágenes de **bloque distribuidas** (RADOS Block Devices) dentro de pools Ceph, permitiendo listar, mapear o redimensionar discos virtuales.
*   **`ceph-volume` / `ceph-mon` / `ceph-osd` / `ceph-mgr`**: Herramientas de gestión para los distintos **daemons** y componentes físicos de Ceph.

---

## 6. Clúster y Corosync
Herramientas de bajo nivel para la sincronización y diagnóstico de la red del clúster.

*   **`corosync-cfgtool` / `corosync-cmapctl` / `corosync-quorumtool`**: Comandos técnicos para diagnosticar la comunicación de red, modificar la base de datos de configuración en memoria y verificar los votos del **quórum** del clúster.
*   **`crm_mon`**: Monitor de estado para componentes de **Pacemaker**, útil si se han integrado servicios de clúster externos a la gestión nativa de Proxmox.