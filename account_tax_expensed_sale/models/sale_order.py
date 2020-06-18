# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    amount_tax_expense = fields.Monetary(
        string="Tax Expense", compute="_compute_amount_tax_expense",
    )

    @api.depends("order_line.tax_expense")
    def _compute_amount_tax_expense(self):
        """ Compute Expensed Tax """
        for order in self:
            round_curr = order.currency_id.round
            order.amount_tax_expense = round_curr(
                sum([line.tax_expense for line in order.order_line])
            )
