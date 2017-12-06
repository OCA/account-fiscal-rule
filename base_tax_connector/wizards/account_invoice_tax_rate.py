# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountInvoiceTaxRate(models.AbstractModel):
    """Provides helpers for Tax Rate interfacing with Invoices."""

    _name = 'account.invoice.tax.rate'
    _description = 'Account Invoice Tax Rate'

    @api.model_cr_context
    def get_rate_lines(self, invoice):
        return [self.get_rate_line(l) for l in invoice.invoice_line_ids]

    @api.model_cr_context
    def get_rate_line(self, invoice_line):
        # @TODO: this is wrong
        try:
            shipping_product = invoice_line.sale_id.carrier_id.product_id
            is_shipping_charge = shipping_product == invoice_line.product_id
        except AttributeError:
            is_shipping_charge = False
        partner = self.get_partner(invoice_line.invoice_id)
        company = self.get_company(invoice_line.invoice_id)
        return {
            'company_id': company.id,
            'partner_id': partner.id,
            'product_id': invoice_line.product_id.id,
            'price_unit': invoice_line.price_unit,
            'discount': invoice_line.discount,
            'quantity': invoice_line.quantity,
            'is_shipping_charge': is_shipping_charge,
            'price_tax': 0.0,  # @TODO: invoice_line.price_tax,
            'tax_ids': invoice_line.invoice_line_tax_ids.ids,
            'reference': invoice_line,
        }

    @api.model_cr_context
    def get_company(self, invoice):
        return invoice.company_id

    @api.model_cr_context
    def get_partner(self, invoice):
        return invoice.partner_id.commercial_partner_id

    @api.model_cr_context
    def get_untaxed_amount(self, invoice):
        return invoice.amount_untaxed
