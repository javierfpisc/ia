# Unidad 5.4 · Acciones en Odoo: Definición y Configuración

## Qué aprenderás

!!! note "Objetivos de este apartado"
    - Qué son las acciones y por qué las necesitas
    - Tipos de acciones: ventanas, informes, servidores, URLs
    - Crear y configurar acciones en XML
    - Vincular acciones a menús y botones
    - Acciones con parámetros y contexto
    - Flujos de trabajo (workflows)

---

## Conceptos Fundamentales

### Las Acciones: Conectando Vistas con Modelos

!!! example "¿Qué es una acción?"
    Una **acción** en Odoo es lo que **abre una vista, ejecuta un proceso o navega entre pantallas**. Es el puente entre la interfaz y la lógica.
    
    ```
    Botón/Menú → Acción → Vista → Modelo
    ```
    
    Ejemplos:
    - Botón "Clientes" abre la lista de clientes
    - Botón "Generar factura" ejecuta un proceso
    - Botón "Imprimir" abre un informe
    - Botón "Web" abre una URL

**Sin acciones:** Las vistas existirían pero serían inaccesibles.

---

## Tipos de Acciones

### 1. Acción de Ventana (ir.actions.act_window)

La más común: abre una vista.

```xml
<record id="action_cliente_list" model="ir.actions.act_window">
    <field name="name">Clientes</field>               <!-- Nombre del botón -->
    <field name="res_model">cliente.cliente</field>   <!-- Modelo a abrir -->
    <field name="view_mode">list,form</field>         <!-- Orden de vistas -->
    <field name="view_id" ref="view_cliente_list"/>   <!-- Vista por defecto -->
    <field name="target">current</field>              <!-- Abre en ventana actual -->
</record>
```

!!! info "Atributos de ventana"
    - `res_model` — Modelo a abrir (obligatorio)
    - `view_mode` — Orden: `list,form,graph,kanban`
    - `view_id` — ID de la vista por defecto
    - `target` — `current` (misma ventana) o `new` (nueva ventana)
    - `context` — Parámetros adicionales

### 2. Acción de Servidor (ir.actions.server)

Ejecuta código Python al hacer click.

```xml
<record id="action_marcar_pagado" model="ir.actions.server">
    <field name="name">Marcar como pagado</field>
    <field name="model_id" ref="model_factura_factura"/>
    <field name="code">
for record in records:
    record.write({'estado': 'pagado'})
    </field>
</record>
```

!!! tip "Casos de uso"
    - Cambiar estado de registros
    - Enviar correos automáticos
    - Procesar datos
    - Crear registros relacionados

### 3. Acción de Informe (ir.actions.report)

Genera un PDF o documento.

```xml
<record id="action_factura_print" model="ir.actions.report">
    <field name="name">Imprimir Factura</field>
    <field name="model">factura.factura</field>
    <field name="report_type">qweb-pdf</field>
    <field name="report_name">modulo.reporte_factura</field>
</record>
```

### 4. Acción URL (ir.actions.act_url)

Abre un enlace externo.

```xml
<record id="action_ir_documentacion" model="ir.actions.act_url">
    <field name="name">Documentación Odoo</field>
    <field name="url">https://www.odoo.com/documentation</field>
    <field name="target">new</field>              <!-- Abre en nueva pestaña -->
</record>
```

---

## Vinculación a Menús

Una vez que tienes una acción, la vinculas a un menú:

```xml
<!-- Acción -->
<record id="action_cliente_list" model="ir.actions.act_window">
    <field name="name">Clientes</field>
    <field name="res_model">cliente.cliente</field>
    <field name="view_mode">list,form</field>
</record>

<!-- Menú principal -->
<menuitem id="menu_ventas" 
    name="Ventas" 
    sequence="10"
/>

<!-- Menú hijo (bajo "Ventas") -->
<menuitem id="menu_clientes"
    name="Clientes"
    parent="menu_ventas"
    action="action_cliente_list"
    sequence="20"
/>
```

!!! warning "Estructura de menús"
    - Primer nivel sin `parent` — Menú principal
    - Con `parent="..."` — Submenú
    - `sequence` — Orden de aparición (menor = más arriba)

---

## Acciones en Botones

Agrega botones en las vistas que ejecuten acciones:

### En vistas Form

```xml
<form>
    <sheet>
        <!-- Contenido -->
    </sheet>
    
    <footer>
        <button name="action_marcar_pagado" 
                type="action"
                string="Marcar como pagado"
                class="btn-primary"/>
        <button name="action_enviar_email" 
                type="action"
                string="Enviar por email"/>
        <button name="cerrar" 
                type="object"
                string="Cerrar"
                class="btn-secondary"/>
    </footer>
</form>
```

### En vistas List

```xml
<list>
    <!-- Columnas -->
    <field name="nombre"/>
    
    <!-- Botón de acción -->
    <button name="action_duplicar" 
            type="action"
            string="Duplicar"
            icon="fa-copy"/>
</list>
```

