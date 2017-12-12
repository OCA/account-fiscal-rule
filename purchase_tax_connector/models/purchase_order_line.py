# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for order in self.mapped('order_id'):
            self.env['account.tax.rate'].get(
                'sale.order.tax.rate', order,
            )
        return super(SaleOrderLine, self)._compute_amount()
