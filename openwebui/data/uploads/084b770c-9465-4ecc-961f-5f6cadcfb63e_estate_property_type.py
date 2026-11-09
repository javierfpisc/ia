from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Property Type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=1, help="Used to order types")
    property_ids = fields.One2many("estate.property", "property_type_id")
