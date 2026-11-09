# Despliegue de imágenes seguras
En Kubernetes, la seguridad de las cargas de trabajo comienza por la base: las **imágenes de los contenedores**. Estas imágenes son la base de las aplicaciones y garantizar que sean seguras es fundamental para proteger el clúster.

El uso de imágenes seguras implica no solo descargarlas de fuentes confiables, sino también gestionar adecuadamente las credenciales cuando se utilizan **registros privados** mediante el uso de **Secrets** de Kubernetes. Además, es una buena práctica aplicar **Estándares de Seguridad de Pods** y utilizar **Namespaces** para aislar los recursos y limitar el radio de alcance de posibles vulnerabilidades.

Disponemos de herramientas específicas que pueden facilitar enormemente esta tarea. El ecosistema **Cloud Native** se apoya en soluciones externas para cubrir todo el ciclo de vida de la imagen:

*   **Harbor**: Un registro privado de confianza que permite almacenar y gestionar imágenes de forma segura dentro de la propia infraestructura.
*   **Trivy**: Una herramienta de escaneo que busca vulnerabilidades conocidas dentro de las imágenes antes de que lleguen al clúster.
*   **Cosign**: Permite la firma y verificación de imágenes, asegurando que el contenedor que se ejecuta es exactamente el autorizado.
*   **Kyverno**: Un motor de políticas que puede impedir, por ejemplo, que se desplieguen imágenes que no hayan sido escaneadas por Trivy o firmadas con Cosign.

## Harbor. Nuestro Registry privado
Comencemos por montar Harbor en nuestro clúster, para ello haremos uso de Helm.
Crearemos un namespace asociado a Harbor:
```bash
kubectl create namespace harbor
```
Añadimos el repositorio de Helm y lo actualizamos:
```bash
helm repo add harbor https://helm.goharbor.io
helm repo update
```
Definimos nuestro archivo de values personalizado para helm, **harbor-values.yaml:**
```yaml
expose:
  type: ingress
  ingress:
    className: traefik
    hosts:
      core: harbor.192.168.56.41.nip.io
    annotations:
      cert-manager.io/cluster-issuer: internal-ca-issuer
      traefik.ingress.kubernetes.io/router.entrypoints: websecure
externalURL: https://harbor.192.168.56.41.nip.io
harborAdminPassword: "Harbor12345"
persistence:
  enabled: true
  persistentVolumeClaim:
    registry:
      storageClass: ceph-filesystem
      size: 20Gi
    jobservice:
      storageClass: ceph-filesystem
      size: 3Gi
    database:
      storageClass: ceph-filesystem
      size: 5Gi
    redis:
      storageClass: ceph-filesystem
      size: 3Gi
    trivy:
      storageClass: ceph-filesystem
      size: 3Gi
trivy:
  enabled: true
  vulnType: "os,library"
  severity: "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL"
portal:
  replicas: 1
core:
  replicas: 1
jobservice:
  replicas: 1
registry:
  replicas: 1
database:
  internal:
    password: "Harbor12345"
redis:
  internal:
    password: "Harbor12345"
```
Instalamos el Chart con Helm, tomando como referencia los valores del archivo anterior:
```bash
helm install harbor harbor/harbor -n harbor -f harbor-values.yaml
```
Comprobamos tras la ejecución si "todo está en su sitio":
```bash
kubectl -n harbor get pods
kubectl -n harbor get ingress
```
Ya podemos entrar a través de la URL **https://harbor.192.168.56.41.nip.io**. La autenticación sería con las credenciales (según lo anterior):

* usuario: **admin**
* password: **Harbor12345**

