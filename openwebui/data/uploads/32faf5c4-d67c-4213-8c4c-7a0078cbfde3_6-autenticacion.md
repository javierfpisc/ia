# Métodos de autenticación en Proxmox VE
En Proxmox VE (versiones 9.1 y superiores), la seguridad de acceso se gestiona a través de diversos mecanismos que permiten desde la interacción humana mediante una interfaz web hasta la automatización programática mediante APIs. 

A continuación, se describen los principales sistemas de autenticación solicitados y otros métodos complementarios integrados en la plataforma:

## 1. Autenticación mediante Tickets (Ticket System)
Es el método estándar utilizado para las sesiones de la interfaz web y algunas operaciones de consola.

*   **Funcionamiento:** Cuando un usuario inicia sesión correctamente, el sistema genera un ticket de autenticación firmado. Este ticket es una cadena de caracteres que el cliente (navegador) presenta en las solicitudes subsiguientes.
*   **Seguridad:** Proxmox utiliza una pareja de claves (pública y privada) localizadas en `/etc/pve/authkey.pub` y `/etc/pve/priv/authkey.key` para firmar y verificar estos tickets dentro del clúster.
*   **CSRF:** Adicionalmente, se generan tokens **CSRF** (Cross-Site Request Forgery) utilizando la clave `/etc/pve/pve-www.key` para prevenir ataques de falsificación de peticiones en sitios cruzados durante la navegación por la GUI.

## 2. Tokens de API (API Tokens)
Diseñados específicamente para la **automatización** y el acceso apátrida (stateless) a la API RESTful sin necesidad de usar contraseñas interactivas.

*   **Tipos de Tokens:**
    *   **Con privilegios separados:** El token requiere permisos ACL explícitos. Su capacidad operativa es la intersección entre los permisos del usuario y los asignados al token.
    *   **Con privilegios completos:** El token hereda automáticamente todos los permisos del usuario asociado.
*   **Gestión:** Se crean mediante el comando `pveum user token add` o la GUI. Es crítico guardar el "secret" del token al momento de su creación, ya que **solo se muestra una vez** y no se puede recuperar después.
*   **Uso:** Se integran en las cabeceras HTTP de las peticiones mediante el formato: `Authorization: PVEAPIToken=USUARIO@REALM!TOKENID=UUID`.

## 3. Certificados TLS y Gestión de Identidad del Nodo
La seguridad en la comunicación y la identidad de los nodos se apoya en una infraestructura de clave pública (PKI) interna.

*   **Certificados de Clúster:** Por defecto, cada clúster de Proxmox genera su propia **Autoridad de Certificación (CA)** autofirmada que emite certificados para cada nodo (`/etc/pve/nodes/NOMBRE/pve-ssl.pem`).
*   **Certificados Externos y ACME:** Para evitar advertencias de seguridad en el navegador, Proxmox permite integrar certificados de terceros o utilizar el protocolo **ACME** (ej. Let's Encrypt) para obtener certificados válidos y con renovación automática.
*   **Fingerprints:** Para vincular servidores externos (como un **Proxmox Backup Server**), se utiliza el *fingerprint* del certificado TLS para asegurar que la conexión se realiza con el servidor correcto sin necesidad de una CA pública.

En el caso de **Proxmox VE**, la API REST **no utiliza certificados TLS de cliente como mecanismo de autenticación de usuarios**. Los métodos de autenticación soportados son los **tickets de sesión** y los **API Tokens**.

No obstante, los certificados TLS de cliente pueden desempeñar un papel importante en la seguridad de las comunicaciones. Cuando una aplicación o un proxy inverso se configura para requerir autenticación mutua TLS (mTLS), el certificado de cliente permite demostrar la identidad del equipo que establece la conexión antes incluso de que la petición llegue a la aplicación. Este mecanismo añade una capa adicional de protección, ya que únicamente los clientes que posean un certificado válido emitido por una Autoridad de Certificación (CA) de confianza podrán establecer la conexión.

Por tanto, aunque **los certificados TLS de cliente no constituyen un mecanismo de autenticación propio de la API de Proxmox**, sí pueden utilizarse como un mecanismo complementario para reforzar la seguridad del acceso, por ejemplo, mediante un proxy inverso configurado con autenticación mutua TLS o en otras aplicaciones que sí soporten este tipo de autenticación de forma nativa.

## 4. Ámbitos de Autenticación (Realms)
Proxmox no almacena las contraseñas en su base de datos de usuarios principal (`user.cfg`), sino que las vincula a "Realms":

*   **Linux PAM:** Utiliza los usuarios del sistema operativo subyacente (Debian). Es el método para el usuario `root`.
*   **Proxmox VE Authentication Server (pve):** Un almacén de contraseñas local de Proxmox que guarda hashes SHA-256 en `/etc/pve/priv/shadow.cfg`.
*   **LDAP / Microsoft Active Directory:** Permite integrar Proxmox con directorios corporativos externos, soportando sincronización automática de usuarios y grupos.
*   **OpenID Connect:** Permite la autenticación contra proveedores de identidad modernos como Keycloak o Google.

## 5. Autenticación de Segundo Factor (TFA/2FA)
Para elevar la seguridad en versiones recientes, Proxmox ofrece soporte robusto para:

*   **TOTP:** Códigos temporales generados por aplicaciones móviles (Google Authenticator, FreeOTP).
*   **WebAuthn:** Estándar moderno que permite el uso de llaves de seguridad físicas (ej. YubiKey) o biometría (TPM de ordenadores o smartphones).
*   **Recovery Keys:** Una lista de códigos de un solo uso para evitar el bloqueo de cuenta en caso de pérdida del factor principal.