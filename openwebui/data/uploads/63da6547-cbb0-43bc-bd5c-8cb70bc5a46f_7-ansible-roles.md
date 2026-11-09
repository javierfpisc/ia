# Uso de Roles en Ansible para Desplegar Nodos Kubernetes
Vamos a ver mediante un sencillo ejemplo el uso de **roles** de Ansible. El objetivo será desplegar una infraestructura de nodos que pertenezcan a un cluster de kubernetes.

## Introducción: ¿Qué son los Roles en Ansible?
Los **roles** son una estructura organizada que permite modularizar y reutilizar playbooks de Ansible. En lugar de escribir una única configuración compleja para un solo caso de uso, puedes crear roles modulares que se puedan aplicar en múltiples proyectos.

---

## Estructura de un Role Básico
Nuestro directorio base de trabajo para esta práctica será **tools/ansible/roles/kubernetes**. Dentro de él irán todos los elementos que se detallan a continuación. Cada rol sigue una estructura de carpetas estandarizada. Para un rol llamado `kube_node`:

```
roles/
└── kube_node/
    ├── tasks/
    │   └── main.yml
    ├── handlers/
    │   └── main.yml
    ├── templates/
    │   └── kubelet.conf.j2
    ├── vars/
    │   └── main.yml
    └── defaults/
        └── main.yml
playbook_kube_nodes.yml
inventory.yml
```
Esta organización separa claramente las responsabilidades: tareas principales, servicios a reiniciar, archivos de configuración, y variables.

---

## Definición de la Estructura
Disponemos de todos los elementos necesarios para el despliegue en el directorio. A continuación se describen los elementos y su función.

### Tareas Principales (`roles/kube_node/tasks/main.yml`)
Esta será la lista de tareas (tasks) ansible que definen qué debe hacer el rol cada vez que se ejecute. Al final del archivo tendremos las tareas:
```yaml
---
--- # tareas de instalación de kubernetes -- (omitidas)

- name: Configurar kubelet
  template:
    src: kubelet.conf.j2
    dest: /etc/default/kubelet
    owner: root
    group: root
    mode: '0644'
  notify: Reiniciar kubelet

- name: Verificar instalación de kubeadm
  command: kubeadm version
  register: kubeadm_result
  changed_when: false
```
La interpretación de la sintaxis debe de ser clara a estas alturas y ha sido el objetivo de las anteriores prácticas.

### Handlers (`roles/kube_node/handlers/main.yml`)
El archivo de tareas anterior, **tasks/main.yaml** hace uso de varios handlers, que como vimos actúan bajo un mecanismo de notificación. Los handlers se ejecutan cuando se les notifica desde una tarea.

### Plantillas (`roles/kube_node/templates/kubelet.conf.j2`)
La task `Configurar kubelet` de **tasks/main.yml** hace uso de una plantilla Jinja2 para generar configuraciones dinámicas. En este caso se utiliza para la generación del archivo de configuración del componente **kubelet** de kubernetes, definida en el archivo **/etc/default/kubelet**. Veamos a continuación la plantilla:
```jinja2
KUBELET_KUBECONFIG_ARGS="--kubeconfig=/etc/kubernetes/kubelet.conf"
KUBELET_KUBELET_ARGS="--node-ip={{ ansible_host }}"
```
Notar el uso de la variable `ansible_host` según la sintaxis entre **{{}}**. Esta variable se define en el inventario.

### Variables (`roles/kube_node/vars/main.yml`)
En este archivo se establecen definiciones de variables globales del rol, no sobreescribibles desde fuera.

### Variables por Defecto (`roles/kube_node/defaults/main.yml`)
Variables predeterminadas que pueden sobrescribirse:
```yaml
---
kube_node_ip: "192.168.56.71"
kube_node_control_plane: false
```

### Playbook Principal (`playbook_kube_nodes.yml`)
Es necesario definir un playbook a modo de elemento de ejecución principal de la automatización. A continuación vemos su contenido, básicamente se reduce a llamar al rol y definir el alcance según lo definido en el inventario:
```yaml
---
- name: Desplegar nodos Kubernetes
  hosts: k8s_nodes
  become: yes
  roles:
    - kube_node
```

### Configuración del Inventario (inventory.yml)
El archivo de inventario, **inventory.yml** ya está disponible en el directorio correspondiente. Define básicamente la estructura para el grupo de nodos `k8s_nodes`

### Ejecución
Veremos varios modos de ejecución:

```bash
# Ejecución "normal"
ansible-playbook -i inventory.yml playbook_kube_nodes.yml

# Modo comprobación (dry-run)
ansible-playbook -i inventory.yml playbook_kube_nodes.yml --check

# Solo ciertos tareas usando tags
ansible-playbook -i inventory.yml playbook_kube_nodes.yml \
--tags "Instalar dependencias"
```

---

## Ventajas de Usar Roles

| Ventaja | Descripción |
|---------|-------------|
| **Modularidad** | Separación clara de responsabilidades |
| **Reutilización** | Un mismo rol puede aplicarse en múltiples playbooks |
| **Legibilidad** | Código más limpio y mantenible |
| **Escalabilidad** | Fácil adicionar nuevos roles para Calico, CoreDNS, etc. |
| **Colaboración** | Equipos pueden trabajar en roles independientes |

---

## Recursos Adicionales

- Documentación oficial de Ansible: https://docs.ansible.com/
- Ansible Galaxy para roles compartidos: https://galaxy.ansible.com/
- Consulte la documentación sobre Playbook Roles and Include Statements

