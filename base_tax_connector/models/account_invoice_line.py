# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models


_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    @api.multi
    def _compute_price(self):
        origin = getattr(self, '_origin', None)
        for invoice in self.mapped('invoice_id'):
            self.env['account.tax.rate'].get(
                'account.invoice.tax.rate',
                invoice,
                origin and origin.invoice_id,
            )
        _logger.info(
            'Rates primed for invoice lines. In onchange? %s & %s',
            self.env.in_onchange, self.env.in_draft,
        )
        return super(AccountInvoiceLine, self)._compute_price()
