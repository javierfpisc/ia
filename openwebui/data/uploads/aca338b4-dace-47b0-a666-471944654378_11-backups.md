# Práctica: Gestión de Backups en Proxmox VE

## Backups en Proxmox VE. Modo sencillo
Para poder ejecutar backups de nuestros recursos, MVs, será necesario disponer de un Storage preparado para ello. Por defecto el Storage **local** tiene habilitada la opción de almacenar backups, por lo que podemos utilizarlo para ello.

Vamos a crear un backup de nuestra MV 100 en el almacenamiento local, para ello ejecutamos desde **pve1**:
```bash
vzdump 100 --storage local --mode snapshot --compress zstd
```

## Backups en Proxmox VE. Despliegue e Integración de Proxmox Backup Server (PBS)
A continuación se presenta la guía detallada para la instalación y configuración de **Proxmox Backup Server (PBS)** en un entorno **Proxmox VE**.

### Introducción
**Proxmox Backup Server** es una solución de copia de seguridad de nivel empresarial optimizada para entornos virtuales. Su integración con Proxmox VE permite realizar copias de seguridad incrementales, deduplicadas y cifradas, reduciendo significativamente el uso de almacenamiento y la carga de red.

### Preparación de la Máquina Virtual
Para este laboratorio, utilizaremos una base de Debian instalada previamente.

1.  **Clonación**: Realiza un clon de la máquina base (ID 100) asignándole el ID 500 y el nombre `pbs`.
2.  **Configuración de Red**: Accede a la consola de la nueva MV y edita el archivo `/etc/network/interfaces`:
    *   **IP**: `192.168.56.99/24`
    *   **Gateway**: `192.168.56.11` (IP de gestión del nodo `pve1`).
3.  **Configuración de DNS**: Edita `/etc/resolv.conf` y añade un servidor DNS para permitir la resolución de nombres externa:
    ```bash
    nameserver 8.8.8.8
    ```

### Acceso a Internet mediante Masquerading (NAT)
Dado que la MV utiliza un nodo de Proxmox como gateway, debemos configurar el host para que reenvíe el tráfico y actúe como un router.

**En el nodo físico (pve1):**
Ejecuta el siguiente comando para permitir que la MV salga a internet a través de la interfaz física del host:
```bash
iptables -t nat -A POSTROUTING -j MASQUERADE
```
> **Nota**: El *Masquerading* permite que dispositivos con IPs privadas accedan a redes externas utilizando la IP del host. Asegúrese de que el reenvío de IP (`ip_forward`) esté activo en el kernel del host.

### Configuración de Repositorios (Debian Trixie)
Proxmox VE 9 se basa en **Debian 13 (Trixie)**. Debemos asegurar que las fuentes de software sean las correctas.

**En la MV PBS:**
Edita `/etc/apt/sources.list` y añade los repositorios oficiales de Debian Trixie (Principal, Actualizaciones y Seguridad) siguientes:
```bash
# Repositorio principal
deb http://deb.debian.org/debian trixie \
main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian trixie \
main contrib non-free non-free-firmware

# Actualizaciones (bugfixes antes de point release)
deb http://deb.debian.org/debian trixie-updates \
main contrib non-free non-free-firmware
deb-src http://deb.debian.org/debian trixie-updates \
main contrib non-free non-free-firmware

# Seguridad
deb http://security.debian.org/debian-security trixie-security \
main contrib non-free non-free-firmware
deb-src http://security.debian.org/debian-security trixie-security \
main contrib non-free non-free-firmware
```

Posteriormente, instalaremos `openssh-server` para gestionar más cómodamente la MV y la herramienta gpg para añadir las claves del repositorio PBS:
```bash
apt update
apt install -y openssh-server gpg
```
> **Nota**: Tras instalar SSH, edita `/etc/ssh/sshd_config` para habilitar `PermitRootLogin yes` si quieres administrar la máquina directamente como root. También será necesario establecer la directiva `PasswordAuthentication yes`

Reinica ssh:
```bash
service ssh restart
```

### Instalación de Proxmox Backup Server
Para instalar PBS sobre Debian, añadiremos el repositorio "No-Subscription" de Proxmox.

1.  **Añadir Repositorio PBS**:
    ```bash
    echo "deb http://download.proxmox.com/debian/pbs \
    trixie  pbs-no-subscription" > /etc/apt/sources.list.d/pbs.list
    ```
2.  **Importar Clave GPG**: Descarga e instala la clave oficial para verificar la autenticidad de los paquetes:
    ```bash
    wget -qO - \
    https://enterprise.proxmox.com/debian/proxmox-release-trixie.gpg  \
    | gpg --dearmor -o /etc/apt/trusted.gpg.d/proxmox.gpg
    ```
3.  **Instalación**:
    ```bash
    apt update
    apt install proxmox-backup-server
    ```

### Configuración Inicial en PBS (Interfaz Web)
Una vez finalizada la instalación, el servidor escucha en el puerto **8007**.

1.  **Acceso**: Abre un navegador y entra en `https://192.168.56.99:8007`.
2.  **Creación de Datastore**: Un *Datastore* es el lugar físico donde se guardarán los backups. Define un **Datastore** desde la interfaz de PBS, **Datastore > Add Datastore**:
    *   En local en la ruta `/mnt/backups`.

### Configuración de Alta Disponibilidad (HA)
Para garantizar que nuestro servidor de backups esté siempre operativo, lo añadiremos al gestor de HA del clúster.

1.  **Crear Recurso**: Añade la MV 500 al sistema de HA (Datacenter->HA).
2.  **Afinidad de Nodo**: Establece una regla de afinidad hacia el nodo `pve1` de tipo **estricta**.
    > **Aclaración**: Una afinidad estricta para un solo nodo significa que, si `pve1` falla, la MV **no se reiniciará en otro nodo**. Esto se suele hacer cuando el recurso depende de hardware o redes específicas que solo existen en ese servidor físico.

### Vinculación de Proxmox VE con PBS
El paso final es decirle al hipervisor que utilice el nuevo servidor como destino de sus copias de seguridad.

1.  **Obtener Fingerprint**: En la MV PBS, ejecuta:
    ```bash
    proxmox-backup-manager cert info
    ```
    Copia la cadena hexadecimal del certificado (Fingerprint).
2.  **Añadir Almacenamiento**: En la interfaz de Proxmox VE, navegue a **Datacenter > Storage > Add > Proxmox Backup Server**.
3.  **Información Requerida**:
    *   **ID**: Nombre para identificar el storage (ej. `pbs-storage`).
    *   **Server**: `192.168.56.99`.
    *   **Username**: `root@pam` (o el usuario configurado en PBS).
    *   **Password**: La contraseña de root de la MV PBS.
    *   **Datastore**: El nombre del datastore creado en el paso 5.
    *   **Fingerprint**: Pega la cadena obtenida anteriormente.

Al finalizar, el nuevo almacenamiento aparecerá disponible en todo el clúster para realizar copias de seguridad inmediatas o programadas.

