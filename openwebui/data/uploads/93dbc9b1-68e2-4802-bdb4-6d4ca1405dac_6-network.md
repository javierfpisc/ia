# Gestión de la red en Proxmox
La gestión de red en **Proxmox VE** es uno de sus pilares fundamentales, permitiendo desde configuraciones básicas de puentes virtuales hasta complejas infraestructuras de **Redes Definidas por Software (SDN)**. Basado en los manuales y la arquitectura del sistema, a continuación se presenta una introducción detallada a estos conceptos.

## 1. El Concepto de Bridge (vmbr)
En Proxmox, el modelo de red se basa primordialmente en el uso de **Linux Bridges** (identificados como `vmbrX`). Un bridge funciona como un **switch virtual de capa 2**, permitiendo que las máquinas virtuales (VM) y contenedores (LXC) se comuniquen entre sí y con la red física externa.

* **Funcionamiento:** Las interfaces físicas del servidor (como `eth0` o `enp...`) se "esclavizan" al bridge. Para que esto funcione correctamente, la interfaz física no debe tener una dirección IP propia; en su lugar, la IP de gestión se asigna directamente al bridge virtual.
* **Flexibilidad:** Este modelo permite que múltiples VMs compartan una única interfaz de red física, manteniendo su tráfico aislado o etiquetado mediante VLANs.

## 2. Software-Defined Network (SDN)
La introducción de las **SDN** en Proxmox VE permite gestionar redes virtuales a nivel de todo el clúster de forma centralizada.

* **Zonas:** Definen el alcance y el tipo de tecnología de red virtual. Proxmox soporta varios tipos de zonas:
    *   **Simple:** Para redes aisladas en un solo nodo.
    *   **VLAN / QinQ:** Para segmentación estándar basada en etiquetas.
    *   **VXLAN:** Permite crear redes de capa 2 sobre una infraestructura de capa 3, ideal para clústeres que se extienden a través de diferentes subredes físicas.
    *   **EVPN:** Para configuraciones avanzadas de enrutamiento y escalabilidad en grandes centros de datos.
* **VNets y Subnets:** Dentro de estas zonas, se pueden crear redes virtuales (VNets) y asignarles rangos de direcciones IP (Subnets), facilitando entornos de **multi-tenancy** donde diferentes usuarios o proyectos están aislados a nivel de red.

## 3. VXLAN SDN en Proxmox
**VXLAN (Virtual Extensible LAN)** es una tecnología de encapsulación de red que permite extender redes de **capa 2 (L2)** sobre una infraestructura de **capa 3 (IP)**.

En lugar de depender de VLANs tradicionales, VXLAN encapsula tramas Ethernet dentro de paquetes **UDP**, lo que permite crear redes L2 virtuales altamente escalables entre nodos distribuidos.

En Proxmox VE, el sistema **SDN (Software Defined Networking)** brinda, entre otras opciones, VXLAN para construir redes virtuales distribuidas entre nodos del clúster.

El objetivo es que las máquinas virtuales puedan conectarse a redes L2 comunes aunque estén ejecutándose en hosts físicos diferentes.

### Peers (VTEPs)

Los nodos del clúster Proxmox actúan como **VTEPs (VXLAN Tunnel Endpoints)**, también llamados *peers*.

Cada peer:

- Encapsula tráfico Ethernet en VXLAN (UDP)
- Envía tráfico a otros nodos del clúster
- Desencapsula tráfico VXLAN recibido
- Participa en uno o varios dominios VXLAN

En otras palabras, los peers son los puntos donde entra y sale el tráfico VXLAN.

### Encapsulación VXLAN sobre UDP

VXLAN funciona encapsulando tramas L2 dentro de UDP. Esto permite que:

- El tráfico L2 se transporte sobre redes L3
- No sea necesario depender de VLANs físicas
- Se escale fácilmente entre nodos distribuidos

El puerto UDP estándar utilizado es el **4789**.

### VNets en Proxmox

En Proxmox SDN, una **VNet** representa una red virtual L2 definida por software.

Cada VNet:

- Está asociada a un **VNI (VXLAN Network Identifier)**
- Define un dominio de broadcast L2 virtual
- Puede abarcar múltiples nodos del clúster

Relación clave:

> **VNet (Proxmox SDN) ≈ Red L2 virtual**

> **VNI (VXLAN) = Identificador técnico de esa red**

### Relación entre VNets, VXLAN y Peers

- Los **VNets** definen la red lógica
- Los **VNIs** identifican la red VXLAN subyacente
- Los **peers (VTEPs)** transportan el tráfico entre nodos
- VXLAN encapsula el tráfico L2 en UDP para atravesar la red IP

En conjunto, esto permite construir redes L2 virtuales distribuidas sobre una infraestructura L3.

---

**En resumen:**

VXLAN en Proxmox SDN permite crear redes L2 virtuales (VNets) que se extienden entre nodos del clúster mediante encapsulación de tráfico Ethernet en UDP.

Los nodos actúan como peers (VTEPs), que encapsulan y transportan tráfico entre sí, permitiendo que las máquinas virtuales compartan redes lógicas independientemente de su ubicación física.


## 4. Características de Red en Proxmox VE
Las últimas versiones introducen y consolidan mejoras críticas en el stack de red y seguridad:

* **Redundancia de Corosync:** Para garantizar la estabilidad del clúster, se soportan hasta **8 enlaces de red redundantes**. Es vital mantener una latencia inferior a **5ms** para que la comunicación del clúster sea estable.
* **Firewall con nftables:** En versiones recientes se ofrece un nuevo motor de firewall basado en **nftables**, que sustituye progresivamente a iptables para ofrecer un mayor rendimiento en el filtrado de paquetes de las máquinas virtuales y el host.
* **Redes para Hiperconvergencia (Ceph):** Se recomienda encarecidamente separar el tráfico de almacenamiento del tráfico de gestión y de las VMs. Para implementaciones de **Ceph**, es estándar utilizar redes dedicadas de al menos **10 Gbps** para la replicación de datos.

## 5. Herramientas de Gestión y Servicios
La configuración de red puede realizarse tanto desde la interfaz gráfica como mediante la línea de comandos, utilizando herramientas específicas:

* **pvesh:** Interfaz de shell para la API de Proxmox que permite automatizar la creación de interfaces y bridges .
* **pve-firewall:** Servicio encargado de gestionar las reglas de seguridad a nivel de Datacenter, Nodo y VM.
* **Archivos de configuración:** El archivo principal de red reside en `/etc/network/interfaces`, aunque Proxmox gestiona sus propios archivos de estado para SDN en la base de datos distribuida **pmxcfs** para asegurar que la configuración sea idéntica en todos los nodos.

En resumen, Proxmox VE transforma la red física en una plataforma ágil y altamente configurable, permitiendo desde el uso sencillo de switches virtuales hasta la implementación de infraestructuras complejas mediante SDN, todo ello protegido por un sistema de firewall distribuido.