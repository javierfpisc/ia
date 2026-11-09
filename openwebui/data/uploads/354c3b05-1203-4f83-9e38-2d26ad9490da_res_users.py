from odoo import fields, models


class ResUsers(models.Model):
    # _inherit (not _name) EXTENDS the existing res.users model — this is how
    # Odoo adds a field to a core model without touching its source.
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property",
        "salesperson_id",
        string="Properties",
        domain=[("state", "in", ["new", "offer_received"])],
    )
