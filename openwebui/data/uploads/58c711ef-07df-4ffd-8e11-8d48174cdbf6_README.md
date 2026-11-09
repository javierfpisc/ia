# Módulos de ejemplo

Estos módulos sirven para consultar estructura y patrones; no forman parte del
directorio `addons/` y no se instalan directamente desde aquí. No se debe
modificar su código para implementar la práctica.

## `estate`

Tutorial de gestión inmobiliaria con modelos relacionados, campos calculados,
restricciones, vistas, menús y seguridad. Es el ejemplo más completo y puede
servir para estudiar cómo organizar un módulo funcional.

- Manifiesto: `estate/__manifest__.py`
- Modelos: `estate/models/`
- Vistas y navegación: `estate/views/`
- Seguridad: `estate/security/`
- Otros patrones: `estate/wizard/`, `estate/data/` y `estate/report/`

## `estate_accounts`

Ejemplo de extensión de `estate.property` con dependencias de `estate` y
`account`. Puede servir para observar la herencia de modelos, pero no es un
módulo completo de referencia: `estate_accounts/views/estate_property_views.xml`
contiene una vista explícitamente marcada como provisional. Verifica y completa
cualquier patrón antes de reutilizarlo.

## Procedencia y compatibilidad

El repositorio no documenta la procedencia ni la rama de origen de estos
ejemplos. Antes de apoyarse en ellos para una API concreta, comprueba el patrón
contra las fuentes locales de Odoo/OCB 19.0. No presupongas que un ejemplo es
compatible solo por estar incluido en esta carpeta.
