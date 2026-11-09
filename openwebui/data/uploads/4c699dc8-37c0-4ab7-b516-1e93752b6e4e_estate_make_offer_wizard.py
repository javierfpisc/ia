from odoo import api, fields, models
from odoo.exceptions import UserError


class EstateMakeOfferWizard(models.TransientModel):
    _name = "estate.make.offer.wizard"
    _description = "Make an Offer on a Property"

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
        default=lambda self: self.env.context.get("default_property_id"),
    )
    partner_id = fields.Many2one("res.partner", string="Buyer", required=True)
    price = fields.Float(string="Offer Price", required=True)
    validity = fields.Integer(string="Validity (days)", default=7)

    def action_submit(self):
        self.ensure_one()
        if self.price <= 0:
            raise UserError("The offer price must be strictly positive.")
        self.env["estate.property.offer"].create(
            {
                "property_id": self.property_id.id,
                "partner_id": self.partner_id.id,
                "price": self.price,
                "validity": self.validity,
            }
        )
        # Returning False closes the dialog (standard Odoo wizard close pattern).
        return {"type": "ir.actions.act_window_close"}
