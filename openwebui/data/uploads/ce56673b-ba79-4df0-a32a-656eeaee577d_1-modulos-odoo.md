# Unidad 5.1 · Creación de Módulos en Odoo: Estructura y Componentes

## Qué aprenderás

!!! note "Objetivos de este apartado"
    - Qué son los módulos en Odoo y por qué son fundamentales
    - Cómo se organiza la estructura interna de un módulo
    - Cuáles son los componentes clave y sus funciones específicas
    - Crear tu primer módulo básico desde cero
    - Configurar el archivo manifest y las dependencias

---

## Conceptos Fundamentales

### Módulos: La base modular de Odoo

!!! example "¿Qué es un módulo en Odoo?"
    Odoo es una plataforma 100% modular. Todo lo que ves funcionar en Odoo —desde la gestión de ventas hasta reportes, desde la contabilidad hasta recursos humanos— es un **módulo** (también llamado *addon*).
    
    Un módulo es simplemente un **paquete de Python organizado** que contiene:
    - Código (lógica de negocio)
    - Datos (información inicial)
    - Vistas (interfaz visual)
    - Configuración (cómo se instala)

**¿Por qué esto es genial?**

| Ventaja | Explicación |
|---------|-------------|
| Reutilizable | Instala el mismo módulo en múltiples empresas/servidores |
| Mantenible | Cada módulo tiene una responsabilidad clara |
| Extensible | Extiende módulos existentes sin tocar el código original |
| Escalable | Agrega funcionalidad sin afectar lo existente |
| Desacoplado | Los módulos pueden actualizarse independientemente |

### Estructura de un módulo Odoo

La estructura de un módulo Odoo sigue un patrón estándar que todo desarrollador reconoce al instante:

```
mi_primer_modulo/
├── __init__.py              # Marca como paquete Python
├── __manifest__.py          # Metadatos del módulo (lo más importante)
├── models/
│   ├── __init__.py
│   └── cliente.py           # Definición de modelos
├── views/
│   └── cliente_views.xml    # Definición de vistas (UI)
├── data/
│   └── datos_iniciales.xml  # Datos por defecto
├── security/
│   └── ir.model.access.csv  # Permisos de acceso
└── README.md                # Documentación
```

Cada carpeta tiene un propósito específico:

| Carpeta | Contenido | Propósito |
|---------|-----------|-----------|
| `models/` | Clases Python | Define la lógica y estructura de datos |
| `views/` | XML | Define la interfaz visual (formularios, tablas) |
| `data/` | XML/CSV | Carga datos iniciales o de configuración |
| `security/` | CSV/XML | Define permisos y control de acceso |
| `static/` | CSS, JS | Recursos estáticos (opcional) |
| `tests/` | Python | Pruebas unitarias (opcional) |

---

## El Archivo __manifest__.py

El `__manifest__.py` (o `__openerp__.py` en versiones antiguas) es el **corazón del módulo**. Contiene metadatos que Odoo usa para cargar e identificar el módulo.

### Estructura básica

```python
{
    'name': 'Gestión de Clientes',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Sistema de gestión completo de clientes',
    'author': 'Mi Empresa',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/cliente_views.xml',
        'data/datos_iniciales.xml',
    ],
    'demo': [
        'demo/demo_clientes.xml',
    ],
}
```

**Explicación de campos:**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | str | Nombre del módulo (visible en la UI) |
| `version` | str | Versión semántica (1.0, 1.1, 2.0, etc.) |
| `category` | str | Categoría: Sales, Accounting, HR, etc. |
| `summary` | str | Descripción corta de una línea |
| `author` | str | Autor o empresa |
| `license` | str | LGPL-3, AGPL-3, etc. |
| `installable` | bool | Si puede instalarse (`True` o `False`) |
| `auto_install` | bool | Se instala automáticamente si deps están presentes |
| `depends` | list | Módulos que deben instalarse primero |
| `data` | list | Archivos XML/CSV a cargar en orden |
| `demo` | list | Datos de demostración (solo en modo demo) |
| `post_init_hook` | str | Función a ejecutar después de instalar |
| `uninstall_hook` | str | Función a ejecutar al desinstalar |

!!! warning "Sobre dependencias"
    El campo `depends` es crucial. Asegúrate de:
    - Siempre incluir `'base'` (módulo principal de Odoo)
    - Listar solo dependencias directas
    - No crear dependencias cíclicas (A → B → A)

### Ejemplo: manifest completo

```python
{
    'name': 'Sistema de Pedidos Premium',
    'version': '2.1.3',
    'category': 'Sales',
    'sequence': 10,
    'summary': 'Gestión avanzada de pedidos con aprobaciones',
    'description': '''
        Módulo para gestionar pedidos de clientes con:
        - Aprobación en cascada
        - Seguimiento de entregas
        - Integración con almacén
    ''',
    'author': 'Juan García <juan@miempresa.com>',
    'website': 'https://miempresa.com',
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'sale',
        'stock',
    ],
    'data': [
        'security/grupos.xml',
        'security/ir.model.access.csv',
        'views/pedido_views.xml',
        'views/cliente_views.xml',
        'data/secuencias.xml',
        'data/datos_iniciales.xml',
    ],
    'demo': [
        'demo/demo_pedidos.xml',
    ],
    'post_init_hook': 'inicializar_datos',
    'external_dependencies': {
        'python': ['requests', 'lxml'],
        'bin': ['wkhtmltopdf'],
    },
}
```

---

## Estructura interna del módulo

### models/__init__.py

Este archivo carga todos los modelos:

