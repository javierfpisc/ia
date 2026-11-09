# Gestíon de Certificados TLS

## Instalación de cert-manager
`cert-manager` es un sistema dentro de Kubernetes que:

* Crea certificados TLS automáticamente
* Los renueva antes de que caduquen
* Habla con Let’s Encrypt usando ACME
* Guarda los certificados como Secrets

Desde el nodo Manager:
```bash
kubectl apply -f \
https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml
```
Despliegue en el clúster, dentro del namespace `cert-manager`:

* cert-mangaer controller
* webhook
* cainjector
* CRDs (Certificate, Issuer, ClusterIssuer, etc.)

Comprobamos:
```bash
kubectl get pods -n cert-manager
```
Produce una salida del estilo:
```
NAME                                       READY   STATUS    RESTARTS   AGE
cert-manager-5cd87b5494-q7phg              1/1     Running   0          70s
cert-manager-cainjector-6787bd5556-bp4cv   1/1     Running   0          70s
cert-manager-webhook-5d8d9bb8fd-fvsnm      1/1     Running   0          70s
```

## Creación del ClusterIssuer
Ahora creamos el “emisor global de certificados”. Este es el componente que conecta cert-manager con **Let’s Encrypt**.
Creamos el archivo `cluster-issuer.yaml` con el siguiente contenido:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    email: cedpsc@iessanclemente.net
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-account-key
    solvers:
      - http01:
          ingress:
            class: traefik
```

Creamos el recurso ClusterIssuer ejecutando en `kuber1`:
```bash
kubectl apply -f cluster-issuer.yaml
```
Comprobamos estado:
```bash
kubectl get clusterissuers.cert-manager.io
```
Mostraría:
```
NAME               READY   AGE
letsencrypt-prod   True    2m12s
```

## Explicación del ClusterIssuer anterior:
`ClusterIssuer` es un recurso “global” del clúster, por tanto se puede usar desde cualquier namespace.
Para que nuestro clúster pueda obtener certificados SSL/TLS de forma automática y gratuita, utilizamos un componente llamado **cert-manager**. El recurso `ClusterIssuer` es la configuración global que le dice al clúster quién va a emitir esos certificados (en este caso, **Let's Encrypt**).

A continuación, se explica de forma sencilla cada parte del archivo YAML:

### Identificación del Recurso

*   **`apiVersion: cert-manager.io/v1`**: Indica que estamos usando la API de **cert-manager**, que es el estándar para gestionar certificados en Kubernetes.
*   **`kind: ClusterIssuer`**: A diferencia de un `Issuer` normal (que solo funciona en un Namespace), un **ClusterIssuer** es un recurso global que puede emitir certificados para aplicaciones en cualquier parte de vuestro clúster.

### Metadatos

*   **`name: letsencrypt-prod`**: Es el nombre que le damos a este emisor. Cuando queráis proteger una web, tendréis que hacer referencia a este nombre en vuestros objetos Ingress.

### Configuración de ACME (Let's Encrypt)
La sección `spec.acme` contiene la configuración para el protocolo ACME, que es el lenguaje que usa Let's Encrypt para validar dominios:

*   **`email: cedpsc@iessanclemente.net`**: Es nuestro correo de contacto. Let's Encrypt lo usará para avisaros si un certificado está a punto de caducar o si hay problemas con vuestra cuenta.
*   **`server: https://acme-v02.api.letsencrypt.org/directory`**: Es la dirección oficial del servidor de producción de **Let's Encrypt**. Es el "lugar" al que el clúster llamará para pedir los certificados.
*   **`privateKeySecretRef`**:
    *   **`name: letsencrypt-account-key`**: Es el nombre del **Secret** donde Kubernetes guardará de forma segura la clave privada de vuestra cuenta de Let's Encrypt.

### Resolución del Desafío (Solvers)
Para que Let's Encrypt nos dé un certificado, debemos demostrar que somos los dueños del dominio. A esto se le llama "desafío".

*   **`http01`**: Indica que usaremos el método de validación por HTTP. Let's Encrypt intentará acceder a un archivo temporal en vuestra web para verificar la propiedad.
*   **`ingress.class: traefik`**: Le indica a `cert-manager` que debe coordinarse con nuestro Ingress Controller (**Traefik**) para exponer temporalmente ese archivo de validación al mundo exterior.

