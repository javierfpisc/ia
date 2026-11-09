from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Properties"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- Basic fields ---
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=3),
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False, tracking=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    has_garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        copy=False,
        default="new",
        tracking=True,
    )

    # --- Relations ---
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False, tracking=True)
    salesperson_id = fields.Many2one("res.users", string="Real Estate Agent", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag")
    amenity_ids = fields.Many2many("estate.property.amenity", string="Amenities")
    offer_ids = fields.One2many("estate.property.offer", "property_id")

    # --- Location ---
    country_id = fields.Many2one("res.country", string="Country")
    # Relay the flag URL so the kanban widget="image_url" can render it directly.
    # Pattern taken verbatim from website.visitor (Odoo 19 core).
    country_flag = fields.Char(related="country_id.image_url", string="Country Flag")

    # --- Image + currency (currency lets prices render with the monetary widget) ---
    image = fields.Image("Property Image", max_width=1920, max_height=1920)
    image_128 = fields.Image("Thumbnail", related="image", max_width=128, max_height=128, store=True)
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)

    # --- Computed fields ---
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(string="Best Price", compute="_compute_best_price")
    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")

    # --- SQL constraints (Odoo 19 declarative API — replaces the old _sql_constraints) ---
    _check_expected_price = models.Constraint(
        "CHECK(expected_price > 0)",
        "The expected price must be strictly positive.",
    )
    _check_selling_price = models.Constraint(
        "CHECK(selling_price >= 0)",
        "The selling price must be positive.",
    )

    @api.depends("living_area", "garden_area", "has_garden")
    def _compute_total_area(self):
        for record in self:
            if record.has_garden:
                record.total_area = record.living_area + record.garden_area
            else:
                record.total_area = record.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    # --- Onchange (UI helper) ---
    @api.onchange("has_garden")
    def _onchange_has_garden(self):
        if self.has_garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # --- Action buttons (wired to the form header) ---
    def sell_property(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled properties cannot be sold.")
            record.state = "sold"
            record.message_post(
                body="Property marked as <b>Sold</b>.",
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
        return True

    def cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be cancelled.")
            record.state = "cancelled"
        return True

    # --- Python constraint: selling price can't fall below 90% of expected ---
    @api.constrains("expected_price", "selling_price")
    def _check_valid_selling_price(self):
        for record in self:
            # GUARD: skip while selling_price is still 0 (no offer accepted yet).
            # Without this, creating any property would fail — her on-screen
            # version omits it; the official tutorial uses float_is_zero here.
            if record.selling_price > 0 and float_compare(
                record.selling_price, 0.9 * record.expected_price, precision_digits=2
            ) < 0:
                raise ValidationError(
                    "Selling price must be at least 90 percent of the expected price."
                )

    # --- Guard: only New or Cancelled properties may be deleted ---
    @api.ondelete(at_uninstall=False)
    def _unlink_only_new_or_cancelled(self):
        for record in self:
            if record.state not in ("new", "cancelled"):
                raise UserError("Only New or Cancelled properties can be deleted.")


    # --- Wizard: open "Make an Offer" dialog pre-filled with this property ---
    def action_make_offer(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Make an Offer",
            "res_model": "estate.make.offer.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_property_id": self.id},
        }

    # --- Smart button: jump to this property's offers ---
    def action_view_offers(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Offers",
            "res_model": "estate.property.offer",
            "view_mode": "list,form",
            "domain": [("property_id", "=", self.id)],
            "context": {"default_property_id": self.id},
        }