## Subiendo imágenes a Harbor
Para probar las funcionalidades de gestión de imágenes seguras de Harbor empezaremos por crear una imagen de prueba local con vulnerabilidades reconocibles. Generamos mediante a partir del siguiente **Dockerfile** la imagen:
### Generación de la imagen con Dockerfile
```bash
FROM debian:10

RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until && \
    apt-get update && \
    apt-get install -y curl openssl && \
    rm -rf /var/lib/apt/lists/*

CMD ["sleep", "3600"]
```
Generamos la imagen a partir del Dockerfile y la etiquetamos para hacer referencia a nuestro Registry de Harbor:
```bash
docker build -t harbor.192.168.56.41.nip.io/library/debian:vuln .
```
### Subida de la imagen al Registry
Para poder autenticar contra el Registry de Harbor necesitamos disponer del certificado de la CA asociada, para obtenerlo ejecutamos en `kuber1`:
```bash
kubectl get secret harbor-tls -n harbor -o jsonpath="{.data.ca\.crt}" \
| base64 -d > harbor-ca.crt
```
Tomamos el contenido del archivo anterior, conteniendo la crt de la CA **harbor-ca.crt** y en el equipo cliente, en el que hemos generado la imagen Docker y desde el que la vamos a subir al Registry, creamos el archivo correspondiente **harbor-ca.crt**, a continuación:
```bash
mkdir -p ~/.docker/certs.d/harbor.192.168.56.41.nip.io
cp harbor-ca.crt ~/.docker/certs.d/harbor.192.168.56.41.nip.io/ca.crt
```
Subimos la imagen a Harbor, en primer lugar hacemos login al Registry:
```bash
docker login harbor.192.168.56.41.nip.io
```
A continuación hacemos push de la imagen:
```bash
docker push harbor.192.168.56.41.nip.io/library/debian:vuln
```
### Escaneo de la imagen y obtención de información de la misma
Una vez subida la imagen, desde la interfaz de Harbor, **Proyectos->library**, seleccionamos la imagen subida y activamos **Escanear Vulnerabilidad**. Esta opción hará uso de **Trivy** para mostrar las vulnerabilidades encontradas en la imagen.
También disponemos de la opción **Generar SBOM (Software Bill Of Materials)**, qie es básicamente **"la lista de ingredientes de una imagen Docker"**, que contiene:

* paquetes del sistema
* librerías
* dependencias
* paquetes software
* versiones
* hashes
* licencias
* proveedor/origen

Estas SBOM se utilizan para auditoría, compliance, trazabilidad, análisis de vulnerabilidades, etc.

## Firmado de imágenes docker con Cosign
En el ecosistema actual, el software sin firmar está expuesto a varios riesgos críticos:

*   **Suplantación (Typosquatting):** Alguien publica una imagen con un nombre casi idéntico a una oficial.
*   **Sitios comprometidos:** El registro donde guardamos nuestras imágenes (como Docker Hub o uno propio) es hackeado.
*   **Alteración post-publicación:** Un atacante modifica una imagen ya publicada para incluir código malicioso.

La **firma criptográfica** permite a los consumidores del software (en nuestro caso, el clúster de Kubernetes) verificar que el artefacto proviene de una fuente confiable y que **no ha sido alterado** desde su creación.

**Cosign** es una herramienta del proyecto de código abierto **Sigstore**. Está diseñada específicamente para facilitar la firma y verificación de contenedores, integrándose de forma natural con los registros de imágenes. 

Aunque Sigstore es famoso por su modo "keyless" (sin claves permanentes), entender el flujo con un par de claves (pública, privada) manual es la mejor forma de entender el concepto.

### Firmando una imagen docker
Lo primero será instalar, por ejemplo en el equipo de trabajo en el que hemos creado la imagen, la herramienta, para ello ejecutamos:
```bash
LATEST_VERSION=$(curl https://api.github.com/repos/sigstore/cosign/releases/latest \
| grep tag_name | cut -d : -f2 | tr -d "v\", ")
curl -O -L \
"https://github.com/sigstore/cosign/releases/latest/download/cosign_${LATEST_VERSION}_amd64.deb"
sudo dpkg -i cosign_${LATEST_VERSION}_amd64.deb
```
Una vez instalada la herramienta dispondremos del comando **cosign** para operar con ella. Empezamos creando un par de claves para la firma:
```bash
cosign generate-key-pair
```
A continuación firmamos la imagen docker generada anteriormente:
```bash
cosign sign --key cosign.key harbor.192.168.56.41.nip.io/library/debian:vuln
```
Enviamos la imagen al registry de Harbor:
```bash
docker push harbor.192.168.56.41.nip.io/library/debian:vul
```
Si a continuación accedemos a la interfaz del registry de Harbor veremos como ahora la imagen aparece marcada como **Firmada**.

