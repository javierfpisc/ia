# Despliegue Automatizado de Máquinas Virtuales en Proxmox con OpenTofu

## Introducción y Contexto de OpenTofu
OpenTofu es una herramienta de Infraestructura como Código (IaC) de código abierto, surgida como un fork que garantiza la continuidad del ecosistema tras los cambios de licenciamiento en otras herramientas similares. Como Técnicos de DevOps, adoptamos OpenTofu para definir, versionar y desplegar infraestructura de forma declarativa, permitiendo que el estado de nuestros servidores sea predecible y reproducible.

El uso de la última versión estable es fundamental en entornos de producción modernos. Esta versión no solo representa la evolución estable más reciente del proyecto, sino que introduce mejoras significativas en la compatibilidad con proveedores y una optimización en la gestión de estados. El objetivo de esta guía práctica es proporcionar una introducción para automatizar la creación de máquinas virtuales (VM) en Proxmox VE, utilizando el proveedor bpg/proxmox. Este proveedor es la elección preferida en el ámbito profesional por su robustez y su soporte nativo a funciones avanzadas de Cloud-Init.

---

## Instalación de OpenTofu
Aunque existen varios modos de instalación la forma más sencilla es la descarga directa del script instalador, como se muestra a continuación:
```bash
curl --proto '=https' --tlsv1.2 -fsSL \
https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh
chmod +x install-opentofu.sh
./install-opentofu.sh --install-method deb
rm install-opentofu.sh
```
Tras la instalación comprobamos la disponibilidad del comando:
```bash
tofu --help
```

---

## Estructura del proyecto de Infraestructura y análisis descriptivo de la configuración
En la ingeniería de infraestructura, la organización del código es tan crítica como la lógica misma. Un proyecto desordenado es difícil de auditar y escalar. Por ello, segmentamos la configuración en archivos especializados para lograr una arquitectura modular:

* providers.tf: Configuración de los motores de ejecución y credenciales de acceso.
* variables.tf: Definición de la interfaz (diccionario de parámetros) sin asignar valores.
* main.tf: El núcleo de la lógica donde se declaran los recursos a desplegar.
* outputs.tf: Definición de los datos de retorno tras una ejecución exitosa.
* terraform.tfvars: Asignación de valores reales y sensibles (este archivo debe protegerse rigurosamente).

A continuación, desglosamos la implementación técnica basándonos en las mejores prácticas y la sintaxis del proveedor bpg/proxmox.

### providers.tf (Configuración del Entorno)
Este archivo instruye a OpenTofu sobre qué binarios descargar. Es una buena práctica fijar versiones específicas para evitar cambios disruptivos (breaking changes).
```bash
terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "~> 0.66.0" # Bloqueo de versión para estabilidad
    }
  }
}

provider "proxmox" {
  endpoint = var.proxmox_api_url
  api_token = var.proxmox_api_token
  insecure = true # Necesario si usas certificados auto-firmados
}
```
!!!Nota
    El bloque anterior hace referencia a variables que se definirán en el siguiente archivo.

### variables.tf (Definición de la Interfaz)
Aquí definimos el "qué" pero no el "cuánto". Establecemos el tipo de dato y si la información es sensible para que OpenTofu la enmascare en los logs.

```bash
variable "proxmox_api_url" {
  description = "URL de la API de Proxmox (ej. https://pve.example.com:8006/)"
  type        = string
}

variable "proxmox_api_token" {
  description = "Token de API con formato usuario@pve!token_id=secret-uuid"
  type        = string
  sensitive   = true
}

variable "vm_template_id" {
  description = "ID de la VM plantilla (Cloud-Init)"
  type        = number
}
```

### main.tf (Lógica de Recursos)
Este archivo ejecuta la clonación. Nótese el uso de node_name y la inclusión de un bloque de red, obligatorios para operar con el proveedor bpg/proxmox.
```bash
resource "proxmox_virtual_environment_vm" "example_vm" {
  name      = "srv-opentofu-prod"
  node_name = "pve1" # Nodo de destino en el clúster
  vm_id     = 601   # ID de la nueva VM

  clone {
    vm_id = var.vm_template_id
  }

  network_device {
    bridge = "vmbr0"
  }

  # Soporte nativo para Cloud-Init
  initialization {
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }
}
```

### outputs.tf (Extracción de Datos)
Permite obtener información útil sin navegar por la consola web.

!!!Nota
    Para que la dirección IP se reporte correctamente, la plantilla origen debe tener instalado y habilitado el QEMU Guest Agent.

```bash
output "vm_ipv4_address" {
  description = "Dirección IP asignada a la VM"
  value       = proxmox_virtual_machine.example_vm.ipv4_addresses[1][0]
}
```

### terraform.tfvars (Asignación de Valores)
Aquí es donde inyectamos los datos reales.

```bash
proxmox_api_url   = "https://192.168.1.10:8006/"
proxmox_api_token = "admin@pve!automation=12345-abcde-..."
vm_template_id    = 9000
```

---

## Flujo de Trabajo y Comandos de la CLI
El ciclo de vida en DevOps sigue un proceso estricto de validación antes de la ejecución.

1. `tofu init`: Descarga los plugins de los proveedores y prepara el backend.
2. `tofu plan -out=main.tfplan`: Genera un plan de ejecución y lo guarda en un archivo. Esta es una práctica profesional esencial para garantizar que lo que se revisa es exactamente lo que se aplica.
3. `tofu apply "main.tfplan"`: Aplica los cambios utilizando el archivo de plan previamente aprobado.
4. `tofu destroy`: Elimina los recursos de forma controlada.

---

## Configuración de Proxmox y Seguridad
La seguridad es el pilar de la automatización. Un entorno mal configurado es una vulnerabilidad expuesta.

* API Tokens: Nunca deben utilizarse las credenciales de root. Crea un token en Datacenter → Permissions → API Tokens.
* Principio de Menor Privilegio: Asigna el rol **PVEVMAdmin** específicamente al Token generado. Esto permite gestionar VMs sin comprometer el almacenamiento o la configuración de red global del Datacenter.
* Gestión de Secretos: El archivo **terraform.tfvars** nunca debe llegar a un sistema de control de versiones. Utiliza un archivo .gitignore.
* Variables de Entorno: En sistemas de CI/CD, utiliza variables de entorno como **TF_VAR_proxmox_api_token** para inyectar credenciales sin dejar rastros en archivos físicos.

---

## Consideraciones Adicionales y Mejores Prácticas

* ¿Por qué bpg/proxmox?: A diferencia de Telmate/proxmox, el proveedor bpg ofrece un soporte superior para el ecosistema moderno de Proxmox, incluyendo una gestión más profunda de discos, interfaces de red y, fundamentalmente, una integración nativa con los bloques de initialization de Cloud-Init.
* Preparación de Plantillas: El éxito del despliegue depende de tener una plantilla funcional (Template). Asegúrate de que la plantilla tenga configurado el hardware necesario.
* Estado de Infraestructura: Recuerda que OpenTofu mantiene un archivo **.tfstate.** Este archivo es la "fuente de verdad"; si se pierde, OpenTofu perderá el control sobre los recursos creados.
