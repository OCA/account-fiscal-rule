# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'
    #
    # @api.multi
    # def get_taxes_values(self):
    #     for invoice in self:
    #         self.env['account.tax.rate'].get(
    #             'account.invoice.tax.rate', invoice,
    #         )
    #     return super(AccountInvoice, self).get_taxes_values()
    #
    # @api.multi
    # def invoice_validate(self):
    #     # Re-prime the rate caches
    #     super(AccountInvoice, self).invoice_validate()
