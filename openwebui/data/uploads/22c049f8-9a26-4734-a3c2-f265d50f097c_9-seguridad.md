# Práctica: Gestión de RBAC en Proxmox VE

## Introducción
El sistema de **Control de Acceso Basado en Roles (RBAC)** de Proxmox permite gestionar de manera granular quién puede realizar qué acciones y sobre qué recursos específicos. En Proxmox, un permiso se define como una **ACL (Lista de Control de Acceso)** que une tres elementos: un sujeto (usuario o grupo), una ruta (el recurso) y un rol (conjunto de privilegios).

## Objetivos
*   Comprender el funcionamiento de usuarios, grupos y roles.
*   Aplicar el **principio de mínimo privilegio**.
*   Configurar entornos de seguridad reales: administradores, operadores y auditores.


## Preparación del Entorno
Antes de gestionar los accesos, es necesario contar con recursos y organizarlos lógicamente mediante un **Pool**. Los pools permiten agrupar máquinas virtuales (VM) y contenedores (CT) para facilitar la asignación de permisos masivos.

**Ejecutamos los siguientes pasos:**

1.  Asegúrate de tener algún tipo de recurso de ejecución creado. En este caso usaremos una VM (ID 100).
2.  Crea un pool llamado **LAB** y asigna los recursos mediante la herramienta de API `pvesh`:
    ```bash
    pvesh create /pools -poolid LAB
    pvesh set /pool/LAB -vms 100
    ```

## Gestión de Identidades (Usuarios y Grupos)
Proxmox utiliza diferentes **Realms** (ámbitos) para la autenticación. En esta práctica, utilizaremos el realm local `pve` (Proxmox VE authentication server).

### Creación de Usuarios
Utilizaremos el comando `pveum` (User Manager) para dar de alta a los sujetos en el sistema:
```bash
pveum useradd admin1@pve
pveum useradd operador1@pve
pveum useradd auditor1@pve

# Asignar contraseñas
# Una contraseña que verifica los criterios de complejidad es Abc1234.
pveum passwd admin1@pve
pveum passwd operador1@pve
pveum passwd auditor1@pve
```
Para ver los usuarios ejecutamos:
```bash
pveum user list
```

### Organización en Grupos
Como es bien sabido y práctica común en administración de sistemas, los grupos simplifican la gestión; es preferible asignar permisos a un grupo que a usuarios individuales.
```bash
pveum groupadd admins
pveum groupadd operadores
pveum groupadd auditores

# Añadir usuarios a sus respectivos grupos
pveum usermod admin1@pve -group admins
pveum usermod operador1@pve -group operadores
pveum usermod auditor1@pve -group auditores
```

Para ver grupos de usuarios ejecutamos:
```bash
pveum group list
```

## Definición de Roles
Un **Rol** es simplemente una lista de privilegios. Proxmox incluye roles predefinidos como `Administrator` (acceso total) o `PVEAuditor` (lectura). Listemos los roles existentes:
```bash
pveum role list
```
### Crear Roles Personalizados
Para ajustar la seguridad, crearemos roles con privilegios específicos:

* **VMOperator:** Permite gestionar el estado de la VM (encendido/apagado) y ver la consola, pero no modificar el hardware ni borrar el recurso.
  ```bash
  pveum roleadd VMOperator -privs "VM.PowerMgmt VM.Console"
  ```
* **ReadOnlyAudit:** Permite una auditoría completa de solo lectura.
  ```bash
  pveum roleadd ReadOnlyAudit -privs "Sys.Audit VM.Audit Datastore.Audit"
  ```

Si por alguna razón tenemos que modificar un role existente usaremos el comando **pveum rolemod**. A modo de ejemplo ejecutemos el siguiente comando para añadir un permiso adicional a nuestro role anterior:
```bash
pveum rolemod VMOperator -privs "VM.PowerMgmt VM.Console VM.Audit"
```

## Aplicación de ACLs (Asignación de Permisos)
Como vimos anteriormente, una ACL une semánticamente bajo una asignación de permisos a tres elementos, **sujeto** (a quién se aplica, usuario o grupo), **ruta o path** (indica el alcance o ámbito de la ACL) y el **rol**. La **Ruta (Path)** es crítica, ya que define el alcance del permiso. La raíz `/` implica todo el clúster, mientras que `/pool/LAB` limita el acceso solo a los recursos de ese grupo.

```bash
# Administradores: Acceso total a todo el clúster
pveum aclmod / -group admins -role Administrator

# Operadores: Solo pueden gestionar recursos dentro del pool LAB
pveum aclmod /pool/LAB -group operadores -role VMOperator

# Auditores: Pueden ver todo el sistema, pero no realizar cambios
pveum aclmod / -group auditores -role ReadOnlyAudit
```

Como es de esperar, con el siguiente comando obtenemos la lista de ACLs:
```bash
pveum acl list
```

## Validación de Escenarios
Para comprobar el éxito de la configuración, accederemos a la interfaz de gestión web de proxmox con cada uno de los usuarios y verificaremos sus capacidades.

### Conceptos Clave a comprobar
1.  **RBAC es Acumulativo:** Proxmox suma todos los permisos que un usuario recibe individualmente y a través de sus grupos.
2.  **No existe el "Deny":** No hay una instrucción para denegar explícitamente; el acceso se restringe simplemente no otorgando el privilegio o limitando el **Scope** (alcance) de la ruta.
3.  **Conflicto de Permisos:** Si a un operador se le asigna accidentalmente el rol de `PVEAdmin` en la raíz `/`, podrá ver y gestionar todo el clúster, invalidando la restricción del pool anterior.

### Pruebas
1. Entremos como **operador1** en la interfaz de administración web (seleccionar en la interfaz el Realm de autenticacion **Proxmox VE authentication server**) y comprobad como podremos operar con la MV con ID 100 (que está dentro del path /pool/LAB sobre el que opera la ACL que afecta a ese usuario), de modo que podremos detenerla, pausarla o reiniciarla.
2. Entremos a continuación como **auditor1** y comprobaremos que, aunque veremos todas las MVs del clúster, no podremos realizar ninguna operación con ellas salvo ver su estado.
3. Al entrar con **admin1** no habrá ninguna restriccion pues ese usuario pertenece al grupo **admins** y tiene asignado el rol predefinido de **Administrator**, además la ACL asociada se aplica a todo el clúster.

