# Profundizando en las funcionalidades de Ansible
Vamos a ampliar un poco nuestro uso de playbooks Ansible de la práctica anterior para añadir nuevas funcionalidades y usos.

## Playbook ampliado
Usaremos el archivo **tasks.yml** en nuestro directorio de trabajo **tools/ansible/avanzado**, con el siguiente contenido:
``` yaml
#Metadatos del playbook (incluye definición de variables)
- name: Tareas básicas de mantenimiento
  hosts: debian_servers
  become: yes
  vars:
    mensaje_bienvenida: "Playbook de prácticas de Ansible"
    paquetes:
      - htop
      - curl
      - vim
  #Tareas del playbook
  tasks:
    - name: Obtener información de los hosts
      ansible.builtin.setup:
    - name: Mostrar información del sistema
      ansible.builtin.debug:
        msg: >
          Host: {{ inventory_hostname }}
          - Sistema: {{ ansible_system }}
          - Distribución: {{ ansible_distribution }}
          - Versión: {{ ansible_distribution_version }}
    - name: Mostrar mensaje de bienvenida
      ansible.builtin.debug:
        msg: "{{ mensaje_bienvenida }}"
    # -------------------------------------------------
    # Condicional
    # -------------------------------------------------
    - name: Ejecutar solo en sistemas Debian
      ansible.builtin.debug:
        msg: "Este host utiliza Debian"
      when: ansible_distribution == "Debian"
    # -------------------------------------------------
    # Comprobación y registro de resultados
    # -------------------------------------------------
    - name: Comprobar si existe auth.log
      ansible.builtin.stat:
        path: /var/log/auth.log
      register: auth_log
    - name: Mostrar mensaje si auth.log existe
      ansible.builtin.debug:
        msg: "El archivo /var/log/auth.log existe"
      when: auth_log.stat.exists
    - name: Mostrar mensaje si auth.log no existe
      ansible.builtin.debug:
        msg: "El archivo /var/log/auth.log no existe"
      when: not auth_log.stat.exists
    # -------------------------------------------------
    # Uso de variables y bucles
    # -------------------------------------------------
    - name: Instalar paquetes de utilidad
      ansible.builtin.apt:
        name: "{{ paquetes }}"
        state: present
        update_cache: yes
    # -------------------------------------------------
    # Bloque de tareas
    # -------------------------------------------------
    - name: Preparar directorio de demostración
      block:
        - name: Crear directorio de trabajo
          ansible.builtin.file:
            path: /opt/ansible-demo
            state: directory
            mode: "0755"
        - name: Crear archivo de información si no existe
          ansible.builtin.copy:
            content: |
              Archivo creado mediante Ansible.
              Host: {{ inventory_hostname }}
            dest: /opt/ansible-demo/info.txt
            force: no
            mode: "0644"
      rescue:
        - name: Mostrar error
          ansible.builtin.debug:
            msg: "Se ha producido un error en la preparación del directorio"
      always:
        - name: Mensaje final del bloque
          ansible.builtin.debug:
            msg: "Finalizada la preparación del directorio"
    # -------------------------------------------------
    # Notificación de handler
    # -------------------------------------------------
    - name: Añadir una línea al archivo de información
      ansible.builtin.lineinfile:
        path: /opt/ansible-demo/info.txt
        line: "Última ejecución gestionada por Ansible"
      notify: Informar de modificación

  handlers:
    - name: Informar de modificación
      ansible.builtin.debug:
        msg: "El archivo info.txt ha sido modificado"
```

### Explicación del playbook
Este playbook amplía el ejemplo inicial de mantenimiento para introducir algunas funcionalidades adicionales de **Ansible**. Su objetivo es servir como práctica para conocer diferentes formas de organizar tareas, utilizar información de los hosts y controlar el flujo de ejecución.

#### Variables
En la sección `vars` se definen valores que pueden reutilizarse posteriormente en el playbook:
```yaml
vars:
  mensaje_bienvenida: "Playbook de prácticas de Ansible"

  paquetes:
    - htop
    - curl
    - vim
```
En este caso se define una variable de texto y una lista de paquetes.

#### Facts e información de los hosts
Ansible puede recopilar información sobre los equipos gestionados, conocida como **facts**. Esta información permite conocer, entre otros datos, el sistema operativo, la distribución, la versión o la dirección IP. Posteriormente, estos valores pueden utilizarse como variables:
```yaml
ansible_distribution
ansible_distribution_version
ansible_system
```
Por ejemplo:
```yaml
msg: "La distribución es {{ ansible_distribution }}"
```
!!!Nota
     La recolección de facts de los hosts consume tiempo y si el número de hosts es muy elevado puede ralentizar considerablemente la ejecución del playbook. Para desactivar la recolección añadimos la directiva:

     `gather_facts: no`

     en la sección principal del playbook (metadatos). De este modo los facts no se recopilarán ahorrando tiempo de ejecución, si bien como es lógico ya no podremos hacer uso de ellos

