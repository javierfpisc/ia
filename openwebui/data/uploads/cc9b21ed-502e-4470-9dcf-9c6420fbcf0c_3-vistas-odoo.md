# Unidad 5.3 · Vistas en Odoo: Definición y Configuración

## Qué aprenderás

!!! note "Objetivos de este apartado"
    - Qué son las vistas y cómo conectan con los modelos
    - Tipos de vistas: form, tree, list, kanban, graph, calendar
    - Crear vistas con XML y estructura básica
    - Personalizar campos: atributos, grupos, separadores
    - Vistas heredadas y extensiones de vistas existentes
    - Buenas prácticas en diseño de interfaces

---

## Conceptos Fundamentales

### Las Vistas: La Cara de los Modelos

!!! example "¿Qué es una vista?"
    Una **vista** es la **interfaz gráfica que permite a los usuarios interactuar** con los datos de un modelo. 
    
    ```
    Modelo (datos) + Vista (interfaz) = Experiencia del usuario
    ```
    
    Tipos de vistas:
    - Form — Formulario para editar un registro
    - List — Tabla para ver varios registros
    - Tree — Estructura jerárquica
    - Graph — Gráficos y estadísticas
    - Calendar — Calendario con eventos
    - Kanban — Tablero estilo Kanban

**Separación de responsabilidades:**

| Capa | Función | Ejemplo |
|------|---------|---------|
| Modelo | Lógica y datos | Clase Python con campos |
| Vista | Presentación | XML con campos mostrados |
| Controlador | Acciones | Botones, cambios de vista |

---

## Estructura de Vistas con XML

### Archivo básico: `views/mi_vista.xml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <!-- Definición de vista -->
        <record id="view_mi_modelo_form" model="ir.ui.view">
            <field name="name">Mi Modelo - Formulario</field>
            <field name="model">mi.modelo</field>
            <field name="arch" type="xml">
                <form>
                    <!-- Aquí va el contenido de la vista -->
                    <field name="nombre"/>
                </form>
            </field>
        </record>
    </data>
</odoo>
```

**Conceptos clave:**

| Elemento | Significado | Ejemplo |
|----------|-------------|---------|
| `<record>` | Crea un registro | ID único: `view_cliente_form` |
| `id` | Identificador único | Usado para heredar o referenciar |
| `model="ir.ui.view"` | Tipo de registro | Siempre igual para vistas |
| `<field name="name">` | Nombre visible | "Cliente - Formulario" |
| `<field name="model">` | Modelo asociado | `cliente.cliente` |
| `<field name="arch">` | Arquitectura XML | El contenido de la vista |

---

## Vista Form (Formulario)

La más común: permite editar un registro completo.

### Estructura básica

```xml
<record id="view_cliente_form" model="ir.ui.view">
    <field name="name">Cliente - Formulario</field>
    <field name="model">cliente.cliente</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <!-- Encabezado -->
                <h1>
                    <field name="nombre"/>
                </h1>
                
                <!-- Campos en 2 columnas -->
                <group>
                    <group>
                        <field name="email"/>
                        <field name="telefono"/>
                    </group>
                    <group>
                        <field name="direccion"/>
                        <field name="ciudad"/>
                    </group>
                </group>
                
                <!-- Sección con título -->
                <group string="Información adicional">
                    <field name="notas"/>
                    <field name="activo"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

### Componentes principales

**`<sheet>`** — Contenedor principal (con fondo blanco)

```xml
<sheet>
    <!-- Todo el contenido va aquí -->
</sheet>
```

**`<group>`** — Agrupa campos en columnas

```xml
<group>
    <group>
        <!-- Columna izquierda -->
        <field name="campo1"/>
        <field name="campo2"/>
    </group>
    <group>
        <!-- Columna derecha -->
        <field name="campo3"/>
        <field name="campo4"/>
    </group>
</group>
```

**`<group string="..."`** — Grupo con título

