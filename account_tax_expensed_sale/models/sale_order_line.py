# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
        compute="_compute_tax_total",
        help="Total tax amount, both collected from the customer "
        "and expensed by the company.",
    )

    def _get_expensed_tax_price(self):
        """
        Returns the Base Amount to use for Expensed Tax
        Can be extended to implement specific taxes.
        """
        self.ensure_one()
        return self.price_unit * (1 - (self.discount or 0.0) / 100.0)

    def _compute_amount(self):
        """
        Compute the Tax Expense field
        Needs to be done on the same method computing the tax amount.
        """
        super()._compute_amount()
        for line in self:
            line.tax_expense = 0
            has_expensed_tax = any(x.is_expensed_tax for x in line.tax_id)
            if has_expensed_tax:
                price = line._get_expensed_tax_price()
                taxes = line.tax_id.compute_all(
                    price,
                    line.order_id.currency_id,
                    line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )
                line.tax_expense = taxes["total_expense"]
                line.price_tax = 0
                line.price_total = line.price_subtotal

    @api.depends("price_tax", "tax_expense")
    def _compute_tax_total(self):
        """
        Compute the Tax Total field,
        as the sum of included taxes and expensed taxes
        """
        for line in self:
            line.tax_total = line.price_tax + line.tax_expense
