# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class SaleOrderTaxRate(models.AbstractModel):
    """Provides helpers for Tax Rate interfacing with Sales Orders.
    """

    _name = 'sale.order.tax.rate'
    _description = 'Sale Order Tax Rate'

    @api.model_cr_context
    def get_rate_lines(self, sale):
        return [self.get_rate_line(l) for l in sale.order_line]

    @api.model_cr_context
    def get_rate_line(self, sale_line):
        """Return values for a rate line representing multiple taxes."""
        try:
            shipping_product = sale_line.sale_id.carrier_id.product_id
            is_shipping_charge = shipping_product == sale_line.product_id
        except AttributeError:
            is_shipping_charge = False
        partner = self.get_partner(sale_line.order_id)
        company = self.get_company(sale_line.order_id)
        return {
            'company_id': company.id,
            'partner_id': partner.id,
            'product_id': sale_line.product_id.id,
            'price_unit': sale_line.price_unit,
            'discount': sale_line.discount,
            'quantity': sale_line.product_uom_qty,
            'is_shipping_charge': is_shipping_charge,
            'price_tax': sale_line.price_tax,
            'tax_ids': sale_line.tax_id.ids,
            'reference': sale_line,
        }

    @api.model_cr_context
    def get_company(self, sale):
        return sale.company_id

    @api.model_cr_context
    def get_partner(self, sale):
        return sale.partner_id.commercial_partner_id

    @api.model_cr_context
    def get_untaxed_amount(self, sale):
        return sale.amount_untaxed
