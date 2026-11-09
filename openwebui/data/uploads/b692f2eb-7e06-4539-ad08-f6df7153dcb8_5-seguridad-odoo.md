# Unidad 5.5 · Seguridad en Odoo: Definición y Configuración

## Qué aprenderás

!!! note "Objetivos de este apartado"
    - Qué es el control de acceso en Odoo
    - Usuarios, grupos y permisos
    - Reglas de control de acceso (ACL)
    - Reglas de modelo: restricciones SQL y validaciones Python
    - Reglas de registro (ir.rule) y filtrado de registros
    - Campos restringidos (seguridad a nivel de campo)
    - Auditoría y registros de cambios

---

## Conceptos Fundamentales

### Seguridad en Capas

!!! example "¿Por qué seguridad?"
    Odoo es un **sistema empresarial** con datos sensibles:
    
    - Salarios y datos financieros
    - Información personal de clientes
    - Estrategia comercial confidencial
    - Credenciales y secretos
    
    Sin seguridad, cualquiera podría:
    - Leer datos que no le pertenecen
    - Modificar registros importantes
    - Eliminar información crítica

**Capas de seguridad en Odoo:**

```
1. Autenticación     → ¿Quién eres?
2. Autorización      → ¿Tienes permiso?
3. Control de Acceso → ¿Puedes hacer esto?
4. Seguridad a Nivel de Registro → ¿Es tu dato?
```

---

## Usuarios y Grupos

### Conceptos básicos

!!! warning "Diferencia importante"
    - **Usuario** — Persona que entra al sistema (correo + contraseña)
    - **Grupo** — Conjunto de permisos (ej: "Vendedor", "Contador")
    - **Un usuario puede estar en múltiples grupos**

**Ejemplo:**

```
Usuario: Juan García
├─ Grupo: Vendedor
│  └─ Permisos: Crear pedidos, ver clientes
│
├─ Grupo: Gerente
│  └─ Permisos: Ver reportes, aprobar pedidos
│
└─ Grupo: Usuario base
   └─ Permisos: Acceso al sistema
```

### Crear un grupo

En **Configuración → Usuarios y Grupos → Grupos**:

```xml
<record id="grupo_vendedor" model="res.groups">
    <field name="name">Vendedor</field>
    <field name="comment">Puede crear y editar pedidos</field>
    <!-- Permisos se asignan en la UI o vía XML -->
</record>
```

---

## Control de Acceso (ACL)

Las ACL definen **qué puede hacer cada grupo con cada modelo**.

### Syntax básico

```xml
<record id="acl_pedido_vendedor" model="ir.model.access">
    <field name="name">Pedido - Vendedor Lectura/Escritura</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="group_id" ref="grupo_vendedor"/>
    
    <!-- Permisos: crear, leer, escribir, eliminar -->
    <field name="perm_create">True</field>
    <field name="perm_read">True</field>
    <field name="perm_write">True</field>
    <field name="perm_unlink">False</field>
</record>
```

**Tabla de permisos:**

| Permiso | CRUD | Significado |
|---------|------|-------------|
| `perm_create` | C | Crear nuevos registros |
| `perm_read` | R | Ver registros |
| `perm_write` | W | Editar registros |
| `perm_unlink` | D | Eliminar registros |

### Ejemplo: Diferentes permisos por grupo

```xml
<!-- Grupo 1: Vendedor (puede crear y editar, pero NO eliminar) -->
<record id="acl_pedido_vendedor" model="ir.model.access">
    <field name="name">Pedido - Vendedor</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="group_id" ref="grupo_vendedor"/>
    <field name="perm_create">True</field>
    <field name="perm_read">True</field>
    <field name="perm_write">True</field>
    <field name="perm_unlink">False</field>
</record>

<!-- Grupo 2: Administrador (permisos totales) -->
<record id="acl_pedido_admin" model="ir.model.access">
    <field name="name">Pedido - Administrador</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="group_id" ref="base.group_system"/>
    <field name="perm_create">True</field>
    <field name="perm_read">True</field>
    <field name="perm_write">True</field>
    <field name="perm_unlink">True</field>
</record>

<!-- Grupo 3: Cliente (solo puede leer su propia información) -->
<record id="acl_pedido_cliente" model="ir.model.access">
    <field name="name">Pedido - Cliente Lectura</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="group_id" ref="base.group_portal"/>
    <field name="perm_create">False</field>
    <field name="perm_read">True</field>
    <field name="perm_write">False</field>
    <field name="perm_unlink">False</field>
</record>
```

