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
        compute="_compute_price",
        help="Total tax amount, collected plus expensed",
    )

    @api.one
    def _compute_price(self):
        """ Compute the tax_expense field """
        super()._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if any(x.is_expensed_tax for x in self.invoice_line_tax_ids):
            taxes = self.invoice_line_tax_ids.compute_all(
                price,
                currency,
                self.quantity,
                product=self.product_id,
                partner=self.invoice_id.partner_id,
            )
        self.tax_expense = taxes.get("total_expense", 0) if taxes else 0
        self.tax_total = self.tax_expense + self.price_tax
