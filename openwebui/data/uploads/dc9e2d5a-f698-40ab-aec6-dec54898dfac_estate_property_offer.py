import logging

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offers on estate properties"
    _order = "price desc"

    price = fields.Float()
    state = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    # related field (stored) so offers can be grouped by property type
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )

    # SQL constraint (Odoo 19): the offer price must be positive
    _check_offer_price = models.Constraint(
        "CHECK(price > 0)",
        "The offer price must be strictly positive.",
    )

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for offer in self:
            base = fields.Date.to_date(offer.create_date) if offer.create_date else fields.Date.today()
            offer.date_deadline = base + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            base = fields.Date.to_date(offer.create_date) if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - base).days

    @api.model_create_multi
    def create(self, vals_list):
        # When an offer comes in, move the property to "Offer Received".
        for vals in vals_list:
            if vals.get("property_id"):
                prop = self.env["estate.property"].browse(vals["property_id"])
                if prop.state == "new":
                    prop.state = "offer_received"
        return super().create(vals_list)

    def accept_offer(self):
        for record in self:
            if record.state == "refused":
                raise UserError("You cannot accept a refused offer.")
            elif record.property_id.state == "offer_accepted":
                raise UserError("This property already has an accepted offer.")
            else:
                record.state = "accepted"
                record.property_id.buyer_id = record.partner_id
                record.property_id.state = "offer_accepted"
                record.property_id.selling_price = record.price
        return True

    def refuse_offer(self):
        for record in self:
            record.state = "refused"
        return True

    @api.model
    def _cron_expire_offers(self):
        """Scheduled action: mark pending offers whose deadline has passed as refused.

        'Pending' means state is False/None (never set — neither accepted nor refused).
        Offers that are already accepted or refused are left untouched.
        """
        today = fields.Date.today()
        expired = self.search([
            ("state", "=", False),
            ("date_deadline", "<", today),
        ])
        if expired:
            expired.write({"state": "refused"})
            _logger.info(
                "estate.property.offer._cron_expire_offers: "
                "expired %d offer(s) with ids %s",
                len(expired),
                expired.ids,
            )
