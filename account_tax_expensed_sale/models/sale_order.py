# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# We are extending a base methods that does not follow conventions
# pylint: disable=C8108

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    amount_tax_expense = fields.Monetary(
        string="Tax Expense",
        readonly=True,
        compute="_amount_all",
    )

    def _amount_all(self):
        super()._amount_all()
        for order in self:
            round_curr = order.currency_id.round
            order.amount_tax_expense = sum(
                round_curr(line.tax_expense)
                for line in order.order_line
            )
