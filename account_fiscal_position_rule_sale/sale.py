# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_sale for OpenERP
#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
#     @author Raphaël Valyi <raphael.valyi@akretion.com>
#   Copyright 2012 Camptocamp SA
#     @author: Guewen Baconnier
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from osv import osv


class sale_order(osv.Model):
    _inherit = 'sale.order'

    def _fiscal_position_map(self, cr, uid, result, **kwargs):

        if not kwargs.get('context', False):
            kwargs['context'] = {}

        kwargs['context'].update({'use_domain': ('use_sale', '=', True)})
        obj_shop = self.pool.get('sale.shop').browse(
            cr, uid, kwargs.get('shop_id'))
        company_id = obj_shop.company_id.id
        kwargs.update({'company_id': company_id})
        fp_rule_obj = self.pool.get('account.fiscal.position.rule')
        return fp_rule_obj.apply_fiscal_mapping(cr, uid, result, **kwargs)

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if not context:
            context = {}

        result = super(sale_order, self).onchange_partner_id(
            cr, uid, ids, partner_id, context=context)

        if not context.get('shop_id'):
            return result

        values = result['value']
        kwargs = {
            'shop_id': context['shop_id'],
            'partner_id': partner_id,
            'partner_invoice_id': values.get('partner_invoice_id', False),
            'partner_shipping_id': values.get('partner_shipping_id', False),
            'context': context
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_address_id(self, cr, uid, ids, partner_invoice_id,
                            partner_shipping_id, partner_id,
                            shop_id=False, context=None, **kwargs):

        if not context:
            context = {}

        result = {'value': {}}
        if not shop_id or not partner_invoice_id:
            return result

        kwargs.update({
            'shop_id': shop_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'partner_shipping_id': partner_shipping_id,
            'context': context
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_shop_id(self, cr, uid, ids, shop_id, context=None,
                         partner_id=None, partner_invoice_id=None,
                         partner_shipping_id=None, **kwargs):

        if not context:
            context = {}

        result = {'value': {}}
        if not shop_id or not partner_id:
            return result

        kwargs.update({
            'shop_id': shop_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'partner_shipping_id': partner_shipping_id,
            'context': context
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)