---

## Generación de certificados autofirmados
Cuando no sea posible responder al desafío de ACME de Letsencrypt y éste, u otro proveedor de certificados, no puede validar el dominio (muy típico en entornos de laboratorio, redes privadas o sin acceso público al puerto 80/443), la alternativa correcta en Kubernetes es usar **certificados autofirmados** gestionados por cert-manager. Para disponer de infraestructura que pueda operar en estos casos procedemos según los siguientes pasos:

### Crear una CA autofirmada
Partiendo de una especificación de tipo de ClusterIssuer como la siguiente `clissuer-selfsigned.yaml`:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-ca
spec:
  selfSigned: {}
```
Creamos el ClusterIssuer para certificados autofirmados:
```bash
kubectl apply -f clissuer-selfsigned.yaml
```

### Crear certificado que actúa como CA
Usamos el siguiente archivo de recurso `internal-ca.yaml`
```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: internal-ca
  namespace: cert-manager
spec:
  isCA: true
  commonName: internal-ca
  secretName: internal-ca-secret
  privateKey:
    algorithm: RSA
    size: 2048
  issuerRef:
    name: selfsigned-ca
    kind: ClusterIssuer
```
En la definición anterior podemos ver como el Certificate hace referencia, en la sección `issuerRef` al `ClusterIssuer` anterior. A continuación creamos el Certificate:
```bash
kubectl apply -f internal-ca.yaml
```

### Creamos ClusterIssuer basado en la CA anterior
Partimos del siguiente archivo de recurso `interal-ca-issuer.yaml`:
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: internal-ca-issuer
spec:
  ca:
    secretName: internal-ca-secret
```
Creamos la nueva ClusterIssuer basada en la CA:
```bash
kubectl apply -f internal-ca-issuer.yaml
```
El objeto `ClusterIssuer` definido de este modo será el que utilicemos en nuestros `Ingress` para hacer uso de certificados autofirmados.

!!! important "SECCIÓN DEL INGRESS"
    La sección del ingress **metadata** sería algo como:

    ```
    metadata:

      name: nginx-ingress
    
      namespace: ejemplos

      annotations:

        cert-manager.io/cluster-issuer: internal-ca-issuer
    ```

## Reescritura del Ingress con certificado
Incorporaremos los datos del certificado a la definición del `Ingress`de una práctica anterior:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: ejemplos
  annotations:
    # Definición de los endopints http y https
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
    # Cert-manager (emite el certificado)
    cert-manager.io/cluster-issuer: internal-ca-issuer
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - nginx.192.168.56.41.nip.io
      secretName: nginx-tls
  rules:
    - host: nginx.192.168.56.41.nip.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx-service
                port:
                  number: 80
```
Aplicamos:
```bash
kubectl apply -f ingress-1.yaml
```
El comando anterior aplica los cambios al objeto Ingress, que ya existe. Esto es un comportamiento habitual en kubernetes, modificar los yaml de definición de recursos y aplicar los cambios directamente. Al acceder a través del navegador por la URL **https://nginx.192.168.56.41.nip.io** llegaremos al Ingress anterior y nos responderá con el certificado autofirmado.

El yaml anterior incluye una nueva sección, **tls**, dentro del **spec** del objeto **Ingress**, la cual define dos directivas:

* **host**: Define el dominio al que se aplicará el certificado TLS.
* **secretName**: Es el nombre del Secret de Kubernetes que contiene el certificado y la clave privada TLS.

También añade dos nuevas **annotations** dentro del **metadata**:

* **traefik.ingress.kubernetes.io/router.entrypoints: web,websecure**: Habilita los 2 endpoints **http/https**
* **cert-manager.io/cluster-issuer: internal-ca-issuer**: Esta anotación le indica a cert-manager qué emisor de certificados, **CluserIssuer**, debe usar para generar el certificado TLS del Ingress

## Resumen
En nuestro laboratorio, este archivo es el que "conecta" el clúster con internet para que todas nuestras aplicaciones web tengan el candado verde de HTTPS automáticamente. 

1.  **Cert-manager** lee esta configuración.
2.  Habla con **Let's Encrypt**.
3.  Usa a **Traefik** para demostrar que somos los dueños del dominio.
4.  Guarda el certificado resultante en un **Secret** para que nuestra web pueda usarlo.
