# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def action_move_create(self):
        """Add tax purchase/refund logic into invoice validation."""
        res = super(AccountInvoice, self).action_move_create()
        for invoice in self:
            if 'refund' in invoice.type:
                method = self.env['account.tax.group'].invoice_tax_refund
            else:
                method = self.env['account.tax.group'].invoice_tax_purchase
            _logger.info('Running %s on %s with type %s',
                         method, invoice, invoice.type)
            method(invoice)
        return res
