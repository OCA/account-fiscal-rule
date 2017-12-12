# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.multi
    def _compute_amount(self):
        for order in self.mapped('order_id'):
            self.env['account.tax.rate'].get(
                'purchase.order.tax.rate', order,
            )
        return super(PurchaseOrderLine, self)._compute_amount()
