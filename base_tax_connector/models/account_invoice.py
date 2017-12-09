# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def invoice_validate(self):
        """Add tax purchase/refund logic into invoice validation."""
        res = super(AccountInvoice, self).invoice_validate()
        for invoice in self:
            if 'refund' in invoice.type:
                method = self.env['account.tax.group'].invoice_tax_refund
            else:
                method = self.env['account.tax.group'].invoice_tax_purchase
            method(invoice)
        return res