```xml
<group string="Datos personales">
    <field name="nombre"/>
    <field name="email"/>
</group>
```

**`<notebook>`** — Pestañas dentro del formulario

```xml
<notebook>
    <page string="General">
        <field name="nombre"/>
        <field name="email"/>
    </page>
    <page string="Contacto">
        <field name="telefono"/>
        <field name="direccion"/>
    </page>
</notebook>
```

### Atributos de campos

```xml
<field name="email" 
    required="1"                    <!-- Obligatorio -->
    readonly="1"                    <!-- Solo lectura -->
    invisible="1"                   <!-- Oculto -->
    nolabel="1"                     <!-- Sin etiqueta -->
    colspan="2"                     <!-- Ancho doble -->
    widget="email"                  <!-- Tipo de widget -->
/>
```

!!! tip "Widgets disponibles"
    - `email` — Para campos email
    - `phone` — Para teléfonos
    - `many2one` — Para relaciones
    - `many2many` — Para múltiples selecciones
    - `one2many` — Para tablas de registros relacionados
    - `html` — Editor HTML
    - `image` — Visualizador de imágenes
    - `date`, `datetime` — Selectores de fecha

---

## Vista List (Tabla/Listado)

Muestra múltiples registros en forma de tabla.

### Estructura básica

```xml
<record id="view_cliente_list" model="ir.ui.view">
    <field name="name">Cliente - Listado</field>
    <field name="model">cliente.cliente</field>
    <field name="arch" type="xml">
        <list>
            <!-- Columnas -->
            <field name="nombre"/>
            <field name="email"/>
            <field name="ciudad"/>
            <field name="activo"/>
        </list>
    </field>
</record>
```

### Atributos y características

```xml
<list editable="bottom">
    <!-- editable="bottom" : permite editar haciendo click en fila -->
    <!-- editable="top" : agrega fila nueva arriba -->
    
    <field name="nombre" optional="show"/>
    <!-- optional="show" : columna visible -->
    <!-- optional="hide" : columna oculta por defecto -->
    
    <field name="prioridad" widget="progress"/>
    <!-- Muestra barra de progreso -->
    
    <field name="estado" decoration-success="estado=='activo'"/>
    <!-- Colores condicionales -->
</list>
```

**Decoraciones (colores):**

```xml
<field name="estado" 
    decoration-success="estado=='completado'"      <!-- Verde -->
    decoration-warning="estado=='pendiente'"       <!-- Naranja -->
    decoration-danger="estado=='cancelado'"        <!-- Rojo -->
    decoration-info="estado=='nuevo'"              <!-- Azul -->
    decoration-muted="estado=='archivado'"         <!-- Gris -->
/>
```

---

## Vista Graph (Gráficos)

Visualización de datos estadísticos.

```xml
<record id="view_venta_graph" model="ir.ui.view">
    <field name="name">Venta - Gráfico</field>
    <field name="model">venta.venta</field>
    <field name="arch" type="xml">
        <graph type="bar">
            <!-- Eje X: clasificación -->
            <field name="producto_id" type="row"/>
            
            <!-- Eje Y: valor a sumar -->
            <field name="total" type="measure"/>
        </graph>
    </field>
</record>
```

**Tipos de gráficos:**

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| `bar` | Barras | Ventas por producto |
| `line` | Líneas | Tendencia en tiempo |
| `pie` | Pastel | Distribución de porcentajes |
| `pivot` | Tabla dinámica | Análisis multidimensional |

---

## Vista Calendar (Calendario)

Eventos en un calendario.

```xml
<record id="view_cita_calendar" model="ir.ui.view">
    <field name="name">Cita - Calendario</field>
    <field name="model">cita.cita</field>
    <field name="arch" type="xml">
        <calendar date_start="fecha_inicio"
                  date_stop="fecha_fin"
                  color="cliente_id"
                  event_open_popup="true">
            <field name="titulo"/>
            <field name="cliente_id"/>
        </calendar>
    </field>
</record>
```

