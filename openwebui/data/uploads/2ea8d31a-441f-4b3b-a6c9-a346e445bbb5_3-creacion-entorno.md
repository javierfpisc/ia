# Preparación del entorno de trabajo
Para trabajar en nuestros entornos de laboratorio necesitaremos instalar un conjunto básico de herramientas en nuestro sistema **Debian 13**. Los procedimientos de instalación se detallan a continuación.

## Dependencias básicas
Como root instalamos una serie de paquetes básicos:
```bash
apt update
apt upgrade -y

apt install -y curl wget ca-certificates gnupg \
    lsb-release build-essential dkms sudo
```

## Instalación de VirtualBox 7.2.16
Descargamos el paquete binario .deb (la versión puede variar) ejecutando el comando:

`wget https://download.virtualbox.org/virtualbox/7.2.16/virtualbox-7.2_7.2.16-174877~Debian~trixie_amd64.deb`

Instalamos el paquete anterior con:

`apt install -y ./$(ls virtualbox*.deb)`

Si aparecen dependencias pendientes ejecutamos:

`apt -f install`

y repetimos el comando anterior. Una vez se ha instalado comprobamos con:

`VBoxManage --version`

A continuación añadimos el usuario de trabajo (no root) a vboxusers. Suponiendo que ejecutamos el comando desde una sesión del usuario y que éste es sudoer, ejecutamos:

`sudo usermod -aG vboxusers $(whoami)`

Por último instalamos el **Extension Pack** para la versión correspondiente. Para ello es necesario acceder directamente a través de la página web de descargas: [Descargas VirtualBox](https://www.oracle.com/virtualization/technologies/vm/downloads/virtualbox-downloads.html).

Desde allí, tras aceptar el acuerdo de licencia, descargamos el archivo de Extension Pack **.vbox-extpack**. Una vez descargado se instala sencillamente con el comando:

`VBoxManage extpack install Oracle_VirtualBox_Extension_Pack-7.2.16.vbox-extpack`

También es posible instarlo abriéndolo con el programa VirtualBox directamente.

## Instalación de Docker
Para la instalación de Docker debemos ejecutar, como root, una serie de pasos. En primer lugar descargamos la clave del repositorio desde el que obtendremos los binarios:
```bash
install -m 0755 -d /etc/apt/keyrings

curl -fsSL \
    https://download.docker.com/linux/debian/gpg \
    -o /etc/apt/keyrings/docker.asc

chmod a+r /etc/apt/keyrings/docker.asc
```
Una vez descargada la clave creamos el archivo del repositorio:
```bash
tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```
Tras lo cual procedemos a actualizar caché local e instalar los paquetes necesarios:
```bash
apt update
apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin
```
Añadimos a nuestro usuario de trabajo al grupo docker, ejecutando con el usuario correspondiente (no root):
```bash
sudo usermod -aG docker $(whoami)
newgrp docker
```

## Instalación de Vagrant
Siguiendo las instrucciones de la página oficial de [Instalación de Vagrant](https://developer.hashicorp.com/vagrant/install) ejecutamos, como root:

`wget -O - https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg`

Añadimos el repositorio:

```bash
echo "deb [arch=$(dpkg --print-architecture) \
signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com \
$(grep -oP '(?<=UBUNTU_CODENAME=).*' \
/etc/os-release || lsb_release -cs) main" \
| tee /etc/apt/sources.list.d/hashicorp.list
```

Por último actualizamos caché e instalamos:

`apt update && apt install vagrant`

## Intalación de Git
Git se instala directamente desde los repositorios oficiales:
```bash
apt update
apt install -y git
```