**Tipos de botones:**

| Tipo | Función | Ejemplo |
|------|---------|---------|
| `action` | Ejecuta una acción | Abre informe, crea registro |
| `object` | Llama método Python | `def cerrar(self):` |
| `workflow` | Cambia estado en workflow | Transiciones |

---

## Acciones con Contexto y Parámetros

Puedes pasar información adicional a una acción:

```xml
<record id="action_ordenes_nuevas" model="ir.actions.act_window">
    <field name="name">Órdenes nuevas</field>
    <field name="res_model">orden.orden</field>
    <field name="view_mode">list,form</field>
    <!-- Filtra solo órdenes con estado 'nuevo' -->
    <field name="domain">[('estado', '=', 'nuevo')]</field>
    <!-- Parámetros adicionales -->
    <field name="context">{'default_estado': 'nuevo'}</field>
</record>
```

!!! tip "Domain: filtrar registros"
    ```python
    # Sintaxis de domain
    [('estado', '=', 'nuevo')]              # Estado igual a 'nuevo'
    [('precio', '>', 100)]                  # Precio mayor a 100
    [('activo', '=', True)]                 # Solo activos
    [('estado', 'in', ['nuevo', 'urgente'])]  # Estado en lista
    [('fecha', '>=', '2026-01-01')]         # Fecha desde
    ```

---

## Flujos de Trabajo (Workflows)

Un workflow define los estados posibles de un registro y las transiciones entre ellos.

### Definir un workflow

```xml
<!-- Definición del workflow -->
<record id="wf_factura" model="workflow">
    <field name="name">Flujo de Factura</field>
    <field name="osv">factura.factura</field>
    <field name="on_create">True</field>
</record>

<!-- Estados del workflow -->
<record id="wf_estado_borrador" model="workflow.activity">
    <field name="name">Borrador</field>
    <field name="wkf_id" ref="wf_factura"/>
    <field name="kind">function</field>
    <field name="action">action_draft()</field>
</record>

<record id="wf_estado_confirmado" model="workflow.activity">
    <field name="name">Confirmado</field>
    <field name="wkf_id" ref="wf_factura"/>
</record>

<!-- Transiciones (cambios de estado) -->
<record id="wf_trans_confirmar" model="workflow.transition">
    <field name="name">Confirmar</field>
    <field name="act_from" ref="wf_estado_borrador"/>
    <field name="act_to" ref="wf_estado_confirmado"/>
    <field name="trigger">manual</field>
    <field name="signal">confirmar</field>
</record>
```

### Usar workflow en Python

```python
from odoo import models, fields, api

class Factura(models.Model):
    _name = 'factura.factura'
    
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado')
    ], default='borrador')
    
    @api.multi
    def action_confirmar(self):
        """Confirma la factura"""
        for record in self:
            record.estado = 'confirmado'
    
    @api.multi
    def action_pagar(self):
        """Marca como pagada"""
        self.estado = 'pagado'
```

---

## Ejemplo Completo: Flujo de Pedidos

### Paso 1: Modelo (`models/pedido.py`)

```python
from odoo import models, fields, api

class Pedido(models.Model):
    _name = 'pedido.pedido'
    _description = 'Pedidos de clientes'
    
    numero = fields.Char(string='Número', default='Nuevo')
    cliente_id = fields.Many2one('cliente.cliente', required=True)
    fecha = fields.Date(default=fields.Date.today)
    total = fields.Float(string='Total')
    
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado')
    ], default='borrador', readonly=True)
    
    @api.model
    def create(self, values):
        if values.get('numero', 'Nuevo') == 'Nuevo':
            values['numero'] = self.env['ir.sequence'].next_by_code(
                'pedido.pedido'
            ) or 'PED/001'
        return super().create(values)
    
    def action_confirmar(self):
        """Confirma el pedido"""
        self.estado = 'confirmado'
    
    def action_entregar(self):
        """Marca como entregado"""
        self.estado = 'entregado'
    
    def action_cancelar(self):
        """Cancela el pedido"""
        self.estado = 'cancelado'
```

