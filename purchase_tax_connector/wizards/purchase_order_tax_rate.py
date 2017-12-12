# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class PurchaseOrderTaxRate(models.AbstractModel):
    """Provides helpers for Tax Rate interfacing with Purchases Orders.
    """

    _name = 'purchase.order.tax.rate'
    _description = 'Purchase Order Tax Rate'

    @api.model_cr_context
    def get_rate_lines(self, purchase):
        return [self.get_rate_line(l) for l in purchase.order_line]

    @api.model_cr_context
    def get_rate_line(self, purchase_line):
        """Return values for a rate line representing multiple taxes."""
        partner = self.get_partner(purchase_line.order_id)
        company = self.get_company(purchase_line.order_id)
        return {
            'company_id': company.id,
            'partner_id': partner.id,
            'product_id': purchase_line.product_id.id,
            'price_unit': purchase_line.price_unit,
            'discount': 0.0,
            'quantity': purchase_line.product_qty,
            'is_shipping_charge': False,
            'price_tax': purchase_line.price_tax,
            'tax_ids': purchase_line.taxes_id.ids,
            'reference': purchase_line,
        }

    @api.model_cr_context
    def get_company(self, purchase):
        return purchase.company_id

    @api.model_cr_context
    def get_partner(self, purchase):
        return purchase.partner_id.commercial_partner_id

    @api.model_cr_context
    def get_untaxed_amount(self, purchase):
        return purchase.amount_untaxed
