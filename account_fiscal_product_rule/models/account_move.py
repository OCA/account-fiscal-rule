# Copyright 2022 Akretion France (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            super(
                AccountMoveLine, line.with_context(product=line.product_id)
            )._onchange_product_id()

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        for line in self:
            super(
                AccountMoveLine, line.with_context(product=line.product_id)
            )._onchange_uom_id()
