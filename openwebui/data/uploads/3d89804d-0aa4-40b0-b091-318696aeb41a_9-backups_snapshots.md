# Snapshots y Backups en Proxmox VE

## 1. Snapshots (Instantáneas)

### Concepto y Función
Un **snapshot** captura el estado de una máquina virtual (VM) o un contenedor (CT) en un momento específico. Incluye la configuración del recurso y, de forma opcional en las VMs, el contenido de la memoria RAM (estado de ejecución).

### Usos principales
*   **Reversión rápida:** Volver a un estado estable antes de realizar cambios arriesgados (actualizaciones de software, pruebas de configuración).
*   **Pruebas temporales:** Permite realizar "rollbacks" casi instantáneos si algo falla.

### Gestión y Requisitos
*   **Almacenamiento:** No todos los almacenamientos soportan snapshots de forma nativa. Es ideal utilizar **ZFS, Ceph o LVM-thin** para una gestión eficiente. En almacenamientos basados en ficheros (NFS/CIFS), se requiere el formato de disco **qcow2**.
*   **Comandos:**
    *   VM: `qm snapshot <vmid> <nombre>`.
    *   CT: `pct snapshot <vmid> <nombre>`.
*   **Limitaciones:** Los snapshots no son copias de seguridad externas; dependen de la integridad de los discos originales y del almacenamiento local.

---

## 2. Backups y Restauración en Proxmox VE

A diferencia de los snapshots, que son dependientes del almacenamiento original, los backups en Proxmox son **copias completas e independientes** que incluyen tanto los archivos de configuración del recurso como la totalidad de sus datos.

### Modos de Ejecución (Consistencia vs. Disponibilidad)

El administrador debe elegir el modo según la criticidad del servicio y la tolerancia al tiempo de inactividad.

#### Para Máquinas Virtuales (KVM)
*   **Modo Stop (Parada):** Proporciona la **máxima consistencia**. Realiza un apagado ordenado de la VM, ejecuta el backup y la vuelve a encender.
*   **Modo Snapshot (Live Backup):** Es el que ofrece el **menor tiempo de inactividad**. Utiliza un mecanismo de "live backup" de QEMU que copia los bloques de datos mientras la VM sigue funcionando. Si el *Guest Agent* está activo, el sistema congela temporalmente el sistema de archivos para mejorar la integridad.
*   **Modo Suspend (Suspensión):** Suspende la VM antes de llamar al modo snapshot. Se mantiene principalmente por compatibilidad, pero suele preferirse el modo snapshot directo.

#### Para Contenedores (LXC)
*   **Modo Stop:** Detiene el contenedor durante todo el proceso. Puede implicar tiempos de caída largos.
*   **Modo Suspend:** Utiliza `rsync` para copiar datos a una ubicación temporal, suspende el contenedor para copiar los cambios finales y lo reanuda. Minimiza la caída pero requiere espacio extra en disco.
*   **Modo Snapshot:** Utiliza las facultades del almacenamiento subyacente (como ZFS o Ceph). El contenedor se suspende brevemente para asegurar la consistencia antes de crear la instantánea temporal.

---

### Destinos de Almacenamiento

Proxmox permite definir diversos destinos para las copias:

*   **Proxmox Backup Server (PBS):** La opción recomendada. Permite **deduplicación** a nivel de bloque, copias incrementales (solo se envía lo que ha cambiado), cifrado del lado del cliente y verificación de integridad.
*   **Almacenamientos de Red (NFS/CIFS):** Almacenan los backups como archivos regulares comprimidos.
*   **Directorio Local:** Generalmente ubicado en `/var/lib/vz/dump`.

---

### Gestión de Retención (Pruning)

Para evitar que el almacenamiento se agote, se utilizan las opciones de **poda (pruning)** que definen cuántas copias mantener en una jerarquía temporal:

*   `keep-last`: Número de copias más recientes.
*   `keep-daily`: Copias de los últimos días.
*   `keep-weekly/monthly/yearly`: Archivos a largo plazo.

**Nota:** Es posible marcar un backup específico como **Protegido** para evitar que sea eliminado automáticamente por las reglas de retención.

---

### Funcionalidades Avanzadas

#### Restauración en Vivo (Live-Restore)
Exclusivo para VMs en **Proxmox Backup Server**. Permite iniciar la VM inmediatamente después de comenzar la restauración. Los datos se copian en segundo plano, priorizando los bloques que el sistema operativo está intentando leer en ese momento.

#### Restauración de Archivos Individuales
Permite navegar por el contenido de un backup de VM o contenedor directamente desde la interfaz web y descargar archivos específicos sin necesidad de restaurar el disco completo (Solo disponible con PBS).

#### Backup Fleecing
Mecanismo para mejorar el rendimiento de E/S durante un backup en caliente. Utiliza una imagen temporal (caché) para almacenar los datos "viejos" cuando la VM intenta escribir en bloques que aún no han sido respaldados, evitando que la VM se ralentice por la velocidad del almacenamiento de backup.

---

### Comandos Esenciales de Línea de Interfaz

| Acción | Comando |
| :--- | :--- |
| Crear backup manual | `vzdump <VMID> --storage <ID_Almacenamiento> --mode snapshot` |
| Restaurar una VM | `qmrestore <archivo_backup> <nuevo_VMID>` |
| Restaurar un contenedor | `pct restore <nuevo_VMID> <archivo_backup>` |
| Extraer configuración | `pvesm extractconfig <volid_del_backup>` |
| Listar backups en un storage | `pvesm list <ID_Almacenamiento> --content backup` |

#### Advertencia de Seguridad
Si utilizas **cifrado** con Proxmox Backup Server, debes guardar la **clave de cifrado** de forma externa (en un gestor de contraseñas o copia física). Si se pierde la clave, los backups serán totalmente inaccesibles incluso si el servidor Proxmox está intacto.

---

## 3. Cuadro Comparativo

| Característica | Snapshots | Backups (`vzdump`) |
| :--- | :--- | :--- |
| **Objetivo** | Guardar estado previo a un cambio rápido. | Recuperación ante desastres (DR). |
| **Ubicación** | Generalmente en el mismo almacenamiento. | Almacenamiento externo o dedicado. |
| **Independencia** | Depende del disco original. | Totalmente independiente. |
| **Estado de RAM** | Puede guardarlo (solo en VMs). | No guarda el estado de la RAM. |
| **Frecuencia** | Manual o replicación frecuente. | Programada (diaria/semanal). |

---