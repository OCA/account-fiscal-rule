# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from collections import defaultdict

from odoo import api, models, fields


_logger = logging.getLogger(__name__)


class AccountTax(models.Model):

    _inherit = 'account.tax'

    amount_type = fields.Selection(
        selection_add=[('cache', 'Cached Data')],
    )

    @api.multi
    def _compute_amount(self, base_amount, price_unit, quantity=1.0,
                        product=None, partner=None):
        """Return the cached rate if it's a cached tax, otherwise super."""
        self.ensure_one()
        if self.amount_type == 'cache':
            cached = self.env['account.tax.rate.line'].get(
                self, base_amount, price_unit, quantity, product, partner,
            )
            _logger.info('Got cached rate %s' % cached.price_tax)
            return cached and cached.price_tax or 0.0
        return super(AccountTax, self)._compute_amount(
            base_amount, price_unit, quantity, product, partner,
        )

    @api.multi
    def _get_by_group(self):
        """Return the taxes in a dictionary keyed by tax group."""
        grouped = defaultdict(self.env['account.tax'].browse)
        for tax in self:
            grouped[tax.tax_group_id] += tax
        return grouped
