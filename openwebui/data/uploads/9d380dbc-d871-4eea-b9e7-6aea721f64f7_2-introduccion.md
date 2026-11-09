# Introducción a Proxmox

## Introducción
Proxmox VE es una plataforma de virtualización de código abierto basada en **Debian Linux** que integra dos tecnologías fundamentales: **KVM** (Kernel-based Virtual Machine) para la virtualización completa de hardware y **LXC** (Linux Containers) para una virtualización ligera a nivel de sistema operativo. Su arquitectura se distingue por un diseño **Multi-Master** único, donde no existe un nodo de gestión centralizado, permitiendo administrar todo el entorno desde la interfaz web de cualquier nodo.

## Arquitectura y características

### El Corazón del Sistema: Proxmox Cluster File System (pmxcfs)
A diferencia de otras soluciones, Proxmox utiliza un sistema de archivos propio denominado **pmxcfs**, el cual es un sistema de archivos basado en una base de datos distribuida que almacena los archivos de configuración de hasta miles de máquinas virtuales.

* **Replicación en tiempo real:** Utiliza **Corosync** para replicar los cambios de configuración instantáneamente en todos los nodos.
* **Persistencia y Rendimiento:** Aunque los datos se guardan en disco, reside una copia en la memoria RAM para garantizar un acceso extremadamente rápido.
* **Consistencia:** Proporciona comprobaciones para evitar duplicidad de IDs de VM y bloqueos distribuidos.

### Gestión de Clúster y Quórum
El clúster de Proxmox permite agrupar servidores físicos bajo una gestión centralizada.

* **Quórum:** Utiliza una técnica de votación para mantener un estado consistente; si el clúster pierde la mayoría de votos, entra en modo de solo lectura para proteger los datos.
* **QDevice:** Soporta un dispositivo de quórum externo para evitar situaciones de "split-brain" en clústeres pequeños (ej. 2 nodos).
* **Requisitos de Red:** Se recomienda una latencia inferior a **5ms** para un funcionamiento estable de Corosync. En la versión 9.1, se soportan hasta 8 enlaces de red redundantes.

## Infraestructura Hiperconvergente con Ceph
Proxmox VE permite el despliegue de una infraestructura hiperconvergente (**HCI**) integrando **Ceph**, un sistema de almacenamiento distribuido y auto-reparable.

**Componentes Clave:**

* **Monitores (MON):** Mantienen el mapa del clúster (mínimo 3 recomendados).
* **OSDs (Object Storage Daemons):** Gestionan el almacenamiento en los discos físicos (uno por disco).
* **Managers (MGR):** Manejan métricas y estado del clúster.
* **MDS (Metadata Servers):** Necesarios si se utiliza CephFS.

**Beneficios y Red:** Elimina la necesidad de cabinas externas (SAN/NAS) costosas, escalando linealmente al añadir nodos. Se recomienda una red física separada de al menos **10 Gbps** para el tráfico de replicación de Ceph.

## Redes Definidas por Software (SDN)
La integración de **SDN** permite crear redes virtuales complejas sobre la infraestructura física.

* **Zonas:** Definen el alcance de la red virtual (Simple, VLAN/QinQ, VXLAN, EVPN).
* **VNets y Subnets:** Permiten segmentar el tráfico y asignar rangos IP específicos, facilitando entornos de multi-tenancy.

## Alta Disponibilidad (HA)
El **ha-manager** actúa como un administrador automatizado que supervisa los recursos.

* **Componentes:** **pve-ha-lrm** (Local Resource Manager) ejecuta acciones en el nodo local y **pve-ha-crm** (Cluster Resource Manager) toma decisiones globales.
* **Fencing (Cercado):** Asegura que un nodo fallido esté desconectado antes de reiniciar sus VMs en otro nodo para evitar corrupción de datos, utilizando preferentemente **watchdogs**.
* **Políticas de Fallo:** Configuración de reintentos de inicio y reubicaciones automáticas (`max_restart`, `max_relocate`).

## Gestión de Usuarios y Seguridad (RBAC)
Proxmox implementa un control de acceso basado en roles (**RBAC**) granular.

* **Realms:** Soporta autenticación local (PVE), PAM, LDAP, Active Directory y OpenID Connect.
* **Roles y Permisos:** Se definen por un sujeto, un rol (lista de privilegios) y una ruta de objeto.
* **Seguridad adicional:** Soporta **Autenticación de Dos Factores (TFA)** (TOTP, WebAuthn) y **Tokens de API** para automatización.

## Firewall Distribuido
Protege el tráfico de los nodos, máquinas virtuales y contenedores.

* **Niveles:** Las reglas se definen a nivel de Datacenter, Nodo o VM.
* **Grupos e IPSets:** Facilitan la gestión de reglas comunes.
* **nftables:** En la versión 9.1, se ofrece como "tech preview" un nuevo motor de firewall basado en nftables para mejorar el rendimiento.

## Backup, Replicación y Recuperación ante Desastres
* **VZDump:** Realiza copias de seguridad consistentes mediante snapshots.
* **Proxmox Backup Server (PBS):** Integración para backups deduplicados, incrementales y cifrados.
* **Replicación de Almacenamiento:** Para nodos con almacenamiento local (ej. ZFS), permite replicar datos periódicamente para reducir el tiempo de recuperación ante desastres.

## Gestión de Recursos y Optimización
* **ZFS on Linux:** Ofrece protección contra corrupción de datos, compresión nativa y snapshots instantáneos.
* **KSM (Kernel Samepage Merging):** Ahorra memoria RAM deduplicando páginas idénticas entre VMs.
* **Ballooning:** Gestión dinámica de la memoria RAM entre el host y los invitados.

## Herramientas de Gestión
Relación de comandos principales para la administración:

* **qm:** QEMU/KVM Manager (gestiona VMs).
* **pvesm:** Proxmox VE Storage Manager.
* **pveum:** Proxmox VE User Manager.
* **ha-manager:** High Availability Manager.
* **pct:** Proxmox Container Toolkit (gestiona contenedores LXC).
* **pvecm:** Proxmox VE Cluster Manager.
* **pveceph:** Herramienta de gestión de Ceph.
* **pve-firewall:** Gestión de reglas de firewall.

## Servicios de Proxmox
* **pveproxy:** Proxy web para la interfaz y API.
* **pvedaemon:** Daemon principal para tareas de gestión.
* **pvestatd:** Servicio de estadísticas de rendimiento.
* **pve-ha-lrm:** Ejecuta las acciones de HA en cada nodo.
* **pve-cluster:** Mantiene la configuración compartida en `/etc/pve`.

## Referencias
Este documento constituye la base conceptual de **Proxmox VE 9.1**.

* Manuales: `man qm`, `man pct`, `man pvesm`.
* [Guía de Administración Oficial](https://pve.proxmox.com/pve-docs/pve-admin-guide.html).