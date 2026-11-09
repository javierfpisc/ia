# Configuración y Secretos: Desacoplando la Aplicación del Entorno

En Kubernetes, una de las mejores prácticas de administración es **separar el código de la configuración**. Para lograr esto, el sistema proporciona dos recursos fundamentales que permiten inyectar datos en los contenedores sin necesidad de modificar las imágenes de las aplicaciones: los **ConfigMaps** y los **Secrets**.

---

## ConfigMaps

*   **¿Qué son?**: Objetos de la API utilizados para almacenar datos no confidenciales en pares clave-valor. Su propósito fundamental es **desacoplar la configuración del entorno de la imagen del contenedor**, lo que permite que tus aplicaciones sean portátiles y fáciles de actualizar sin tener que reconstruir la imagen.
*   **Uso común**: Archivos de configuración (`nginx.conf`), variables de entorno de la aplicación o parámetros de inicio de una base de datos.

### Estructura de un ConfigMap
Un ConfigMap consta principalmente de dos campos donde se almacenan los datos:

*   **`data`**: Para secuencias de caracteres (UTF-8). Es el más común para archivos de texto o variables simples.
*   **`binaryData`**: Para datos binarios codificados en base64 (como imágenes o archivos comprimidos).

### Formas de Consumir ConfigMaps en un Pod
Existen cuatro formas principales de integrar estos datos en un contenedor:

1.  **Variables de entorno individuales**: Utilizando `valueFrom` y `configMapKeyRef` para asignar una clave específica a una variable.
2.  **Carga masiva de variables**: Mediante `envFrom`, Kubernetes inyecta automáticamente todas las claves del ConfigMap como variables de entorno en el contenedor.
3.  **Argumentos de línea de comandos**: Se pueden usar las variables de entorno inyectadas para definir los comandos de inicio del contenedor (`command` y `args`).
4.  **Volúmenes montados (Archivos de configuración)**: Esta es la forma más potente. Kubernetes crea un archivo por cada clave del ConfigMap en una ruta específica del contenedor.

### Actualizaciones y Propagación
Un aspecto crítico a comprender es cómo se reflejan los cambios:

*   **Volúmenes**: Si actualizas un ConfigMap que se consume mediante un volumen, Kubernetes **actualiza automáticamente los archivos** dentro del contenedor transcurrido un breve periodo de tiempo (aunque la aplicación debe ser capaz de detectar el cambio y recargar la configuración).
*   **Variables de entorno**: Si el ConfigMap se usa como variable de entorno, el cambio **no se refleja** hasta que el Pod se reinicia.

### Gestión mediante `kubectl`
Para la administración diaria se usarán estos comandos:

*   **Creación rápida (Imperativa)**:
    ```bash
    # Desde un archivo físico
    kubectl create configmap mi-config --from-file=config.properties
    # Desde valores directos
    kubectl create configmap colores --from-literal=fondo=rojo \
    --from-literal=texto=blanco
    ```
*   **Inspección**:
    ```bash
    kubectl get configmaps           # Listar todos
    kubectl describe configmap <nombre>  # Ver el contenido detallado
    ```

### Buenas Prácticas y Limitaciones
*   **No para datos sensibles**: Las contraseñas o tokens deben usar **Secrets**, no ConfigMaps.
*   **Límite de tamaño**: Un ConfigMap no puede superar el **1 MiB** de tamaño.
*   **Inmutabilidad**: En versiones recientes, puedes marcar un ConfigMap como `immutable: true`. Esto impide cambios accidentales y mejora el rendimiento del clúster, ya que el **kubelet** deja de vigilar cambios en ese objeto.

En resumen, el **ConfigMap** actúa como el "diccionario de configuración" de un microservicio, permitiendo que la misma imagen de NGINX o MariaDB se comporte de forma distinta simplemente cambiando el objeto asociado en el clúster.

## Secrets

*   **¿Qué son?**: Al igual que los ConfigMaps, los **Secrets** son objetos fundamentales para la configuración de aplicaciones, pero con una distinción crítica: están diseñados específicamente para manejar **información sensible** o confidencial. Mientras que un ConfigMap es para datos públicos (como un archivo `.conf`), un Secret es para contraseñas, tokens de API o llaves privadas.
*   **Uso común**: Contraseñas, tokens de autenticación, llaves SSH o certificados TLS.
*   **Nota de seguridad**: Por defecto, los Secrets se almacenan como texto codificado en **Base64**. Para una seguridad real en producción, se recomienda activar el cifrado en reposo en el clúster.

### El concepto de "Opaque" y Codificación
Por defecto, la mayoría de los Secrets que se crearán son de tipo **Opaque**. Es vital constatar que los datos en un Secret no están cifrados de forma nativa en el archivo YAML, sino **codificados en Base64**.

*   **Codificación no es Cifrado:** Base64 es solo un formato de representación. Cualquiera con acceso al YAML puede decodificarlo fácilmente.
*   **Seguridad real:** Para una protección robusta, el clúster debe configurarse con **cifrado en reposo** (at rest) en la base de datos `etcd`.

