# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    tax_expense = fields.Monetary(
        string="Tax Expense",
        readonly=True,
        compute="_compute_amount",
        help="Total tax amount expensed by the company",
    )
    tax_total = fields.Monetary(
        string="Tax",
        readonly=True,
        compute="_compute_amount",
        help="Total tax amount, both collected from the customer "
        "and expensed by the company.",
    )

    def _compute_amount(self):
        """ Compute the tax_expense field """
        super()._compute_amount()
        for line in self:
            taxes = {}
            if any(x.is_expensed_tax for x in line.tax_id):
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(
                    price, line.order_id.currency_id, line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id)
            line.tax_expense = taxes.get('total_expense') or 0
            line.tax_total = line.price_tax + line.tax_expense
