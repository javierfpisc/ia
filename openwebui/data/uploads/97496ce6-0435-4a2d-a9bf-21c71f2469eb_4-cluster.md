# Clúster de Proxmox

## ¿Qué es Proxmox VE?

**Proxmox Virtual Environment (Proxmox VE o PVE)** es una plataforma de virtualización de código abierto basada en Debian GNU/Linux que integra en un solo producto:

| Tecnología | Uso |
|---|---|
| **KVM/QEMU** | Máquinas virtuales completas (hardware virtualizado) |
| **LXC** | Contenedores de sistema ligeros |
| **Ceph** | Almacenamiento distribuido hiperconvergente |
| **SDN** | Redes definidas por software (VLAN, VXLAN, zonas) |
| **Corosync + pmxcfs** | Formación del clúster y configuración compartida |

Se administra desde una **interfaz web en el puerto 8006** o desde la línea de comandos (`qm`, `pct`, `pvecm`, `pvesm`).

Un **Cluster de Proxmox VE** consta de un conjunto de nodos (servidores) que trabajan juntos como una única infraestructura virtualizada. A través de este clúster, los nodos comparten configuración, gestión y, opcionalmente, almacenamiento, permitiendo administrar todas las máquinas virtuales y contenedores desde un solo panel.

Las ventajas principales que ofrece son las siguientes:

- **Gestión centralizada:** puedes administrar todos los nodos como un solo sistema desde una única interfaz web. Además comparten una única configuración (la misma vista de `/etc/pve`).
- **Vigilancia mutua**: mediante un protocolo de mensajería (corosync) decidiendo por mayoría (quórum) qué hacer si un nodo desaparece.
- **Alta disponibilidad (HA):** si un nodo falla, las VMs pueden reiniciarse automáticamente en otro nodo.
- **Migración en caliente:** mover VMs entre nodos sin interrumpir el servicio.
- **Escalabilidad:** puedes añadir más nodos al clúster para aumentar recursos fácilmente.
- **Balanceo de carga:** distribuir las cargas de trabajo entre los nodos disponibles.
- **Redundancia y resiliencia:** mayor tolerancia a fallos frente a un solo servidor.

En resumen, un clúster en Proxmox permite construir una infraestructura más robusta, flexible y fácil de gestionar, especialmente útil en entornos de laboratorio, producción o virtualización a gran escala.

## Componentes clave

### Nodo
Estos se definen como cada servidor con Proxmox VE instalado. Los requisitos básicos para formar clúster son:

- Misma **versión** de Proxmox VE en todos los nodos.
- **Nombre de host único** y resolución de nombres funcionando (DNS o `/etc/hosts` en todos los nodos).
- **Hora sincronizada** (NTP/chrony), imprescindible para los certificados y corosync.
- Acceso **SSH como root** entre nodos (por clave o contraseña) para el `join`.

### Corosync (la "voz" del clúster)
Es el motor de comunicaciones. Mantiene la lista de nodos vivos, detecta caídas y transporta los mensajes de `pmxcfs`.

- Usa **UDP 5404–5405** (y puertos superiores con el transporte *knet*).
- Exige **baja latencia y poca pérdida de paquetes**: en producción se recomienda una red dedicada (≥ 1 GbE, mejor 10 GbE). En un laboratorio de pruebas puede compartirse la red de gestión, con menos garantías.
- Límite soportado: **hasta 32 nodos** por clúster.

### pmxcfs (la "memoria compartida" de configuración)
Acrónimo de **Proxmox Cluster File System**: un sistema de ficheros basado en base de datos que mantiene `/etc/pve` (definiciones de VMs, contenedores, usuarios, firewall, almacenamiento) **replicado en tiempo real en todos los nodos** a través de corosync.

**Consecuencias**:

- Da igual por qué nodo entres: ves lo mismo.
- Si el clúster pierde el quórum, `/etc/pve` pasa a **solo lectura**: no podrás crear ni arrancar VMs. Por eso el quórum es crítico.

### Quórum (la "mayoría")
El clúster solo toma decisiones si más de la mitad de los votos están presentes. Cada nodo = 1 voto.

| Nodos | Votos necesarios | Tolera la caída de… |
|---|---|---|
| 1 (sin clúster real) | 1 | 0 |
| 2 | 2 | 0 (mal diseño: al caer uno pierdes quórum) |
| 3 | 2 | 1 nodo |
| 5 | 3 | 2 nodos |

**Regla de oro:** usa un **número impar de nodos** (3 es lo mínimo). Si solo tienes 2, añade un **QDevice** (un "testigo" externo, p. ej. una Raspberry Pi) que aporta un voto extra.

## Red y puertos asociados

| Puerto / Protocolo | Servicio |
|---|---|
| TCP 8006 | Interfaz web y API |
| TCP 22 | SSH (`pvecm add`, `qm`, `pct`) |
| UDP 5404–5405 | Corosync (clúster) |
| TCP 60000–60050 | Migración en vivo de VMs/contenedores |
| TCP 3128 | Proxy SPICE (consola), si se usa |

## Glosario

| Término | Significado |
|---|---|
| **Nodo** | Servidor Proxmox miembro del clúster |
| **Quórum** | Mayoría de votos necesaria para que el clúster opere |
| **Corosync** | Protocolo de comunicaciones y vigilancia entre nodos |
| **pmxcfs** | Sistema de ficheros que replica `/etc/pve` en todo el clúster |
| **QDevice** | Testigo externo que aporta un voto (útil con 2 nodos) |
| **HA** | Alta disponibilidad: reinicia recursos en otro nodo tras una caída |
| **Fencing / watchdog** | Mecanismo que garantiza que un nodo "muerto" no escribe en discos compartidos |
| **Ceph** | Almacenamiento distribuido hiperconvergente (mínimo 3 nodos) |
| **LXC** | Contenedor de sistema ligero de Proxmox |
| **KVM/QEMU** | Virtualización completa usada por las VMs |
