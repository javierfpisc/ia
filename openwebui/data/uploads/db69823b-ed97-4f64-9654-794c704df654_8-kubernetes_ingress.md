# Ingress en Kubernetes
Si el **Service** era nuestra puerta de entrada rudimentaria al clúster, el **Ingress** es nuestra "recepción inteligente". Mientras que un Service trabaja a nivel de red (Capa 4), el Ingress gestiona el tráfico a nivel de aplicación (Capa 7), permitiendo usar nombres de dominio, rutas URL y certificados SSL.

A continuación, crearemos en el Manager `kuber1` el archivo `ingress-1.yaml` con el siguiente contenido:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  namespace: ejemplos
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: web
spec:
  ingressClassName: traefik
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

Creamos el archivo dentro del nodo Manager `kuber1` y lo aplicamos con kubectl:
```bash
kubectl apply -f ingress-1.yaml
```
Tras crearlo lo comprobamos:
```bash
kubectl get ingress -n ejemplos
```
Mostraría algo como lo siguiente:
```
NAME            CLASS     HOSTS                        ADDRESS                                     PORTS   AGE
nginx-ingress   traefik   nginx.192.168.56.41.nip.io   192.168.56.41,192.168.56.42,192.168.56.43   80      22s
```

---

## Identificación y Metadatos

*   **`apiVersion: networking.k8s.io/v1`**: Define la versión de la API para recursos de red.
*   **`kind: Ingress`**: Indica que este objeto define reglas de acceso externo a los servicios del clúster.
*   **`metadata`**:
    *   **`name: nginx-ingress`**: Nombre identificativo del recurso.
    *   **`namespace: ejemplos`**: Al igual que el Service y el Deployment, debe estar en el mismo Namespace para poder encontrar el servicio al que apunta.
    *   **`annotations`**: Son metadatos que no usa Kubernetes directamente, sino herramientas externas. 
        *   **`traefik.ingress.kubernetes.io/router.entrypoints: web`**: Esta anotación específica le dice a **Traefik** (nuestro Ingress Controller) que debe escuchar este dominio en su punto de entrada llamado "web" (normalmente el puerto 80/HTTP).

## Especificación (Spec)

La sección `spec` es donde definimos la lógica de enrutamiento:

*   **`ingressClassName: traefik`**: Este campo es fundamental. Le indica a Kubernetes qué controlador debe procesar esta regla. Como en el clúster tenemos instalado **Traefik**, usamos su nombre para que él tome el control de este tráfico.
*   **`rules` (Reglas)**: Aquí definimos cómo se mapea el tráfico entrante.
    *   **`host: nginx.192.168.56.41.nip.io`**: Es el dominio o nombre DNS. Solo el tráfico que llegue preguntando por "nginx.192.168.56.41.nip.io" será procesado por esta regla. 
        *   *Nota:* Para probar esto en el laboratorio sin un servidor DNS real, usamos el "truco" del subdominio de **.nip.io**. Este proveedor incluye la resolución en el propio hostname de la petición, por eso al resolver el hostname `nginx.192.168.56.41.nip.io` contestará con la IP del nodo Manager (192.168.56.41). Es un truco simplón, pero funciona.
*   **`http.paths`**: Define las rutas dentro del dominio.
    *   **`path: /`**: Indica que cualquier petición a la raíz del sitio se redirija al backend.
    *   **`pathType: Prefix`**: Significa que coincidirá con cualquier ruta que empiece por `/` (por ejemplo, `/contacto` o `/imagenes` también entrarían aquí a menos que definamos otra regla específica).

## El Backend (Destino)

!!! important "NOTA"
    No usaremos el `NodePort`como Service para la definición del `Ingress`, en la definición de éste se enlazará directamente al Service `ClusterIP`, el cual como vimos es una IP interna dentro del clúster que representa a los Pods del Deployment que actúa como backend.

*   **`backend`**: Es el destino final del tráfico una vez que cumple las reglas anteriores.
    *   **`service.name: nginx-service`**: Es el nombre del **Service** que creamos en la práctica anterior.
    *   **`service.port.number: 80`**: El puerto del Service (ClusterIP) al que Traefik debe enviar los paquetes.

## Flujo de Comunicación en vuestro Clúster

Para que los alumnos visualicen la integración completa en vuestro clúster de 3 nodos:

1.  **Petición:** Escribimos `http://nginx.192.168.56.41.nip.io` en el navegador. Veremos como responde la página de bienvenida de nginx.
2.  **Entrada:** El tráfico llega al clúster. **Traefik** (que está escuchando en los nodos) recibe la petición y lee el campo `host` de la cabecera HTTP.
3.  **Procesamiento:** Traefik consulta sus reglas internas (generadas por este archivo Ingress), ve que `nginx.192.168.56.41.nip.io` debe ir a `nginx-service`.
4.  **Redirección:** Traefik envía el tráfico internamente a la IP del **Service** (ClusterIP).
5.  **Destino:** El Service balancea el tráfico hacia uno de los **Pods** de NGINX que están corriendo en los nodos worker.

### ¿Por qué usar Ingress y no solo NodePort?

*   **Ahorro de IPs y Puertos:** Podemos tener decenas de aplicaciones (nginx.local, api.local, app.local) todas entrando por el mismo puerto (80) y Traefik sabrá a dónde enviarlas basándose en el nombre.
*   **Flexibilidad:** Podemos cambiar el servicio de destino o la ruta sin que el usuario final note ningún cambio en la URL.
*   **Centralización:** Podemos gestionar la seguridad SSL y los límites de tráfico en un solo punto (el Ingress Controller) en lugar de hacerlo servicio por servicio.