### Paso 2: Vistas y Acciones (`views/pedido_views.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <!-- VISTA FORM CON BOTONES -->
        <record id="view_pedido_form" model="ir.ui.view">
            <field name="name">Pedido - Formulario</field>
            <field name="model">pedido.pedido</field>
            <field name="arch" type="xml">
                <form>
                    <sheet>
                        <div class="alert alert-info" 
                             attrs="{'invisible': [('estado', '!=', 'borrador')]}">
                            Este pedido aún está en borrador
                        </div>
                        
                        <h1>
                            <field name="numero"/>
                        </h1>
                        
                        <group>
                            <group>
                                <field name="cliente_id"/>
                                <field name="fecha"/>
                            </group>
                            <group>
                                <field name="estado" readonly="1"/>
                                <field name="total"/>
                            </group>
                        </group>
                    </sheet>
                    
                    <footer>
                        <!-- Botón confirmar (solo si borrador) -->
                        <button name="action_confirmar"
                                type="object"
                                string="Confirmar"
                                class="btn-primary"
                                attrs="{'invisible': [('estado', '!=', 'borrador')]}"/>
                        
                        <!-- Botón entregar (solo si confirmado) -->
                        <button name="action_entregar"
                                type="object"
                                string="Entregar"
                                class="btn-success"
                                attrs="{'invisible': [('estado', '!=', 'confirmado')]}"/>
                        
                        <!-- Botón cancelar -->
                        <button name="action_cancelar"
                                type="object"
                                string="Cancelar"
                                class="btn-danger"
                                attrs="{'invisible': [('estado', 'in', ['entregado', 'cancelado'])]}"/>
                        
                        <button name="cerrar"
                                type="object"
                                string="Cerrar"
                                class="btn-secondary"/>
                    </footer>
                </form>
            </field>
        </record>
        
        <!-- VISTA LIST -->
        <record id="view_pedido_list" model="ir.ui.view">
            <field name="name">Pedido - Listado</field>
            <field name="model">pedido.pedido</field>
            <field name="arch" type="xml">
                <list>
                    <field name="numero"/>
                    <field name="cliente_id"/>
                    <field name="fecha"/>
                    <field name="total"/>
                    <field name="estado" 
                           decoration-success="estado=='entregado'"
                           decoration-warning="estado=='confirmado'"
                           decoration-danger="estado=='cancelado'"/>
                </list>
            </field>
        </record>
        
        <!-- ACCIONES DE LISTADO -->
        <record id="action_pedido_list" model="ir.actions.act_window">
            <field name="name">Pedidos</field>
            <field name="res_model">pedido.pedido</field>
            <field name="view_mode">list,form</field>
        </record>
        
        <record id="action_pedido_nuevo" model="ir.actions.act_window">
            <field name="name">Nuevo Pedido</field>
            <field name="res_model">pedido.pedido</field>
            <field name="view_mode">form</field>
            <field name="target">new</field>
        </record>
        
        <!-- ACCIONES DE SERVIDOR -->
        <record id="action_confirmar_todos" model="ir.actions.server">
            <field name="name">Confirmar seleccionados</field>
            <field name="model_id" ref="model_pedido_pedido"/>
            <field name="code">
for record in records:
    record.action_confirmar()
            </field>
        </record>
        
        <!-- MENÚ -->
        <menuitem id="menu_pedido_principal"
            name="Pedidos"
            sequence="20"
        />
        
        <menuitem id="menu_pedido_list"
            name="Todos los pedidos"
            parent="menu_pedido_principal"
            action="action_pedido_list"
            sequence="10"
        />
        
        <menuitem id="menu_pedido_nuevo"
            name="Crear pedido"
            parent="menu_pedido_principal"
            action="action_pedido_nuevo"
            sequence="20"
        />
    </data>
</odoo>
```

### Paso 3: Secuencia para numeración

```xml
<!-- En el mismo archivo o en otro XML -->
<record id="seq_pedido" model="ir.sequence">
    <field name="name">Pedido</field>
    <field name="code">pedido.pedido</field>
    <field name="prefix">PED/%(y)s/</field>
    <field name="number_next">1</field>
    <field name="padding">4</field>
</record>
```

!!! success "¡Lo lograste!"
    Ahora tienes un flujo de pedidos completo con estados, transiciones y botones contextuales.

---

## Checklist de aprendizaje

- [ ] Entiendo qué es una acción y para qué sirve
- [ ] Puedo crear acciones de ventana que abran vistas
- [ ] Sé cómo crear acciones de servidor que ejecuten código
- [ ] He vinculado acciones a menús
- [ ] Puedo agregar botones a formularios y listas
- [ ] Entiendo cómo funcionan los workflows
- [ ] Puedo filtrar registros con domain y context

---

## Ejercicio propuesto

!!! example "Ejercicio: Sistema de Pedidos con Transiciones"
    **Objetivo:** Crear un sistema de pedidos con flujo de estados.
    
    **Requisitos:**
    - Modelo `Pedido`: número (secuencia), cliente, fecha, total, estado
    - Estados: Borrador → Confirmado → Enviado → Entregado → (Cancelado)
    - Botones contextuales: Confirmar (solo borrador), Enviar (solo confirmado), Entregar (solo enviado)
    - Acción de servidor: "Confirmar todos los seleccionados"
    - Menú: Todos los pedidos, Nuevo pedido, Filtro por estado
    - Vistas: List y Form
    
    **Criterios de éxito:**
    - Un pedido nuevo empieza en Borrador
    - Solo se puede confirmar si está en Borrador
    - Los botones aparecen/desaparecen según el estado
    - Se puede filtrar por estado desde el menú

---

## Referencias

- [Acciones en Odoo](https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html)
- [Tipos de acciones](https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html)
- [Flujos de trabajo](https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html)
