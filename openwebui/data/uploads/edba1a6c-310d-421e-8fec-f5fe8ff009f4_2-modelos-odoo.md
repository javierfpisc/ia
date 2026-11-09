# Unidad 5.2 · Modelos de Datos en Odoo: Creación y Gestión

## Qué aprenderás

!!! note "Objetivos de este apartado"
    - Qué son los modelos y cómo se mapean con la base de datos
    - Cómo funciona el ORM (Object-Relational Mapping) de Odoo
    - Atributos del modelo (_name, _description, _order, etc.)
    - Importancia del atributo "string" en campos para la interfaz
    - Concepto de XML ID y su uso en referencias
    - Crear modelos personalizados con campos de diferentes tipos
    - Establecer relaciones entre modelos (One2many, Many2one, Many2many)
    - Heredar y extender modelos existentes
    - Agregar métodos y validaciones personalizadas

---

## Conceptos Fundamentales

### Los Modelos: Entidades de Negocio en Python

!!! example "¿Qué es un modelo?"
    Un **modelo** en Odoo es una **clase Python que representa una entidad de negocio**. Piensa en modelos como:
    
    - Cliente — representa a cada cliente
    - Producto — representa cada producto en venta
    - Pedido — representa cada pedido realizado
    - Factura — representa cada factura emitida
    
    Cada modelo se mapea automáticamente con una **tabla en PostgreSQL**. Cuando creas un modelo, Odoo crea la tabla por ti.

**¿Por qué es genial?**

| Ventaja | Ejemplo |
|---------|---------|
| Automático | Creas una clase Python, Odoo crea la tabla DB |
| Seguro | Sin SQL manual = sin inyecciones SQL |
| Inteligente | Valida tipos de datos automáticamente |
| Relacional | Conecta modelos fácilmente |
| Persistente | Los datos se guardan en PostgreSQL |

### El ORM: La magia detrás

!!! tip "¿Qué es ORM?"
    **ORM** = Object-Relational Mapping. Es una capa que traduce entre:
    
    ```
    Objetos Python ←→ ORM de Odoo ←→ Tablas en PostgreSQL
    ```
    
    No escribes SQL. Odoo lo genera automáticamente.

```python
# Así escribes en Odoo (Python):
cliente = self.env['cliente.cliente'].create({
    'nombre': 'Juan García',
    'email': 'juan@ejemplo.com'
})

# Lo que Odoo ejecuta en PostgreSQL internamente:
# INSERT INTO cliente_cliente (nombre, email) 
# VALUES ('Juan García', 'juan@ejemplo.com');
```

---

## Creando Tu Primer Modelo

### Estructura básica

```python
from odoo import models, fields

class MiModelo(models.Model):
    _name = 'mi.modelo'                    # Identificador único del modelo
    _description = 'Mi primer modelo'      # Descripción legible en interfaz
    
    # Aquí van los campos
    nombre = fields.Char(string='Nombre')
    descripcion = fields.Text(string='Descripción')
```

### Atributos del Modelo (Model Attributes)

Cada modelo tiene **atributos especiales** que comienzan con `_` y controlan su comportamiento:

| Atributo | Obligatorio | Significado | Ejemplo |
|----------|-----------|-----------|---------|
| `_name` | Sí | ID único del modelo (usado internamente) | `'producto.producto'` |
| `_description` | No | Nombre legible en la interfaz | `'Catálogo de productos'` |
| `_order` | No | Ordenamiento por defecto en listas | `'nombre asc, fecha desc'` |
| `_table` | No | Nombre tabla DB (si difiere de _name) | `'producto_articulo'` |
| `_inherit` | No | Heredar de otro modelo | `'modelo.padre'` |
| `_inherits` | No | Herencia múltiple | `{'modelo.a': 'campo_fk'}` |
| `_auto` | No | Auto-crear tabla (por defecto: True) | `False` para modelos abstractos |
| `_rec_name` | No | Campo usado como identificador visual | `'codigo'` (por defecto: 'name') |
| `_log_access` | No | Registrar create_date, write_date | `False` para no registrar |

#### Ejemplo con múltiples atributos:

```python
from odoo import models, fields

class Pedido(models.Model):
    _name = 'ventas.pedido'
    _description = 'Pedidos de venta'
    _order = 'fecha desc'                  # Ordenar por fecha (más recientes primero)
    _rec_name = 'numero'                   # Mostrar el número, no el ID
    
    numero = fields.Char(string='Número', required=True, size=20)
    cliente = fields.Char(string='Cliente')
    fecha = fields.Date(string='Fecha', default=fields.Date.today)
```

