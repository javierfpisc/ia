# Mecanismos de Autenticación en Automatización en Proxmox VE
La API REST de Proxmox VE implementa sus propios mecanismos de autenticación para verificar la identidad de los usuarios y aplicaciones que solicitan acceso a los recursos del clúster. Estos mecanismos funcionan sobre conexiones HTTPS, aprovechando TLS para garantizar la confidencialidad e integridad de las comunicaciones. Proxmox VE admite dos métodos principales de autenticación para acceder a su API REST:

- **Autenticación mediante tickets de sesión**, orientada principalmente a usuarios interactivos y utilizada por la interfaz web de administración.
- **Autenticación mediante API Tokens**, diseñada para la automatización mediante scripts, herramientas de Infraestructura como Código (IaC), plataformas de integración y aplicaciones de terceros.

En los siguientes apartados veremos algún ejemplo de uso de cada uno.

## Autenticación mediante Ticket
A continuación vemos un ejemplo de un proceso de autenticación con el **usuario root** del sistema. La respuesta es un json del cual extraemos los elementos `ticket` y `CSRFPreventionToken` que necesitaremos como elementos de autenticación en llamadas posteriores al API mediante curl:
```bash
RESPONSE=$(curl -sk \
  -d "username=root@pam" \
  -d "password=abc123." \
  https://192.168.56.11:8006/api2/json/access/ticket)

TICKET=$(echo "$RESPONSE" | grep -o '"ticket":"[^"]*"' | cut -d'"' -f4)
CSRF=$(echo "$RESPONSE" | grep -o '"CSRFPreventionToken":"[^"]*"' | cut -d'"' -f4)
```
Una vez obtenidos los elementos de autenticación en las variables `TICKET`Y `CSRF` las usaremos en las siguientes llamadas:
```bash
curl -k \
-b "PVEAuthCookie=$TICKET" -H "CSRFPreventionToken:$CSRF" \
https://192.168.56.11:8006/api2/json/nodes
```
Veremos la respuesta al comando anterior en formato json mostrando la información de los nodos del clúster.

## Autenticación mediante Token
Creamos un usuario dentro de la base de datos de usuarios de Proxmox y generemos un token para él:
```bash
pveum user add automatizacion@pve
pveum user token add automatizacion@pve terraform
```
El último de los comandos anteriores mostrará una salida como la siguiente:
```
┌──────────────┬──────────────────────────────────────┐
│ key          │ value                                │
╞══════════════╪══════════════════════════════════════╡
│ full-tokenid │ automatizacion@pve!terraform         │
├──────────────┼──────────────────────────────────────┤
│ info         │ {"privsep":1}                        │
├──────────────┼──────────────────────────────────────┤
│ value        │ b90a514a-27ac-4117-b02c-6b22a99835ec │
└──────────────┴──────────────────────────────────────┘
```
Tomamos los datos de la tabla anterior, `full-tokenid y value`, y construimos la petición al API que utilice la autenticación con el Token:
```bash
curl -k \
-H 'Authorization: PVEAPIToken=automatizacion@pve!terraform=b90a514a-27ac-4117-b02c-6b22a99835ec' \
https://192.168.56.11:8006/api2/json/nodes
```

Este último método de autenticación será el utilizado por los scripts y herramientas de automatización que interactúen con el API Rest de Proxmox.
