from odoo import Command, models


class EstateProperty(models.Model):
    # Extend the estate.property defined in the 'estate' module.
    _inherit = "estate.property"

    def sell_property(self):
        # Run the original sell logic first (state -> sold, with its guards).
        res = super().sell_property()
        # Then bill the buyer: 6% commission on the selling price + a flat admin fee.
        for prop in self:
            if not prop.buyer_id:
                continue
            self.env["account.move"].create({
                "partner_id": prop.buyer_id.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create({
                        "name": "6%% Commission - %s" % prop.name,
                        "quantity": 1,
                        "price_unit": prop.selling_price * 0.06,
                    }),
                    Command.create({
                        "name": "Administrative fees",
                        "quantity": 1,
                        "price_unit": 100.00,
                    }),
                ],
            })
        return res
