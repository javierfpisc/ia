# Monitorización de Salud en Kubernetes: Probes (Sondas)

Para que un clúster de Kubernetes sea verdaderamente **auto-reparable (Self-Healing)**, no basta con que un contenedor esté "encendido"; debe estar funcionando correctamente. Kubernetes utiliza el agente **kubelet** para asegurar que los contenedores descritos en los Pods estén funcionando y saludables mediante el uso de **Probes** (sondas).

A continuación, se detalla el funcionamiento de los tres mecanismos principales de monitorización de salud según la documentación oficial.

---

## Tipos de Sondas (Probes)

El kubelet puede realizar tres tipos de comprobaciones sobre un contenedor en ejecución:

### A. Liveness Probe (Sonda de Supervivencia)
*   **Objetivo:** Indica si el contenedor está vivo y funcionando.
*   **Acción tras fallo:** Si la sonda de supervivencia falla, el kubelet mata el contenedor y este queda sujeto a su política de reinicio (**restartPolicy**).
*   **Uso:** Se usa para detectar estados de bloqueo (deadlocks) donde la aplicación sigue encendida pero no puede progresar.

### B. Readiness Probe (Sonda de Disponibilidad)
*   **Objetivo:** Indica si el contenedor está listo para recibir tráfico de red.
*   **Acción tras fallo:** Si falla, el controlador de endpoints elimina la dirección IP del Pod de las listas de todos los **Services** que coincidan con el Pod.
*   **Uso:** Es vital para aplicaciones que tardan en cargar datos o configuraciones al arrancar, evitando que el usuario reciba errores mientras el servicio se estabiliza.

### C. Startup Probe (Sonda de Inicio)
*   **Objetivo:** Indica si la aplicación dentro del contenedor ha arrancado correctamente.
*   **Acción tras fallo:** Si se proporciona esta sonda, todas las demás (liveness y readiness) se desactivan hasta que esta tenga éxito.
*   **Uso:** Ideal para aplicaciones antiguas o pesadas que tienen tiempos de inicio muy largos e impredecibles.

### Readiness vs Liveness
La `readinessProbe` y la `livenessProbe` pueden parecer similares porque ambas realizan comprobaciones de salud sobre un contenedor, pero en realidad tienen objetivos distintos dentro de Kubernetes.
La `readinessProbe` se utiliza para determinar si el servicio está preparado para recibir tráfico de red. Su función es evaluar el estado “general” del servicio desde el punto de vista del clúster. Kubernetes usa esta información para decidir si el Pod debe participar o no en el balanceo de carga de un `Service`.
Por ejemplo, una aplicación puede estar ejecutándose correctamente, pero no estar preparada todavía para atender peticiones porque:

* está arrancando,
* todavía no ha conectado con la base de datos,
* está cargando datos,
* o un servicio externo necesario no está disponible.

En esos casos, la `readinessProbe` puede fallar temporalmente y Kubernetes dejará de enviar tráfico al Pod, pero el contenedor seguirá funcionando. Es decir, `readiness` controla si el servicio debe considerarse “disponible” dentro del sistema.

La `livenessProbe`, en cambio, tiene un objetivo más específico: comprobar si el microservicio concreto sigue funcionando internamente de forma correcta. Aquí Kubernetes ya no se pregunta si el Pod debe recibir tráfico, sino si la aplicación está realmente viva o se ha quedado bloqueada o inutilizable.
Por ejemplo, una aplicación puede:

* seguir ejecutándose como proceso,
* mantener el puerto abierto,
* pero estar colgada internamente,
* no responder,
* o haber entrado en un estado inconsistente.

En esa situación, la `livenessProbe` detectará el problema y Kubernetes reiniciará automáticamente el contenedor para intentar recuperar el servicio.

En resumen:

* `readinessProbe` decide si el Pod debe recibir tráfico dentro del clúster.
* `livenessProbe` decide si el contenedor debe reiniciarse porque la aplicación ya no funciona correctamente.

---

## Mecanismos de Comprobación (Handlers)

El kubelet puede ejecutar estas sondas utilizando cuatro métodos distintos:

1.  **`exec`**: Ejecuta un comando específico dentro del contenedor. Se considera saludable si el comando termina con un código de estado 0.
2.  **`httpGet`**: Realiza una petición HTTP GET contra la IP del Pod en un puerto y ruta específicos. Se considera saludable si el código de respuesta es mayor o igual a 200 y menor que 400.
3.  **`tcpSocket`**: Realiza una comprobación TCP contra la IP del Pod en un puerto específico. Si el puerto está abierto, se considera saludable.
4.  **`grpc`**: Realiza una comprobación de salud mediante el protocolo gRPC.

---

## Integración con el Entorno y Servicios

La monitorización de salud es el puente entre el **Plano de Control** y la disponibilidad del servicio:

*   **Ciclo de Vida:** Las sondas forman parte del ciclo de vida del Pod (**Pod Lifecycle**). Un Pod no se considera "Ready" (listo) hasta que sus sondas de disponibilidad tengan éxito.
*   **Relación con Services:** El recurso **Service** depende directamente del estado de las sondas de disponibilidad. Si la sonda falla, el Service deja de enviar tráfico a ese Pod específico, redirigiéndolo a otros Pods saludables del mismo Deployment.
*   **Auto-reparación:** El kubelet monitoriza constantemente estos estados y toma acciones inmediatas (reiniciar contenedores) sin intervención humana, manteniendo el estado deseado definido por el administrador.

### Resumen

| Sonda | ¿Qué pregunta? | ¿Qué pasa si falla? |
| :--- | :--- | :--- |
| **Liveness** | ¿La app se ha quedado colgada? | Se reinicia el contenedor. |
| **Readiness** | ¿Puedo enviarle tráfico ahora mismo? | Se retira del balanceador del Service. |
| **Startup** | ¿Ha terminado de arrancar por primera vez? | Bloquea otras sondas hasta que sea OK. |

Para configurar estas opciones, en los **Controllers** deben incluirse las sección `livenessProbe` o `readinessProbe` dentro de la especificación de los contenedores en sus archivos YAML de **Deployment** o **StatefulSet**.