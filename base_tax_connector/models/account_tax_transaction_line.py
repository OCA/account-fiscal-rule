# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountTaxTransactionLine(models.Model):

    _name = 'account.tax.transaction.line'
    _inherit = 'account.invoice.tax'
    _description = 'Account Tax Transaction Line'

    type_transaction = fields.Selection([
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
    ],
        compute='_compute_type_transaction',
        store=True,
    )
    transaction_id = fields.Many2one(
        string='Transaction',
        comodel_name='account.tax.transaction',
        readonly=True,
    )
    invoice_line_ids = fields.Many2many(
        string='Invoice Lines',
        comodel_name='account.invoice.line',
        compute='_compute_invoice_line_ids',
        store=True,
    )
    parent_id = fields.Many2one(
        string='Purchase',
        comodel_name=_name,
        readonly=True,
    )
    child_ids = fields.One2many(
        string='Refunds',
        comodel_name=_name,
        inverse_name='parent_id',
        readonly=True,
    )

    @api.multi
    @api.depends('parent_id')
    def _compute_type_transaction(self):
        for record in self:
            _type = 'refund' if record.parent_id else 'purchase'
            record.type_transaction = _type

    @api.multi
    @api.depends('tax_id',
                 'invoice_id.invoice_line_ids.invoice_line_tax_ids',
                 )
    def _compute_invoice_line_ids(self):
        for record in self:
            lines = self._get_invoice_lines_for_tax(
                record.tax_id, record.invoice_id,
            )
            record.invoice_line_ids = [(6, 0, lines.ids)]

    @api.multi
    @api.constrains('type_transaction')
    def _check_type_transaction(self):
        for record in self:
            tx_types = record.transaction_id.mapped(
                'line_ids.type_transaction',
            )
            if len(set(tx_types)) > 1:
                raise ValidationError(_(
                    'You cannot mix refund and purchase transaction lines '
                    'in the same transaction.',
                ))

    @api.multi
    @api.constrains('invoice_line_ids')
    def _check_line_line_ids(self):
        for record in self:
            invoices = record.mapped(
                'transaction_id.invoice_line_ids.invoice_id',
            )
            if len(invoices) > 1:
                raise ValidationError(_(
                    'A tax transaction cannot represent multiple invoices at '
                    'one time. Each invoice should receive its own '
                    'transactions.'
                ))

    @api.model
    def get_values_buy(self, account_invoice_tax):
        """Return the values for the permanent storage of a rate purchase.

        Args:
            account_invoice_tax (AccountInvoiceTax): The related tax invoice.

        Returns:
            dict: The values that will be used for the creation of a new tax
                transaction.
        """
        account_invoice_tax.ensure_one()
        purchase_values = account_invoice_tax.copy_data()[0]
        return purchase_values

    @api.model
    def get_values_refund(self, account_invoice_tax):
        """Return the values to indicate the cancellation of the transaction.

        Args:
            account_invoice_tax (AccountInvoiceTax): The related tax invoice.

        Returns:
            dict: The values that will be used for the creation of a new tax
                transaction.
        """

        account_invoice_tax.ensure_one()

        original_invoice = account_invoice_tax.invoice_id.refund_invoice_id
        if not original_invoice:
            raise ValidationError(_(
                "You cannot refund a tax transaction on an invoice that is "
                "not a refund.",
            ))

        purchase = self.search([
            ('invoice_line_ids', 'in', original_invoice.invoice_line_ids.ids),
            ('tax_id', '=', account_invoice_tax.tax_id.id),
            ('account_analytic_id', '=',
             account_invoice_tax.account_analytic_id.id),
            ('account_id', '=', account_invoice_tax.account_id.id),
        ])

        if not purchase:
            raise ValidationError(_(
                "A purchase transaction was not found for this invoice's "
                "origin. You cannot refund a transaction that was not "
                "purchased.",
            ))

        refund_values = account_invoice_tax.copy_data()[0]
        refund_values.update({
            'parent_id': purchase.id,
        })

        return refund_values

    @api.model_cr_context
    def _get_invoice_lines_for_tax(self, tax, invoice):
        return invoice.invoice_line_ids.filtered(
            lambda r: tax in r.invoice_line_tax_ids,
        )
