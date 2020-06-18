# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# We need to use @api.one to extend base methods using it
# pylint: disable=W8104

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    tax_expense = fields.Monetary(
        string="Tax Expense",
        store=True,
        readonly=True,
        compute="_compute_price",
        help="Tax expense amount",
    )
    tax_total = fields.Monetary(
        string="Tax",
        store=True,
        readonly=True,
        compute="_compute_tax_total",
        help="Total tax amount, collected plus expensed",
    )

    def _get_expensed_tax_price(self):
        """
        Returns the Base Amount to use for Expensed Tax
        Can be extended to implement specific taxes.
        """
        self.ensure_one()
        return self.price_unit * (1 - (self.discount or 0.0) / 100.0)

    def _compute_price(self):
        """
        Compute the tax_expense field.
        Needs to be done on the same method computing the tax amount.
        """
        super()._compute_price()
        for line in self:
            line.tax_expense = 0
            has_expensed_tax = any(x.is_expensed_tax for x in line.invoice_line_tax_ids)
            if has_expensed_tax:
                currency = line.invoice_id.currency_id or None
                price = line._get_expensed_tax_price()
                taxes = line.invoice_line_tax_ids.compute_all(
                    price,
                    currency,
                    line.quantity,
                    product=line.product_id,
                    partner=line.invoice_id.partner_id,
                )
                line.tax_expense = taxes.get("total_expense", 0) if taxes else 0

    @api.depends("price_tax", "tax_expense")
    def _compute_tax_total(self):
        """
        Compute the Tax Total field,
        as the sum of included taxes and expensed taxes
        """
        for line in self:
            line.tax_total = line.price_tax + line.tax_expense