**¿Por qué es importante `_name`?**

El `_name` es el **identificador único del modelo** que Odoo usa internamente:

- Crea automáticamente la tabla en BD con ese nombre (convertido: `ventas_pedido`)
- Es el que usas en búsquedas: `self.env['ventas.pedido'].search([])`
- Aparece en el archivo manifest como dependencia
- Forma parte del XML ID único: `modulo.ventas_pedido.record_id`

### El atributo "string": Etiquetas en la Interfaz

Cada campo puede tener un atributo **`string`** que define su **etiqueta visible** en la interfaz:

```python
# SIN string: Muestra el ID del campo (confuso)
nombre = fields.Char()
# En interfaz: "nombre" (ID interno del campo)

# CON string: Muestra una etiqueta legible
nombre = fields.Char(string='Nombre del Cliente')
# En interfaz: "Nombre del Cliente" (mucho mejor)

# Ejemplo completo
class Cliente(models.Model):
    _name = 'cliente.cliente'
    _description = 'Clientes'
    
    # Campos con etiquetas descriptivas
    nombre_completo = fields.Char(
        string='Nombre Completo',         # Lo que ve el usuario
        required=True
    )
    
    email = fields.Char(
        string='Correo electrónico'      # Más claro que "email"
    )
    
    telefono = fields.Char(
        string='Teléfono de contacto'    # Más descriptivo
    )
    
    fecha_registro = fields.Date(
        string='Fecha de registro'
    )
```

### XML ID: Identificadores Únicos Internos

Además del `_name`, Odoo usa **XML IDs** para identificar **registros específicos** dentro de un módulo.

**Formato:** `modulo.modelo.identificador_registro` o `modulo.identificador_registro`

#### Ejemplos:

```xml
<!-- XML ID de un registro específico -->
<record id="cliente_acme" model="cliente.cliente">
    <field name="nombre">ACME Corp</field>
    <field name="email">info@acme.com</field>
</record>

<!-- XML ID completo: cliente.cliente.cliente_acme -->

<!-- Dentro del mismo módulo, puedes referenciar con ref() -->
<record id="pedido_001" model="ventas.pedido">
    <field name="cliente_id" ref="cliente.cliente.cliente_acme"/>
</record>
```

**¿Por qué importan los XML IDs?**

- Son **únicos dentro de cada módulo**
- Permiten **referenciar registros** sin conocer su ID de BD
- Se usan en **datos de demostración** (demo data)
- Se usan en **reglas de seguridad** (referencia a grupos, modelos, etc.)
- Facilitan la **portabilidad** del módulo

#### XML ID vs Model _name vs ID de Base de Datos:

| Concepto | Formato | Ejemplo | Uso |
|----------|---------|---------|-----|
| **Model _name** | `modulo.modelo` | `ventas.pedido` | Identificar el modelo |
| **XML ID** | `modulo.modelo.registro` | `ventas.pedido.pedido_001` | Referenciar un registro |
| **DB ID** | Número entero | `42` | ID interno de BD (autonumérico) |

```python
# En código Python
cliente = self.env['cliente.cliente'].ref('cliente.cliente.cliente_acme')
# Busca usando XML ID

pedido = self.env['ventas.pedido'].browse(42)
# Busca usando ID de BD

pedidos = self.env['ventas.pedido'].search([])
# Busca todos los registros del modelo
```

---

## Tipos de Campos Disponibles

!!! note "Campos básicos"
    Odoo ofrece muchos tipos de campos. Los más comunes:

| Campo | Tipo Python | Ejemplo | Uso |
|-------|-------------|---------|-----|
| `Char` | Texto | `Nombre: Juan` | Campos cortos |
| `Text` | Párrafo | `Descripción: ...` | Campos largos |
| `Integer` | Número entero | `Cantidad: 5` | Conteos |
| `Float` | Número decimal | `Precio: 19.99` | Dinero, medidas |
| `Boolean` | Verdadero/Falso | `Activo: True` | Flags |
| `Date` | Fecha | `2026-11-06` | Solo fecha |
| `Datetime` | Fecha + Hora | `2026-11-06 12:30` | Auditoría |
| `Selection` | Opciones | `Estado: Nuevo/Proceso/Done` | Categorización |
| `Binary` | Archivo | Adjuntos | Descargas |

