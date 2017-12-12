# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields


class AccountTaxTransaction(models.Model):

    _name = 'account.tax.transaction'

    line_ids = fields.One2many(
        string='Transaction Lines',
        comodel_name='account.tax.transaction.line',
        inverse_name='transaction_id',
    )
    amount_tax = fields.Float(
        compute='_compute_amount_tax',
        store=True,
    )
    amount_subtotal = fields.Float(
        compute='_compute_amount_subtotal',
        store=True,
    )
    amount_total = fields.Float(
        compute='_compute_amount_total',
        store=True,
    )
    invoice_id = fields.Many2one(
        string='Invoice',
        comodel_name='account.invoice',
        compute='_compute_invoice_id',
        store=True,
    )
    invoice_line_ids = fields.Many2many(
        string='Invoice Lines',
        comodel_name='account.invoice.line',
        compute='_compute_invoice_line_ids',
        store=True,
    )
    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        related='invoice_id.partner_id',
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        related='invoice_id.company_id',
    )
    date = fields.Date(
        related='invoice_id.date',
    )

    @api.multi
    @api.depends('line_ids.amount')
    def _compute_amount_tax(self):
        for record in self:
            record.amount_tax = sum([l.amount for l in record.line_ids])

    @api.multi
    @api.depends('invoice_line_ids.price_subtotal')
    def _compute_amount_subtotal(self):
        for record in self:
            record.amount_subtotal = sum([
                l.price_subtotal for l in record.invoice_line_ids
            ])

    @api.multi
    @api.depends('amount_subtotal', 'amount_tax')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.amount_subtotal + record.amount_tax

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_invoice_id(self):
        for record in self:
            record.invoice_id = record.invoice_line_ids[0:].invoice_id.id

    @api.multi
    @api.depends('line_ids.invoice_line_ids')
    def _compute_invoice_line_ids(self):
        for record in self:
            lines = self.mapped('line_ids.invoice_line_ids')
            record.invoice_line_ids = [(6, 0, lines.ids)]

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
