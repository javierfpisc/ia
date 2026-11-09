from odoo import fields, models


class EstatePropertyAmenity(models.Model):
    # A lookup/catalog table: one row per amenity (Pool, Gym, Parking...).
    # Linked to properties through a Many2many — same shape as estate.property.tag.
    _name = "estate.property.amenity"
    _description = "Property Amenity"
    _order = "category, name"

    name = fields.Char(required=True)
    category = fields.Selection(
        selection=[
            ("indoor", "Indoor / Unit"),
            ("shared", "Building / Shared"),
            ("view", "View"),
            ("other", "Other"),
        ],
        default="other",
        string="Category",
    )
    active = fields.Boolean(default=True)