---

## Vista Kanban (Tablero)

Estilo Kanban con tarjetas.

```xml
<record id="view_tarea_kanban" model="ir.ui.view">
    <field name="name">Tarea - Kanban</field>
    <field name="model">tarea.tarea</field>
    <field name="arch" type="xml">
        <kanban default_group_by="estado">
            <field name="titulo"/>
            <field name="asignado_a"/>
            <field name="prioridad"/>
            
            <templates>
                <t t-name="kanban-box">
                    <div class="oe_kanban_card">
                        <h4>
                            <field name="titulo"/>
                        </h4>
                        <p>
                            Asignado: <field name="asignado_a"/>
                        </p>
                        <span class="badge badge-danger">
                            <field name="prioridad"/>
                        </span>
                    </div>
                </t>
            </templates>
        </kanban>
    </field>
</record>
```

---

## Acciones y menús

Para que una vista sea accesible, necesitas una **acción** que la abra:

```xml
<!-- Acción que abre la lista de clientes -->
<record id="action_cliente_list" model="ir.actions.act_window">
    <field name="name">Clientes</field>
    <field name="res_model">cliente.cliente</field>
    <field name="view_mode">list,form</field>
    <field name="view_id" ref="view_cliente_list"/>
</record>

<!-- Menú en la navegación -->
<menuitem id="menu_cliente"
    name="Clientes"
    action="action_cliente_list"
    sequence="10"
/>
```

---

## Heredar y Personalizar Vistas

### Extender una vista existente

En lugar de modificar el archivo original, **heredas** la vista:

```xml
<record id="view_cliente_form_custom" model="ir.ui.view">
    <field name="name">Cliente - Formulario Personalizado</field>
    <field name="model">cliente.cliente</field>
    <field name="inherit_id" ref="base.view_cliente_form"/>
    <field name="arch" type="xml">
        <!-- Busca el campo 'email' y agrégale atributo required -->
        <xpath expr="//field[@name='email']" position="attributes">
            <attribute name="required">1</attribute>
        </xpath>
    </field>
</record>
```

!!! warning "XPath: la clave de la herencia"
    **XPath** es el lenguaje para buscar elementos XML:
    
    ```xml
    <!-- Encuentra elemento con atributo name="email" -->
    //field[@name='email']
    
    <!-- Encuentra dentro de un group -->
    //group/field[@name='email']
    
    <!-- Encuentra el primer campo -->
    //field[1]
    ```

**Posiciones de modificación:**

```xml
<!-- 1. Agregar atributos -->
<xpath expr="//field[@name='email']" position="attributes">
    <attribute name="readonly">1</attribute>
</xpath>

<!-- 2. Insertar antes -->
<xpath expr="//field[@name='email']" position="before">
    <field name="nuevo_campo"/>
</xpath>

<!-- 3. Insertar después -->
<xpath expr="//field[@name='email']" position="after">
    <field name="otro_campo"/>
</xpath>

<!-- 4. Reemplazar -->
<xpath expr="//field[@name='email']" position="replace">
    <field name="email" readonly="1"/>
</xpath>

<!-- 5. Dentro (al final) -->
<xpath expr="//group[@string='Contacto']" position="inside">
    <field name="nuevo_contacto"/>
</xpath>
```

---

## Ejemplo Completo: Aplicación de Contactos

### Paso 1: Modelo (`models/contacto.py`)

```python
from odoo import models, fields

class Contacto(models.Model):
    _name = 'contacto.contacto'
    _description = 'Contactos'
    
    nombre = fields.Char(string='Nombre', required=True)
    email = fields.Char(string='Email')
    telefono = fields.Char(string='Teléfono')
    empresa = fields.Char(string='Empresa')
    ciudad = fields.Char(string='Ciudad')
    notas = fields.Text(string='Notas')
    prioridad = fields.Selection([
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta')
    ], string='Prioridad', default='media')
    activo = fields.Boolean(default=True)
    fecha_creacion = fields.Date(string='Fecha', default=fields.Date.today)
```

