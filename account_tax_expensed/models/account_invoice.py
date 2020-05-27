# Copyright 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# We need to use @api.one to extend base methods using it
# pylint: disable=W8104

from odoo import api, fields, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    amount_tax_expense = fields.Monetary(
        string="Tax Expense", store=True, readonly=True, compute="_compute_amount",
    )

    @api.one
    def _compute_amount(self):
        super()._compute_amount()
        round_curr = self.currency_id.round
        self.amount_tax_expense = sum(
            round_curr(line.tax_expense) for line in self.invoice_line_ids
        )

    def _prepare_tax_line_vals(self, line, tax):
        """ Prepare values to create an account.invoice.tax line

        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        vals = super()._prepare_tax_line_vals(line, tax)
        if tax.get("amount_expense"):
            vals["amount_tax_expense"] = tax.get("amount_expense")
        return vals

    def tax_line_move_line_get(self):
        res = super().tax_line_move_line_get() or []
        for tax_line in sorted(self.tax_line_ids, key=lambda x: -x.sequence):
            if tax_line.amount_tax_expense:
                # Tax Payable move
                res.append(tax_line._prepare_tax_line_move_vals(sign=+1))
                # Tax Expense move
                res.append(tax_line._prepare_tax_line_move_vals(sign=-1))
        return res


class AccountInvoiceTax(models.Model):

    _inherit = "account.invoice.tax"

    amount_tax_expense = fields.Monetary(string="Tax Expense")

    def _prepare_tax_line_move_vals(self, sign=1):
        self.ensure_one()
        tax_line = self
        account = (
            tax_line.account_id if sign == 1 else tax_line.tax_id.expense_account_id
        )
        analytic_tag_ids = [
            (4, analytic_tag.id, None) for analytic_tag in tax_line.analytic_tag_ids
        ]
        value = {
            "invoice_tax_line_id": tax_line.id,
            "tax_line_id": tax_line.tax_id.id,
            "type": "tax",
            "name": tax_line.name,
            "price_unit": tax_line.amount_tax_expense,
            "quantity": 1 * sign,
            "price": tax_line.amount_tax_expense * sign,
            "account_id": account.id,
            "account_analytic_id": tax_line.account_analytic_id.id,
            "analytic_tag_ids": analytic_tag_ids,
            "invoice_id": self.id,
        }
        return value
