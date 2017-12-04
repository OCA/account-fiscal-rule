# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountTaxTransaction(models.Model):

    _name = 'account.tax.transaction'
    _inherit = 'account.tax.rate'

    line_ids = fields.One2many(
        string='Lines',
        comodel_name='account.tax.transaction.line',
        inverse_name='rate_id',
    )
    date_transaction = fields.Datetime(
        string='Transaction Date',
        default=lambda s: fields.Datetime.now(),
        required=True,
    )
    type_transaction = fields.Selection([
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
    ],
        required=True,
    )
    parent_id = fields.Many2one(
        string='Parent',
        comodel_name=_name,
        readonly=True,
    )
    child_ids = fields.One2many(
        string='Children',
        comodel_name=_name,
        inverse_name='parent_id',
        readonly=True,
    )

    @api.multi
    def write(self, vals):
        raise ValidationError(_(
            'You cannot edit a tax transaction. You should instead create '
            'child transaction(s).'
        ))

    @api.model
    def buy(self, rate):
        """Perform a rate purchase."""
        rate_values = self.get_values_buy(rate)
        rate_values['line_ids'] = [
            (0, 0, l) for l in rate_values['line_ids']
        ]
        return self.create(rate_values)

    @api.multi
    def refund(self, lines=None):
        """Create a refund for a transaction."""
        refund_values = self.get_values_refund(lines)
        refund_values['line_ids'] = [
            (0, 0, l) for l in refund_values['line_ids']
        ]
        return self.create(refund_values)

    @api.model
    def get_values_buy(self, rate):
        """Return the values for the permanent storage of a rate purchase.

        These will be passed into ``create`` during ``buy``.

        Connectors should inherit this to provide tax purchasing
        functionality, calling the super and editing the values where
        required.
        """
        rate_values = rate.copy_data()[0]
        rate_values.update({
            'line_ids': rate.line_ids.copy_data(),
            'type_transaction': 'purchase',
        })
        return rate_values

    @api.multi
    def get_values_refund(self, lines=None):
        """Return the values to indicate the cancellation of the transaction.

        These will be passed into ``create`` during ``refund``.

        Connectors should inherit this to provide cancellation of existing
        transactions.

        Args:
            lines (AccountTaxTransactionLine, optional): The lines to refund.
            If no lines are provided, all lines in the transaction will be
            refunded.

        Raises:
            ValidationError: In the event of line/transaction mis-matches.
        """

        self.ensure_one()

        if lines is None:
            lines = self.line_ids
        else:

            transactions = lines.mapped('rate_id')
            if len(transactions) != 1:
                raise ValidationError(_(
                    'You cannot refund lines from different transactions.',
                ))
            elif transactions[0].rate_id != self:
                raise ValidationError(_(
                    'You are trying to refund lines from a transaction that '
                    'is not selected.'
                ))

        refund_values = self.copy_data()[0]
        refund_values.update({
            'line_ids': lines.copy_data(),
            'type_transaction': 'refund',
            'parent_id': self.id,
        })
        return refund_values
