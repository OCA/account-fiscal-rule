# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    vat_vies_required = fields.Boolean(
        string="Vat was VIES validated",
        help="Apply only if VAT passed VIES validation.",
    )

    @api.model
    def search(self, domain, offset=0, limit=None, order=None, count=False):
        if "vat_vies_required" in self.env.context:
            domain = expression.AND(
                (
                    domain,
                    [
                        (
                            "vat_vies_required",
                            "=",
                            self.env.context["vat_vies_required"],
                        )
                    ],
                )
            )
        return super().search(
            domain, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def _get_fiscal_position(self, partner, delivery=None):
        _self = self
        if delivery or partner:
            partner_vat_vies = delivery or partner
            _self = self.with_context(
                vat_vies_required=partner_vat_vies.commercial_partner_id.vies_passed
            )
        return super(AccountFiscalPosition, _self)._get_fiscal_position(
            partner, delivery=delivery
        )
