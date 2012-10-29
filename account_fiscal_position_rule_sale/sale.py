# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion                                    #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU Affero General Public License for more details.                            #
#                                                                               #
#You should have received a copy of the GNU Affero General Public License       #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from osv import fields, osv

class sale_order(osv.osv):

    _inherit = "sale.order"

    def onchange_partner_id(self, cr, uid, ids, partner_id, shop_id=False):

        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, partner_id)

        if not shop_id:
            return result

        obj_shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
        company_id = obj_shop.company_id.id

        partner_invoice_id = result['value'].get('partner_invoice_id', False)
        partner_shipping_id = result['value'].get('partner_shipping_id', False)
        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid, 
                                partner_id, partner_invoice_id,
                                partner_shipping_id, company_id,
                                context={'use_domain': ('use_sale','=',True)})

        result['value'].update(fiscal_result)

        return result

    def onchange_address_id(self, cr, uid, ids, partner_invoice_id,
                                partner_shipping_id, partner_id, shop_id=False):

        result = {'value': {}}
        if not shop_id or not partner_invoice_id:
            return result

        obj_shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
        company_id = obj_shop.company_id.id


        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid, 
                                partner_id, partner_invoice_id,
                                partner_shipping_id, company_id,
                                context={'use_domain': ('use_sale','=',True)})

        result['value'].update(fiscal_result)

        return result

    def onchange_shop_id(self, cr, uid, ids, shop_id, partner_id=None,
                        partner_invoice_id=None, partner_shipping_id=None):
        result = super(sale_order, self).onchange_shop_id(cr, uid, ids, shop_id)
        if not shop_id or not partner_id:
            return result

        obj_shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
        company_id = obj_shop.company_id.id

        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')
        fiscal_result = obj_fiscal_position_rule.fiscal_position_map(cr, uid, 
                                partner_id, partner_invoice_id,
                                partner_shipping_id, company_id,
                                context={'use_domain': ('use_sale','=',True)})

        result['value'].update(fiscal_result)

        return result

sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
