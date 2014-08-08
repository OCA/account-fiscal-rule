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

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _fiscal_position_map(self, result, **kwargs):
        ctx = dict(self._context)
        ctx.update({'use_domain': ('use_sale', '=', True)})
        return self.env['account.fiscal.position.rule'].with_context(
            ctx).apply_fiscal_mapping(result, **kwargs)

    @api.multi
    def onchange_partner_id(self, partner_id):
        ctx = dict(self._context)

        result = super(SaleOrder, self).onchange_partner_id(partner_id)

        if not ctx.get('company_id'):
            return result

        kwargs = {
            'company_id': ctx.get('company_id'),
            'partner_id': partner_id,
            'partner_invoice_id': result['value'].get(
                'partner_invoice_id', False),
            'partner_shipping_id': result['value'].get(
                'partner_shipping_id', False),
        }
        return self._fiscal_position_map(result, **kwargs)

    @api.multi
    def onchange_address_id(self, partner_invoice_id, partner_shipping_id,
                            partner_id, company_id):

        result = {'value': {}}
        if not company_id or not partner_invoice_id:
            return result

        kwargs = {
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'partner_shipping_id': partner_shipping_id,
        }
        return self._fiscal_position_map(result, **kwargs)

    @api.multi
    def onchange_company_id(self, company_id, partner_id, partner_invoice_id,
                            partner_shipping_id):

        result = {'value': {}}

        if not company_id or not partner_id:
            return result

        kwargs = {
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'partner_shipping_id': partner_shipping_id,
        }
        return self._fiscal_position_map(result, **kwargs)
