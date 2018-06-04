# -*- coding: utf-8 -*-
# Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#   @author Renato Lima <renato.lima@akretion.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _fiscal_position_map(self, **kwargs):
        ctx = dict(self._context)
        ctx.update({'use_domain': ('use_purchase', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(**kwargs)

    @api.onchange('partner_id', 'dest_address_id', 'company_id')
    def onchange_fiscal_position_map(self):

        kwargs = {
            'company_id': self.company_id,
            'partner_id': self.partner_id,
            'partner_invoice_id': self.partner_id,
            'partner_shipping_id': self.partner_id,
        }

        obj_fiscal_position = self._fiscal_position_map(**kwargs)
        if obj_fiscal_position:
            self.fiscal_position_id = obj_fiscal_position.id

    # re-call onchange_fiscal_position_map on onchange_partner_id cause,
    # fiscal_position_id is crush by the onchange_partner_id onchange
    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        super(PurchaseOrder, self).onchange_partner_id()
        self.onchange_fiscal_position_map()