### Ejemplo completo con varios campos

```python
from odoo import models, fields

class Producto(models.Model):
    _name = 'producto.producto'
    _description = 'Catálogo de productos'
    
    # Campos básicos
    nombre = fields.Char(
        string='Nombre del Producto',
        required=True,                    # Campo obligatorio
        size=100                          # Máximo 100 caracteres
    )
    
    descripcion = fields.Text(
        string='Descripción detallada'
    )
    
    # Números
    precio = fields.Float(
        string='Precio (€)',
        digits=(10, 2),                   # Máx 10 dígitos, 2 decimales
        default=0.0
    )
    
    cantidad = fields.Integer(
        string='Cantidad en almacén',
        default=0
    )
    
    # Opciones
    categoria = fields.Selection([
        ('electronica', 'Electrónica'),
        ('ropa', 'Ropa'),
        ('libros', 'Libros')
    ], string='Categoría')
    
    # Estado
    activo = fields.Boolean(
        string='¿Activo?',
        default=True
    )
    
    # Fechas
    fecha_creacion = fields.Date(
        string='Fecha de creación',
        default=fields.Date.today
    )
```

!!! warning "Atributos clave"
    - `required=True` — El campo es obligatorio
    - `default=valor` — Valor por defecto
    - `string='...'` — Etiqueta mostrada al usuario
    - `digits=(n, m)` — n dígitos totales, m decimales

---

## Relaciones entre Modelos

Las relaciones son lo que hace que Odoo sea poderoso. Te permiten conectar modelos:

### 1. Many2one: El cliente tiene muchos pedidos

!!! example "Many2one"
    ```
    Pedido → Cliente (muchos pedidos de un cliente)
    ```

```python
class Pedido(models.Model):
    _name = 'pedido.pedido'
    _description = 'Pedidos de clientes'
    
    # Este pedido pertenece a UN cliente
    cliente_id = fields.Many2one(
        'cliente.cliente',                # Modelo relacionado
        string='Cliente',
        required=True                     # Todo pedido debe tener cliente
    )
    
    numero = fields.Char(string='Número de pedido')
    fecha = fields.Date(string='Fecha')
```

**Resultado en Odoo:**
- En el formulario de Pedido: campo dropdown para seleccionar cliente
- La BD guarda el ID del cliente

### 2. One2many: El cliente TIENE múltiples pedidos

!!! example "One2many"
    ```
    Cliente ← Pedidos (un cliente tiene muchos pedidos)
    ```

```python
class Cliente(models.Model):
    _name = 'cliente.cliente'
    _description = 'Clientes'
    
    nombre = fields.Char(string='Nombre')
    email = fields.Char(string='Email')
    
    # Este cliente TIENE muchos pedidos
    pedidos_ids = fields.One2many(
        'pedido.pedido',                  # Modelo relacionado
        'cliente_id',                     # Campo que referencia a este cliente
        string='Mis Pedidos'
    )
```

**Resultado en Odoo:**
- En el formulario de Cliente: tabla con todos sus pedidos
- Puedes crear/editar pedidos desde aquí

### 3. Many2many: Ejemplo con Etiquetas

!!! example "Many2many"
    ```
    Producto ↔ Etiquetas (muchos productos usan muchas etiquetas)
    ```

```python
class Etiqueta(models.Model):
    _name = 'etiqueta.etiqueta'
    nombre = fields.Char(string='Nombre')

class Producto(models.Model):
    _name = 'producto.producto'
    
    nombre = fields.Char(string='Nombre')
    
    # Este producto tiene MUCHAS etiquetas
    # Y cada etiqueta puede estar en MUCHOS productos
    etiquetas_ids = fields.Many2many(
        'etiqueta.etiqueta',              # Modelo relacionado
        string='Etiquetas'
    )
```

**Resultado en Odoo:**
- En el formulario: checkboxes para seleccionar múltiples etiquetas
- Odoo crea una tabla intermedia automáticamente

---

## Herencia de Modelos

### Extender modelos existentes sin modificar el original

!!! tip "Herencia"
    En lugar de modificar un módulo existente, **hereda** de sus modelos.

```python
# Módulo base (no modificas esto)
class Cliente(models.Model):
    _name = 'cliente.cliente'
    nombre = fields.Char()

# Tu módulo lo extiende
class ClienteExtendido(models.Model):
    _name = 'cliente.cliente'           # Mismo nombre = herencia
    _inherit = 'cliente.cliente'
    
    # Agregamos un nuevo campo
    numero_cliente_especial = fields.Char(
        string='Número de cliente VIP'
    )
```

