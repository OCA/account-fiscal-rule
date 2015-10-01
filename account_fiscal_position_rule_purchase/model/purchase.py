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

from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _fiscal_position_map(self, result, **kwargs):
        ctx = dict(self._context)
        ctx.update({'use_domain': ('use_purchase', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(result, **kwargs)

    @api.multi
    def onchange_partner_id(self, partner_id):
        ctx = dict(self._context)
        result = super(PurchaseOrder, self).onchange_partner_id(partner_id)

        if not partner_id or not ctx.get('company_id'):
            return result

        kwargs = {
            'company_id': ctx.get('company_id'),
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': partner_id,
        }
        return self._fiscal_position_map(result, **kwargs)

    @api.multi
    def onchange_dest_address_id(self, dest_address_id):
        ctx = dict(self._context)
        result = {'value': {'fiscal_position': False}}

        if not ctx.get('partner_id') and not ctx.get('company_id'):
            return result

        kwargs = {
            'company_id': ctx.get('company_id'),
            'partner_id': ctx.get('partner_id'),
            'partner_invoice_id': ctx.get('partner_id'),
            'partner_shipping_id': dest_address_id,
        }
        return self._fiscal_position_map(result, **kwargs)

    @api.multi
    def onchange_company_id(self, partner_id, dest_address_id, company_id):

        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        kwargs = {
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': dest_address_id,
        }
        return self._fiscal_position_map(result, **kwargs)
