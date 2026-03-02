# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _compute_account_id(self):
        res = super()._compute_account_id()
        refund_lines = self.filtered(
            lambda ml: ml.display_type == "product"
            and ml.product_id
            and ml.move_id.move_type in ("in_refund", "out_refund")
        )
        for line in refund_lines:
            product = line.with_company(line.company_id).product_id.product_tmpl_id
            if line.move_id.move_type == "in_refund":
                refund_account = (
                    product.property_account_refund_in_id
                    or product.categ_id.property_account_refund_in_categ_id
                )
            else:
                refund_account = (
                    product.property_account_refund_out_id
                    or product.categ_id.property_account_refund_out_categ_id
                )
            if refund_account:
                line.account_id = refund_account
        return res