### Paso 2: Vistas (`views/contacto_views.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <!-- VISTA FORM -->
        <record id="view_contacto_form" model="ir.ui.view">
            <field name="name">Contacto - Formulario</field>
            <field name="model">contacto.contacto</field>
            <field name="arch" type="xml">
                <form>
                    <sheet>
                        <h1>
                            <field name="nombre"/>
                        </h1>
                        
                        <group>
                            <group>
                                <field name="email"/>
                                <field name="telefono"/>
                                <field name="empresa"/>
                            </group>
                            <group>
                                <field name="ciudad"/>
                                <field name="prioridad" widget="radio"/>
                                <field name="activo"/>
                            </group>
                        </group>
                        
                        <group string="Información adicional">
                            <field name="notas" nolabel="1"/>
                        </group>
                        
                        <footer>
                            <field name="fecha_creacion" readonly="1"/>
                        </footer>
                    </sheet>
                </form>
            </field>
        </record>
        
        <!-- VISTA LIST -->
        <record id="view_contacto_list" model="ir.ui.view">
            <field name="name">Contacto - Listado</field>
            <field name="model">contacto.contacto</field>
            <field name="arch" type="xml">
                <list editable="bottom">
                    <field name="nombre"/>
                    <field name="email"/>
                    <field name="telefono" optional="hide"/>
                    <field name="empresa"/>
                    <field name="ciudad" optional="hide"/>
                    <field name="prioridad" 
                           decoration-danger="prioridad=='alta'"
                           decoration-warning="prioridad=='media'"/>
                    <field name="activo" optional="hide"/>
                </list>
            </field>
        </record>
        
        <!-- ACCIÓN -->
        <record id="action_contacto_list" model="ir.actions.act_window">
            <field name="name">Contactos</field>
            <field name="res_model">contacto.contacto</field>
            <field name="view_mode">list,form</field>
        </record>
        
        <!-- MENÚ -->
        <menuitem id="menu_contacto"
            name="Contactos"
            action="action_contacto_list"
            sequence="10"
        />
    </data>
</odoo>
```

### Paso 3: Registrar en `__manifest__.py`

```python
{
    'name': 'Gestión de Contactos',
    'data': [
        'views/contacto_views.xml',
    ],
}
```

!!! success "¡Lo lograste!"
    Ahora tienes un módulo completo con vistas form, list y acción.

---

## Checklist de aprendizaje

- [ ] Entiendo la estructura básica de una vista XML
- [ ] Puedo crear vistas form con grupos y pestañas
- [ ] Sé cómo hacer una vista list con columnas editables
- [ ] Conozco los widgets disponibles (email, phone, etc.)
- [ ] He heredado una vista con XPath
- [ ] Puedo agregar decoraciones (colores condicionales)
- [ ] He creado una acción y un menú para abrir vistas

---

## Ejercicio propuesto

!!! example "Ejercicio: Sistema de Gestión de Tareas"
    **Objetivo:** Crear vistas profesionales para una aplicación de tareas.
    
    **Requisitos:**
    - Modelo `Tarea`: título, descripción, asignado_a (many2one usuario), estado, prioridad, fecha_vencimiento
    - Vista Form: con pestañas (General, Detalles, Seguimiento)
    - Vista List: editable, con decoraciones por estado y prioridad
    - Vista Kanban: agrupada por estado, mostrando tarjetas con prioridad
    - Acción y menú para acceder
    
    **Criterios de éxito:**
    - Al abrir un formulario: se ve título grande, estado con radio buttons, descripción en editor
    - En listado: puedo editar título y estado directamente
    - En Kanban: veo columnas NUEVO/EN PROGRESO/COMPLETADO con tarjetas deslizables

---

## Referencias

- [Arquitecturas de Vistas](https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html)
- [Vista Form](https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html)
- [Herencia de Vistas con XPath](https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html)
