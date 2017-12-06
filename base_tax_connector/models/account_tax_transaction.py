# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountTaxTransaction(models.Model):

    _name = 'account.tax.transaction'
    _inherit = 'account.invoice.tax'

    type_transaction = fields.Selection([
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
    ],
        compute='_compute_type_transaction',
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
    invoice_line_ids = fields.Many2many(
        string='Invoice Lines',
        comodel_name='account.invoice.line',
        compute='_compute_invoice_line_ids',
        store=True,
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
            AccountTaxTransaction: The transactions that were created.
        """
        purchases = self.browse()
        for tax in account_invoice_tax:
            purchase_values = self.get_values_buy(tax)
            purchases += self.create(purchase_values)
        return purchases

    @api.model
    def refund(self, account_invoice_tax):
        """Create a refund for a transaction.

        Args:
            account_invoice_tax (AccountInvoiceTax): The
                ``account.invoice.tax`` records that represent the tax refund.

        Returns:
            AccountTaxTransaction: The transactions that were created.
        """
        refunds = self.browse()
        for tax in account_invoice_tax:
            refunds += self._refund(tax)
        return refunds

    @api.model
    def _refund(self, account_invoice_tax):
        """Perform the refund creation for an invoice tax singleton."""

        account_invoice_tax.ensure_one()

        original_invoice = account_invoice_tax.invoice_id.refund_invoice_id
        if not original_invoice:
            raise ValidationError(_(
                "You cannot refund a tax transaction on an invoice that is "
                "not a refund.",
            ))

        purchase = self.search([
            ('invoice_id', '=',original_invoice.id),
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

        refund_values = purchase.get_values_refund(account_invoice_tax)

        return self.create(refund_values)

    @api.model
    def get_values_buy(self, account_invoice_tax):
        """Return the values for the permanent storage of a rate purchase.

        These will be passed into ``create`` during ``buy``.

        Connectors should inherit this to provide tax purchasing
        functionality, calling the super and editing the values where
        required.


        """
        purchase_values = account_invoice_tax.copy_data()[0]
        return purchase_values

    @api.multi
    def get_values_refund(self, account_invoice_tax):
        """Return the values to indicate the cancellation of the transaction.

        These will be passed into ``create`` during ``refund``.

        Connectors should inherit this to provide cancellation of existing
        transactions, calling the super and editing the values where
        required.

        Args:
            account_invoice_tax (AccountInvoiceTax): The related tax invoice.

        Returns:
            dict: The values that will be used for the creation of a new tax
                transaction.
        """

        self.ensure_one()

        refund_values = self.copy_data()[0]
        refund_values.update({
            'parent_id': self.id,
        })

        return refund_values

    @api.model_cr_context
    def _get_invoice_lines_for_tax(self, tax, invoice):
        return invoice.invoice_line_ids.filtered(
            lambda r: tax in r.invoice_line_tax_ids,
        )
