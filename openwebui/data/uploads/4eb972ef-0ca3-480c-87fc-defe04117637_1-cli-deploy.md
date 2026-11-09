# Administración de Clúster Proxmox VE vía CLI

Este documento está diseñado como introducción a las herramientas de línea de comandos en un entorno de **proxmox** como el de nuestro laboratorio, con almacenamiento distribuido **Ceph**, red basada en bridge (**vmbr0**) e imágenes ISO locales.

## 1. Exploración del Clúster y sus Recursos
Antes de realizar cambios, es vital verificar la salud del sistema y la visibilidad de los recursos.

*   **`pvecm status`**: Proporciona una visión general del quórum y la comunicación de **Corosync**, asegurando que el clúster puede tomar decisiones de escritura.
*   **`pvesh get /nodes`** (o su equivalente **`pvecm nodes`**): Consulta a través de la API (o del gestor de clúster) la lista de nodos activos y sus identificadores únicos.
*   **`cat /etc/pve/storage.cfg`**: Permite leer el archivo de configuración distribuido para verificar los backends de almacenamiento disponibles en todo el clúster.
*   **`rbd ls labpool`**: Comando nativo de Ceph para listar las imágenes de disco existentes dentro del pool de bloques (**RBD**) denominado `labpool`.
*   **`rbd info labpool/vm-100-disk-0`**: Muestra detalles técnicos (tamaño, características, formato) de un volumen específico dentro de Ceph.

## 2. Creación de Máquinas Virtuales desde CLI
Utilizaremos la herramienta **`qm`** (QEMU/KVM Virtual Machine Manager) para el despliegue granular de recursos.

*   **`qm create 300 --name debian-test --memory 1024 --cores 1 --net0 virtio,bridge=vmbr0`**: Crea la VM con ID 300, asignando nombre, 1GB de RAM, 1 CPU y una tarjeta de red paravirtualizada conectada al bridge físico.
*   **`qm config 300`**: Muestra la configuración actual de la máquina, permitiendo verificar los cambios pendientes o aplicados.
*   **`qm set 300 --ide2 local:iso/debian-13.4.0-amd64-netinst.iso,media=cdrom`**: Conecta la imagen ISO del sistema operativo (alojada en el almacenamiento local) a la unidad de CD-ROM virtual.
*   **`qm set 300 --scsihw virtio-scsi-single`**: Define el tipo de controladora SCSI; se recomienda `virtio-scsi-single` para obtener el mejor rendimiento y soporte de comandos avanzados en Linux.
*   **`qm set 300 --scsi0 ceph-rbd:20`**: Crea y asigna un disco virtual de 20GB directamente en el almacenamiento distribuido Ceph.
*   **`qm set 300 --boot order=ide2`**: Establece la prioridad de arranque para que la VM inicie desde la unidad de CD-ROM y así comenzar la instalación.
*   **`qm start 300`**: Inicia el proceso de ejecución de la máquina virtual.
*   **`qm status 300`**: Verifica si la máquina está en ejecución (`running`) o detenida (`stopped`).

## 3. Ciclo de Vida y Movilidad
Gestión de estados operativos y migración entre nodos físicos.

*   **`qm shutdown 300`**: Envía una señal de apagado ordenado al sistema operativo invitado (requiere ACPI o Guest Agent).
*   **`qm stop 300`**: Apagado forzado inmediato; equivale a desconectar la alimentación eléctrica.
*   **`qm reboot 300`**: Reinicia la máquina virtual, aplicando cualquier cambio de configuración pendiente que requiera un ciclo de encendido.
*   **`qm migrate 300 pve2`**: Mueve la VM al nodo `pve2`. Al usar almacenamiento compartido (**Ceph**), esto puede realizarse en caliente si se añade el parámetro `--online`.

## 4. Snapshots (Instantáneas)
Preservación del estado de los discos en momentos críticos, por ejemplo antes de una actualización o cambio en el sistema que pueda ser destructivo.

*   **`qm snapshot 300 snapshot-inicial`**: Captura el estado actual de los discos de la VM.
*   **`qm listsnapshot 300`**: Muestra la jerarquía de instantáneas tomadas, permitiendo ver la línea de tiempo de cambios.
*   **`qm rollback 300 snapshot-inicial`**: Revierte la máquina virtual exactamente al estado en que se encontraba cuando se tomó el snapshot.

## 5. Clonación y Plantillas
Optimización del despliegue masivo mediante el uso de moldes inmutables.

*   **`qm template 300`**: Convierte la VM 300 en una plantilla de solo lectura, impidiendo que sea iniciada pero permitiendo que sirva de base para clones.
*   **`qm clone 300 301 --name debian-test-clone`**: Crea una nueva máquina (ID 301) que es una copia idéntica de la plantilla.

## 6. Gestión de Almacenamiento Ceph
Supervisión directa del motor de almacenamiento hiperconvergente.

*   **`ceph -s`**: Muestra el estado de salud general, el uso de datos y el estado de los monitores y OSDs.
*   **`ceph health detail`**: Ofrece un desglose detallado si el sistema presenta algún error o advertencia de salud.
*   **`ceph osd pool ls`**: Lista todos los pools de almacenamiento configurados en el clúster Ceph.
*   **`ceph df`**: Informa sobre la capacidad total, disponible y utilizada por cada pool.
*   **`ceph osd tree`**: Visualiza la estructura física del almacenamiento, mostrando qué discos están en qué nodos.

## 7. Alta Disponibilidad (HA)
Garantiza la resiliencia de los servicios ante fallos de hardware.

*   **`ha-manager status`**: Muestra qué nodos están activos, quién es el "Master" del clúster y el estado de los recursos protegidos.
*   **`ha-manager add vm:300`**: Añade la VM 300 al sistema de HA para que se reinicie automáticamente en otro nodo si su anfitrión actual falla.
*   **`ha-manager remove vm:300`**: Retira la protección de alta disponibilidad del recurso.

## 8. Automatización mediante la API (`pvesh`)
Esta herramienta permite interactuar con la infraestructura de forma programática, ideal para la creación de scripts.

*   **`pvesh get /cluster/resources --type vm`**: Recupera una lista en formato estructurado de todas las máquinas virtuales del clúster y su estado.
*   **`pvesh create /nodes/pve2/qemu --vmid 400 --name api-vm --memory 1024 --cores 1`**: Crea una nueva VM (ID 400) directamente invocando el endpoint de la API en el nodo `pve2`.
*   **`pvesh delete /nodes/pve2/qemu/400`**: Elimina el recurso a través de una petición DELETE a la API.

## 9. Configuración Distribuida
Inspección de los archivos replicados en tiempo real por el sistema de archivos del clúster (**pmxcfs**).

*   **`cat /etc/pve/corosync.conf`**: Muestra la configuración de red y votación del clúster.
*   **`cat /etc/pve/qemu-server/300.conf`**: Muestra el archivo de texto que define todo el hardware y opciones de la VM 300.