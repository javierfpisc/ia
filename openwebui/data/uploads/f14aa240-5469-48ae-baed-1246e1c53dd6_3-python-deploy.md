# Automatización de Despliegues con Python y API de Proxmox

## Introducción
La automatización mediante la **API RESTful** de Proxmox permite gestionar infraestructuras de forma programática, eliminando tareas repetitivas y permitiendo la integración con flujos de trabajo DevOps. En esta práctica, prepararemos una plantilla base y configuraremos un **Token de API** para permitir que un script de Python realice despliegues automáticos.

Para esta práctica utilizaremos los artefactos de despliegue del directorio **tools/python**, dentro de ese directorio disponemos de varios scripts python que ejecutan distintos aspectos de la lógica de despliegue. Además también tendremos un archivo **config.yaml** que describe la infraestructura:

* **xxxxx.py**: Scripts en python para lanzar procesos de creación, borrado o actualización de de MVs en proxmox a partir de un template dado
* **config.yaml**: Archivo que define la estructura a crear, básicamente son las MVs que se generarán a partir del template con sus características correspondientes.

---

## 1. Preparación de la Plantilla (Template) con Cloud-Init
Preparemos la plantilla a partir de la cual se clonarán las MVs de nuestro aprovisionamiento masivo a partir de una imagen **Cloud-Init** de Debian 13. Para ello ejecutaremos los siguientes pasos en `pve1`

### Descarga de imagen cloud-init
```bash
wget https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2
```

### Creación de MV a partir de imagen cloud-init
```bash
qm create 9000 \
    --name debian13-cloud \
    --memory 1024 \
    --cores 1 \
    --net0 virtio,bridge=vmbr0
```

### Importación del disco
Importamos:
```bash
qm importdisk 9000 debian-13-genericcloud-amd64.qcow2 ceph-rbd
```
Conectamos el disco a la MV:
```bash
qm set 9000 \
    --scsihw virtio-scsi-pci \
    --scsi0 ceph-rbd:vm-9000-disk-0
```

### Añadir disco cloud-init
```bash
qm set 9000 --ide2 ceph-rbd:cloudinit
```

### Establecemos disco de arranque
```bash
qm set 9000 --boot order=scsi0
```

El uso de plantillas es fundamental para el despliegue rápido de máquinas virtuales completas, ya que permite crear clones de forma casi instantánea. Accederemos al nodo **pve1** del clúster Proxmox, a través del comando `vagrant ssh` y ejecutaremos los comandos siguientes.

### Convertir a Plantilla
Una vez configurada la VM 9000, la convertimos en un **Template**. Esto la marca como de solo lectura y permite que sea el origen de futuros clones.
```bash
qm template 9000
```

### Par de claves SSH
En el diretorio **keys** disponemos de un par de claves ssh, generadas para la ocasión, y necesarias para la configuración remota de las instancias de MVs creadas en el proceso de despliegue. En el despliegue el propio script `deploy.py` inyectará la clave pública en cada instancia para facilitar posteriores accesos remotos de forma automática a cada MV.

---

## 2. Configuración de Seguridad y Autenticación contra el API Proxmox
Para que aplicaciones externas (como nuestro script de Python) interactúen con la API sin usar la contraseña de root, Proxmox utiliza **Tokens de API**.

### Paso 2.1: Crear Token de Autenticación
Crearemos un token llamado `automation` para el usuario `root`. El parámetro `--privsep 0` indica que el token tendrá los mismos privilegios que el usuario asociado.
```bash
pveum user token add root@pam automation --privsep 0
```
!!!IMPORTANTE 
    El valor del token (el "Secret") **solo se mostrará una vez** en pantalla. Si se pierde, deberá generar uno nuevo, ya que Proxmox no permite recuperarlo por seguridad.

### Paso 2.2: Configurar el archivo de despliegue
Abre el archivo `config.yaml` y añada la información del token siguiendo el formato de autorización de la API:
`token_value: TU-TOKEN-SECRET`.

---

## 3. Automatización con Script Python
La gestión avanzada mediante **Python** se apoya en el uso de entornos virtuales para mantener las dependencias aisladas y seguras. Antes de lanzar el script desde nuestro equipo de trabajo vamos a ejecutar los siguientes pasos de preparación.

### Paso 1: Preparar el Entorno Virtual
Es una buena práctica de administración utilizar `venv` para evitar conflictos entre librerías del sistema y del proyecto. Ejecutamos desde el directorio en el que reside el script **deploy.py**, esto es en el host, no en la MV, los siguientes comandos para constituir el entorno virtual de python:

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno. 
# Este comando habrá que ejecutarlo cada vez que trabajemos con el entorno virtual
source venv/bin/activate