!!! warning "Cuidado con la sintaxis"
    - `_name` debe ser **igual** al modelo padre (para heredar)
    - Agregamos `_inherit` para indicar explícitamente que heredamos

---

## Métodos y Validaciones

### Crear métodos personalizados

```python
from odoo import models, fields, api

class Factura(models.Model):
    _name = 'factura.factura'
    
    numero = fields.Char(string='Número')
    total = fields.Float(string='Total')
    pagada = fields.Boolean(default=False)
    
    # Método personalizado
    @api.model
    def crear_factura_demo(self):
        """Crea una factura de ejemplo"""
        return self.create({
            'numero': 'FAC-001',
            'total': 100.0
        })
    
    # Método que se ejecuta cuando se guarda
    def write(self, values):
        """Se ejecuta cada vez que se modifica"""
        print(f"Actualizando factura: {self.numero}")
        return super().write(values)
```

### Validaciones

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Producto(models.Model):
    _name = 'producto.producto'
    
    nombre = fields.Char()
    precio = fields.Float()
    cantidad = fields.Integer()
    
    @api.constrains('precio')
    def _check_precio_positivo(self):
        """Validación: el precio no puede ser negativo"""
        for record in self:
            if record.precio < 0:
                raise ValidationError(
                    f"El precio no puede ser negativo: {record.precio}"
                )
    
    @api.constrains('cantidad')
    def _check_cantidad_minima(self):
        """Validación: la cantidad mínima es 0"""
        for record in self:
            if record.cantidad < 0:
                raise ValidationError(
                    "La cantidad no puede ser negativa"
                )
```

---

## Campos Calculados

Campos que se calculan automáticamente sin guardarse en BD:

```python
class Pedido(models.Model):
    _name = 'pedido.pedido'
    
    lineas_ids = fields.One2many('pedido.linea', 'pedido_id')
    
    # Campo calculado (solo lectura)
    @api.depends('lineas_ids')
    def _compute_total(self):
        """Calcula el total sumando líneas"""
        for record in self:
            record.total = sum(linea.subtotal for linea in record.lineas_ids)
    
    total = fields.Float(
        string='Total',
        compute='_compute_total',        # Método que lo calcula
        store=False                      # No guardar en BD
    )

class LineaPedido(models.Model):
    _name = 'pedido.linea'
    
    pedido_id = fields.Many2one('pedido.pedido')
    cantidad = fields.Integer()
    precio_unitario = fields.Float()
    
    # Campo calculado
    @api.depends('cantidad', 'precio_unitario')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.cantidad * record.precio_unitario
    
    subtotal = fields.Float(compute='_compute_subtotal')
```

---

## Decoradores del API ORM

Un **decorador** es una línea que empieza por `@` y que se coloca justo encima de la definición de un método. Le indica a Odoo **cuándo** debe ejecutar ese método o **cómo** debe tratarlo. El cuerpo de la función no cambia: lo que cambia es el momento en que el ORM la invoca.

!!! tip "Idea clave"
    Un método sin decorador se ejecuta solo cuando alguien lo llama. Con un decorador, Odoo lo engancha a un evento (cambiar un campo, guardar, borrar, calcular un valor) o modifica la forma en que recibe sus argumentos.

### Tabla resumen

| Decorador | Función | Cuándo se ejecuta |
|-----------|---------|-------------------|
| `@api.model` | Método a nivel de modelo: `self` no apunta a registros concretos | Cuando se llama al método desde el modelo |
| `@api.model_create_multi` | Permite que `create()` reciba una **lista** de diccionarios | En cada llamada a `create()` |
| `@api.depends('campo')` | Indica de qué campos depende un campo calculado | Cuando cambia alguno de los campos indicados |
| `@api.depends_context('clave')` | Indica de qué claves del contexto depende un campo calculado | Cuando cambia el valor de esa clave en el contexto |
| `@api.constrains('campo')` | Valida los campos indicados | Al crear o modificar registros que cambian esos campos |
| `@api.onchange('campo')` | Reacciona en la interfaz cuando el usuario cambia un campo | Solo en el formulario, antes de guardar |
| `@api.ondelete(at_uninstall=False)` | Comprueba si se pueden eliminar los registros | Antes de borrar registros |

### `@api.model`

Se usa para métodos que no trabajan con un registro concreto, sino con el modelo en general. Por ejemplo, una consulta de utilidad:

```python
from odoo import models, fields, api

