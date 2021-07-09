# -*- encoding: utf-8 -*-
# Copyright 2021 Valentin Vinagre <valentin.vinagre@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.osv import expression


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    fiscal_position_type = fields.Selection(
        selection=[("b2c", "End customer (B2C)"), ("b2b", "Company (B2B)")],
        string="Type",
        default=lambda self: self._default_fiscal_position_type(),
    )

    @api.model
    def _default_fiscal_position_type(self):
        return self.env.user.company_id.default_fiscal_position_type

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.context.get("fiscal_position_type"):
            args = expression.AND(
                (
                    args,
                    [
                        (
                            "fiscal_position_type",
                            "=",
                            self.env.context.get("fiscal_position_type", False),
                        )
                    ],
                )
            )
        return super(AccountFiscalPosition, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def get_fiscal_position(
            self, company_id, partner_id, delivery_id=None, context=None):
        fiscal_type = False
        if partner_id:
            delivery = self.env["res.partner"].browse(delivery_id or partner_id)
            # Only type has been configured
            if (
                delivery.fiscal_position_type
                and not delivery.property_account_position
            ):
                fiscal_type = delivery.fiscal_position_type
        fp_id = super(
            AccountFiscalPosition, self.with_context(fiscal_position_type=fiscal_type)
            ).get_fiscal_position(
                company_id, partner_id, delivery_id=delivery_id, context=context)
        return fp_id
