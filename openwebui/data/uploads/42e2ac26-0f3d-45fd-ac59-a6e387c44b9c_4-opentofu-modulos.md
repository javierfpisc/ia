# Despliegue Automatizado y Modular de Máquinas Virtuales en Proxmox con OpenTofu
En esta práctica evolucionaremos en nuestro despliegue con OpenTofu para pasar de un `main.tf` monolítico a una infraestructura modular.

## Objetivo
Partimos de un despliegue **funcional pero monolítico**: un único `main.tf` que mezcla la definición de las VMs y el recurso del snippet Cloud-Init, con toda
la configuración repetida implícitamente vía `for_each`. El objetivo es entender la mejora en el proceso mediante el uso de **módulos**.

## Antecedentes
En el `main.tf` de partida encontramos dos recursos en el mismo archivo:

- `proxmox_virtual_environment_vm.vms` (con `for_each`) → una VM por entrada del mapa `vms`.
- `proxmox_virtual_environment_file.cloud_config` → **un único** snippet, compartido por las VMs.

Pero debemos de plantearnos las siguientes cuestiones:

1. ¿Qué pasaría si quisiéramos reutilizar la lógica de "clonar una VM" en otro proyecto o entorno (dev, staging)?, habría que **copiar y pegar** código.
2. ¿El snippet Cloud-Init debería crearse una vez por VM o una sola vez para todas?, es un recurso **compartido**, no "por instancia".
3. ¿Qué ocurre si cambiamos el proveedor de versión o afinamos un detalle del recurso VM?, hay que tocarlo en tantos sitios como copias existan del código.

Esto son exactamente los problemas que resuelve la **modularización**.

---

## Nuevo diseño: separar por "quién repite" vs "quién no repite"
| Recurso | ¿Se repite por VM? | Dónde va |
|---|---|---|
| `proxmox_virtual_environment_vm` | Sí (una por entrada de `vms`) | Módulo `modules/vm` |
| `proxmox_virtual_environment_file` (snippet) | No, es compartido | Módulo `modules/cloud-init-file` |

Este es el primer aprendizaje clave: **un módulo no es simplemente "meter el código en otra carpeta"**, sino identificar la unidad de reutilización correcta.

### Nueva estructura de directorios
```
infra-proxmox/
├── environments/
│ └── prod/ <- "root module": orquesta, no contiene lógica de bajo nivel
│ ├── providers.tf
│ ├── variables.tf
│ ├── main.tf <- solo llamadas a module "..."
│ ├── outputs.tf
│ └── terraform.tfvars.sample
├── modules/
│ ├── vm/ <- lógica genérica: clonar plantilla -> VM
│ └── cloud-init-file/<- lógica genérica: crear snippet Cloud-Init
└── keys/
```

### Regla de oro
- `environments/prod/main.tf` **no debe contener ningún `resource`** directamente, solo bloques `module "..." { source = ... }`. Toda la lógica de "cómo se crea
una VM" vive dentro de `modules/vm`.
- Cada módulo declara sus propias `variables.tf` (su "interfaz de entrada") y `outputs.tf` (lo que expone hacia quien lo use).

---

## Cómo cambia el despliegue
Veamos en detalle los artefactos del "nuevo" despliegue

### `modules/vm/`
Recibe como variables todo lo que antes estaba fijo o venía directamente de `each.value` (`name`, `node_name`, `vm_id`, `template_id`, `template_node`...), y también lo que antes eran variables globales del entorno (`cloud_init_disk_storage`, `cloud_init_disk_interface`). El módulo no sabe nada sobre "cuántas VMs" hay ni de dónde salen los datos, solo sabe **cómo construir una VM** a partir de los parámetros que recibe.

### `modules/cloud-init-file/`
Encapsula la creación del snippet, parametrizando `node_name`, `datastore_id`, `file_name` y `cloud_config_data`. Expone su `id` como output, que es lo que el entorno pasará al módulo `vm` a través de `user_data_file_id`.

### `environments/prod/main.tf`
Pasa de contener recursos a contener **orquestación**:
```hcl
module "cloud_init_web" {
source = "../../modules/cloud-init-file"
...
}
module "vms" {
source = "../../modules/vm"
for_each = var.vms
...
user_data_file_id = module.cloud_init_web.id
}
```
Nótese cómo el `for_each` sigue estando en el entorno (es una decisión de "cuántas y cuáles VMs quiero en prod"), pero la lógica de "qué es una VM" vive en el módulo.

### `environments/prod/outputs.tf`
Cambia la referencia de `proxmox_virtual_environment_vm.vms` a `module.vms`, porque el recurso real ahora está encapsulado dentro del módulo y no es visible directamente desde el entorno.

