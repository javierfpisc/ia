# Despliegue Declarativo (GitOps)
**ArgoCD** es una herramienta de **Entrega Continua (CD)** declarativa diseñada específicamente para Kubernetes. Se basa en la metodología **GitOps**, que consiste en utilizar un repositorio de Git (como GitHub o GitLab) como la "fuente de verdad" de todo lo que debe estar instalado en el clúster.

## ¿Qué función cumple en la administración?
Si hasta ahora hemos usado `kubectl apply -f` o `helm install` desde nuestros terminales, ArgoCD cambia el flujo:

*   **Sincronización Automática:** ArgoCD vigila repositorios de Git. En cuanto detecta un cambio en un archivo YAML (como un cambio en el número de réplicas de un Deployment), lo aplica automáticamente en el clúster.
*   **Detección de "Drift":** Si alguien cambia algo manualmente en el clúster (por ejemplo, borra un Service por error), ArgoCD detecta que el clúster ya no coincide con lo que dice Git y lo "corrige" para volver al estado deseado.
*   **Interfaz Visual:** Ofrece un panel web donde los podemos ver de forma gráfica cómo están conectados Pods, Services e Ingress, y si están "Sincronizados" o no.

## Alternativas a ArgoCD
Aunque ArgoCD es muy popular por su interfaz visual, existen otras opciones en el ecosistema:

1.  **FluxCD:** Es el principal competidor. A diferencia de ArgoCD, no tiene una interfaz web nativa tan pesada; es más ligero y se gestiona principalmente mediante terminal y código. Es la opción preferida para quienes buscan "puro código".
2.  **Jenkins X:** Una versión de Jenkins rediseñada para Kubernetes que automatiza todo el flujo, desde que el programador escribe el código hasta que llega al clúster.
3.  **GitLab Agent for Kubernetes:** Si utilizáis GitLab, su agente nativo permite realizar despliegues siguiendo la filosofía GitOps de forma integrada.

---

## Desplegando ArgoCD
Vamos a desplegar ArgoCD en nuestro clúster empleando para ello  Helm. Comenzamos añadiendo el repositorio:
```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```
Creamos el namespace para el despliegue:
```bash
kubectl create namespace argocd
```
Usaremos para la instalación con Helm el sencillo archivo de parametrización **argocd-values.yaml**:
```yaml
global:
  domain: argocd.192.168.56.41.nip.io
configs:
  params:
    server.insecure: true
server:
  replicas: 1
  service:
    type: ClusterIP
  extraArgs:
    - --insecure
repoServer:
  replicas: 1
applicationSet:
  replicas: 1
controller:
  replicas: 1
redis:
  enabled: true
dex:
  enabled: false
notifications:
  enabled: false
```
Instalamos:
```bash
helm install argocd argo/argo-cd -n argocd -f argocd-values.yaml
```
Creamos un **Ingress** para poder llegar al servicio mediante https desde el navegador. Usamos el siguiente archivo **argocd-ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server
  namespace: argocd
  annotations:
    cert-manager.io/cluster-issuer: internal-ca-issuer
    traefik.ingress.kubernetes.io/router.entrypoints: web,websecure
spec:
  ingressClassName: traefik
  tls:
    - hosts:
        - argocd.192.168.56.41.nip.io
      secretName: argocd-tls
  rules:
    - host: argocd.192.168.56.41.nip.io
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: argocd-server
                port:
                  number: 80
```
Como siempre lo aplicamos con:
```bash
kubectl apply -f argocd-ingress.yaml
```
Una vez desplegado el Ingress podremos acceder a través de la URL **https://argocd.192.168.56.41.nip.io**. Para acceder con el usuario **admin** deberemos de recuperar la password inicial (que está almacenada en un secreto generado durante el despliegue con Helm) ejecutando:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o \
jsonpath="{.data.password}" | base64 -d; echo
```
Una vez dentro de la interfaz de ArgoCD podremos cambiar la contraseña de admin desde **User Info**

### Añadiendo un repositorio Helm ArgoCD
Desde la interfaz web, en **Settings->Repositories** añadiremos (Connect Repo) a modo de ejemplo el siguiente repo:

* **Connection method**: http/https
* **Type**: helm
* **Name**: bitnami
* **Repository url:** https://charts.bitnami.com/bitnami

### Creando nuestra primera Apliación en ArgoCD. Wordpress.
Partiendo del repositorio anterior, Helm de bitnami, vamos a crear una aplicación a partir de los Charts de ese repositorio.
Bien desde la lista de repositorios (opción **Create Application** desde los "3 puntos" del lado derecho), bien desde **Applications**, daremos de alta una nueva aplicación a partir de unos de los Charts Helm del repositorio de bitnami.
Los datos para definir el template de la aplicación:

* name: wordpress
* project: default
* marcamos **auto create namespace**
* chart: wordpress
* cluster: https://kubernetes.default.svc
* namespace: wordpress
* version: 31.0.0 (Una vez seleccionada esperados a que (Loading...) se carguen las opciones del Chart)

Para las opciones del Chart marcamos:

* service.type: ClusterIP
* global.defaultStorageClass: ceph-filesystem
* mariadb.primary.persistence.storageClass: ceph-filesystem
* persistence.storageClass: ceph-filesystem
* ingress.enabled: 'true'
* ingress.hostname: wordpress.192.168.56.41.nip.io
* ingress.ingressClassName: traefik
* wordpressPassword: abc123.
* wordpressUsername: admin

Una vez terminadas de definir las opciones activamos **Create**. Esto desencadenará el procedimiento de despliegue del Chart y creación de todos los artefactos asociados (namespace, config map, secret, deployment, pvc, network policy, statefulset, service e ingress).
Desde la interfaz de la aplicación podremos visualizar de distintos modos estos elementos, sus relaciones y estado de sincronización de varias maneras (diagrama en árbol, tabla, agrupación por nodo, etc.).

Desde los **Details** de la aplicación podremos acceder al archivo **Manifest**, el cual recoge la configuración realizada para ese Chart en formato **yaml**. Podremos editar ese archivo y efectuar cambios desde él. En nuestro caso su contenido sería:
```yaml
project: default
source:
  repoURL: https://charts.bitnami.com/bitnami
  targetRevision: 30.1.8
  helm:
    parameters:
      - name: service.type
        value: ClusterIP
      - name: global.defaultStorageClass
        value: ceph-filesystem
      - name: mariadb.primary.persistence.storageClass
        value: ceph-filesystem
      - name: persistence.storageClass
        value: ceph-filesystem
      - name: ingress.enabled
        value: 'true'
      - name: ingress.hostname
        value: wordpress.192.168.56.41.nip.io
      - name: ingress.ingressClassName
        value: traefik
      - name: wordpressPassword
        value: abc123.
      - name: wordpressUsername
        value: admin
  chart: wordpress
destination:
  server: https://kubernetes.default.svc
  namespace: wordpress
syncPolicy:
  syncOptions:
    - CreateNamespace=true
```