# Instalar las librerías necesarias (ej: proxmoxer, requests, pyyaml)
pip3 install -r requirements.txt
```

### Paso 2: Ejecutar el Despliegue
Una vez configurado el entorno y las credenciales en el archivo YAML, lanzamos el script para que realice las llamadas a la API de Proxmox.
```bash
python3 deploy.py config.yaml
```

### Explicación del script deploy.py
El script de Python **tools/python/deploy.py** utiliza la librería `proxmoxer` para interactuar con la **API RESTful** de Proxmox VE. Su objetivo es automatizar el despliegue de máquinas virtuales a partir de una plantilla, siguiendo un flujo de trabajo lógico de administración de sistemas. A continuación se detalla la estructura y los pasos ejecutados:

#### Estructura de Funcionamiento
El script está diseñado de forma modular, dividiendo las tareas en funciones específicas para facilitar el mantenimiento y la gestión de errores:

1.  **Carga de Configuración (`load_config`):** Lee el archivo `config.yaml` que contiene los parámetros de conexión al clúster, los datos de la plantilla y la lista de máquinas virtuales a crear.
2.  **Conexión y Autenticación (`connect_proxmox`):** Establece la conexión con el servidor Proxmox. Utiliza **Tokens de API** (`token_name` y `token_value`), lo cual es una mejor práctica de seguridad que evita el uso de contraseñas de usuario real en scripts.
3.  **Gestión de Tareas Asíncronas (`wait_task`):** Dado que operaciones como el clonado son procesos que tardan tiempo en completarse en el servidor, esta función monitoriza el **UPID** (identificador único de tarea) y detiene el script hasta que Proxmox confirma que la tarea ha finalizado con éxito ("OK").
4.  **Bucle de Despliegue (`deploy`):** Itera sobre la lista de VMs definidas en el archivo YAML, ejecutando secuencialmente el clonado, la configuración y el arranque. Incluye control de excepciones para que, si una VM falla, el script continúe con la siguiente.

#### Pasos Ejecutados en el Despliegue
Por cada máquina virtual definida en la configuración, el script realiza los siguientes pasos técnicos:

*   **Paso 1: Clonado Full (`clone_vm`)**
    Se realiza un clon completo (`full=1`) desde la plantilla especificada hacia el nodo de destino. A diferencia de un clon enlazado, el **clon completo** crea un disco independiente, lo que permite mover la VM entre almacenamientos (como Ceph) con mayor flexibilidad.
*   **Paso 2: Configuración de Recursos (`configure_vm`)**
    Una vez creada la VM, el script ajusta los parámetros de hardware "en caliente" (hot-plug):
    *   **CPU y RAM:** Asigna el número de núcleos (`cores`) y la cantidad de memoria especificada.
    *   **SSH**: Define los parámetros de Cloud-Init, usuario inicial, contraseña y clave pública SSH que se instalará automáticamente para permitir el acceso remoto seguro.
    *   **Red:** Configura la interfaz `net0` utilizando el modelo `virtio` (paravirtualizado para mejor rendimiento) conectado al bridge predeterminado `vmbr0`.
    *   **Red (IP estática):** Utiliza parámetros de **Cloud-Init** (`ipconfig0`) para inyectar la dirección IP y la puerta de enlace directamente en el sistema operativo invitado sin intervención manual.
*   **Paso 3: Arranque (`start_vm`)**
    Finalmente, tras verificar que la configuración es correcta, envía la orden de inicio a la máquina virtual para que los servicios queden operativos.

**Nota de Seguridad:** El script deshabilita las advertencias de certificados SSL (`urllib3.disable_warnings()`), lo cual es habitual en laboratorios con certificados auto-firmados generados por la CA interna de Proxmox.

## Script service.py
El script service.py permite realizar tareas de administración y mantenimiento de forma centralizada sobre todas las máquinas virtuales definidas en el archivo `config.yaml`. Para ello, establece una conexión SSH con cada una de las VMs utilizando la clave privada especificada en la configuración y ejecuta secuencialmente la lista de comandos incluida en la sección **commands** del fichero. Este enfoque facilita la automatización de operaciones repetitivas, como la instalación de software, la actualización del sistema, el reinicio de servicios o la ejecución de tareas de configuración, permitiendo administrar de manera uniforme toda la infraestructura desplegada con un único comando. Podemos ejecutarlo mediante:
```bash
python3 service.py config.yaml
```

## Script delete.py
En el mismo directorio en que reside el script **deploy.py** disponemos de otro script, **delete.py**, el cual usaremos para limpiar el entorno de nuestro laboratorio y así poder repetir las pruebas sin acumular "basura" en nuestro Proxmox. Para ejecutarlo simplemente añadiremos en al sección `delete` del archivo **config.yaml** la lista de las MVs que queremos eliminar. A continuación ejecutamos el script:
```bash
python3 delete.py config.yaml
```

---

## Conceptos Clave
*   **API RESTful:** Interfaz que permite a sistemas externos (scripts) controlar Proxmox enviando comandos en formato JSON.
*   **Tokens de API:** Método de acceso seguro que evita exponer contraseñas reales en scripts de automatización.
*   **Idempotencia:** En automatización, buscamos que el script pueda ejecutarse varias veces asegurando que el estado final sea siempre el deseado.
*   **Seguridad:** Aunque en este laboratorio usamos el usuario `root`, en entornos de producción se recomienda crear usuarios específicos con roles limitados mediante el sistema **RBAC** (Control de Acceso Basado en Roles).