Vamos a verificar de modo manual la firma. Para ello necesitamos la clave pública asociada:
```bash
cosign verify --key cosign.pub harbor.192.168.56.41.nip.io/library/debian:vuln
```

## Establecimiento de políticas de uso de imágenes
A continuación vamos a efectuar un sencillo ejemplo de aplicación de política de imágenes mediante **ClusterPolicy** de **Kyverno**. En él trataremos de desplegar en el cluster un **Pod** basado en una imagen con la etiqueta **latest**, lo cual se considera una mala práctica, ya que esa etiqueta no hace referencia a una versión específica, la cual puede variar. A través de una **ClusterPolicy** impondremos que solo se admitan en el clúster containers basados en imágenes que no utilicen esa etiqueta.

Creamos el **ClusterPolicy** en el archivo **disable-latest-tag.yaml**:
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: require-image-tag
      match:
        any:
        - resources:
            kinds:
              - Pod
      validate:
        message: "No se permite utilizar imágenes con la etiqueta latest."
        pattern:
          spec:
            containers:
            - image: "!*:latest"
```

Para desplegar el **ClusterPolicy** anterior necesitamos disponer de **Kyverno** el cual podemos instalar con **Helm** siguiendo los pasos siguientes:
Creamos el namespace:
```bash
kubectl create ns kyverno
```
Añadimos el repo del Helm:
```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update
```
Instalamos:
```bash
helm install kyverno kyverno/kyverno -n kyverno
```
Una vez desplegado **Kyverno** aplicamos la **ClusterPolicy**:
```bash
kubectl apply -f disable-latest-tag.yaml
```
Comprobamos si la **ClusterPolicy** se aplica. En primer lugar lancemos un Pod de ngnix con una etiqueta de imagen específica:
```bash
kubectl run nginx-ok --image=nginx:1.27 --restart=Never
```
El Pod anterior debería ser admitido por kubernetes y ejecutado. Ahora lancemos Pod de la imagen nginx con etiqueta latest (no admitida):
```bash
kubectl run nginx-bad --image=nginx:latest --restart=Never
```
Veremos un mensaje de error como el siguiente:
```
Error from server: admission webhook "validate.kyverno.svc-fail" denied the request: 

resource Pod/default/nginx-bad was blocked due to the following policies 

disallow-latest-tag:
  require-image-tag: 'validation error: No se permite utilizar imágenes con la etiqueta
    latest. rule require-image-tag failed at path /spec/containers/0/image/'
```
A continuación creemos una **ClusterPolicy** más restrictiva, que permita solamente Pods basados en imágenes de nuestro registry. Creemos el archivo **allow-only-harbor.yaml**:
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: only-harbor-images
spec:
  validationFailureAction: Enforce
  background: true
  rules:
    - name: restrict-image-registries
      match:
        any:
        - resources:
            kinds:
              - Pod
      validate:
        message: "Solo se permiten imágenes almacenadas en Harbor."
        pattern:
          spec:
            containers:
            - image: "harbor.192.168.56.41.nip.io/*"
```
Aplicamos la política:
```bash
kubectl apply -f allow-only-harbor.yaml
```
Ahora lancemos un Pod que verifique la restricción, el cual será admitido:
```bash
kubectl run debian-harbor \
--image=harbor.192.168.56.41.nip.io/library/debian:vul --restart=Never
```
Si lanzamos un Pod de una imagen que no esté en el registry, como a continuación:
```bash
kubectl run debian-bad --image=debian:bookworm --restart=Never
```
Obtendremos el error causado por el no cumplimiento de la política:
```
Error from server: admission webhook "validate.kyverno.svc-fail" denied the request: 

resource Pod/default/debian-bad was blocked due to the following policies 

only-harbor-images:
  restrict-image-registries: 'validation error: Solo se permiten imágenes almacenadas
    en Harbor. rule restrict-image-registries failed at path /spec/containers/0/image/'
```
## Limpieza del entorno
Para evitar problemas futuros con las restricciones que hemos definido las borraremos al terminar la práctica, para ello simplemente:
```bash
kubectl delete clusterpolicy disallow-latest-tag
kubectl delete clusterpolicy only-harbor-images
```
También, para liberar recursos del cluster, podemos eliminar el stack de Kyverno con el comando:
```bash
helm uninstall kyverno -n kyverno
```