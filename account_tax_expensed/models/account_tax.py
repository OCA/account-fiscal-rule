# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountTax(models.Model):

    _inherit = "account.tax"

    is_expensed_tax = fields.Boolean(
        help="Tax is an expense supported by the company. "
        "Invoices don't include it in customer totals."
    )
    expense_account_id = fields.Many2one(
        "account.account",
        domain=[("deprecated", "=", False)],
        string="Tax Expense Tax",
        ondelete="restrict",
        help="Account for supported tax expense."
        " The Tax Account definition should be used for the owed tax.",
    )

    @api.multi
    def compute_all(
        self, price_unit, currency=None, quantity=1.0, product=None, partner=None
    ):
        """
        Remove supported tax amounts from the "Total Included",
        so that the tax amount is not added to the invoice amounts.
        """
        taxes = super().compute_all(price_unit, currency, quantity, product, partner)
        taxes["total_expense"] = 0
        for tax_line in taxes["taxes"]:
            tax = self.browse(tax_line["id"])
            if tax.is_expensed_tax:
                amount = tax_line["amount"]
                taxes["total_included"] -= amount
                taxes["total_expense"] += amount
                tax_line["amount_expense"] = amount
                tax_line["amount"] = 0
        return taxes
