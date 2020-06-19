# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    amount_tax_expense = fields.Monetary(string="Tax Expense", compute="_amount_all")

    def _amount_all(self):
        """
        Compute Expensed Tax
        Correct the previously computed tax, deducting the expensed tax
        """
        super()._amount_all()
        for order in self:
            order.amount_tax_expense = sum(
                line.tax_expense for line in order.order_line
            )
            order.amount_tax -= order.amount_tax_expense
            order.amount_total -= order.amount_tax_expense
