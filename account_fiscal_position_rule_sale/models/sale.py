# -*- coding: utf-8 -*-
#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#     @author Raphaël Valyi <raphael.valyi@akretion.com>
#   Copyright 2012 Camptocamp SA
#     @author: Guewen Baconnier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _fiscal_position_map(self, **kwargs):
        ctx = dict(self._context)
        ctx.update({'use_domain': ('use_sale', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(**kwargs)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        result = super(SaleOrder, self).onchange_partner_id()
        if not self.company_id:
            return result

        kwargs = {
            'company_id': self.company_id,
            'partner_id': self.partner_id,
            'partner_invoice_id': self.partner_invoice_id,
            'partner_shipping_id': self.partner_shipping_id,
        }

        obj_fiscal_position = self._fiscal_position_map(**kwargs)
        if obj_fiscal_position is not False:
            self.fiscal_position_id = obj_fiscal_position.id

    @api.onchange('partner_invoice_id', 'partner_shipping_id')
    def _onchange_address_id(self):

        if self.company_id and self.partner_invoice_id:
            kwargs = {
                'company_id': self.company_id,
                'partner_id': self.partner_id,
                'partner_invoice_id': self.partner_invoice_id,
                'partner_shipping_id': self.partner_shipping_id,
            }
            obj_fiscal_position = self._fiscal_position_map(**kwargs)
            if obj_fiscal_position is not False:
                self.fiscal_position_id = obj_fiscal_position.id

    @api.onchange('company_id')
    def _onchange_company_id(self):

        if self.company_id and self.partner_invoice_id:
            kwargs = {
                'company_id': self.company_id,
                'partner_id': self.partner_id,
                'partner_invoice_id': self.partner_invoice_id,
                'partner_shipping_id': self.partner_shipping_id,
            }
            obj_fiscal_position = self._fiscal_position_map(**kwargs)
            if obj_fiscal_position is not False:
                self.fiscal_position_id = obj_fiscal_position.id
