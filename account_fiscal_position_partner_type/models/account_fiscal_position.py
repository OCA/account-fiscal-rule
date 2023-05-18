# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    fiscal_position_type = fields.Selection(
        selection=[("b2c", "End customer (B2C)"), ("b2b", "Company (B2B)")],
        string="Type",
        default=lambda self: self.env.company.default_fiscal_position_type,
    )

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("fiscal_position_type"):
            domain = expression.AND(
                (
                    domain,
                    [
                        (
                            "fiscal_position_type",
                            "=",
                            self.env.context["fiscal_position_type"],
                        )
                    ],
                )
            )
        return super().search(
            domain, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def _get_fiscal_position(self, partner, delivery=None):
        fiscal_type = False
        if partner:
            delivery = delivery or partner
            # Only type has been configured
            if (
                delivery.fiscal_position_type
                and not delivery.property_account_position_id
            ):
                fiscal_type = delivery.fiscal_position_type
        return super(
            AccountFiscalPosition, self.with_context(fiscal_position_type=fiscal_type)
        )._get_fiscal_position(partner=partner, delivery=delivery)