```python
# models/__init__.py
from . import cliente
from . import pedido
from . import factura
```

### models/cliente.py

Define el modelo de datos:

```python
from odoo import models, fields, api

class Cliente(models.Model):
    _name = 'cliente.cliente'
    _description = 'Clientes de la empresa'
    
    nombre = fields.Char(string='Nombre', required=True)
    email = fields.Char(string='Email')
    telefono = fields.Char(string='Teléfono')
    activo = fields.Boolean(default=True)
```

### views/cliente_views.xml

Define cómo se ven los datos:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <record id="view_cliente_form" model="ir.ui.view">
            <field name="name">Cliente - Formulario</field>
            <field name="model">cliente.cliente</field>
            <field name="arch" type="xml">
                <form>
                    <sheet>
                        <h1>
                            <field name="nombre"/>
                        </h1>
                        <group>
                            <field name="email"/>
                            <field name="telefono"/>
                            <field name="activo"/>
                        </group>
                    </sheet>
                </form>
            </field>
        </record>
    </data>
</odoo>
```

### __init__.py (raíz)

```python
# __init__.py
from . import models
```

---

## Crear tu primer módulo

### Paso 1: Crear la estructura

```bash
cd /ruta/a/addons
mkdir mi_primer_modulo
cd mi_primer_modulo

mkdir -p models views data security
touch __init__.py __manifest__.py
touch models/__init__.py
touch views/mi_vista.xml
```

### Paso 2: Crear __manifest__.py

```python
{
    'name': 'Mi Primer Módulo',
    'version': '1.0',
    'category': 'Tools',
    'author': 'Tu Nombre',
    'license': 'LGPL-3',
    'installable': True,
    'depends': ['base'],
    'data': [
        'views/mi_vista.xml',
    ],
}
```

### Paso 3: Crear el modelo

```python
# models/mi_modelo.py
from odoo import models, fields

class MiModelo(models.Model):
    _name = 'mi.modelo'
    _description = 'Mi Modelo'
    
    nombre = fields.Char(string='Nombre', required=True)
    descripcion = fields.Text(string='Descripción')
```

### Paso 4: Registrar en models/__init__.py

```python
from . import mi_modelo
```

### Paso 5: Crear la vista

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <record id="view_mi_modelo_form" model="ir.ui.view">
            <field name="name">Mi Modelo - Formulario</field>
            <field name="model">mi.modelo</field>
            <field name="arch" type="xml">
                <form>
                    <sheet>
                        <h1><field name="nombre"/></h1>
                        <field name="descripcion"/>
                    </sheet>
                </form>
            </field>
        </record>
        
        <record id="action_mi_modelo" model="ir.actions.act_window">
            <field name="name">Mi Modelo</field>
            <field name="res_model">mi.modelo</field>
            <field name="view_mode">list,form</field>
        </record>
        
        <menuitem id="menu_mi_modelo"
            name="Mi Modelo"
            action="action_mi_modelo"
        />
    </data>
</odoo>
```

### Paso 6: Registrar en __init__.py (raíz)

```python
from . import models
```

### Paso 7: Instalar el módulo

En Odoo, ve a **Aplicaciones → Actualizar lista de aplicaciones**, busca tu módulo y haz clic en **Instalar**.

!!! success "¡Lo lograste!"
    Tu primer módulo está instalado y listo para usar.

---

## Dependencias y extensiones

### Especificar dependencias

Las dependencias aseguran que los módulos necesarios se instalen primero:

```python
'depends': [
    'base',           # Siempre incluir
    'sale',           # Depende de ventas
    'account',        # Depende de contabilidad
    'mi_otro_modulo', # Depende de tu propio módulo
],
```

### Extender módulos existentes

En lugar de modificar un módulo existente, extiéndelo:

```python
# En un nuevo módulo
class ClienteExtendido(models.Model):
    _inherit = 'cliente.cliente'  # Hereda del modelo base
    
    # Agrega nuevos campos
    codigo_especial = fields.Char(string='Código especial')
    es_vip = fields.Boolean(default=False)
```

!!! warning "Herencia vs Modificación"
    Nunca modifiques directamente un módulo existente. Siempre hereda y extiende:
    - ✓ Crea un nuevo módulo que herede
    - ✗ Edites el módulo original

---

## Checklist de aprendizaje

- [ ] Entiendo la estructura básica de un módulo
- [ ] Sé qué es un __manifest__.py y para qué sirve
- [ ] Puedo crear un módulo desde cero
- [ ] Entiendo las dependencias entre módulos
- [ ] Sé cómo extender módulos sin modificar originales
- [ ] He instalado y activado mi primer módulo

---

## Ejercicio propuesto

!!! example "Ejercicio: Crear módulo de Contactos"
    **Objetivo:** Crear un módulo completo de gestión de contactos.
    
    **Requisitos:**
    - Nombre: `mi_contactos`
    - Modelo `Contacto` con campos: nombre, email, teléfono, empresa, ciudad
    - Vista form con 2 columnas
    - Vista list editable
    - Acción para abrir la lista
    - Menú en la navegación principal
    
    **Criterios de éxito:**
    - El módulo se instala correctamente
    - Aparece en el menú
    - Puedo crear, editar y eliminar contactos
    - La lista es editable

---

## Referencias

- [Módulos en Odoo](https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101.html)
- [Estructura de carpetas](https://www.odoo.com/documentation/19.0/developer/reference/cli.html)
- [Manifest guide](https://www.odoo.com/documentation/19.0/developer/howtos/backend_module_dev.html)