!!! danger "ACL = Acceso al Modelo"
    **ACL define si puedo acceder al modelo completo**, pero **NO a registros específicos**.
    
    Para seguridad de registros necesitas **Reglas de Registro (ir.rule)**.
    Para restricciones a nivel de modelo necesitas **Reglas de Modelo** (validaciones).

---

## Reglas de Modelo (Restricciones y Validaciones)

Las reglas de modelo son **restricciones y validaciones definidas EN el modelo (Python)** que se aplican a **todos los registros** de ese modelo.

!!! note "Diferencia importante"
    - **Reglas de Modelo**: Restricciones EN el código (Python) — aplican a TODOS los registros
    - **Reglas de Registro (ir.rule)**: Filtros EN XML — aplican solo a ciertos registros

### Tipos de reglas de modelo

**1. Restricciones SQL (`_sql_constraints`)**

Se aplican a nivel de base de datos:

```python
from odoo import models, fields

class Pedido(models.Model):
    _name = 'ventas.pedido'
    _description = 'Pedidos de venta'
    
    numero = fields.Char(string='Número', required=True)
    fecha = fields.Date(string='Fecha', required=True)
    monto = fields.Float(string='Monto Total')
    
    # Restricción 1: El número debe ser único
    # Restricción 2: El monto no puede ser negativo
    _sql_constraints = [
        ('numero_unico', 'UNIQUE(numero)', 'El número de pedido debe ser único'),
        ('monto_positivo', 'CHECK(monto >= 0)', 'El monto debe ser positivo o cero'),
    ]
```

**Estructura de `_sql_constraints`:**

```python
_sql_constraints = [
    (
        'constraint_name',      # Nombre único de la restricción
        'SQL CONSTRAINT',       # Condición SQL
        'Mensaje de error'      # Mensaje si falla
    ),
]
```

**Ejemplos de restricciones SQL:**

```python
_sql_constraints = [
    # Unicidad
    ('numero_unico', 'UNIQUE(numero)', 'Número duplicado'),
    ('email_unico', 'UNIQUE(email)', 'Email ya registrado'),
    
    # Valores válidos
    ('edad_valida', 'CHECK(edad >= 18)', 'Debe ser mayor de edad'),
    ('cantidad_positiva', 'CHECK(cantidad > 0)', 'Cantidad debe ser positiva'),
    
    # Combinaciones
    ('periodo_valido', 'CHECK(fecha_inicio <= fecha_fin)', 
     'Fecha inicio debe ser menor a fecha fin'),
]
```

**2. Validaciones Python (`@api.constrains`)**

Se aplican en la lógica de negocio:

```python
from odoo import models, fields, api

class Pedido(models.Model):
    _name = 'ventas.pedido'
    
    numero = fields.Char(string='Número')
    cliente_id = fields.Many2one('cliente.cliente', string='Cliente')
    fecha = fields.Date(string='Fecha')
    lineas = fields.One2many('ventas.linea', 'pedido_id', string='Líneas')
    
    # Validación: El pedido debe tener al menos una línea
    @api.constrains('lineas')
    def _check_lineas_no_vacio(self):
        for pedido in self:
            if not pedido.lineas:
                raise models.ValidationError(
                    f"Pedido {pedido.numero} debe tener al menos una línea"
                )
    
    # Validación: El cliente no puede tener más de 5 pedidos pendientes
    @api.constrains('cliente_id')
    def _check_pedidos_limite(self):
        for pedido in self:
            pedidos_pendientes = self.env['ventas.pedido'].search([
                ('cliente_id', '=', pedido.cliente_id.id),
                ('estado', '=', 'borrador'),
            ])
            if len(pedidos_pendientes) > 5:
                raise models.ValidationError(
                    f"Cliente {pedido.cliente_id.nombre} tiene demasiados "
                    f"pedidos pendientes ({len(pedidos_pendientes)})"
                )
```

**Estructura de `@api.constrains`:**

```python
@api.constrains('campo1', 'campo2', ...)  # Campos que gatillan la validación
def _check_nombre_validacion(self):
    for record in self:
        if no_es_valido:
            raise models.ValidationError('Mensaje de error')
```

### Diferencias: SQL vs Python

