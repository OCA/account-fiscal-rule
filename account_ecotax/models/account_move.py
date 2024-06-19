# © 2014-2023 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_ecotax = fields.Float(
        digits="Ecotax",
        string="Included Ecotax",
        store=True,
        compute="_compute_ecotax",
    )

    @api.depends("invoice_line_ids.subtotal_ecotax")
    def _compute_ecotax(self):
        for move in self:
            move.amount_ecotax = sum(move.line_ids.mapped("subtotal_ecotax"))

    # copy dependencies of the original method
    @api.depends_context("lang")
    @api.depends(
        "invoice_line_ids.currency_rate",
        "invoice_line_ids.tax_base_amount",
        "invoice_line_ids.tax_line_id",
        "invoice_line_ids.price_total",
        "invoice_line_ids.price_subtotal",
        "invoice_payment_term_id",
        "partner_id",
        "currency_id",
    )
    def _compute_tax_totals(self):
        """We will include ecotax in totals computation only
        if this method is called upon a single invoice"""
        if len(self) == 1:
            self = self.with_context(move_id=self.id)
        return super()._compute_tax_totals()
