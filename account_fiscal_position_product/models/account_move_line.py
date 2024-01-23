#  Copyright 2024 Damien Carlier - TOODIGIT
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _set_price_and_tax_after_fpos(self):
        """
        Inherit to pass product in map_tax() function on fiscal position.
        """
        super(
            AccountMoveLine,
            self.with_context(on_change_product_from_aml=self.product_id),
        )._set_price_and_tax_after_fpos()

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """
        Inherit to pass product in map_tax() function on fiscal position.
        """
        for line in self:
            super(
                AccountMoveLine,
                line.with_context(on_change_product_from_aml=line.product_id),
            )._onchange_product_id()

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        """
        Inherit to pass product in map_tax() function on fiscal position.
        """
        super(
            AccountMoveLine,
            self.with_context(on_change_product_from_aml=self.product_id),
        )._onchange_uom_id()

    @api.onchange("account_id")
    def _onchange_account_id(self):
        """
        Inherit to pass product in map_tax() function on fiscal position.
        """
        super(
            AccountMoveLine,
            self.with_context(on_change_product_from_aml=self.product_id),
        )._onchange_account_id()
