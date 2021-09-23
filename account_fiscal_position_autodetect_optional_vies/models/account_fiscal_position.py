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
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if "vat_vies_required" in self.env.context:
            args = expression.AND(
                (
                    args,
                    [
                        (
                            "vat_vies_required",
                            "=",
                            self.env.context.get("vat_vies_required"),
                        )
                    ],
                )
            )
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    @api.model
    def get_fiscal_position(self, partner_id, delivery_id=None):
        _self = self
        if partner_id:
            partner = self.env["res.partner"].browse(delivery_id or partner_id)
            _self = self.with_context(vat_vies_required=partner.vies_passed)
        return super(AccountFiscalPosition, _self).get_fiscal_position(
            partner_id, delivery_id
        )
