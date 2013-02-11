# -*- encoding: utf-8 -*-
###############################################################################
#
#   account_fiscal_position_rule_purchase for OpenERP
#   Copyright (C) 2009-TODAY Akretion <http://www.akretion.com>
#     @author Renato Lima <renato.lima@akretion.com>
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


class purchase_order(osv.Model):
    _inherit = 'purchase.order'

    def _fiscal_position_map(self, cr, uid, result, **kwargs):

        if not kwargs.get('context', False):
            kwargs['context'] = {}

        kwargs['context'].update({'use_domain': ('use_purchase', '=', True)})
        fp_rule_obj = self.pool.get('account.fiscal.position.rule')
        return fp_rule_obj.apply_fiscal_mapping(cr, uid, result, kwargs)

    def onchange_partner_id(self, cr, uid, ids, partner_id, company_id=None,
                            context=None, **kwargs):
        if not context:
            context = {}

        result = super(purchase_order, self).onchange_partner_id(
            cr, uid, ids, partner_id)

        if not partner_id or not company_id:
            return result

        kwargs.update({
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': partner_id,
            'context': context
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_dest_address_id(self, cr, uid, ids, partner_id,
                                dest_address_id, company_id=None,
                                context=None, **kwargs):
        if not context:
            context = {}

        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        kwargs.update({
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': dest_address_id,
            'context': context
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_company_id(self, cr, uid, ids, partner_id,
                            dest_address_id=False, company_id=False,
                            context=None, **kwargs):
        if not context:
            context = {}

        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        kwargs.update({
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': dest_address_id,
            'context': context
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)
