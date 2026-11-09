# Namespaces: Organización y Aislamiento en Kubernetes

En Kubernetes, los **Namespaces** (espacios de nombres) son la herramienta fundamental para dividir un único clúster físico en múltiples "clústeres virtuales". Son esenciales para entornos donde múltiples usuarios, equipos o proyectos comparten la misma infraestructura, como es el caso de vuestro clúster de laboratorio.

---

## ¿Para qué se usan los Namespaces?
El objetivo principal de un Namespace es proporcionar un alcance o **scope** para los nombres de los recursos. Mientras que algunos recursos son globales (como los Nodos o los PersistentVolumes), la mayoría de los objetos (Pods, Services, Deployments) deben vivir dentro de un Namespace.

Por defecto, Kubernetes arranca con algunos Namespaces predefinidos:
*   **default:** Donde van los recursos si no se especifica otro espacio.
*   **kube-system:** Reservado para los objetos creados por el sistema de Kubernetes (como el DNS o el proxy).
*   **kube-public:** Legible por todos los usuarios, se usa para recursos que deben ser visibles en todo el clúster.

---

## Ventajas y Beneficios
El uso de Namespaces ofrece ventajas críticas para la administración de sistemas:

*   **Organización Logística:** Permiten separar entornos (ej: `desarrollo`, `preproducción`, `producción`) sin necesidad de mantener clústeres separados.
*   **Evitar Conflictos de Nombres:** Dos equipos diferentes pueden crear un Service llamado `frontend` siempre que estén en Namespaces distintos.
*   **Delegación de Administración:** Permiten que un administrador gestione quién tiene permisos sobre un entorno específico.

---

## Impacto en la Seguridad
Los Namespaces son la primera línea de defensa para el aislamiento en el clúster:

*   **RBAC (Control de Acceso):** Se pueden asignar permisos para que un usuario solo pueda ver o modificar recursos dentro de un Namespace concreto.
*   **Políticas de Seguridad de Pods:** Kubernetes permite aplicar estándares de seguridad (Pod Security Standards) a nivel de Namespace mediante etiquetas, asegurando que todos los contenedores de ese espacio cumplan con normas estrictas.
*   **Aislamiento de Red:** Aunque por defecto todos los Pods se hablan, se pueden usar **Network Policies** para restringir que el tráfico fluya entre diferentes Namespaces.

---

## Rendimiento y Gestión de Recursos
Contrario a lo que se podría pensar, los Namespaces **no afectan negativamente al rendimiento** del plano de datos (la velocidad de vuestras aplicaciones), pero son vitales para la estabilidad del clúster mediante:

*   **Resource Quotas:** Permiten limitar el consumo total de CPU, memoria o número de objetos que un Namespace puede usar. Esto evita que un error en una aplicación de `desarrollo` agote los recursos del clúster y afecte a `producción`.
*   **Limit Ranges:** Permiten definir valores por defecto de CPU y memoria para cada contenedor que se cree en ese espacio de nombres.

---

## Gestión Básica
Para nuestras prácticas, utilizaremos comandos sencillos de `kubectl` para gestionar estos entornos:

*   **Crear un Namespace:** `kubectl create namespace mi-proyecto`.
*   **Ver recursos de un Namespace:** `kubectl get pods -n mi-proyecto`.
*   **Establecer un Namespace por defecto:** Se puede configurar el contexto para no tener que escribir `-n` en cada comando.

### Resumen
En nuestro clúster, los Namespaces serán "tabiques" lógicos. Nos permitirán trabajar en nuestros proyectos sin interferir con los servicios del sistema o con otros despliegues, garantizando que cada proyecto tenga sus propios límites de recursos y reglas de seguridad.