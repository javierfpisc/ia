# Requisitos funcionales

> Sustituye este contenido por el enunciado de la práctica. Describe el comportamiento esperado con lenguaje natural. No es necesario indicar cómo debe programarse.

## 1. Contexto y objetivo (Describe brevemente el problema que debe resolver el módulo y el objetivo de negocio.)
Crearemos un sencillo módulo de gestión de préstamos de libros de una biblioteca

## 2. Usuarios y perfiles (Indica qué tipos de usuarios utilizarán la funcionalidad y qué responsabilidades tiene cada uno.)
Crea una estructura de usuarios sencilla, un usuario administrador de la biblioteca, y otro "librero" con un perfil funcional básico

## 3. Funcionalidades (Enumera las operaciones que debe permitir el sistema. Para cada una, explica quién puede realizarla y qué resultado se espera.)
-Crear y gestionar libros (puedes heredar algún modelo estándar como product.product)
-Crea una estructura de campos para el libro sencilla (ISBN, Año, Edición, etc.)
-Gestionar los usuarios (a través de algún modelo que herede de res.partner)
-Gestionar los préstamos de libros a usuarios (mediante campos relacionales)
-Crea datos demo para pruebas, 10 libros y 10 socios
-Añade un sistema de puntuación a los libros, para que los usuarios pueda puntura y añadir una breve crítica o reseña al mismo


## 4. Información que se debe gestionar (Describe los datos que deben almacenarse, sus relaciones y cuáles son obligatorios, únicos o calculados, si se conocen.)
-Usuarios de la biblioteca: Modelo heredado de res.partner
-Libros: Modelo heredado de product.product, añadiendo campos específicos para caracterizar un libro (Estado, ISBN, año edicición, edición, etc.)
-Un préstamo es un elemento que relaciona un libro con un usuario. Se gestionará mediante un modelo propio


## 5. Reglas de negocio (Explica las condiciones que deben cumplirse, las validaciones y las transiciones de estado.)
-Un préstamo (relación libro con usuario) solo puede implicar un usuario, es decir un libro puede estar en estado prestado/no prestado, y de ser el caso solamente se puede hacer un préstamo a un único usuario en un instante dado
-Un socio puede tener un máximo fijo de 3 préstamos activos
-El préstamo registra fecha de inicio, fecha prevista de devolución, fecha real de devolución, socio y libro asociados
-La fecha prevista no finaliza automáticamente el préstamo; el librero debe registrar la devolución
-Configura los permisos para que al asignar el rol de librero o administrador de biblioteca se disponga de todos los permisos necesarios para operar con libros, prestamos y usuarios.

## 6. Pantallas y navegación (Describe qué información debe consultar o modificar cada usuario y cómo espera acceder a ella. Puedes aportar capturas o ejemplos.)
-Vistas formulario, tree y kanban para libros. La vista kanban se gestiona en función del estado de préstamo del libro
-Vistas formulario y tree para usuarios
-Vistas formulario, tree, y calendario para para prestamos. La vista calendario tendrá en cuenta las fechas de inicio y fin del préstamo


## 7. Casos de uso y aceptación

- Dado un libro disponible, cuando se registra un préstamo para un socio, entonces el libro aparece como prestado.
- Dado un libro con un préstamo activo, cuando se intenta crear otro préstamo para ese libro, entonces la operación se rechaza.
- Dado un socio con tres préstamos activos, cuando se intenta registrar un cuarto, entonces la operación se rechaza.
- Dado un préstamo activo, cuando el librero registra la devolución, entonces se guarda la fecha real y el libro vuelve a estar disponible.
- Dada una fecha prevista de devolución anterior a la fecha de préstamo, cuando se guarda el préstamo, entonces la operación se rechaza.

## 8. Fuera de alcance

- Cierre automático de préstamos al alcanzar la fecha prevista.
- Gestión de multas, pagos, reservas, avisos por correo y acceso de socios al portal.

## 9. Requisitos y restricciones y buenas prácticas

-Los modelos deben disponer de un campo de referencia legible (name) usado como _rec_name para mostrar etiquetas intuitivas en la interfaz (breadcrumbs, títulos, selectores).
-Los modelos nuevos (_name) deben definir _description para etiqueta legible en menús y vistas; los modelos heredados (_inherit) no requieren _name ni _description propios.
-Validaciones de integridad de negocio: usar @api.constrains (Python) para reglas que deben cumplirse siempre; evitar depender solo de validaciones en vistas (JS).
-Campos computados que se usan en búsquedas, dominios o agrupaciones: definir store=True y @api.depends correcto con todas las dependencias.
-Preferir herencia de modelos estándar (res.partner, product.product, product.template) sobre crear modelos desde cero cuando la semántica encaje; aprovecha campos, vistas y lógica existente.
-No duplicar lógica: centralizar reglas de negocio en el modelo (métodos Python), no en controladores ni vistas.
-Nomenclatura coherente: campos booleanos con prefijo "is_" o "has_", campos de conteo con sufijo "_count", campos de estado con "state" y selection.
-Usar _order en modelos con listas naturales (fechas, nombres) para UX predecible.
-Permisos (ACL) por modelo en ir.model.access.csv: mínimo lectura/creación/escritura según rol; reglas de registro (record rules) solo si hay requisito real de segregación de datos.
-No conceder permisos de unlink (eliminar) a roles funcionales básicos; reservar a administrador.
-Evitar hardcoded strings en Python: usar _() para traducibles; etiquetas de campos y vistas en español (idioma base del proyecto).
-Vistas: usar widgets apropiados (badge para selection/state, statusbar para flujos, kanban para tableros visuales).
-Acciones de ventana (ir.actions.act_window): definir domain y context para filtrar y pre-rellenar según el caso de uso.
-Menús: agrupar por área funcional, sequence ordenado, groups para control de visibilidad.
-Pruebas: cubrir casos de uso críticos (reglas de negocio, transiciones de estado, validaciones) con tests unitarios en tests/.
-Documentación: README.md del módulo con instalación, configuración y casos de uso principales; actualizar requirements/ ante decisiones de diseño relevantes.

