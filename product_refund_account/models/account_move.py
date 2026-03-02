# Copyright 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _reverse_moves(self, default_values_list=None, cancel=False):
        reverse_moves = super()._reverse_moves(default_values_list, cancel)
        for move in reverse_moves.filtered(
            lambda m: m.move_type in ("in_refund", "out_refund")
        ):
            for line in move.invoice_line_ids.filtered(
                lambda ml: ml.display_type == "product" and ml.product_id
            ):
                product = line.with_company(line.company_id).product_id.product_tmpl_id
                if move.move_type == "in_refund":
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
        return reverse_moves
