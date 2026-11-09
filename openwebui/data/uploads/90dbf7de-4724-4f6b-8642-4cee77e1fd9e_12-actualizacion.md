# Actualización del clúster Proxmox VE

## Objetivos
Al finalizar esta práctica habremos realizado lo siguiente:

- Verificar el estado de un clúster Proxmox antes de una actualización.
- Actualizar los paquetes de un nodo de forma segura.
- Mantener la disponibilidad de las máquinas virtuales mediante migraciones en vivo.
- Validar el funcionamiento del clúster tras la actualización.
- Comprender los riesgos asociados a las actualizaciones en entornos productivos.

## Verificar el estado del clúster
> **Nota:** Ejecutaremos los siguientes comandos como root

Desde cualquier nodo:
```bash
pvecm status
```

Comprobar:

- Todos los nodos aparecen online.
- Existe quórum (Quorate: Yes).
- No hay particiones de red.

Ejemplo:
```
Quorate: Yes
Nodes: 3
```

### ¿Por qué es importante?
Si el clúster ya presenta problemas antes de actualizar, el proceso puede agravarlos y provocar pérdida de servicios.

## Verificar el estado de almacenamiento
```bash
pvesm status
```
Comprobar:

- Datastores accesibles.
- Ceph (si existe) en estado saludable.
- Espacio libre suficiente.

## Verificar tareas en ejecución
```bash
pvesh get /cluster/tasks
```
o desde la interfaz web nos aseguramos de que no existan:

- Backups en ejecución.
- Migraciones activas.
- Replicaciones pendientes.

## Actualizar índices de paquetes
```bash
apt update
```
Comprobar si existen paquetes pendientes:
```bash
apt list --upgradable
```

## Seleccionar el primer nodo
Nunca se actualizan todos los nodos simultáneamente. Supongamos un clúster:

- pve1
- pve2
- pve3

Comenzaremos por **pve1**.

## Migrar las máquinas virtuales
Listar las máquinas virtuales del nodo:
```bash
qm list
```
Listar contenedores:
```bash
pct list
```
Migrar las máquinas a otro nodo:
```bash
qm migrate 100 pve2 --online
```
Migrar contenedores:
```bash
pct migrate 101 pve2
```
Verificar que el nodo queda vacío:
```bash
qm list
pct list
```

### ¿Por qué se realiza?
Permite reiniciar el nodo sin interrumpir los servicios. Es una de las ventajas fundamentales de un clúster Proxmox.

## Actualizar el nodo
Actualizar repositorios:
```bash
apt update
```

## Actualizar todos los paquetes
```bash
apt full-upgrade
```
Durante el proceso pueden actualizarse:

- Kernel Linux
- Proxmox VE
- QEMU
- LXC
- Corosync
- Herramientas del sistema

> **Nota:** Si durante el proceso de actualización anterior obtenemos un error de falta de espacio en disco, es probable que sea debido a falta de espacio en la partición /boot. En ese caso borramos de ese directorio los archivos "initrd.img-xxxx" y "vmlinuz-xxx" correspondientes a kernels de actualizaciones anteriores.

## Eliminar paquetes obsoletos
```bash
apt autoremove
```

## Verificar si es necesario reiniciar
Comprobar la versión del kernel instalada:
```bash
dpkg -l | grep proxmox-kernel
```
Comprobar el kernel actualmente cargado:

```bash
uname -r
```
Si no coinciden, será necesario reiniciar.

## Reiniciar el nodo
```bash
reboot
```
Esperar a que el nodo vuelva a incorporarse al clúster.

## Validar el nodo actualizado
Verificamos versión:
```bash
pveversion
```
Ejemplo:
```bash
pve-manager/9.1.x
```

## Verificar el estado del clúster
```bash
pvecm status
```
Comprobar:
```text
Quorate: Yes
```

## Verificar servicios críticos
```bash
systemctl status pve-cluster
systemctl status corosync
systemctl status pvedaemon
systemctl status pveproxy
```

Todos deben aparecer como:
```text
active (running)
```

## Repetir en el resto de nodos
Una vez validado el primer nodo:

1. Migrar cargas desde pve2.
2. Actualizar pve2.
3. Reiniciar pve2.
4. Validar pve2.

Después:

1. Migrar cargas desde pve3.
2. Actualizar pve3.
3. Reiniciar pve3.
4. Validar pve3.

## Comprobar todos los nodos
```bash
pvecm nodes
```
Deben aparecer todos online.

## Verificar máquinas virtuales

```bash
qm list
```

## Verificar contenedores
```bash
pct list
```

## Verificar almacenamiento
```bash
pvesm status
```

## Verificar logs
```bash
journalctl -p err -b
```
Buscar errores relacionados con:

- Corosync
- Ceph
- QEMU
- Almacenamiento compartido

## Riesgos y buenas prácticas

### Nunca actualizar todos los nodos a la vez
Un reinicio simultáneo puede provocar:

- Pérdida de quórum.
- Caída del clúster.
- Interrupción de servicios.

### Mantener copias de seguridad
Antes de cualquier actualización:
```bash
vzdump <VMID>
```
o utilizar la infraestructura de backup corporativa.

### Actualizar primero un entorno de pruebas
La práctica recomendada es:
```text
Laboratorio
    ↓
Preproducción
    ↓
Producción
```

### Verificar compatibilidad
Especial atención a:

- Ceph
- Drivers de almacenamiento
- Plugins de backup
- Integraciones externas

## Resumen del procedimiento
1. Verificar estado del clúster.
2. Migrar las cargas del nodo.
3. Ejecutar `apt update`.
4. Ejecutar `apt full-upgrade`.
5. Reiniciar el nodo.
6. Validar servicios y clúster.
7. Repetir en el siguiente nodo.
8. Realizar comprobaciones finales.