#### Condicionales con `when`
La directiva `when` permite ejecutar una tarea únicamente si se cumple una determinada condición:
```yaml
- name: Ejecutar solo en sistemas Debian
  ansible.builtin.debug:
    msg: "Este host utiliza Debian"
  when: ansible_distribution == "Debian"
```
Si el host no utiliza Debian, la tarea aparecerá como `skipped`.

#### Registrar el resultado de una tarea
La directiva `register` permite almacenar el resultado de una tarea en una variable para utilizarlo posteriormente. En este ejemplo se comprueba si existe un archivo:
```yaml
- name: Comprobar si existe auth.log
  ansible.builtin.stat:
    path: /var/log/auth.log
  register: auth_log
```
Después podemos consultar el resultado mediante:
```yaml
auth_log.stat.exists
```
Esto permite combinar `register` con `when` para tomar decisiones:
```yaml
when: auth_log.stat.exists
```

#### Gestión de varios elementos
La variable definida anteriormente `paquetes` contiene una lista:
```yaml
paquetes:
  - htop
  - curl
  - vim
```
Esta lista se pasa directamente al módulo `apt` para instalar todos los paquetes en una única tarea:
```yaml
- name: Instalar paquetes de utilidad
  ansible.builtin.apt:
    name: "{{ paquetes }}"
    state: present
```

#### Bloques de tareas
`block` permite agrupar varias tareas relacionadas:
```yaml
block:
  - name: Crear directorio
    ...
  - name: Crear archivo
    ...
```
Esta estructura facilita organizar el playbook y permite aplicar un tratamiento común a un conjunto de tareas.

#### Gestión de errores con `rescue`
Un ejemplo del tratamiento común mencionada arriba es el ilustrado a continuación. Si alguna tarea dentro de un `block` falla, Ansible puede ejecutar las tareas definidas en `rescue`.
El comportamiento es el siguiente: si una tarea dentro de block falla, Ansible deja de ejecutar las tareas restantes de ese block para ese host y pasa a la sección rescue, si existe. Veamos un ejemplo:
```yaml
block:
  - name: Tarea que puede fallar
    ...
rescue:
  - name: Informar del error
    ansible.builtin.debug:
      msg: "Se ha producido un error"
```
Esto permite controlar determinados errores sin detener necesariamente toda la lógica definida para el bloque. La sección `always` se ejecuta independientemente de que las tareas del bloque hayan finalizado correctamente o se haya producido un error:
```yaml
always:
  - name: Mensaje final
    ansible.builtin.debug:
      msg: "Finalizada la ejecución"
```
Es similar a una sección de limpieza o finalización. Toda la estructura anterior simula un tratamiento al **try...catch** de los lenguajes de programación

#### Handlers y `notify`
Un **handler** es una tarea especial que se ejecuta cuando otra tarea le envía una notificación. Por ejemplo:
```yaml
- name: Modificar archivo
  ansible.builtin.lineinfile:
    path: /opt/ansible-demo/info.txt
    line: "Última ejecución gestionada por Ansible"
  notify: Informar de modificación
```
Si esta tarea produce un cambio, se notificará al handler:
```yaml
handlers:
  - name: Informar de modificación
    ansible.builtin.debug:
      msg: "El archivo info.txt ha sido modificado"
```
Una característica importante es que el handler **solo se ejecutará si la tarea notificadora ha producido realmente un cambio**.

#### Idempotencia
Como vimos uno de los conceptos más importantes de Ansible es la **idempotencia**. Un playbook idempotente puede ejecutarse varias veces y, una vez alcanzado el estado deseado, las siguientes ejecuciones no deberían realizar cambios innecesarios. Por ejemplo:
```yaml
ansible.builtin.file:
  path: /opt/ansible-demo
  state: directory
```
La primera ejecución creará el directorio y la tarea aparecerá como:
```text
changed
```
En ejecuciones posteriores, si el directorio ya existe y tiene el estado correcto, aparecerá como:
```text
ok
```
Este comportamiento permite utilizar Ansible para describir **el estado que queremos que tengan nuestros sistemas**, en lugar de limitarse a ejecutar una secuencia de comandos.

## Ejecución del ejemplo
Desde el directorio de trabajo lanzamos el playbook:
```bash
ansible-playbook -i inventory.yml tasks.yml
```
Tras la ejecución es conveniente revisar en detalle la salida e interpretar los resultados.