| Aspecto | SQL Constraints | Python Constrains |
|---------|-----------------|-------------------|
| **Ubicación** | Base de datos | Lógica Odoo |
| **Rendimiento** | Rápido (BD) | Más lento (Python) |
| **Complejidad** | Limitado a SQL | Acceso a modelos Odoo |
| **Mensaje** | Genérico BD | Personalizado |
| **Ejemplo** | UNIQUE, CHECK | Búsquedas, lógica |
| **Cuándo usar** | Restricciones simples | Lógica compleja |

### Ejemplo completo: Validar estado de pedido

```python
from odoo import models, fields, api
from datetime import datetime

class Pedido(models.Model):
    _name = 'ventas.pedido'
    _description = 'Pedidos de venta'
    
    numero = fields.Char(string='Número')
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ], string='Estado', default='borrador')
    
    fecha_pedido = fields.Date(string='Fecha Pedido', default=fields.Date.today)
    fecha_entrega = fields.Date(string='Fecha Entrega esperada')
    monto = fields.Float(string='Monto Total')
    lineas = fields.One2many('ventas.linea', 'pedido_id', string='Líneas')
    
    # Restricción SQL: Monto no puede ser negativo
    _sql_constraints = [
        ('monto_positivo', 'CHECK(monto >= 0)', 'Monto debe ser positivo'),
        ('numero_unico', 'UNIQUE(numero)', 'Número de pedido duplicado'),
    ]
    
    # Validación 1: Fecha entrega debe ser después de fecha pedido
    @api.constrains('fecha_pedido', 'fecha_entrega')
    def _check_fechas(self):
        for pedido in self:
            if (pedido.fecha_pedido and pedido.fecha_entrega and
                pedido.fecha_entrega < pedido.fecha_pedido):
                raise models.ValidationError(
                    'Fecha de entrega no puede ser antes de fecha de pedido'
                )
    
    # Validación 2: Pedido debe tener líneas
    @api.constrains('lineas')
    def _check_lineas(self):
        for pedido in self:
            if not pedido.lineas:
                raise models.ValidationError(
                    'Pedido debe tener al menos una línea de producto'
                )
    
    # Validación 3: No puede cambiar a cancelado si ya está entregado
    @api.constrains('estado')
    def _check_cambio_estado(self):
        for pedido in self:
            # Buscar estado anterior
            pedido_anterior = self.env['ventas.pedido'].browse(pedido.id)
            if pedido_anterior.estado == 'entregado' and pedido.estado == 'cancelado':
                raise models.ValidationError(
                    'No puedes cancelar un pedido ya entregado'
                )
```

### Orden de validación en Odoo

```
1. @api.constrains (Python)
   └─ Se ejecutan ANTES de guardar
   └─ Pueden acceder a modelos Odoo
   └─ Mensajes personalizados
    
2. _sql_constraints (SQL)
   └─ Se ejecutan en la base de datos
   └─ Más rápidas pero menos flexibles
   └─ Última línea de defensa
    
3. Reglas de Registro (ir.rule)
   └─ Se aplican DESPUÉS de guardar
   └─ Filtran visibilidad de registros
```

---

## Reglas de Registro (Record Rules / ir.rule)

Las reglas de registro **filtran qué registros específicos puede ver/editar cada usuario**, mediante un dominio (condición) que se aplica automáticamente.

!!! note "Diferencia clave"
    - **ACL (ir.model.access)**: ¿Tengo permiso sobre el MODELO completo?
    - **Regla de Registro (ir.rule)**: ¿Veo ESTE REGISTRO específico?

### Estructura de una regla de registro

```xml
<record id="rule_ejemplo" model="ir.rule">
    <!-- Identificadores -->
    <field name="name">Nombre descriptivo de la regla</field>
    <field name="model_id" ref="model_modulo_modelo"/>
    
    <!-- Aplicación -->
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    
    <!-- Dominio (filtro) -->
    <field name="domain_force">[('usuario_id', '=', user.id)]</field>
    
    <!-- Permisos -->
    <field name="perm_read">True</field>
    <field name="perm_write">True</field>
    <field name="perm_create">False</field>
    <field name="perm_unlink">False</field>
</record>
```

### Atributos principales

| Atributo | Significado | Ejemplo |
|----------|-----------|---------|
| `name` | Nombre de la regla (solo documentación) | `"Pedido - Vendedor ve solo suyos"` |
| `model_id` | Modelo al que aplica | `ref="model_pedido_pedido"` |
| `domain_force` | Filtro de registros (sintaxis Odoo domain) | `[('vendedor_id', '=', user.id)]` |
| `groups` | Grupos a los que aplica | `[(4, ref('base.group_user'))]` |
| `perm_read` | Permite lectura de registros filtrados | `True` o `False` |
| `perm_write` | Permite edición de registros filtrados | `True` o `False` |
| `perm_create` | Permite crear nuevos registros | `True` o `False` |
| `perm_unlink` | Permite eliminar registros filtrados | `True` o `False` |
| `perm_unlink_all` | Permite eliminar incluso fuera del dominio | `False` (peligroso si `True`) |

