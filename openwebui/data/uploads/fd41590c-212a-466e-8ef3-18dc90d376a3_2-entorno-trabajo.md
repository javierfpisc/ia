# Guía del Entorno de Prácticas: Infraestructura y Herramientas de Trabajo
Para la construcción del entorno práctico del Curso de Especialización de despliegue de contenedores y metodologías DevOps, necesitaremos diseñar una serie de laboratorios técnicos basados en cuatro pilares fundamentales:

* **código abierto**
* **alta replicabilidad**
* **bajo consumo de recursos**
* **facilidad de automatización**

A continuación, se detallam la infraestructura y las herramientas que utilizaremos a lo largo del curso y que necesitarás configurar en tu equipo de trabajo.

---

## 1. El Corazón de la Infraestructura (Unidades 1, 2 y 3)

Durante la primera parte del curso (Unidades 1, 2 y 3), nos enfocaremos en aprender a desplegar la infraestructura base y servicios esenciales. 

*   **Tecnología Principal:** **Proxmox VE (Versión reciente)**.
*   **¿Cómo trabajaremos?:** Utilizaremos Proxmox como hipervisor de tipo 1 para gestionar la virtualización en todos sus niveles. Sobre este entorno, desplegaremos un **clúster de nodos** interconectados. 
*   **Objetivo:** Aprenderás a configurar direccionamiento IP, segmentación de redes de seguridad y almacenamiento compartido. Este clúster será tu base de operaciones para entender cómo se aíslan y protegen los entornos reales de clientes.

---

## 2. Orquestación y Alta Disponibilidad con Kubernetes (Unidad 4)

En la Unidad 4 daremos el salto cualitativo hacia la orquestación a gran escala, tal como lo exige el diseño de este curso de especialización.

*   **Tecnología Principal:** **Kubernetes (K8s estándar)**.
*   **¿Cómo trabajaremos?:** Para que el entorno sea accesible y no requiera de un ordenador excesivamente costoso, construiremos nuestro clúster de Kubernetes utilizando **máquinas virtuales en VirtualBox** que actuarán como nodos del clúster (nodos *control plane* y nodos *worker*).
*   **Objetivo:** Instalar, parametrizar y validar un orquestador de contenedores real, regulando permisos, balanceadores de carga y almacenamiento dinámico para tus aplicaciones.

---

## 3. Tu Sistema Base y Caja de Herramientas (Toolbox)

Para asegurar que los laboratorios funcionen de manera idéntica en cualquier ordenador (evitando el clásico *"en mi máquina sí funciona"*), utilizaremos un sistema base robusto y un conjunto de herramientas estándar de la industria:

### El Sistema Operativo Base

*   **Distribución:** **Linux Debian 13 (Trixie)** o similar.
*   **¿Por qué?:** Debian es el estándar de facto por su estabilidad, ligereza, respeto absoluto a la filosofía de código abierto y su bajo consumo de recursos, lo que nos permitirá exprimir al máximo el hardware disponible.

### Herramientas de Automatización y Virtualización Local
Para levantar y configurar tus entornos de forma automática (Infraestructura como Código), utilizaremos:

1.  **Vagrant:** Para definir mediante un sencillo archivo de configuración (`Vagrantfile`) la creación, recursos y red de nuestras máquinas virtuales de VirtualBox de forma 100% automatizada.
2.  **VirtualBox:** Nuestro hipervisor local para ejecutar los nodos del laboratorio de forma aislada.
3.  **Docker:** El motor de contenedores estándar para construir, empaquetar y ejecutar microservicios de manera ágil.
4.  **Git:** Para el control de versiones de tu código de infraestructura y desarrollo, permitiéndote mantener la trazabilidad de todo lo que hagas en clase.

---

## 4. Requisitos para comenzar
Para poder seguir las prácticas cómodamente, asegúrate de contar con acceso a:

*   Un ordenador que permita habilitar la **virtualización por hardware** en la BIOS (Intel VT-x o AMD-V).
*   La distribución **Debian 13** instalada (puede ser de forma nativa o en doble arranque).
*   Conexión a internet para la descarga de paquetes y el acceso a los repositorios de código y de imágenes del aula.

Al dominar este stack tecnológico abierto y automatizado, no solo aprobarás el módulo: adquirirás el perfil exacto de un **Administrador o Desarrollador DevOps**, uno de los roles técnicos más demandados y con mayor proyección en el sector tecnológico actual.

## 5. Referencias

* **Docker**: [https://docs.docker.com](https://docs.docker.com)
* **Kubernetes**: [https://kubernetes.io/docs](https://kubernetes.io/docs)
* **Proxmox VE**: [https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation](https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation)
* **VirtualBox**: [https://www.virtualbox.org/wiki/Documentation](https://www.virtualbox.org/wiki/Documentation)
* **Git**: [https://git-scm.com/docs](https://git-scm.com/docs)
* **Vagrant**: [https://developer.hashicorp.com/vagrant/docs](https://developer.hashicorp.com/vagrant/docs)