---

## Ventajas

1. **Reutilización**: si se crea `environments/dev`, puede llamar a los mismos módulos `vm` y `cloud-init-file` sin duplicar código.
2. **Mantenimiento centralizado**: un cambio en cómo se configura una VM (ej. añadir un bloque `cpu` o `memory`) se hace **una sola vez**, en `modules/vm/main.tf`, y afecta a todos los entornos que usen el módulo.
3. **Interfaz clara**: `variables.tf` del módulo documenta exactamente qué necesita saber quien lo use, sin exponer detalles de implementación.
4. **Testabilidad/aislamiento**: se puede razonar sobre el módulo `vm` de forma independiente del resto del despliegue.
5. **Versionado de módulos** (ampliación futura): un `source` de módulo puede apuntar a un repositorio Git con un tag de versión, permitiendo controlar qué versión del módulo usa cada entorno.

---

## Ejecución del despliegue y pasos detallados
Como siempre, desde el directorio en el que residen los recursos de OpenTofu, en este caso **infra-proxmox-2/environments/prod** ejecutamos los pasos necesarios: `tofu init`. El comando anterior es necesario para descargar el provider e incializar el entorno. A continuación ejecutamos para obtener un listado de las acciones a realizar:
`tofu plan`. Por último: `tofu apply`.

A continuación revisamos brevemente el orden en que OpenTofu procesa el despliegue modular, para comprender el flujo de dependencias entre entorno y módulos.

### Inicialización (`tofu init`)

- Lee `providers.tf` en el entorno raíz (`environments/prod`) y descarga el proveedor `bpg/proxmox` fijado en `required_providers`.
- Detecta los bloques `module "..." { source = "../../modules/..." }` en `main.tf` del entorno y copia/enlaza el código de esos módulos localmente.
- Verifica que cada módulo (`vm`, `cloud-init-file`) declare su propio `required_providers` para heredar correctamente el proveedor `proxmox`.

### Planificación (`tofu plan`)

- Carga las variables del entorno: primero los `default` de `variables.tf`, luego los valores reales de `terraform.tfvars`, que los sobrescriben.
- Resuelve el mapa `var.vms` y expande el `for_each` del módulo `vms`, generando una instancia del módulo por cada clave (`srv-tofu-XX`...).
- Construye internamente el grafo de dependencias: primero identifica que `module.vms` necesita el `id` que devuelve `module.cloud_init_web` (vía `user_data_file_id`), estableciendo así el orden de creación.
- Muestra el plan de acción (crear, modificar, destruir) sin ejecutar nada todavía.

### Aplicación (`tofu apply`)
El orden real de ejecución según el grafo de dependencias sería:

1. **Módulo `cloud-init-file`**: se crea primero el recurso `proxmox_virtual_environment_file` (snippet Cloud-Init), ya que ningún otro recurso depende de él y él no depende de nadie.
2. **Módulo `vm` (una instancia por cada entrada de `var.vms`)**: una vez existe el snippet, se lanza el clonado de cada VM:
   - Proxmox clona la plantilla (`clone.vm_id`, `clone.node_name`) en el nodo destino (`node_name`), con `full = true`.
   - Se configura la red (`network_device`).
   - Se configura el bloque `initialization`: disco Cloud-Init (`datastore_id`, `interface`), usuario/password de pruebas, Configuración IP y se asocia el `user_data_file_id` generado en el paso 1.
!!!Nota
    Si no se fuerza secuencialidad del comando, con el parámetro `-parallelism=1`, OpenTofu intenta crear las VMs en paralelo, respetando únicamente la dependencia hacia el snippet, no entre VMs entre sí.

### Salidas (`outputs.tf`)
Tras completar la creación, OpenTofu recorre las instancias resultantes del módulo `vms` y expone:

  - `vms_ipv4`: IP de cada VM (requiere QEMU Guest Agent).
  - `vms_ids`: ID numérico asignado a cada VM en Proxmox.

### Persistencia del estado

Todo lo creado (snippet + VMs) queda registrado en el `terraform.tfstate` del entorno `prod`, asociando cada recurso a la ruta del módulo correspondiente (por ejemplo, `module.vms["srv-tofu-11"].proxmox_virtual_environment_vm.this`), lo que permite que futuras ejecuciones de `plan`/`apply` sepan qué ya existe y qué falta por crear o modificar.

**La idea clave es**: el entorno (`environments/prod`) decide *qué* y *cuántas* VMs crear (vía `var.vms`), mientras que los módulos (`modules/vm`, `modules/cloud-init-file`) definen *cómo* se construye cada recurso y OpenTofu resuelve automáticamente el orden correcto según las dependencias entre ambos.

