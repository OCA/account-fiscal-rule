# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = 'stock.invoice.onshipping'

    @api.multi
    def _build_invoice_values_from_pickings(self, pickings):
        values = super(StockInvoiceOnshipping, self
                       )._build_invoice_values_from_pickings(pickings)
        picking = fields.first(pickings)
        values['fiscal_position_id'] = picking.fiscal_position_id.id
        return values