### Variables especiales en domain_force

```xml
<!-- Usuario actual -->
<field name="domain_force">[('usuario_id', '=', user.id)]</field>

<!-- Departamento del usuario -->
<field name="domain_force">[('departamento_id', '=', user.departamento_id.id)]</field>

<!-- Empresa del usuario (multi-empresa) -->
<field name="domain_force">[('company_id', 'in', user.company_ids.ids)]</field>

<!-- Fecha actual -->
<field name="domain_force">[('fecha', '>=', time.strftime('%Y-%m-%d'))]</field>

<!-- Referencia a usuario global -->
<field name="domain_force">[('usuario_id', '=', user.id), ('activo', '=', True)]</field>
```

### Tipos de reglas de registro comunes

**1. Regla de usuario (Ver solo propios registros)**

```xml
<record id="rule_pedido_propio" model="ir.rule">
    <field name="name">Pedido - Solo propios</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="domain_force">[('usuario_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('grupo_vendedor'))]"/>
    <field name="perm_read">True</field>
    <field name="perm_write">True</field>
</record>
```

**2. Regla de departamento**

```xml
<record id="rule_pedido_departamento" model="ir.rule">
    <field name="name">Pedido - Departamento</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="domain_force">[('departamento_id', '=', user.departamento_id.id)]</field>
    <field name="groups" eval="[(4, ref('grupo_supervisor'))]"/>
</record>
```

**3. Regla de estado (Registros activos)**

```xml
<record id="rule_pedido_activo" model="ir.rule">
    <field name="name">Pedido - Solo activos</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="domain_force">[('activo', '=', True)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

**4. Regla de administrador (Sin restricciones)**

```xml
<record id="rule_pedido_admin" model="ir.rule">
    <field name="name">Pedido - Administrador (sin límite)</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="domain_force">[(1, '=', 1)]</field>  <!-- Siempre verdadero -->
    <field name="groups" eval="[(4, ref('base.group_system'))]"/>
    <field name="perm_read">True</field>
    <field name="perm_write">True</field>
    <field name="perm_create">True</field>
    <field name="perm_unlink">True</field>
</record>
```

### Operadores de dominio

```xml
<!-- Igualdad -->
<field name="domain_force">[('estado', '=', 'borrador')]</field>

<!-- Desigualdad -->
<field name="domain_force">[('estado', '!=', 'cancelado')]</field>

<!-- Mayor/Menor -->
<field name="domain_force">[('monto', '>', 1000)]</field>
<field name="domain_force">[('fecha', '<', '2026-01-01')]</field>

<!-- IN (dentro de lista) -->
<field name="domain_force">[('estado', 'in', ['borrador', 'confirmado'])]</field>

<!-- NOT IN -->
<field name="domain_force">[('estado', 'not in', ['cancelado', 'archivado'])]</field>

<!-- LIKE (búsqueda de texto) -->
<field name="domain_force">[('nombre', 'like', 'Acme')]</field>

<!-- AND lógico (múltiples condiciones) -->
<field name="domain_force">[('usuario_id', '=', user.id), ('estado', '=', 'confirmado')]</field>

