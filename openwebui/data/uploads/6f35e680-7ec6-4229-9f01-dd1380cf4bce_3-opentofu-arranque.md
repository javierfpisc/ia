# Automatización de la configuración inicial de máquinas virtuales mediante Cloud-Init y OpenTofu

## Objetivo
Al finalizar esta práctica habremos alcanzado los siguientes objetivos:

* Comprender el funcionamiento de Cloud-Init.
* Crear archivos de configuración *cloud-config*.
* Distribuir dichos archivos a Proxmox mediante OpenTofu.
* Asociar un fichero de configuración a una máquina virtual.
* Automatizar la instalación de software durante el primer arranque.
* Ejecutar comandos de configuración del sistema sin intervención manual.
* Verificar que la configuración se ha aplicado correctamente.

!!! Nota
    Para realizar esta práctica es conveniente que se haya realizado, como se indica en uno de los ejercicios de la Unidad, la configuración de red estática de la MV. El no hacerlo no afectará a la práctica en sí, pero el resultado no será completo.

---

## Introducción
En las práctica anterior realizamos un sencillo despliegue con OpenTofu donde únicamente se configuraban aspectos básicos como:

* usuario inicial
* contraseña
* configuración de red

Cloud-Init permite ir mucho más allá siendo posible automatizar completamente la configuración inicial de una máquina:

* instalar paquetes
* modificar archivos de configuración
* crear usuarios
* añadir claves SSH
* habilitar servicios
* ejecutar scripts
* descargar software
* aplicar configuraciones de seguridad

Todo ello ocurre automáticamente durante el **primer arranque** de la máquina.

---

## ¿Qué es Cloud-Init?
Como ya vimos en la sección conceptual de la unidad Cloud-Init es una herramienta presente en la mayoría de distribuciones Linux preparadas para entornos cloud. La secuencia de pasos en las que basa su funcionalidad dependen de que durante el primer arranque la máquina:

1. Detecta la unidad Cloud-Init.
2. Lee la configuración suministrada.
3. Ejecuta todas las instrucciones.
4. Marca la configuración como aplicada.
5. No vuelve a ejecutarla en siguientes reinicios (salvo que se limpie el estado de Cloud-Init).

Por ello se utiliza para realizar la configuración inicial de servidores.

---

## Creación del fichero cloud-config
En esta práctica se utilizará un fichero YAML con el siguiente contenido:
```yaml
#cloud-config
package_update: true
#paquetes a instalar
packages:
  - nginx
  - htop
#comandos a ejecutar
runcmd:
  - systemctl enable nginx
  - systemctl start nginx
```

En este fichero se instruye la realización de las siguientes acciones:

1. Actualiza el índice de paquetes.
2. Instala **nginx**.
3. Instala **htop**.
4. Habilita nginx para futuros reinicios.
5. Arranca inmediatamente el servicio.

---

## Copia del fichero a Proxmox mediante OpenTofu
OpenTofu puede crear automáticamente un fichero dentro del almacenamiento de snippets de Proxmox. Para ello se utilizará el recurso **proxmox_virtual_environment_file** definido dentro del archivo **main.tf**:

Al ejecutar:
```bash
tofu apply
```

OpenTofu copiará automáticamente el fichero al nodo Proxmox.

---

## Puesta a disposición del fichero cloud-init a las máquinas
Una vez creado el fichero, únicamente es necesario indicarle a la máquina virtual que lo utilice.

### Creación de recurso CephFS para almacenamiento de archivos compartido
Para poder tener un almacenamiento compartido y distribuído a nivel de clúster en el que almacenar los snippets, y otros archivos, vamos a utilizar Ceph. Para ello necesitamos crear un recurso del tipo **CephFS**. Para eso, dentro de una **sesión de terminal root en pve1**:
```bash
pveceph mds create #Creamos el MDS, MetaDataServer, asociado al recurso
ceph fs volume create cephfs #Creación del sistema de archivos CephFS
```
A continuación, desde la interfaz WebUI de Proxmox, en **Datacenter->Storage->Add->CephFS** añadimos el recurso correspondiente con:

* **ID: cephfs**
* **FS Name: cephfs**

Una vez creado el **Storage** editamos sus propiedades para almacenar **Content** de tipo **Snippets**

### Aplicación del recurso snippet en el despliegue
Dentro del bloque `initialization` en **main.tf** encontramos:

```terraform
initialization {
  ...

  user_data_file_id = proxmox_virtual_environment_file.cloud_config.id
}
```
La variable `user_data_file_id` indica qué fichero Cloud-Init debe utilizar la máquina durante su primer arranque.

---

## Despliegue

### Configuración de la autenticación SSH en pve1 para transferir en Snippet
Para poder enviar el correspondiente archivo cloud-init al nodo, en nuestro caso pve1, deberemos de utilizar el protocolo SSH, por tanto es necesario configurar la autenticación a través de archivo de **clave pública SSH para el usuario root**. Procedemos del siguiente modo:

* **Habilitemos temporalmente la autenticación SSH** con contraseña para el usuario root, para ello accedemos a pve1, elevamos a root y establecemos una password para ese usuario con el comando `passwd`
* **Tomamos la clave pública SSH desde el directorio tools/keys** y la transferimos al nodo con el comando: `ssh-copy-id -i ./id_lab_ed25519.pub root@192.168.56.11`
* **Dentro del archivo providers.tf** tenemos la otra pieza necesaria para la configuración de la autenticación SSH, dentro del bloque `provider "proxmox" { ...ssh{...}}`

### Ejecución
Desde el directorio en donde disponemos de los artefactos OpenTofu aplicamos la configuración:
```bash
tofu apply
```
OpenTofu realizará automáticamente:

* creación del fichero YAML
* subida al nodo Proxmox
* clonación de la plantilla
* asociación del fichero Cloud-Init
* arranque de la máquina

Tras la ejecución podremos comprobar si efectivamente, entre otras acciones, el archivo cloud-init se copió correctamente en su ubicación. Para ello, desde pve1, podemos consultar el estado del Storage **cephfs** simplemente ejecutando el comando `ls -l /mnt/pve/cephfs/snippets` 

!!!Importante
    Al establecer la configuración de cloud-init a través del archivo el resto de las secciones dentro de **inicialization** en el archivo **main.tf** pueden no tener efecto, por ejemplo la sección **user_account** dejará de aplicarse (por ese motivo se han añadido las líneas en runcmd de creación del usuario y su password)

---

## Consultar el registro de Cloud-Init
Todas las acciones ejecutadas por cloud-init quedan registradas. Dentro de la máquina podemos consultar:
```bash
cat /var/log/cloud-init.log
```
también podemos hacer uso del comando `cloud-init` y todas sus opciones

---

## Conclusiones
Cloud-Init constituye una herramienta fundamental para la automatización del despliegue de infraestructuras. Combinado con OpenTofu y Proxmox, permite que las máquinas virtuales se desplieguen completamente configuradas, reduciendo errores manuales, acelerando el aprovisionamiento y garantizando configuraciones reproducibles. Este enfoque es la base de las prácticas modernas de Infraestructura como Código (IaC) y resulta especialmente útil en entornos docentes, de laboratorio y de producción.
