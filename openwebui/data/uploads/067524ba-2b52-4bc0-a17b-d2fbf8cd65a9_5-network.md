# Práctica: Configuración de Red y Bridges mediante CLI en Proxmox VE
Este laboratorio tiene como objetivo configurar un puente virtual (**bridge**) utilizando la interfaz de línea de comandos de la API de Proxmox (`pvesh`), asegurando que las interfaces físicas estén preparadas correctamente para el tráfico virtualizado.

## Contexto Teórico: El Modelo de Red en Proxmox
En Proxmox VE, el modelo de red se basa en **bridges** (puentes) que funcionan como switches virtuales de capa 2. El bridge predeterminado suele ser `vmbr0`. Para que una interfaz física pueda "esclavizarse" a un bridge, esta no debe poseer una configuración IP propia, permitiendo que el bridge gestione todo el tráfico que entra y sale por ese puerto físico.

## Paso 1: Configuración de la Interfaz Física (`eth1`)
Antes de crear el bridge, debemos definir la interfaz física en modo manual dentro del archivo de configuración de red. Toda la configuración descrita a continuación se ejecutará como usuario root en los nodos del clúster:
```bash
sudo -i
```
**Procedimiento en pve1, pve2 y pve3:**
Edita el archivo `/etc/network/interfaces` y asegúrate de que la interfaz `eth1` tenga la siguiente configuración:
```bash
auto eth1
iface eth1 inet manual
```
**Por qué es necesario:**
Al poner la interfaz en `manual`, el sistema operativo la activa al arrancar ("up"), pero no le asigna ninguna dirección IP. Esto es vital porque, en una configuración de bridge, el direccionamiento lógico (la IP) reside en el switch virtual (`vmbr0`) y no en el hardware físico directamente. Tras el cambio ejecutamos reinicio de la pila de red:
```bash
# Aplicar cambios previos en la configuración de red
ifreload -a
systemctl restart networking
```

## Paso 2: Creación del Bridge en el Nodo Principal (`pve1`)
Una vez preparada la interfaz física, aplicamos los cambios y utilizamos la herramienta de la API de Proxmox para generar el puente virtual.

### Procedimiento en pve1
Ejecuta el siguiente comando para crear el dispositivo de tipo bridge **vmbr0** vinculándolo a eth1 con IP estática:
```bash
pvesh create /nodes/$(hostname)/network \
  --iface vmbr0 \
  --type bridge \
  --bridge_ports eth1 \
  --address 192.168.56.11 \
  --netmask 255.255.255.0 \
  --autostart 1
```
Reiniciamos:
```bash
reboot
```
Tras el reinicio añadimos en **/etc/network/interfaces**, a continuación de la definición de vmbr0:
```bash
post-up ip addr add 10.20.20.1/24 dev vmbr0
post-up sysctl -w net.ipv4.ip_forward=1
post-up iptables -t nat -A POSTROUTING -s 10.20.20.0/24 -o eth0 -j MASQUERADE
post-down iptables -t nat -D POSTROUTING -s 10.20.20.0/24 -o eth0 -j MASQUERADE
```
Reiniciamos red:

```bash
systemctl restart networking
```
Los comandos anteriores:

* `post-up ip addr add 10.20.20.1/24 dev vmbr0` → Asigna la IP 10.20.20.1 a la interfaz vmbr0 al levantarla.  
* `post-up sysctl -w net.ipv4.ip_forward=1` → Activa el reenvío de paquetes (routing).  
* `post-up iptables -t nat -A POSTROUTING -s 10.20.20.0/24 -o eth0 -j MASQUERADE` → Aplica NAT para que la red 10.20.20.0/24 salga por eth0.  
* `post-down iptables -t nat -D POSTROUTING -s 10.20.20.0/24 -o eth0 -j MASQUERADE` → Elimina la regla NAT al bajar la interfaz.   

**Conceptos Clave:**

* **`pvesh`**: Es la interfaz de shell para la API de Proxmox VE. Permite realizar cambios en la configuración del clúster y los nodos de forma programática y directa, sin usar la interfaz web.
* **`bridge_ports eth1`**: Indica que el tráfico físico de este bridge pasará a través de la tarjeta `eth1`.
* **`autostart 1`**: Garantiza que el puente virtual se levante automáticamente cada vez que el nodo se inicie.

## Paso 3: Configuración en Nodos Secundarios (`pve2` y `pve3`)
Repetiremos el proceso en los nodos restantes, ajustando la dirección IP para evitar conflictos y asegurar la comunicación interna del clúster.

### Comandos para pve2
Creación del bridge:
```bash
pvesh create /nodes/$(hostname)/network \
  --iface vmbr0 \
  --type bridge \
  --bridge_ports eth1 \
  --address 192.168.56.12 \
  --netmask 255.255.255.0 \
  --autostart 1
```
Reiniciamos:

```bash
reboot
```

### Comandos para pve3
De modo análogo:
```bash
pvesh create /nodes/$(hostname)/network \
  --iface vmbr0 \
  --type bridge \
  --bridge_ports eth1 \
  --address 192.168.56.13 \
  --netmask 255.255.255.0 \
  --autostart 1
```
Reiniciamos:

```bash
reboot
```
**Importancia del Direccionamiento Estático:**
Para el correcto funcionamiento de un clúster de Proxmox y servicios como **Corosync** (comunicación del clúster), es imperativo que los nodos tengan direcciones IP fijas y únicas. El uso de IPs dinámicas en las interfaces de gestión podría causar la pérdida del quórum si las direcciones cambian inesperadamente.

!!!important "IMPORTANTE"
    Tras el reinicio, puedes comprobar que el bridge está operativo y tiene la interfaz física asociada correctamente ejecutando el comando `brctl show` o verificando el estado del nodo con `pvecm status` para confirmar que la red del clúster sigue comunicándose correctamente.