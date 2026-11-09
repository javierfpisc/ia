# Seguridad en Kubernetes: Protegiendo el Clúster y las Aplicaciones

La seguridad en Kubernetes no es un único producto, sino un enfoque de capas conocido como **Cloud Native Security**. Para un administrador de sistemas, asegurar el entorno implica proteger desde el acceso a la API hasta la ejecución de los contenedores y la comunicación cifrada.

---

## Control de Acceso a la API: RBAC y ServiceAccounts
Casi cualquier acción en Kubernetes pasa por el **kube-apiserver**. Por ello, el control de acceso es fundamental.

### RBAC (Role-Based Access Control)
RBAC es el mecanismo que utiliza Kubernetes para controlar **quién** (usuarios o ServiceAccounts) tiene permiso para realizar **qué** acciones sobre **qué** recursos dentro del clúster. Se basa en la gestión de políticas de autorización a través del API Server.

#### Componentes Clave de RBAC
Para implementar RBAC, se utilizan cuatro tipos de objetos principales:

*   **Role**: Define un conjunto de permisos (como "leer" o "crear" pods) dentro de un **Namespace** específico.
*   **ClusterRole**: Similar al anterior, pero define permisos a nivel de **todo el clúster** o sobre recursos que no pertenecen a un namespace (como los nodos).
*   **RoleBinding**: Es el "pegamento" que asigna un `Role` a un usuario o grupo dentro de un namespace concreto.
*   **ClusterRoleBinding**: Asigna un `ClusterRole` a nivel de todo el clúster.

#### Aplicación Práctica
Podemos utilizar comandos de `kubectl` para gestionar estos roles de forma imperativa:

*   `kubectl create role`: Para definir nuevos permisos.
*   `kubectl auth can-i`: Una herramienta vital para que el alumno compruebe si tiene permiso para realizar una acción específica.

### Service Accounts
En Kubernetes, mientras que los usuarios humanos se autentican para usar `kubectl`, las aplicaciones que corren dentro de los Pods también necesitan una forma de identificarse ante el clúster. Para ello existen los **Service Accounts (Cuentas de Servicio)**.

#### ¿Qué es un Service Account?
Un **Service Account** es un recurso de la API de Kubernetes que proporciona una **identidad para los procesos que se ejecutan en un Pod**. 
Cuando un proceso dentro de un contenedor necesita interactuar con el **API Server** (por ejemplo, para listar otros Pods o consultar el estado de un Deployment), utiliza las credenciales asociadas a su Service Account para autenticarse.

#### Relación con RBAC
Como vimos en la sección de seguridad, el control de acceso no sería posible sin una identidad a la que asignar los permisos:

*   **Identidad:** El Service Account es el "quién".
*   **Permisos:** Se definen mediante **Roles** o **ClusterRoles**.
*   **Vínculo:** Un **RoleBinding** o **ClusterRoleBinding** vinculan esos permisos a un usuario o Service Account.

Por defecto, cada Namespace tiene un Service Account llamado `default`. Sin embargo, la **buena práctica** es crear Service Accounts específicos para cada aplicación con el fin de aplicar el **principio de mínimo privilegio**.

#### Funcionamiento en los Pods
Cuando se despliega un Pod, Kubernetes monta automáticamente un **token** (una credencial secreta) del Service Account en una ruta específica del sistema de archivos del contenedor. 

*   Si no se especifica ninguno en el YAML del Deployment, Kubernetes asigna automáticamente el Service Account `default` del Namespace.
*   Puedes cambiarlo usando el campo `serviceAccountName` dentro de la especificación del Pod.

#### Gestión con kubectl
Existen comandos específicos para gestionar estas cuentas:

*   **Creación:** 
    ```bash
    kubectl create serviceaccount <nombre> -n <namespace>
    ```
*   **Asignación (Imperativa):** Aunque se suele definir en el YAML, puedes cambiar el Service Account de un recurso existente:
    ```bash
    kubectl set serviceaccount deployment/<nombre> <nombre-sa>
    ```