class Pedido(models.Model):
    _name = 'pedido.pedido'
    _description = 'Pedidos de clientes'

    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
    ], default='borrador')

    @api.model
    def get_pedidos_pendientes(self):
        """Devuelve los pedidos que aún no se han confirmado"""
        return self.search([('estado', '=', 'borrador')])
```

Se llama desde el modelo, sin necesidad de tener un registro previo:

```python
pendientes = self.env['pedido.pedido'].get_pedidos_pendientes()
```

### `@api.model_create_multi`

Decora el método `create()` para que reciba una **lista de diccionarios**, uno por cada registro que se quiere crear. Así se pueden crear varios registros en una sola llamada. Es la forma habitual de sobrescribir `create()` en Odoo moderno:

```python
from odoo import models, api

class Pedido(models.Model):
    _inherit = 'pedido.pedido'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault('estado', 'borrador')
        return super().create(vals_list)
```

!!! warning "Atención"
    El argumento `vals_list` es una lista. Si lo tratas como un diccionario, el método fallará al crear registros.

### `@api.depends`

Declara los campos de los que depende un campo calculado. Cuando cambia alguno de ellos, Odoo vuelve a calcular el valor. Puedes indicar rutas con punto para seguir relaciones entre modelos:

```python
from odoo import models, fields, api

class Pedido(models.Model):
    _inherit = 'pedido.pedido'

    total = fields.Float(compute='_compute_total')

    @api.depends('lineas_ids.subtotal')
    def _compute_total(self):
        for pedido in self:
            pedido.total = sum(pedido.lineas_ids.mapped('subtotal'))
```

Si cambia el `subtotal` de cualquier línea del pedido, el total se recalcula automáticamente.

### `@api.depends_context`

Funciona como `@api.depends`, pero para el **contexto** (`self.env.context`) en lugar de para campos. Sirve cuando el valor calculado depende de una clave del contexto, por ejemplo la empresa activa (`'company'`).

### `@api.constrains`

Valida los valores de los campos indicados. Se ejecuta al crear o modificar registros que cambian esos campos. Si la condición no se cumple, se lanza una excepción y la operación no se completa:

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Pedido(models.Model):
    _inherit = 'pedido.pedido'

    @api.constrains('total')
    def _check_total_positivo(self):
        for pedido in self:
            if pedido.total < 0:
                raise ValidationError("El total no puede ser negativo.")
```

!!! note "Relación con lo visto"
    Es la versión Python de las validaciones de la sección «Métodos y Validaciones». Las restricciones SQL (`_sql_constraints`) se definen en cambio como atributo de la clase.

### `@api.onchange`

Se ejecuta **solo en la interfaz**, cuando el usuario cambia un campo en el formulario y antes de guardar. Sirve para avisar o rellenar valores sobre la marcha. No se ejecuta cuando los registros se crean o modifican desde código Python (por ejemplo, con `create()` o `write()`).

```python
from odoo import models, fields, api

class Pedido(models.Model):
    _inherit = 'pedido.pedido'

    @api.onchange('estado')
    def _onchange_estado(self):
        if self.estado == 'cancelado':
            return {
                'warning': {
                    'title': 'Pedido cancelado',
                    'message': 'Revisa las líneas antes de guardar.',
                }
            }
```

### `@api.ondelete`

Se ejecuta **antes** de eliminar los registros. Si el método lanza una excepción, el borrado se cancela. El parámetro `at_uninstall=False` indica que la comprobación no se aplica cuando se desinstala el módulo:

```python
from odoo import models, api
from odoo.exceptions import ValidationError

class Pedido(models.Model):
    _inherit = 'pedido.pedido'

    @api.ondelete(at_uninstall=False)
    def _unlink_no_entregados(self):
        if any(pedido.estado == 'entregado' for pedido in self):
            raise ValidationError("No se puede eliminar un pedido ya entregado.")
```

!!! tip "Cómo leer la tabla"
    Pregúntate siempre **quién dispara el método**: un cambio de campo en la interfaz (`@api.onchange`), una validación al guardar (`@api.constrains`), un recálculo automático (`@api.depends`) o una eliminación (`@api.ondelete`).

---

## Práctica: Crear modelo con relaciones

### Paso 1: Crear archivo `models/blog.py`

