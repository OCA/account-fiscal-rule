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

from osv import fields, osv

class purchase_order(osv.osv):

    _inherit = 'purchase.order'

    def onchange_partner_id(self, cr, uid, ids, part, company_id=False):

        result = super(purchase_order, self ).onchange_partner_id(cr, uid, ids, part)

        if not part or not company_id or not result['value']['partner_address_id']:
            return result

        partner_address_id = result['value'].get('partner_address_id', False)
        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid,  part, partner_address_id, company_id, context={'use_domain': ('use_purchase','=',True)})

        result['value'].update(fiscal_result)

        return result

    def onchange_partner_address_id(self, cr, uid, ids, partner_address_id, company_id=False):

        result = {'value': {'fiscal_position': False}}

        if not partner_address_id or not company_id:
            return result

        partner_addr = self.pool.get('res.partner.address').browse(cr, uid, partner_address_id)
        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid,  partner_addr.partner_id.id, partner_address_id, company_id, context={'use_domain': ('use_purchase','=',True)})

        result['value'].update(fiscal_result)

        return result

    def onchange_company_id(self, cr, uid, ids, partner_id, partner_address_id=False, company_id=False):

        result = {'value': {'fiscal_position': False}}

        if not partner_id or not partner_address_id or not company_id:
            return result

        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid,  partner_id, partner_address_id, company_id, context={'use_domain': ('use_purchase','=',True)})

        result['value'].update(fiscal_result)

        return result

purchase_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
