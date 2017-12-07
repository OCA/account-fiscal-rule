# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountTaxTransaction(models.Model):

    _name = 'account.tax.transaction'

    line_ids = fields.One2many(
        string='Lines',
        comodel_name='account.tax.transaction.line',
        inverse_name='transaction_id',
    )
    amount = fields.Float(
        compute='_compute_amount',
        store=True,
    )
    invoice_line_ids = fields.Many2many(
        string='Invoice Lines',
        compute='_compute_invoice_line_ids',
        store=True,
    )

    @api.multi
    @api.depends('line_ids.amount')
    def _compute_amount(self):
        for record in self:
            record.amount = sum(record.line_ids.mapped('amount'))

    @api.multi
    @api.depends('line_ids.invoice_line_ids')
    def _compute_invoice_line_ids(self):
        for record in self:
            lines = self.line_ids.mapped('invoice_line_ids')
            record.invoice_line_ids = [(6, 0, set(lines.ids))]

    @api.multi
    def write(self, vals):
        raise ValidationError(_(
            'You cannot edit a tax transaction.',
        ))

    @api.model
    def buy(self, account_invoice_tax):
        """Perform a rate purchase.

        Args:
            account_invoice_tax (AccountInvoiceTax): The
                ``account.invoice.tax`` records that should be purchased.

        Returns:
            AccountTaxTransaction: The transaction singleton that was created.
        """
        purchases = [
            (0, 0, self.line_ids.get_values_buy(tax))
            for tax in account_invoice_tax
        ]
        return self.create({
            'line_ids': [(5, 0)] + purchases,
        })

    @api.model
    def refund(self, account_invoice_tax):
        """Create a refund for a transaction.

        Args:
            account_invoice_tax (AccountInvoiceTax): The
                ``account.invoice.tax`` records that represent the tax refund.

        Returns:
            AccountTaxTransaction: The transaction singleton that was created.
        """
        refunds = [
            (0, 0, self.line_ids.get_values_refund(tax))
            for tax in account_invoice_tax
        ]
        return self.create({
            'line_ids': [(5, 0)] + refunds,
        })
