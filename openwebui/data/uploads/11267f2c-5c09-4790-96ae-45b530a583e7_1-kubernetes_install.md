# Práctica: Instalación de Kubernetes

## Creación de la infraestructura con vagrant en VirtualBox
De modo similar a la **unidad 1**, usaremos un procedimiento de **provisionamiento de los nodos de nuestro clúster kubernetes** de laboratorio automatizado con vagrant. Desde el directorio **vagrant**, ejecutamos:

`vagrant up`

El comando anterior toma como referencia el archivo de despliegue **Vagrantfile** disponible en el directorio, para crear una infraestructura de 3 nodos:

* **kuber1**: Con dirección IP en la interfaz solo anfitrión->192.168.56.41
* **kuber2**: Con dirección IP en la interfaz solo anfitrión->192.168.56.42
* **kuber3**: Con dirección IP en la interfaz solo anfitrión->192.168.56.43

Los nodos dispondrán de **4GB de RAM** y **2 cores de CPU**.

!!!Nota
    Si disponéis de un equipo con más de 16GB de RAM y más de 8 cores de CPU se podrían ampliar los recursos de cada nodo modificando en el archivo Vagrantfile la sección **nodes**

## Actualización del sistema e instalación de Kubernetes con vagrant y VirtualBox
Tras ejecutar el despliegue de los nodos con vagrant actualizamos las MVs a la versión 13 de Debian. Para ello, desde el directorio **vagrant**, ejecutamos:
```bash
for node in kuber1 kuber2 kuber3; do
  vagrant ssh $node -c "cat > /tmp/install_kubernetes.sh" < install_kubernetes.sh
  vagrant ssh $node -c "chmod a+x /tmp/install_kubernetes.sh"
done
```

El bucle anterior copia el script de instalación en cada una de las nodos MVs que serán los nodos del clúster. A continuación, **para cada nodo** entramos con vagrant ssh `<nodo>` y ejecutamos:
```bash
sudo -i
bash -c /tmp/install_kubernetes.sh
```

## Pasos de ejecución del script:
El script de automatización utilizado está diseñado para transformar una instalación base de Debian en un nodo de **Proxmox VE**, configurando el entorno para que la instalación sea desatendida y el sistema se actualice a una versión específica basada en Debian Trixie.,

A continuación se detallan los pasos ejecutados:

### Preparación del Entorno No Interactivo
El script comienza configurando variables de entorno para que las herramientas de gestión de paquetes no soliciten intervención humana durante la instalación. Esto incluye el modo de reinicio automático para servicios que se actualicen. Además, utiliza `set -e` para asegurar que el script se detenga inmediatamente si ocurre cualquier error durante la ejecución.

### Configuración de Locales e Idioma
Se establece el idioma del sistema y la codificación de caracteres a español (`es_ES.UTF-8`). El script genera los locales necesarios y actualiza la configuración del sistema para que este sea el idioma predeterminado en todas las sesiones.

### Preconfiguración de GRUB
Para evitar interrupciones manuales, el script utiliza `debconf-set-selections` para indicar que el cargador de arranque **GRUB** debe instalarse automáticamente en el disco principal. También se configura para que las librerías se reinicien sin preguntar al usuario.

### Credenciales de Acceso
Se asigna una contraseña estática para el usuario **root** (`abc123.`), garantizando que el administrador tenga acceso inmediato tras la conversión del sistema.

### Actualización de Repositorios (Migración a Trixie)
El script realiza un cambio crítico en la configuración de las fuentes de software, sustituyendo las referencias a Debian *Bookworm* por **Debian Trixie**. Esto prepara el sistema para una base de software más reciente, alineada con las versiones experimentales o futuras de Proxmox. Asimismo, elimina los archivos de repositorios empresariales (`pve-enterprise`) que requieren suscripción de pago.

### Actualización del Sistema
Se realiza una actualización completa de todos los paquetes existentes (`full-upgrade`).

### Configuración del entorno previo a nuestra instalación de Kubernetes (k3s)
Preparamos el entorno para la instalación posterior de k3s en los nodos

### Limpieza
Borramos cachés de paquetes