```python
from odoo import models, fields, api

class BlogAutor(models.Model):
    _name = 'blog.autor'
    _description = 'Autores de blog'
    
    nombre = fields.Char(string='Nombre', required=True)
    email = fields.Char(string='Email')
    bio = fields.Text(string='Biografía')
    
    # One2many: este autor tiene muchos artículos
    articulos_ids = fields.One2many(
        'blog.articulo',
        'autor_id',
        string='Artículos'
    )

class BlogCategoria(models.Model):
    _name = 'blog.categoria'
    _description = 'Categorías de blog'
    
    nombre = fields.Char(string='Nombre', required=True)

class BlogArticulo(models.Model):
    _name = 'blog.articulo'
    _description = 'Artículos de blog'
    
    titulo = fields.Char(string='Título', required=True)
    contenido = fields.Html(string='Contenido')
    fecha_publicacion = fields.Date(string='Fecha', default=fields.Date.today)
    
    # Many2one: cada artículo tiene UN autor
    autor_id = fields.Many2one(
        'blog.autor',
        string='Autor',
        required=True
    )
    
    # Many2one: cada artículo está en UNA categoría
    categoria_id = fields.Many2one(
        'blog.categoria',
        string='Categoría'
    )
    
    # Many2many: un artículo tiene MUCHAS etiquetas
    etiquetas_ids = fields.Many2many(
        'blog.etiqueta',
        string='Etiquetas'
    )
    
    # Campo calculado: número de caracteres
    @api.depends('contenido')
    def _compute_caracteres(self):
        for record in self:
            record.caracteres = len(record.contenido or '') 
    
    caracteres = fields.Integer(
        string='Caracteres',
        compute='_compute_caracteres'
    )

class BlogEtiqueta(models.Model):
    _name = 'blog.etiqueta'
    _description = 'Etiquetas de blog'
    
    nombre = fields.Char(string='Nombre', required=True)
```

### Paso 2: Importar en `models/__init__.py`

```python
from . import blog
```

### Paso 3: Agregar al manifest `__manifest__.py`

```python
{
    'name': 'Blog de Ejemplo',
    'data': [
        'views/blog_views.xml',
    ],
}
```

!!! success "¡Lo lograste!"
    Ahora tienes modelos con relaciones Many2one, One2many y Many2many.

---

## Checklist de aprendizaje

- [ ] Entiendo qué es un modelo y cómo se mapea a la BD
- [ ] Puedo crear un modelo con varios tipos de campos
- [ ] Entiendo la diferencia entre Many2one, One2many y Many2many
- [ ] He creado modelos relacionados (Autor → Artículos)
- [ ] Sé cómo heredar un modelo existente
- [ ] He agregado validaciones a mis modelos
- [ ] Puedo crear campos calculados

---

## Ejercicio propuesto

!!! example "Ejercicio: Sistema de Biblioteca"
    **Objetivo:** Crear un sistema completo de gestión de biblioteca.
    
    **Requisitos:**
    - Modelo `Libro`: título, autor, isbn, cantidad_disponible
    - Modelo `Autor`: nombre, nacionalidad, biografía
    - Modelo `Miembro`: nombre, email, teléfono, fecha_inscripción
    - Modelo `Préstamo`: libro, miembro, fecha_prestamo, fecha_devolución_prevista
    - Relaciones: Autor → Libros (One2many), Libro → Préstamos (One2many), etc.
    - Validación: cantidad_disponible no puede ser negativa
    - Campo calculado en Libro: cantidad_prestada
    
    **Criterios de éxito:**
    - Crear un libro requiere especificar autor
    - Ver un autor muestra todos sus libros
    - Un préstamo no puede ser posterior a hoy

**Solución modelo:**

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Autor(models.Model):
    _name = 'biblioteca.autor'
    nombre = fields.Char(required=True)
    nacionalidad = fields.Char()
    libros_ids = fields.One2many('biblioteca.libro', 'autor_id')

class Libro(models.Model):
    _name = 'biblioteca.libro'
    titulo = fields.Char(required=True)
    isbn = fields.Char()
    autor_id = fields.Many2one('biblioteca.autor', required=True)
    cantidad_disponible = fields.Integer(default=1)
    
    @api.constrains('cantidad_disponible')
    def _check_cantidad(self):
        for record in self:
            if record.cantidad_disponible < 0:
                raise ValidationError("Cantidad no puede ser negativa")
```

---

## Referencias

- [API ORM de Odoo](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Referencia de campos](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#fields)
- [Validaciones y restricciones](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#constraints)
