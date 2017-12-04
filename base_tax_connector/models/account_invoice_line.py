# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    @api.multi
    @api.depends('price_unit',
                 'discount',
                 'invoice_line_tax_ids',
                 'quantity',
                 'product_id',
                 'invoice_id.partner_id',
                 'invoice_id.currency_id',
                 'invoice_id.company_id',
                 'invoice_id.date_invoice',
                 )
    def _compute_price(self):
        for invoice in self.mapped('invoice_id'):
            self.env['account.tax.rate'].get(
                'account.invoice.tax.rate', invoice,
            )
        return super(AccountInvoiceLine, self)._compute_price()
