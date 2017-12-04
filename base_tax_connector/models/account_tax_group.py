# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class AccountTaxGroup(models.Model):

    _inherit = 'account.tax.group'

    cache_name = fields.Char(
        help='This is the name of the cache store. It is an '
             'arbitrary string that is primarily meant for connectors to '
             'identify themselves.',
    )

    @api.multi
    def compute_cache_rate(self, base_amount, rate_line_values):
        """Compute the cached rates for the ``account.tax.rate.line`` records.

        This method should be inherited by connectors in order to get rates
        from an external source. A singleton is guaranteed.

        Connector methods should call super, then edit and return the values.

        Args:
            base_amount (float): The base amount that the taxes are being
                applied on. This is typically the subtotal.
            rate_line_values (list(dict)): List of rate line values.

        Returns:
            rate_line_values (list(dict)): The same input, but with rates
                adjusted by any tax connectors. They will be written to the
                cache during ``account.tax.rate.get_rate_values``.
        """
        self.ensure_one()
        _logger.debug('Computing rate for %s with base amount %s. Lines:\n%s',
                      self, base_amount, rate_line_values)
        return rate_line_values
