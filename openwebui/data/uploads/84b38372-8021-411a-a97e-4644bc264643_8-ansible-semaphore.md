# Mejorando la interacción con Ansible: Semaphore UI  
En esta práctica veremos una de las posibles herramientas que nos permite mejorar nuestra forma de interactuar con las herramientas de automatización.

## Introducción a Semaphore UI
**Semaphore UI** es una interfaz web para automatizar y gestionar la ejecución de Ansible de forma centralizada. Permite definir inventarios, repositorios Git, credenciales y Task Templates desde una interfaz gráfica, evitando tener que ejecutar manualmente los playbooks desde la línea de comandos.

Sus principales funciones y usos son:

* Ejecutar playbooks de Ansible mediante plantillas de tareas.
* Gestionar inventarios de hosts y grupos.
* Integrarse con repositorios Git para obtener playbooks y configuraciones.
* Administrar credenciales y claves SSH de forma centralizada.
* Programar ejecuciones periódicas de tareas.
* Consultar el historial y los logs de las ejecuciones.
* Facilitar la delegación y gestión de automatizaciones entre distintos usuarios.

Además de gestionar ejecuciones de Ansible, Semaphore permite centralizar y automatizar diferentes tareas de infraestructura y despliegue desde una interfaz web. Entre sus principales posibilidades están:

* OpenTofu/Terraform: ejecutar tareas de infraestructura como código, por ejemplo plan y apply.
* Automatización mediante scripts: ejecutar comandos y scripts personalizados.

En conjunto, Semaphore puede utilizarse como una capa de automatización y gestión sobre herramientas como Ansible (principalmente) y OpenTofu, proporcionando una interfaz web desde la que usuarios que no necesitan conocer todos los comandos de estas herramientas pueden ejecutar y controlar los procesos. Esto es especialmente útil para centralizar, simplificar y automatizar la ejecución de tareas de administración de sistemas e infraestructura. 

## Requisitos Previos e instalación
Una de sus ventajas es que es sumamente sencillo de desplegar y utilizar. En nuestro caso necesitaremos un entorno de ejecución docker y conocer ligeramente el funcionamiento de Ansible. Dentro del directorio **tools/ansible/semaphore** disponemos de los recursos para su despliegue.

### Instalación de Semaphore
Usaremos para el despliegue de la herramienta el archivo `docker-compose.yml` del directorio **tools/ansible/semaphore**. Desde ese directorio ejecutamos:
`docker compose up -d`. La ejecución de este comando levantará un container corriendo un servicio web en el que corre la aplicación en la URL **http://localhost:3003**. Además:

* Se han definido en el despliegue las credenciales de acceso para el usuario **admin** y password **abc123.**
* Utiliza como motor de persistencia **SQLite**
* Mapea el directorio dentro de la ruta **ansible** dentro del container, esto nos dará acceso a elementos importantes, como los inventarios.

---

## Artefactos gestionables mediante Semaphore
La configuración es muy sencilla. Semaphore basa su uso en repositorios git, desde donde toma los artefactos para la ejecución. Por tanto a continuación veremos los elementos que es necesario definir.

### Claves de acceso (Keystore)
Los primeros elementos que es preciso definir son las claves de acceso para acceder a los repositorios git donde disponemos de los artefactos de automatización así como a los hosts del inventario. Desde la sección `Key Store` definimos una `Key`:

* Tipo **SSH Key** dentro de la sección **Local**
* **Key Name: ssh-private-key**
* **Valor** lo copiamos del contenido del archivo de clave privada ssh en la ruta **tools/keys/id_lab_ed255519**.

Recordemos que las MVs de Proxmox utilizadas en las prácticas de Ansible, y  a las que apunta el inventario que se ha definido, disponen de la clave pública correspondiente para permitir el acceso SSH a través de Ansible.

### Inventarios
El siguiente elemento es el archivo de inventario, sección `Inventory`. Desde allí podemos definir el inventario bien de forma estática, es decir directamente proporcionando el contenido del archivo, o bien indicando una ruta dentro del sistema de archivos del container que apunte al inventario. En nuestro caso usaremos la última opción, teniendo en cuenta que hemos mapeado el directorio de despliegue dentro de la ruta `/ansible` del container. Por tanto creamos un nuevo elemento `Inventory` de nombre **hosts** con las siguientes propiedades:

* **Tipo:** File
* **Path:** /ansible/inventory/hosts.yml
* **User Credentials**: ssh-private-key

El último campo es necesario para que Ansible pueda acceder a los hosts del inventario, para ello es necesario proporcionar algún método de autenticación. Ésto, cuando hacemos uso de Ansible "directamente", se puede definir en el propio inventario, pero por motivos de seguridad Semaphore fallará si especificamos alguna clave dentro del mismo. La forma correcta de proceder es utilizar una de las claves definidas en el Keystore, precisamente la definida anteriormente.

### Acceso a repositorios
Otro elemento fundamental es la definición de repositorios Git desde los cuales se tomarán los elementos de despliegue, como los Ansible Playbooks. Para poder acceder a ellos debemos definirlos en la interfaz y configurar el acceso a ellos. Para ello desde la sección `Repositories` crearemos un nuevo elemento de este tipo, con las siguientes características:

* **Name:** despliegue_ud3
* **Git URL:** git@github.com:javierfp-isc/despliegue_ud3.git
* **Branch/Tag**: main
* **Access Key**: ssh-private-key (definida en el paso anterior)

!!! Nota
        El repositorio anterior está configurado para permitir el acceso SSH con la clave correspondiente

### Task Templates
Por último definiremos las Task Templates, es decir los elementos de ejecución de Semaphore. Crearemos una Task Template para una tarea de tipo **Ansible Playbook**. Los elementos a definir son los siguientes:

* **Name:** test-playbook
* **Repository:** despliegue_ud3
* **Path to playbook file**: tools/ansible/basico/tasks.yml (ruta dentro del repositorio del archivo de playbook)
* **Inventory:** hosts (El nombre dado al archivo de inventario definido en Inventory)

Los campos anteriores son los elementos mínimos a definir, sin embargo en la interfaz de definición del Task Template encontramos otros muchos elementos:

* **Advanced options**: permite indicar parámetros de ejecución extra y pedir al usuario valores de variables antes de lanzar la ejecución
* **Prompts**: permite inyectar parámetros antes de la ejecución
* **Ansible prompts y Ansible options**: permite definir parámetros restrictivos en la ejecución así como pedirlos al usuario

También encontramos una sencilla funcionalidad de Workflow al principio de la sección **Common Options**, que nos permite "enlazar" la **Task**, con fases **Build y Deploy**.

---

## Lanzamiento del Task Template y comentarios finales
El último paso es lanzar el proceso de ejecución definido en la Task Template. Para ello simplemente activamos el icono de tipo botón "Play", o bien dentro de la definición del Task Template activamos el lanzamiento a través del botón "RUN".

Como podemos observar el uso de Semaphore añade funciones interesantes a la gestión de la automatización con Ansible, no es tanto la facilidad o agilidad de uso, sino la posibilidad de :

* Tener un Dashboard de las ejecuciones de Tasks con los detalles de cada una de ellas (usuario, duración, hora, estado de terminación, logs generados...)
* Posibilidad de programar las ejecuciones
* Definición de Variable Groups, lo cual permite reutilizar variables entre varias tareas
* Soporte a equipos de usuarios y roles
* Pueden definirse Workflows
* Permite integraciones (Integrations) con servicios externos