<!-- OR lógico (dentro de tupla con clave | al principio) -->
<field name="domain_force">['|', ('usuario_id', '=', user.id), ('estado', '=', 'público')]</field>
```

### Combinación de múltiples reglas de registro

Cuando hay varias reglas para un modelo, Odoo las **combina con AND lógico**:

```xml
<!-- Regla 1: Usuario debe ser vendedor -->
<record id="rule_pedido_vendedor" model="ir.rule">
    <field name="name">Pedido - Vendedor</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="domain_force">[('vendedor_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('grupo_vendedor'))]"/>
</record>

<!-- Regla 2: Pedido debe estar confirmado -->
<record id="rule_pedido_confirmado" model="ir.rule">
    <field name="name">Pedido - Confirmado</field>
    <field name="model_id" ref="model_pedido_pedido"/>
    <field name="domain_force">[('estado', '=', 'confirmado')]</field>
    <field name="groups" eval="[(4, ref('grupo_vendedor'))]"/>
</record>

<!-- Resultado: Vendedor solo ve sus pedidos Y confirmados -->
<!-- domain_force = [('vendedor_id', '=', user.id)] AND [('estado', '=', 'confirmado')] -->
```

### Orden de evaluación

```
1. ACL (ir.model.access)
   └─ ¿Tengo permiso sobre el MODELO?
   └─ Si NO → Sin acceso al modelo completo
    
2. Reglas de Registro (ir.rule)
   └─ ¿Este REGISTRO específico pasa el domain_force?
   └─ Si NO → No veo este registro
    
3. Seguridad de Campo
   └─ ¿Puedo ver ESTE CAMPO específico?
   └─ Si NO → Campo oculto/restringido
    
4. Acceso concedido
   └─ Solo registros filtrados y campos permitidos
```

---

## Seguridad a Nivel de Campo

Oculta o hace de solo lectura campos para ciertos grupos.

### Atributos de campo

```xml
<record id="view_empleado_form" model="ir.ui.view">
    <field name="name">Empleado - Formulario</field>
    <field name="model">empleado.empleado</field>
    <field name="arch" type="xml">
        <form>
            <field name="nombre"/>
            
            <!-- Solo HR puede ver/editar salario -->
            <field name="salario" 
                   groups="grupo_rrhh"/>
            
            <!-- Solo lectura para vendedores -->
            <field name="comentarios_internos" 
                   attrs="{'readonly': [('...')]}"/>
        </form>
    </field>
</record>
```

### Atributos en campos

```xml
<!-- Campo visible solo para grupo específico -->
<field name="campo" groups="grupo_nombre"/>

<!-- Campo visible para varios grupos -->
<field name="campo" groups="grupo1,grupo2"/>

<!-- Campo de solo lectura -->
<field name="campo" readonly="1"/>

<!-- Campo con lectura condicional -->
<field name="campo" attrs="{'readonly': [('estado', '!=', 'borrador')]}"/>
```

---

## Ejemplo Completo: Seguridad de Pedidos

### Paso 1: Grupos en XML (`security/grupos.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <record id="grupo_vendedor" model="res.groups">
            <field name="name">Vendedor</field>
            <field name="comment">Gestiona sus propios pedidos</field>
        </record>
        
        <record id="grupo_gerente_venta" model="res.groups">
            <field name="name">Gerente de Ventas</field>
            <field name="comment">Ve todos los pedidos, puede aprobar</field>
        </record>
        
        <record id="grupo_cliente" model="res.groups">
            <field name="name">Cliente</field>
            <field name="comment">Cliente portal, ve solo sus pedidos</field>
        </record>
    </data>
</odoo>
```

### Paso 2: Control de Acceso (`security/acl.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <!-- VENDEDOR -->
        <record id="acl_pedido_vendedor_read" model="ir.model.access">
            <field name="name">Pedido - Vendedor (Lectura/Escritura)</field>
            <field name="model_id" ref="model_pedido_pedido"/>
            <field name="group_id" ref="grupo_vendedor"/>
            <field name="perm_create">True</field>
            <field name="perm_read">True</field>
            <field name="perm_write">True</field>
            <field name="perm_unlink">False</field>
        </record>
        
        <!-- GERENTE -->
        <record id="acl_pedido_gerente" model="ir.model.access">
            <field name="name">Pedido - Gerente (Control total)</field>
            <field name="model_id" ref="model_pedido_pedido"/>
            <field name="group_id" ref="grupo_gerente_venta"/>
            <field name="perm_create">True</field>
            <field name="perm_read">True</field>
            <field name="perm_write">True</field>
            <field name="perm_unlink">True</field>
        </record>
        
        <!-- CLIENTE (Portal) -->
        <record id="acl_pedido_cliente" model="ir.model.access">
            <field name="name">Pedido - Cliente (Solo lectura)</field>
            <field name="model_id" ref="model_pedido_pedido"/>
            <field name="group_id" ref="grupo_cliente"/>
            <field name="perm_create">False</field>
            <field name="perm_read">True</field>
            <field name="perm_write">False</field>
            <field name="perm_unlink">False</field>
        </record>
    </data>
</odoo>
```

### Paso 3: Reglas de Registro (`security/reglas.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data>
        <!-- Vendedor: solo sus pedidos -->
        <record id="rule_pedido_vendedor" model="ir.rule">
            <field name="name">Pedido - Vendedor (propios)</field>
            <field name="model_id" ref="model_pedido_pedido"/>
            <field name="domain_force">[('vendedor_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('grupo_vendedor'))]"/>
            <field name="perm_read">True</field>
            <field name="perm_write">True</field>
            <field name="perm_create">True</field>
            <field name="perm_unlink">False</field>
        </record>
        
        <!-- Gerente: todos los pedidos -->
        <record id="rule_pedido_gerente" model="ir.rule">
            <field name="name">Pedido - Gerente (todos)</field>
            <field name="model_id" ref="model_pedido_pedido"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('grupo_gerente_venta'))]"/>
        </record>
        
        <!-- Cliente: solo sus pedidos -->
        <record id="rule_pedido_cliente" model="ir.rule">
            <field name="name">Pedido - Cliente (propios)</field>
            <field name="model_id" ref="model_pedido_pedido"/>
            <field name="domain_force">[('cliente_id.user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('grupo_cliente'))]"/>
        </record>
    </data>
</odoo>
```

### Paso 4: Campos restringidos (`views/pedido_views.xml`)

```xml
<record id="view_pedido_form" model="ir.ui.view">
    <field name="name">Pedido - Formulario</field>
    <field name="model">pedido.pedido</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <h1>
                    <field name="numero"/>
                </h1>
                
                <group>
                    <field name="cliente_id"/>
                    <field name="fecha"/>
                    
                    <!-- Solo vendedor asignado o gerente ve esto -->
                    <field name="vendedor_id" 
                           groups="grupo_vendedor,grupo_gerente_venta"/>
                    
                    <!-- Solo gerente ve notas confidenciales -->
                    <field name="notas_internas" 
                           groups="grupo_gerente_venta"
                           string="Notas (solo gerencia)"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

### Paso 5: Registrar en manifest (`__manifest__.py`)

```python
{
    'name': 'Gestión de Pedidos',
    'data': [
        'security/grupos.xml',
        'security/acl.xml',
        'security/reglas.xml',
        'views/pedido_views.xml',
    ],
}
```

!!! success "¡Seguridad implementada!"
    - Vendedor solo ve sus pedidos
    - Gerente ve todos
    - Cliente ve solo sus pedidos desde el portal
    - Campos confidenciales ocultos para usuarios normales

---

## Auditoría y Registros

### Registrar cambios automáticamente

```python
from odoo import models, fields

class Pedido(models.Model):
    _name = 'pedido.pedido'
    
    # Campos de auditoría
    create_uid = fields.Many2one('res.users', 'Creado por', readonly=True)
    create_date = fields.Datetime('Creado el', readonly=True)
    write_uid = fields.Many2one('res.users', 'Modificado por', readonly=True)
    write_date = fields.Datetime('Modificado el', readonly=True)
    
    # Odoo los añade automáticamente
```

**En la vista:**

```xml
<footer>
    <span class="oe_read_only">
        <field name="create_uid" invisible="1"/>
        <field name="create_date" invisible="1"/>
        Creado por: <field name="create_uid"/> el <field name="create_date"/>
    </span>
</footer>
```

---

## Checklist de aprendizaje

- [ ] Entiendo la diferencia entre usuarios y grupos
- [ ] Puedo crear grupos y asignar permisos
- [ ] Sé cómo crear ACL (Control de Acceso)
- [ ] Entiendo las Reglas de Dominio
- [ ] Puedo filtrar registros por usuario
- [ ] He restringido campos a ciertos grupos
- [ ] Conozco los campos de auditoría

---

## Ejercicio propuesto

!!! example "Ejercicio: Seguridad en Sistema de Facturas"
    **Objetivo:** Implementar seguridad completa en facturas.
    
    **Requisitos:**
    - Grupos: Contador (crea facturas), Gerente (aprueba), Cliente (ve las suyas), Admin
    - ACL: Contador CRUD, Gerente CRUD, Cliente solo lectura
    - Reglas de dominio:
      - Contador: solo sus facturas
      - Gerente: todas
      - Cliente: solo las suyas (via email)
    - Campos: "Notas internas" solo para gerencia, "Líneas" editables solo contador
    
    **Criterios de éxito:**
    - Contador no ve facturas de otros
    - Gerente aprueba todas
    - Cliente portal ve sus facturas
    - Campos confidenciales ocultos

---

## Referencias

- [Seguridad en Odoo](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)
- [Control de Acceso](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html#access-control)
- [Reglas de Dominio](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html#domain-rules)
