# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models, fields


_logger = logging.getLogger(__name__)


class AccountTax(models.Model):

    _inherit = 'account.tax'

    amount_type = fields.Selection(
        selection_add=[('cache', 'Cached Data')],
    )
    cache_location = fields.Char(
        help='This is the location of the cache store. It is an '
             'arbitrary string that is primarily meant for connectors to '
             'identify themselves.',
    )
    cache_by_group = fields.Boolean(
        help='Check this to perform caching at the group level, instead of '
             'the tax level. If using a connector mechanism, enabling this '
             'will allow for more accurate lookups as well as reduce the '
             'amount of API calls to the external system.',
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