### Tipos comunes de Secrets
Kubernetes ofrece varios tipos especializados para facilitar tareas comunes:

*   **`generic` (Opaque):** El más usado para contraseñas o claves de configuración de la aplicación.
*   **`kubernetes.io/tls`:** Específicamente diseñado para almacenar un certificado y su clave privada (usado frecuentemente con Ingress).
*   **`kubernetes.io/dockerconfigjson`:** Se utiliza para almacenar las credenciales de acceso a un registro de imágenes privado (como Docker Hub o un registro propio).

### Modos de Despliegue y Gestión
Al igual que con otros recursos, se pueden gestionar de tres formas:

*   **Imperativa:** `kubectl create secret generic mi-secreto --from-literal=pass=1234`. Es ideal para evitar dejar rastros de contraseñas en archivos.
*   **Declarativa (Archivo YAML):** Los valores deben estar ya en Base64 bajo el campo `data`, o en texto plano bajo `stringData` (Kubernetes se encargará de convertirlos a Base64 al subirlos).
*   **Kustomize:** Permite generar secretos de forma dinámica a partir de archivos locales.

### Inyección en los Pods
Los Secrets se inyectan de forma idéntica a los ConfigMaps, pero con sus propias etiquetas de referencia:

*   **Como Variables de Entorno:** Usando `secretKeyRef` para mapear una clave del secreto a una variable interna del contenedor.
*   **Como Volúmenes:** Se montan como archivos en una ruta específica. Esto es **más seguro** que las variables de entorno, ya que el contenido del secreto solo reside en la memoria volátil del Pod (tmpfs) y no es visible en los logs del sistema o inspecciones de procesos básicos.

### Buenas Prácticas de Seguridad
Debido a la naturaleza sensible de estos objetos, se deben seguir estas pautas:

1.  **RBAC (Control de Acceso):** Limitar quién puede ejecutar `kubectl get secrets`. Normalmente, solo los administradores o aplicaciones específicas deberían tener este permiso.
2.  **No subir a Git:** Nunca se deben subir los YAML de Secrets con datos reales a repositorios de código. Se deben usar herramientas de gestión de secretos externas o plantillas vacías.
3.  **Principio de menor privilegio:** Un Pod solo debe tener acceso a los Secrets que realmente necesita para funcionar.

### Resumen de comandos útiles
*   **Crear:** `kubectl create secret generic <nombre> --from-literal=key=value`.
*   **Ver (codificado):** `kubectl get secret <nombre> -o yaml`.
*   **Describir (sin mostrar valores):** `kubectl describe secret <nombre>` (solo muestra el tamaño y los nombres de las claves por seguridad).

---

## Modos de Creación (Despliegue)

Al igual que con todos los artefactos de kubernets, existen dos formas principales de crear estos recursos:

### A. Modo Imperativo (Comandos rápidos)
Ideal para pruebas rápidas o para evitar subir datos sensibles a un repositorio Git.

*   **Crear ConfigMap desde un valor directo**:
    ```bash
    kubectl create configmap mi-config --from-literal=APP_COLOR=azul
    ```
*   **Crear Secret de tipo genérico**:
    ```bash
    kubectl create secret generic mi-password --from-literal=password=supersecreto
    ```

### B. Modo Declarativo (Archivos YAML)
Es el modo recomendado para documentar la infraestructura del proyecto.

**Ejemplo de ConfigMap (`config.yaml`):**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-settings
  namespace: ejemplos
data:
  database_url: "mariadb-service"
  log_level: "debug"
```

---

## Modos de Inyección en los Pods

Una vez creados, existen dos formas principales de "entregar" estos datos a los contenedores:

### Como Variables de Entorno
Es el método más sencillo para configuraciones que la aplicación lee al arrancar.

```yaml
spec:
  containers:
    - name: mi-app
      image: nginx
      env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: app-settings
              key: database_url
        - name: DB_PASS
          valueFrom:
            secretKeyRef:
              name: mi-password
              key: password
```

### Como Volúmenes Montados (Archivos)
Ideal para archivos de configuración complejos. Kubernetes monta el contenido del ConfigMap o Secret como archivos dentro de una carpeta del contenedor.

```yaml
spec:
  containers:
    - name: mi-app
      volumeMounts:
        - name: config-volume
          mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: app-settings
```

---

## Resumen

Para gestionar estos recursos a nivel práctico, usaremos estos comandos de inspección:

| Tarea | Comando |
| :--- | :--- |
| **Listar recursos** | `kubectl get configmaps` / `kubectl get secrets` |
| **Ver contenido detallado** | `kubectl describe configmap <nombre>` |
| **Ver valores del Secret** | `kubectl get secret <nombre> -o yaml` |
| **Explicación de campos** | `kubectl explain configmap` / `kubectl explain secret` |