*   **Inspección:**
    ```bash
    kubectl get serviceaccount  # Lista las cuentas disponibles
    ```

---

## Gestión de Datos Sensibles: Secrets
Los **Secrets** son objetos diseñados para almacenar información confidencial, como contraseñas, tokens de OAuth o llaves SSH.

*   **Uso:** En lugar de poner una contraseña en el código o en una variable de entorno de texto plano, se crea un Secret y se inyecta en el Pod como un **volumen montado** o una **variable de entorno**.
*   **Gestión básica:** Se pueden crear rápidamente con `kubectl create secret generic`.
*   **Seguridad avanzada:** Para una implementación profesional, se recomienda activar el **cifrado en reposo (Encryption at rest)** en la base de datos `etcd` del clúster, asegurando que si alguien accede al almacenamiento físico, los datos sigan protegidos.

## Seguridad en la Ejecución: Security Context
Mientras que RBAC controla el acceso a la API, el **SecurityContext** define los privilegios y la configuración de control de acceso para un **Pod** o un **Contenedor** en el momento de su ejecución.

### Funciones Principales
Configurar un contexto de seguridad permite establecer restricciones técnicas directamente en el archivo YAML del Deployment o StatefulSet:

*   **Control de Usuarios y Grupos**: Permite definir con qué ID de usuario (`runAsUser`) o grupo (`runAsGroup`) debe ejecutarse el proceso de la aplicación. Algunos de los **Controles recomendados:**
    *   **runAsNonRoot:** Obliga a que el contenedor no se ejecute como usuario root.
    *   **readOnlyRootFilesystem:** Monta el sistema de archivos del contenedor como solo lectura, evitando que un atacante instale software malicioso si logra entrar.
    *   **Privileged:** Nunca debe marcarse como `true` a menos que sea estrictamente necesario para funciones de infraestructura.
*   **Privilegios del Kernel**: Se pueden restringir capacidades del kernel de Linux para evitar que un contenedor comprometido afecte al nodo worker.
*   **Gestión de Volúmenes**: Mediante el `fsGroup`, se puede asegurar que los archivos creados en volúmenes (como los de **CephFS** en nuestro clúster) pertenezcan a un grupo específico para evitar problemas de permisos.

---

## Gestión de Certificados TLS y Automatización
Para que nuestros servicios sean accesibles de forma segura vía HTTPS, es necesario gestionar certificados TLS. Kubernetes tiene un sistema nativo para manejar esto mediante **CertificateSigningRequests (CSR)**.

*   **TLS en el clúster:** Kubernetes utiliza internamente una infraestructura de clave pública (PKI) para la comunicación entre componentes (como el kubelet y el API server).
*   **Automatización con Let's Encrypt:** Para microservicios web, la forma estándar de automatizar esto es mediante un operador llamado **cert-manager** (un recurso externo común en el ecosistema). 
    *   **Funcionamiento:** El administrador configura un "Issuer" (emisor) que se comunica con **Let's Encrypt**. 
    *   **Integración:** Al definir un Ingress para Traefik, se añade una anotación solicitando un certificado. `cert-manager` gestiona el desafío DNS/HTTP, descarga el certificado y lo guarda automáticamente en un **Secret de tipo TLS** que vuestro Ingress Controller (Traefik) utilizará para servir tráfico cifrado.

## Resumen de Buenas Prácticas

1.  **Principio de menor privilegio:** No otorguéis permisos de ClusterAdmin a aplicaciones que solo necesitan leer un namespace.
2.  **Aislar mediante Namespaces:** Usad namespaces para separar proyectos y aplicar cuotas y políticas de seguridad específicas.
3.  **Vigilar el tráfico:** Recordad que gracias a **Calico** (nuestro CNI), podemos usar **Network Policies** para actuar como un firewall interno entre microservicios.
4.  **No guardar secretos en Git:** Nunca subáis manifiestos YAML con datos sensibles; usad los objetos **Secret** de Kubernetes o soluciones de bóveda externas.