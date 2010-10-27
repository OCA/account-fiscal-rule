# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"

    def onchange_partner_id(self, cr, uid, ids, part, shop_id):

        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)

        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'partner_order_id': False, 'payment_term': False, 'fiscal_position': False}}

        if result['value']['fiscal_position']:
            return result
        
        obj_shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_shop.company_id.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id
        
        if result['value']['partner_invoice_id']:
            ptn_invoice_id = result['value']['partner_invoice_id']

        partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [result['value']['partner_invoice_id']])[0]
        
        to_country = partner_addr_default.country_id.id
        to_state = partner_addr_default.state_id.id

        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, [('company_id','=', obj_shop.company_id.id),('from_country','=',from_country),('from_state','=',from_state),('to_country','=',to_country),('to_state','=',to_state),('use_sale','=',True)])
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').browse(cr, uid, fsc_pos_id)[0]
            result['value']['fiscal_position'] = obj_fpo_rule.fiscal_position_id.id

        return result

    def onchange_partner_invoice_id(self, cr, uid, ids, ptn_invoice_id, ptn_id, shop_id):
        
        result = {'value': {'fiscal_position': False}}

        if not ptn_invoice_id or not ptn_id or not shop_id: 
            return result
  
        partner = self.pool.get('res.partner').browse(cr, uid, ptn_id)
        fiscal_position = partner.property_account_position.id or False

        if fiscal_position:
            result['value']['fiscal_position'] = fiscal_position
            return result

        obj_company = self.pool.get('sale.shop').browse(cr, uid, shop_id).company_id

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id
        
        partner_addr_invoice = self.pool.get('res.partner.address').browse(cr, uid, [ptn_invoice_id])[0]
        
        to_country = partner_addr_invoice.country_id.id
        to_state = partner_addr_invoice.state_id.id
        
        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, [('company_id','=',obj_company.id), ('from_country','=',from_country),('from_state','=',from_state),('to_country','=',to_country),('to_state','=',to_state),('use_sale','=',True)])
        
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').browse(cr, uid, fsc_pos_id)[0]
            result['value']['fiscal_position'] = obj_fpo_rule.fiscal_position_id.id

        return result

    def onchange_shop_id(self, cr, uid, ids, shop_id, ptn_id):

        result = super(sale_order, self).onchange_shop_id(cr, uid, ids, shop_id)

        if not shop_id or not ptn_id:
            return result

        partner = self.pool.get('res.partner').browse(cr, uid, ptn_id)
        fiscal_position = partner.property_account_position.id or False

        if fiscal_position:
            result['value']['fiscal_position'] = fiscal_position
            return result

        obj_shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
        obj_company = self.pool.get('res.company').browse(cr, uid, obj_shop.company_id.id)
        
        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id
        
        ptn_invoice_id = self.pool.get('res.partner').address_get(cr, uid, [ptn_id], ['invoice'])
        partner_addr_invoice = self.pool.get('res.partner.address').browse(cr, uid, [ptn_invoice_id['invoice']])[0]
        
        to_country = partner_addr_invoice.country_id.id
        to_state = partner_addr_invoice.state_id.id
        
        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, [('company_id','=',obj_company.id), ('from_country','=',from_country),('from_state','=',from_state),('to_country','=',to_country),('to_state','=',to_state),('use_sale','=',True)])
        
        if fsc_pos_id:
            obj_fpo_rule = self.pool.get('account.fiscal.position.rule').browse(cr, uid, fsc_pos_id)[0]
            result['value']['fiscal_position'] = obj_fpo_rule.fiscal_position_id.id

        return result

sale_order()
