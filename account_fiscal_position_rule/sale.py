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

    def onchange_partner_id(self, cr, uid, ids, part):

        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)

        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'partner_order_id': False, 'payment_term': False, 'fiscal_position': False}}

        if result['value']['fiscal_position']:
            return result

        #Use the current user to get the company_id
        partner_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]
        
        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        if result['value']['partner_invoice_id']:
            ptn_invoice_id = result['value']['partner_invoice_id']

        partner_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [ptn_invoice_id])[0]

        to_country = partner_addr_default.country_id.id
        to_state = partner_addr_default.state_id.id
        
        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, [('from_country','=',from_country),('from_state','=',from_state),('to_country','=',to_country),('to_state','=',to_state),('use_sale','=',True)])
        if fsc_pos_id: 
            result['value']['fiscal_position'] = fsc_pos_id[0]
        
        return result
        
        
    def onchange_partner_invoice_id(self, cr, uid, ids, ptn_invoice_id, ptn_id, usr_id):
        
        result = {'value': {'fiscal_position': False}}

        if not usr_id or not ptn_invoice_id or not ptn_id:
            return result
  
        partner = self.pool.get('res.partner').browse(cr, uid, ptn_id)
        fiscal_position = partner.property_account_position and partner.property_account_position.id or False

        if fiscal_position:
            result['value']['fiscal_position'] = fiscal_position
            return result

        user_partner_id = self.pool.get('res.users').browse(cr, uid, usr_id).company_id.partner_id

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [user_partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id
        
        partner_addr_invoice = self.pool.get('res.partner.address').browse(cr, uid, [ptn_invoice_id])[0]
        
        to_country = partner_addr_invoice.country_id.id
        to_state = partner_addr_invoice.state_id.id
        
        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, [('from_country','=',from_country),('from_state','=',from_state),('to_country','=',to_country),('to_state','=',to_state),('use_sale','=',True)])
        if fsc_pos_id:
            result['value']['fiscal_position'] = fsc_pos_id[0]

        return result

    def onchange_user_id(self, cr, uid, ids, usr_id, ptn_id, ptn_invoice_id):

        result = {'value': {'fiscal_position': False}}

        if not usr_id or not ptn_id or not ptn_invoice_id:
            return result

        partner = self.pool.get('res.partner').browse(cr, uid, ptn_id)
        fiscal_position = partner.property_account_position and partner.property_account_position.id or False

        if fiscal_position:
            result['value']['fiscal_position'] = fiscal_position
            return result

        user_partner_id = self.pool.get('res.users').browse(cr, uid, usr_id).company_id.partner_id

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [user_partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id
        
        partner_addr_invoice = self.pool.get('res.partner.address').browse(cr, uid, [ptn_invoice_id])[0]
        
        to_country = partner_addr_invoice.country_id.id
        to_state = partner_addr_invoice.state_id.id
        
        fsc_pos_id = self.pool.get('account.fiscal.position.rule').search(cr, uid, [('from_country','=',from_country),('from_state','=',from_state),('to_country','=',to_country),('to_state','=',to_state),('use_sale','=',True)])
        if fsc_pos_id:
            result['value']['fiscal_position'] = fsc_pos_id[0]

        return result

sale_order()