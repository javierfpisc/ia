# Despliegue Automatizado de Máquinas Virtuales en Proxmox con OpenTofu

## Artefactos para el despliegue
Tomaremos los contenidos del directorio **tools/opentofu/infra-proxmox-1** como referencia para la siguiente práctica. Los elementos del despliegue residen dentro del directorio **environments/prod** y son los siguientes:

| Archivo | Descripción |
|---|---|
| **`providers.tf`** | Declara el proveedor `bpg/proxmox` (con versión fijada) y configura la conexión a la API de Proxmox (`endpoint`, `api_token`, `insecure`). |
| **`variables.tf`** | Define la interfaz de entrada del entorno: URL de la API, token (sensible), nodo destino, ID de la plantilla y el mapa `vms` con el nombre/ID de cada una de las 3 máquinas a crear. |
| **`main.tf`** | Lógica de despliegue: recurso `proxmox_virtual_environment_vm` iterado con `for_each` sobre `var.vms`, clonando la plantilla indicada para crear las 3 VMs. |
| **`outputs.tf`** | Expone información post-despliegue: direcciones IPv4 (vía QEMU Guest Agent) y el ID asignado en Proxmox para cada VM creada. |
| **`terraform.tfvars.example`** | Plantilla de ejemplo con valores ficticios, versionable en el repositorio, que sirve de guía para crear el archivo real. |
| **`terraform.tfvars`** | Archivo con los valores reales (URL, token, nodo, plantilla). Contiene datos sensibles y **no se sube al repositorio** (excluido vía `.gitignore`). |

Los elementos anteriores son los artefactos mínimos para el despliegue. Las responsabilidades de cada archivo están claras en la descripción.

### terraform.tfvars
Crearemos una versión específica de las variables que es necesario definir para nuestro despliegue. Para ello comenzaremos haciendo una copia del archivo de ejempo **template.tvars.example**:
```bash
cp terraform.tfvars.example terraform.tfvars
```
En el archivo creado **terraform.tfvars** definiremos los aspectos específicos para nuestro despliegue:
```bash
proxmox_api_url   = "https://192.168.56.11:8006/"
proxmox_api_token = "admin@pve!opentofu=AQUI IRÁ EL TOKEN GENERADO MÁS ABAJO"
target_node       = "pve1"
vm_template_id    = 9000
```

### Creación del usuario Proxmox, asignación de role y Token de autenticación
Comprobamos, en uno de los nodos del clúster, los usuarios disponibles (ejecutamos todos los comandos que siguen como root):
```bash
pveum user list
```
Si en el listado anterior no aparece el usuario **admin@pve** lo crearemos con el siguiente comando:
```bash
pveum user add admin@pve --comment "Administrador de infraestructura"
```
Para simplificar asignamos a continuación el role **Administrator**:
```bash
pveum aclmod / -user admin@pve -role Administrator
```
Por último creamos el Token para el usuario (la opción -privsep 0 permite que el Token herede los permisos del usuario)
```bash
pveum user token add admin@pve opentofu --privsep 0
```
El comando anterior mostrará el Token creado. Específicamente nos interesa la *key* **value** que es la que almacena el valor del Token que deberemos de añadir al final de la variable **proxmox_api_token** (a continuación del admin@pve!opentofu=).

!!!Necesario
    En el archivo terraform.tvars anterior añadimos el valor del Token value al final de la variable proxmox_api_token

## Ejecución del despliegue
Ejecutamos desde el directorio **tools/opentofu/infra-proxmox-1/environments/prod** los comandos:
``` bash
tofu init
```
El comando anterior se ejecuta una vez al crear el proyecto y después cada vez que cambian los proveedores o módulos. Su función es preparar el proyecto. Ejecuta los siguientes pasos:

* Lee todos los archivos *.tf.
* Descarga los proveedores (por ejemplo bpg/proxmox).
* Descarga módulos remotos si los utilizas.
* Crea el directorio:.terraform/
* Crea o actualiza: .terraform.lock.hcl

El siguiente paso será ejecutar:
```bash
tofu plan
```
Al ejecutar el comando anterior OpenTofu compara tres cosas:

* Lo que pone en tus archivos .tf.
* El estado guardado (terraform.tfstate).
* El estado real de Proxmox (consultando la API).

Con esa información calcula qué tendría que hacer. La salida del comando anterior muestra las acciones a realizar por OpenTofu, con la opción **-out** puede volcarse el informe a un archivo.

!!!Importante
    Es conveniente revisar con cuidado la salida del comando anterior para comprobar qué se va a ejecutar precisamente lo que necesitamos.

Por último lanzamos el comando de ejecución del plan
```bash
tofu apply -parallelism=1
```
El comando anterior ejecuta en la infraestructura todos los pasos necesarios para disponer de una versión coherente de ésta según lo descrito en el despliegue. Para ello crea, modifica o elimina todo lo necesario.

### Destrucción de la infraestructura del plan
Si en algún momento obtenemos un error o simplemente necesitamos eliminar la infraestructura podemos ejecutar:
```bash
tofu destroy
```

### Uso de variables
El uso de variables, definidas en **variables.tf**, otorga gran potencia a la personalización del despliegue. A continuación haremos uso de una de las variables definidas para poder arrancar y apagar todas las máquinas de una vez.
Al final del archivo **variables.tf** nos encontramos el bloque:
``` bash
variable "vm_started" {
  type    = bool
  default = false
}
```
Una sencilla variable de tipo booleano que por defecto tiene valor `false`. Observemos que en **main.tf** dentro del **for_each** que recorre todas las `vms` definidas en la variable homónima, y por tanto constituye el bloque principal para la ejecución del despliegue, vemos que se define la variable `started=var.vm_started`, de modo que el estado de inicio de la máquina virtual depende del valor de esa variable, que por defecto es `false`.
Si a continuación añadimos al archivo **terraform.tfvars** la línea: 
```bash
vm_started = true
```
Habremos redefinido el valor de la variable para nuestro despliegue y simplemente ejecutando:
```bash
tofu apply
```
Conseguiremos "reconciliar" el estado de nuestro plan que ahora indica que el estado de inicio de la máquina es `true` (encendido) y por tanto las máquinas pasarán a ese estado de forma automática.
La verdadera potencia de OpenTofu/Terraform está en la flexibilidad a la hora de poder definir variables, establecer valores por defecto y definir sus valores finales, a través del archivo **terraform.tfvars**